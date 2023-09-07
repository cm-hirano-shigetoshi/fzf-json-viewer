import json
import subprocess
import sys
from subprocess import PIPE
from urllib.request import urlopen


def get_input_json(port):
    response_text = urlopen(f"http://localhost:{port}?get_input=json").read().decode()
    return json.loads(response_text)


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


def get_selected_part_text(input_json, items):
    if len(items) == 1:
        cmd = ["jq", items[0]]
        proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
        return proc.stdout.rstrip()
    else:
        arg_list = [x.split("|") for x in items]
        pos = common_prefix_length(arg_list)
        jq_command = make_query(pos, arg_list)

        cmd = ["jq", "-c", jq_command]
        proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
        return proc.stdout.rstrip()


def get_filter_query_text(selector, specified):
    sp = selector.split("|")
    a, b, c = (sp[0], "|".join(sp[:-1]), sp[-1])
    q = f'{{{a[1:]}: [{b}|select({c} == "{specified}")]}}'
    return q


def get_filtered_json(input_json, selector, specified):
    cmd = ["jq", get_filter_query_text(selector, specified)]
    proc = subprocess.run(cmd, input=json.dumps(input_json), stdout=PIPE, text=True)
    return json.loads(proc.stdout)


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


def main(mode, port, args):
    input_json = get_input_json(port)
    if mode == "selected":
        print(format_via_jq(get_selected_part_text(input_json, args), compact=True))
    elif mode == "filtered":
        print(format_via_jq(get_filtered_json(input_json, args[0], args[1])))


if __name__ == "__main__":
    mode = sys.argv[1]
    port = sys.argv[2]
    main(mode, port, sys.argv[3:])
