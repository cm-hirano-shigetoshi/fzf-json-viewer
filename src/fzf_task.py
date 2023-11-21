import json
import subprocess
import sys
from dataclasses import dataclass, field
from subprocess import PIPE

from control_server import ControlServer
from fzf import FzfTask

PYTHON = "python"


def _get_src_list(input_json):
    def quote(s):
        if ":" in s:
            return f'"{s}"'
        else:
            return s

    def _collect_keys(json, prefix=None):
        keys = []
        for key, value in json.items():
            k = quote(f".{key}")
            key_with_prefix = prefix + [k] if prefix else [k]
            keys.append(key_with_prefix)
            if isinstance(value, dict):
                keys.extend(_collect_keys(value, key_with_prefix))
            elif isinstance(value, list) and value:
                # For lists, consider the first item alone as per the request.
                if isinstance((value[0]), dict):
                    # If the first item is a dictionary, recurse with an updated prefix.
                    keys.extend(
                        _collect_keys(value[0], prefix=key_with_prefix + [".[]"])
                    )
        return keys

    return [["."]] + _collect_keys(input_json)


def _optimize_aws_tags(data):
    # If the data is a dict, we can apply our optimization
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # We target the 'Tags' key specifically
            if key == "Tags" and isinstance(value, list):
                tag_dict = {}
                for item in value:
                    # The value should be a dict with 'Key' and 'Value'
                    if isinstance(item, dict) and "Key" in item and "Value" in item:
                        tag_dict[item["Key"]] = item["Value"]
                    else:
                        # If not in the expected format, return the original data without changes
                        return data
                new_dict[key] = tag_dict
            else:
                # For all other keys, we keep their values, potentially optimized if they're dicts too
                new_dict[key] = _optimize_aws_tags(value)
        # The new dict has been fully constructed and is returned
        return new_dict
    # If the data is a list, we apply our function to all its elements and return a new list
    elif isinstance(data, list):
        return [_optimize_aws_tags(i) for i in data]
    else:
        # If the data is neither a dict nor a list, we can't do anything with it and return it as it is
        return data


def _decorate_selector(s):
    elements = []
    for i, e in enumerate(s.split("|.[]|"), start=1):
        elements.append(f"\033[{30+i}m{e}\033[0m")
    sp = elements[-1].split("|")
    elements[-1] = "|".join(sp[:-1] + ["\033[1m" + sp[-1]])
    return "|.[]|".join(elements)


@dataclass
class FzfSelectKeys(FzfTask):
    input_json: dict
    optimize_aws_tags: bool = True
    server: ControlServer = field(default=None)
    options: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.optimize_aws_tags:
            self.input_json = _optimize_aws_tags(self.input_json)
        self.options = {
            "--multi": True,
            "--ansi": True,
            "--reverse": True,
            "--preview": self.get_preview_cmd(),
            "--bind": "alt-c:execute-silent(echo {} | tr -d '\n' | pbcopy)",
            "--bind": f'alt-f:execute-silent(curl "https://localhost:{self.server.port}?port=$FZF_PORT&aaa=bbb")',
        }

    def get_src_list(self):
        src_list = _get_src_list(self.input_json)
        selectors = ["|".join(x) for x in src_list]
        return [_decorate_selector(selector) for selector in selectors]

    def get_preview_cmd(self):
        return f"{PYTHON} {__file__} 'selected' {self.server.port} {{+}}"


"""
preview
"""


def _make_query(pos, args):
    if len(args) == 1:
        return "|".join(args[0])
    common = "|".join(args[0][:pos])
    array = []
    for a in args:
        array.append(f'({"|".join(a[pos:])})')
    if len(common) > 0:
        jq_command = f"{common}|" + f'[{",".join(array)}]'
    else:
        jq_command = f'[{",".join(array)}]'
    return jq_command


def _common_prefix_length(args):
    min_length = 9999
    for i in range(len(args) - 1):
        for j in range(i + 1, len(args)):
            (a, b) = (args[i], args[j])
            if a == b:
                min_length = len(a) if len(a) < min_length else min_length
            common_length = 0
            for k in range(min(len(a), len(b))):
                if a[k] == b[k]:
                    common_length += 1
                else:
                    min_length = (
                        common_length if common_length < min_length else min_length
                    )
    return min_length


def _get_selected_part_text(input_json, items):
    arg_list = [x.split("|") for x in items]
    if len(items) == 1:
        pos = -1
    else:
        pos = _common_prefix_length(arg_list)
    jq_command = _make_query(pos, arg_list)

    cmd = ["jq", "-c", jq_command]
    proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def _is_complex(d_str):
    return "\n" not in d_str.rstrip("\n")


def _format_via_jq(d_str, tty=True, compact="auto"):
    cmd = ["jq"]
    if tty:
        cmd.append("-C")
    if compact.lower() == "auto":
        if not _is_complex(d_str):
            cmd.append("-c")
    elif compact.lower() == "true":
        cmd.append("-c")

    proc = subprocess.run(cmd, input=d_str, stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def _get_input_json_from_server(port):
    cmd = ["curl", f"http://localhost:{port}?get_input=json"]
    proc = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    return json.loads(proc.stdout)


def preview(mode, port, args):
    input_json = _get_input_json_from_server(port)
    if mode == "selected":
        print(_format_via_jq(_get_selected_part_text(input_json, args)))
    elif mode == "filtered":
        print(
            _format_via_jq(
                fzf_options.get_filtered_json(input_json, args[0], args[1]),
                compact="false",
            )
        )


if __name__ == "__main__":
    mode = sys.argv[1]
    port = sys.argv[2]
    preview(mode, port, sys.argv[3:])
