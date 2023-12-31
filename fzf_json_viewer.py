#!/usr/bin/env python
import argparse
import json
import subprocess
import sys
from http.server import HTTPServer
from subprocess import PIPE

import convert_format
import fzf_options
import internal_server


def execute_fzf(input_text, server_port, fzf_port):
    cmd = [
        "fzf",
        "--listen",
        str(fzf_port),
        "--ansi",
        "--print-query",
        "--expect",
        "enter",
        "--bind",
        "alt-c:execute-silent(echo {} | tr -d '\n' | pbcopy)",
    ]
    cmd += fzf_options.get_default_mode_options(server_port)

    proc = subprocess.run(cmd, input=input_text, stdout=PIPE, text=True)
    return proc.stdout


def find_available_port():
    httpd = HTTPServer(("", 0), None)
    return httpd.server_port


def main(args, options):
    input_text = sys.stdin.read()
    if input_text.lstrip()[0] == "[":
        proc = subprocess.run(
            "jq -c '.[]'", shell=True, input=input_text, stdout=PIPE, text=True
        )
        input_json = proc.stdout.rstrip()

        server_port = internal_server.start_server(input_json)
        fzf_port = find_available_port()
        internal_server.set_fzf_port(fzf_port)

        stdout = execute_fzf(input_json, server_port, fzf_port)
    else:
        input_json = json.loads(input_text)
        if not options["no_aws_tags"]:
            input_json = convert_format.optimize_aws_tags(input_json)
        keys = fzf_options.collect_keys(input_json)

        server_port = internal_server.start_server(input_json)
        fzf_port = find_available_port()
        internal_server.set_fzf_port(fzf_port)

        key_list = fzf_options.get_key_list(keys)
        input_text = fzf_options.get_input_text(key_list)
        stdout = execute_fzf(input_text, server_port, fzf_port)

    if len(stdout.strip()) > 0:
        args = stdout.rstrip().split("\n")[2:]
        input_json = internal_server.get_input_json_from_memory()
        output = fzf_options.get_selected_part_text(input_json, args, clipboard=True)
        print(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--no_aws_tags", action="store_true")
    args = p.parse_args()
    main(sys.argv, args.__dict__)
