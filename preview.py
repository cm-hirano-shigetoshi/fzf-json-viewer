import json
import subprocess
import sys
from subprocess import PIPE

import fzf_options


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
        print(format_via_jq(fzf_options.get_selected_part_text(input_json, args)))
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
