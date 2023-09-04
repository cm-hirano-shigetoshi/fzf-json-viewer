#!/usr/bin/env python
import json
import subprocess
import sys
from os.path import dirname, realpath
from subprocess import PIPE


def serialize(elems):
    return "." + "|.".join(elems)


def get_key_list(keys):
    lines = []
    for elems in keys:
        lines.append(serialize(elems))
    return "\n".join(lines)


def get_preview(target_json, script_dir=dirname(realpath(__file__))):
    return f"python {script_dir}/preview.py {target_json} {{+}} | cat -n"


def execute_fzf(keys, target_json):
    key_list = get_key_list(keys)
    preview = get_preview(target_json)
    cmd = [
        "fzf",
        "--multi",
        "--reverse",
        "--preview",
        preview,
        "--preview-window",
        "down:70%",
    ]
    proc = subprocess.run(cmd, input=key_list, stdout=PIPE, text=True)
    print(proc.stdout)


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


def main(args):
    target_json = args[1]
    with open(target_json) as f:
        keys = collect_keys(json.load(f))
        execute_fzf(keys, target_json)


if __name__ == "__main__":
    main(sys.argv)
