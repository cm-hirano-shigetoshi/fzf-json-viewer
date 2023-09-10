import json
import subprocess
from os.path import dirname, realpath
from subprocess import PIPE


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


def get_preview(server_port, script_dir=dirname(realpath(__file__))):
    cmd = f"python {script_dir}/preview.py selected {server_port} {{+}} | cat -n"
    return cmd


def get_filtered_preview_command(
    selector, server_port, script_dir=dirname(realpath(__file__))
):
    return f"python {script_dir}/preview.py filtered {server_port} '{selector}' '{{}}'"


def get_default_mode_options(server_port):
    options = [
        "--multi",
        "--reverse",
        "--prompt",
        "DEFAULT> ",
        "--preview",
        get_preview(server_port),
        "--preview-window",
        "down:70%",
        "--bind",
        "ctrl-l:deselect-all",
        "--bind",
        "alt-l:deselect-all",
        "--bind",
        f'alt-f:execute-silent(curl "localhost:{server_port}?filter={{}}")',
    ]
    return options


def enter_filter_mode(selector, server_port):
    reload_cmd = (
        f"curl \"http://localhost:{server_port}?get_input=json\" | jq -r '{selector}'"
    )
    preview = get_filtered_preview_command(selector, server_port)
    actions = [
        f"reload({reload_cmd})",
        f"change-prompt({selector}> )",
        f"change-preview({preview})",
        "clear-query",
    ]
    return "+".join(actions)


def enter_default_mode(selector, server_port):
    reload_cmd = (
        f"curl \"http://localhost:{server_port}?get_input=json\" | jq -r '{selector}'"
    )
    preview = get_filtered_preview_command(selector, server_port)
    actions = [
        f"reload({reload_cmd})",
        f"change-prompt({selector}> )",
        f"change-preview({preview})",
        "clear-query",
    ]
    return "+".join(actions)
