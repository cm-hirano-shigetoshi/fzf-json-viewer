import json
import subprocess
import sys
from subprocess import PIPE

import fzf_options


def format_via_jq(d, tty=True, compact=False):
    if type(d) is str:
        input_ = d
    else:
        input_ = json.dumps(d)
    cmd = ["jq"]
    if tty:
        cmd.append("-C")
    if compact:
        cmd.append("-c")
    proc = subprocess.run(cmd, input=input_, stdout=PIPE, text=True)
    return proc.stdout.rstrip()


def get_input_json_from_server(port):
    cmd = ["curl", f"http://localhost:{port}?get_input=json"]
    proc = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    return json.loads(proc.stdout)


def main(mode, port, args):
    input_json = get_input_json_from_server(port)
    if mode == "selected":
        print(
            format_via_jq(
                fzf_options.get_selected_part_text(input_json, args), compact=True
            )
        )
    elif mode == "filtered":
        print(
            format_via_jq(fzf_options.get_filtered_json(input_json, args[0], args[1]))
        )


if __name__ == "__main__":
    mode = sys.argv[1]
    port = sys.argv[2]
    main(mode, port, sys.argv[3:])
