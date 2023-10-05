import json
import subprocess
import urllib.parse
from os.path import dirname, realpath
from subprocess import PIPE

SCRIPT_PATH = dirname(__file__)


def decorate(s, bold=False, color=None):
    if not bold and not color:
        return f"\033[33m{s}\033[0m"
    # Unsupported
    return s


def get_input_text(key_list):
    return "\n".join(
        ["|".join(k.split("|")[:-1] + [decorate(k.split("|")[-1])]) for k in key_list]
    )


def get_select_condition_list(lines, selector, selected):
    def _rindex(ls, s):
        return len(ls) - ls[::-1].index(s) - 1

    def _make_select_condition(base, selected):
        conditions = []
        for s in selected.split(","):
            conditions.append(f'{base}=="{s}"')
        return [f'select({"or".join(conditions)})']

    def _make_query(line, selector, selected):
        sp = selector.split("|")
        selector_depth = sp.count(".[]")
        if line.count(".[]") < selector_depth:
            return line
        else:
            base = "".join(sp[_rindex(sp, ".[]") + 1 :])
            return (
                line[: _rindex(line, ".[]") + 1]
                + _make_select_condition(base, selected)
                + line[_rindex(line, ".[]") + 1 :]
            )

    return [_make_query(line, selector, selected) for line in lines]


def collect_keys(json, prefix=None):
    keys = []
    for key, value in json.items():
        key_with_prefix = prefix + [f".{key}"] if prefix else [f".{key}"]
        keys.append(key_with_prefix)
        if isinstance(value, dict):
            keys.extend(collect_keys(value, key_with_prefix))
        elif isinstance(value, list) and value:
            # For lists, consider the first item alone as per the request.
            if isinstance(value[0], dict):
                # If the first item is a dictionary, recurse with an updated prefix.
                keys.extend(collect_keys(value[0], prefix=key_with_prefix + [".[]"]))
    return keys


def get_key_list(keys):
    lines = []
    for elems in keys:
        lines.append("|".join(elems))
    return lines


def common_prefix_length(args):
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


def make_query(pos, args):
    common = "|".join(args[0][:pos])
    array = []
    for a in args:
        array.append(f'({"|".join(a[pos:])})')
    if len(common) > 0:
        jq_command = f"{common}|" + f'[{",".join(array)}]'
    else:
        jq_command = f'[{",".join(array)}]'
    return jq_command


def get_selected_part_text(input_json, items, clipboard=False):
    arg_list = [x.split("|") for x in items]
    if len(items) == 1:
        pos = -1
    else:
        pos = common_prefix_length(arg_list)
    jq_command = make_query(pos, arg_list)

    if clipboard:
        cmd = f"jq -c '{jq_command}' | tee | pbcopy"
        proc = subprocess.run(
            cmd, input=json.dumps(input_json), shell=True, stdout=PIPE, text=True
        )
    else:
        cmd = ["jq", "-c", jq_command]
        proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def get_filter_query_text(selector, specified):
    sp = selector.split("|")
    a, b, c = (sp[0], "|".join(sp[:-1]), sp[-1])
    q = f'{{{a[1:]}: [{b}|select({c} == "{specified}")]}}'
    return q


def get_filtered_json(input_json, selector, specified):
    cmd = ["jq", get_filter_query_text(selector, specified)]
    proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
    return proc.stdout


def get_preview(server_port, script_dir=dirname(realpath(__file__)), selector=None):
    cmd = f"python {script_dir}/preview.py selected {server_port} {{+}} | cat -n"
    return cmd


def get_filtered_preview_command(
    selector, server_port, script_dir=dirname(realpath(__file__))
):
    return f"python {script_dir}/preview.py filtered {server_port} '{selector}' '{{}}'"


def get_default_mode_options(server_port):
    options = [
        "--multi",
        "--reverse",
        "--prompt",
        "DEFAULT> ",
        "--keep-right",
        "--preview",
        get_preview(server_port),
        "--preview-window",
        "down:70%",
        "--bind",
        "ctrl-l:deselect-all",
        "--bind",
        "alt-l:deselect-all",
        "--bind",
        f"alt-f:execute-silent(bash {SCRIPT_PATH}/curl_internal_server.sh filter {server_port} {{+}})",
    ]
    return options


def enter_filter_mode(selector, server_port):
    reload_cmd = f"curl \"http://localhost:{server_port}?get_input=json\" | jq -r '{selector}' | sort -u"
    preview = get_filtered_preview_command(selector, server_port)
    actions = [
        f"reload({reload_cmd})",
        f"change-prompt({selector}> )",
        f"change-preview({preview})",
        "clear-query",
        "first",
    ]
    return "+".join(actions)


def enter_default_mode(selector, selected, server_port):
    selected = urllib.parse.quote(selected)
    reload_cmd = f'curl "http://localhost:{server_port}?get_input=keys:{selected}"'
    preview = get_preview(server_port, selector=selector)
    actions = [
        f"reload({reload_cmd})",
        "change-prompt(DEFAULT> )",
        f"change-preview({preview})",
        "clear-query",
        "first",
    ]
    return "+".join(actions)
