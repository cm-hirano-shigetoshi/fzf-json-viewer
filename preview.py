import json
import subprocess
import sys
from subprocess import PIPE


def common_prefix_length(a, b):
    if a == b:
        return len(a)
    common_length = 0
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            common_length += 1
        else:
            break
    if len(a) > common_length and a[common_length] == ".":
        return common_length
    else:
        return a[:common_length].rfind(".")


def main(target_json, args):
    with open(target_json) as f:
        j = json.load(f)
        if len(args) == 1:
            cmd = ["jq", "-c", args[0]]
            # print(cmd)
            proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
            print(proc.stdout)
        elif len(args) == 2:
            pos = common_prefix_length(args[0], args[1])
            y = args[0][pos:]
            z = args[1][pos:]
            assert "[]" not in y
            assert "[]" not in z
            x = args[0][:pos]
            jq_command = f"{x}[{y},{z}]"

            cmd = ["jq", "-c", f"{jq_command}"]
            proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
            print(proc.stdout)


if __name__ == "__main__":
    target_json = sys.argv[1]
    main(target_json, sys.argv[2:])
