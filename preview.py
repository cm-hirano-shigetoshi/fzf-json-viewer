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


def get_selected_part(port, args, tty=False):
    response_text = urlopen(f"http://localhost:{port}?get_input=json").read().decode()
    j = json.loads(response_text)
    if len(args) == 1:
        if tty:
            cmd = ["jq", "-Cc", args[0]]
        else:
            cmd = ["jq", "-c", args[0]]
        proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
        return proc.stdout.strip()
    else:
        arg_list = [x.split("|") for x in args]
        pos = common_prefix_length(arg_list)
        jq_command = make_query(pos, arg_list)

        if tty:
            cmd = ["jq", "-Cc", f"{jq_command}"]
        else:
            cmd = ["jq", "-c", f"{jq_command}"]
        proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
        return proc.stdout.strip()


def get_filter_query(selector, specified):
    with open("/tmp/aaa", "a") as f:
        print(selector, specified, file=f)
    sp = selector.split("|")
    a, b, c = (sp[0], "|".join(sp[:-1]), sp[-1])
    q = f'{{{a[1:]}: [{b}|select({c} == "{specified}")]}}'
    return q


def get_filtered_json(port, selector, specified, tty=False):
    response_text = urlopen(f"http://localhost:{port}?get_input=json").read().decode()
    j = json.loads(response_text)
    if tty:
        cmd = ["jq", "-C", get_filter_query(selector, specified)]
    else:
        cmd = ["jq", get_filter_query(selector, specified)]
    proc = subprocess.run(cmd, input=json.dumps(j), stdout=PIPE, text=True)
    return proc.stdout.strip()


def main(mode, port, args):
    if mode == "selected":
        print(get_selected_part(port, args, tty=True))
    elif mode == "filtered":
        with open("/tmp/aaa", "a") as f:
            print(args, file=f)
        print(get_filtered_json(port, args[0], args[1], tty=True))


if __name__ == "__main__":
    with open("/tmp/aaa", "a") as f:
        print(sys.argv, file=f)
    mode = sys.argv[1]
    port = sys.argv[2]
    main(mode, port, sys.argv[3:])
