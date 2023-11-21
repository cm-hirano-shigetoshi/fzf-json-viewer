#!/usr/bin/env python
import argparse
import json
import sys

from control_server import ControlServer
from fzf import Fzf
from fzf_task import FzfSelectKeys

# import convert_format
# import fzf_options
# import internal_server


def run(input_text, options):
    input_json = json.loads(input_text)
    control_server = ControlServer()
    fzf_task = FzfSelectKeys(server=control_server, input_json=input_json)
    fzf = Fzf(fzf_task)
    src_list = fzf_task.get_src_list()
    proc = fzf.async_start_with_list(src_list)
    control_server.start(input_json)
    stdout, _ = proc.communicate()
    return stdout


def main(args, options):
    response = run(sys.stdin.read(), options)
    print(response)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--no_aws_tags", action="store_true")
    args = p.parse_args()
    main(sys.argv, args.__dict__)
