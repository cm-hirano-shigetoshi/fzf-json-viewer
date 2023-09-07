import atexit
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import dirname, realpath

import requests

server_port = None
fzf_port = None
input_json = None


def set_fzf_port(port):
    global fzf_port
    fzf_port = port
    return True


def get_fzf_api_url():
    return f"http://localhost:{fzf_port}"


def post_to_localhost(*args, **kwargs):
    requests.post(*args, **kwargs, proxies={"http": None})


def get_filtered_preview_command(selector, script_dir=dirname(realpath(__file__))):
    return f"python {script_dir}/preview.py filtered {server_port} '{selector}' '{{}}'"


def get_filter_mode(selector):
    with open("/tmp/aaa", "a") as f:
        print(f"=== A01 ==={selector}", file=f)
        reload_cmd = f"curl \"http://localhost:{server_port}?get_input=json\" | jq -r '{selector}'"
        print(reload_cmd, file=f)
        preview = get_filtered_preview_command(selector)
        print(preview, file=f)
    return f"reload({reload_cmd})+change-preview({preview})+clear-query"


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        if "set_fzf_port" in params:
            succeeded = set_fzf_port(int(params["set_fzf_port"][0]))
        elif "filter" in params:
            with open("/tmp/aaa", "a") as f:
                print(params["filter"][0], file=f)
            selector = params["filter"][0]
            command = get_filter_mode(selector)
            post_to_localhost(get_fzf_api_url(), data=command)
            return True
        elif "get_input" in params:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            message = json.dumps(input_json)
            self.wfile.write(bytes(message, "utf8"))
            succeeded = False
        else:
            succeeded = False
        if succeeded:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        # supress any log messages
        return


class ThreadedHTTPServer(threading.Thread):
    def bind_socket(self):
        self.httpd = HTTPServer(("", 0), RequestHandler)
        return self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()


def start_server(j):
    global server_port, input_json
    input_json = j

    server = ThreadedHTTPServer(daemon=True)
    port = server.bind_socket()
    server_port = port
    atexit.register(server.stop)
    server.start()
    return port