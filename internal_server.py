import atexit
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

import fzf_options

mode = "default"
selector = None
server_port = None
fzf_port = None
input_json = None


def set_mode(m):
    global mode
    mode = m


def set_selector(s):
    global selector
    selector = s


def set_fzf_port(port):
    global fzf_port
    fzf_port = port
    return True


def get_fzf_api_url():
    return f"http://localhost:{fzf_port}"


def post_to_localhost(*args, **kwargs):
    requests.post(*args, **kwargs, proxies={"http": None})


def get_input_json_from_memory():
    return input_json


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        if "set_fzf_port" in params:
            succeeded = set_fzf_port(int(params["set_fzf_port"][0]))
        elif "filter" in params:
            set_selector(params["filter"][0][1:-1])
            command = fzf_options.enter_filter_mode(selector, server_port)
            post_to_localhost(get_fzf_api_url(), data=command)
            set_mode("filter")
            return True
        elif "selected" in params:
            selected = params["selected"][0][1:-1]
            command = fzf_options.enter_default_mode(selector, selected, server_port)
            post_to_localhost(get_fzf_api_url(), data=command)
            set_mode("default")
            return True
        elif "get_input" in params:
            if params["get_input"][0] == "json":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                message = json.dumps(input_json)
                self.wfile.write(bytes(message, "utf8"))
            elif params["get_input"][0].startswith("keys:"):
                selected = params["get_input"][0][len("keys:") :]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                message = "\n".join(
                    fzf_options.get_key_list(
                        fzf_options.get_select_condition_list(
                            fzf_options.collect_keys(input_json), selector, selected
                        )
                    )
                )
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
