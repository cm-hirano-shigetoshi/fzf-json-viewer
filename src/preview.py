import json
import subprocess
import sys
from subprocess import PIPE


def make_query(pos, args):
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


def get_selected_part_text(input_json, items):
    arg_list = [x.split("|") for x in items]
    if len(items) == 1:
        pos = -1
    else:
        pos = common_prefix_length(arg_list)
    jq_command = make_query(pos, arg_list)

    cmd = ["jq", "-c", jq_command]
    proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def is_complex(d_str):
    return "\n" not in d_str.rstrip("\n")


def format_via_jq(d_str, tty=True, compact="auto"):
    cmd = ["jq"]
    if tty:
        cmd.append("-C")
    if compact.lower() == "auto":
        if not is_complex(d_str):
            cmd.append("-c")
    elif compact.lower() == "true":
        cmd.append("-c")

    proc = subprocess.run(cmd, input=d_str, stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def get_input_json_from_server(port):
    cmd = ["curl", f"http://localhost:{port}?get_input=json"]
    proc = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    return json.loads(proc.stdout)


def main(mode, port, args):
    input_json = get_input_json_from_server(port)
    if mode == "selected":
        print(format_via_jq(get_selected_part_text(input_json, args)))
    elif mode == "filtered":
        print(
            format_via_jq(
                fzf_options.get_filtered_json(input_json, args[0], args[1]),
                compact="false",
            )
        )


if __name__ == "__main__":
    mode = sys.argv[1]
    port = sys.argv[2]
    main(mode, port, sys.argv[3:])
