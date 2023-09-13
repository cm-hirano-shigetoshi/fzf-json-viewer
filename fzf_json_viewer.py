#!/usr/bin/env python
import json
import subprocess
import sys
from http.server import HTTPServer
from subprocess import PIPE

import fzf_options
import internal_server


def execute_fzf(keys, server_port, fzf_port):
    key_list = fzf_options.get_key_list(keys)
    cmd = [
        "fzf",
        "--listen",
        str(fzf_port),
    ]
    cmd += fzf_options.get_default_mode_options(server_port)

    proc = subprocess.run(cmd, input="\n".join(key_list), stdout=PIPE, text=True)
    return proc.stdout


def find_available_port():
    httpd = HTTPServer(("", 0), None)
    return httpd.server_port


def main(args):
    input_json = json.loads(sys.stdin.read())
    keys = fzf_options.collect_keys(input_json)

    server_port = internal_server.start_server(input_json)
    fzf_port = find_available_port()
    internal_server.set_fzf_port(fzf_port)

    stdout = execute_fzf(keys, server_port, fzf_port)

    if len(stdout.strip()) > 0:
        args = stdout.rstrip().split("\n")
        input_json = internal_server.get_input_json_from_memory()
        print(fzf_options.get_selected_part_text(input_json, args))


if __name__ == "__main__":
    main(sys.argv)
