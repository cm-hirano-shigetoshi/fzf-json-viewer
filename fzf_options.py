from os.path import dirname, realpath

server_port = None


def set_server_port(port):
    global server_port
    server_port = port


def get_preview(script_dir=dirname(realpath(__file__)), port=None):
    port = port if port else server_port
    cmd = f"python {script_dir}/preview.py selected {port} {{+}} | cat -n"
    return cmd


def get_filtered_preview_command(selector, script_dir=dirname(realpath(__file__))):
    return f"python {script_dir}/preview.py filtered {server_port} '{selector}' '{{}}'"


def get_options(mode):
    if mode == "default":
        options = [
            "--multi",
            "--reverse",
            "--preview",
            get_preview(),
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
    return []


def get_fzf_options_diff(selector):
    reload_cmd = (
        f"curl \"http://localhost:{server_port}?get_input=json\" | jq -r '{selector}'"
    )
    preview = get_filtered_preview_command(selector)
    return f"reload({reload_cmd})+change-preview({preview})+clear-query"
