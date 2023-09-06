import json
import subprocess
import sys
from subprocess import PIPE
from urllib.request import urlopen


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


def make_query(pos, args):
    common = "|".join(args[0][:pos])
    array = []
    for a in args:
        array.append(f'({"|".join(a[pos:])})')
    if len(common) > 0:
        jq_command = f"{common}|" + f'[{",".join(array)}]'
    else:
        jq_command = f'[{",".join(array)}]'
    return jq_command


def main(port, args):
    response_text = urlopen(f"http://localhost:{port}").read().decode()
    j = json.loads(response_text)
    if len(args) == 1:
        cmd = ["jq", "-Cc", args[0]]
        proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
        print(proc.stdout.strip())
    else:
        arg_list = [x.split("|") for x in args]
        pos = common_prefix_length(arg_list)
        jq_command = make_query(pos, arg_list)

        cmd = ["jq", "-Cc", f"{jq_command}"]
        proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
        print(proc.stdout.strip())


if __name__ == "__main__":
    port = sys.argv[1]
    main(port, sys.argv[2:])
