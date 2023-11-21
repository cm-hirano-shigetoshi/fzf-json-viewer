#!/usr/bin/env python
import argparse
import json
import sys

from control_server import ControlServer
from fzf import Fzf
from fzf_task import FzfSelectKeys


def run(input_text, options):
    control_server = ControlServer()
    fzf_task = FzfSelectKeys(
        input_json=json.loads(input_text),
        optimize_aws_tags=not (options["no_aws_tags"]),
        server=control_server,
    )
    fzf = Fzf(fzf_task)
    src_list = fzf_task.get_src_list()
    proc = fzf.async_start_with_list(src_list)
    control_server.start(fzf_task.input_json)
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
