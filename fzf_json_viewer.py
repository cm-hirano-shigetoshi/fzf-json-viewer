#!/usr/bin/env python
import json
import subprocess
import sys
from http.server import HTTPServer
from subprocess import PIPE

import fzf_options
import internal_server
import preview


def serialize(elems):
    return "." + "|.".join(elems)


def get_key_list(keys):
    lines = []
    for elems in keys:
        lines.append(serialize(elems))
    return "\n".join(lines)


def execute_fzf(keys, fzf_port):
    key_list = get_key_list(keys)
    cmd = [
        "fzf",
        "--listen",
        str(fzf_port),
    ]
    cmd += fzf_options.get_options("default")

    proc = subprocess.run(cmd, input=key_list, stdout=PIPE, text=True)
    args = proc.stdout.rstrip().split("\n")

    input_json = internal_server.get_input_json_from_memory()
    print(preview.get_selected_part_text(input_json, args))


def collect_keys(json, prefix=None):
    keys = []
    for key, value in json.items():
        key_with_prefix = prefix + [key] if prefix else [key]
        keys.append(key_with_prefix)
        if isinstance(value, dict):
            keys.extend(collect_keys(value, key_with_prefix))
        elif isinstance(value, list) and value:
            # For lists, consider the first item alone as per the request.
            if isinstance(value[0], dict):
                # If the first item is a dictionary, recurse with an updated prefix.
                keys.extend(collect_keys(value[0], prefix=key_with_prefix + ["[]"]))
    return keys


def find_available_port():
    httpd = HTTPServer(("", 0), None)
    return httpd.server_port


def main(args):
    input_json = json.loads(sys.stdin.read())
    keys = collect_keys(input_json)

    server_port = internal_server.start_server(input_json)
    fzf_options.set_server_port(server_port)

    fzf_port = find_available_port()
    internal_server.set_fzf_port(fzf_port)

    execute_fzf(keys, fzf_port)


if __name__ == "__main__":
    main(sys.argv)
