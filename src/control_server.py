import json
import threading
from dataclasses import dataclass, field
from http.server import HTTPServer
from urllib.parse import parse_qs
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server


def _find_available_port():
    httpd = HTTPServer(("", 0), None)
    return httpd.server_port


class QuietHandler(WSGIRequestHandler):
    def log_request(*args, **kwargs):
        pass


@dataclass
class ControlServer:
    port: int = _find_available_port()
    server: WSGIServer = field(default=None)
    input_json: dict = field(default_factory=dict)

    def application(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        query_params = parse_qs(query_string)

        body = "".encode()
        if "get_input" in query_params:
            # inputをJSONで返す
            if query_params["get_input"][0] == "json":
                body = json.dumps(self.input_json).encode()

        status = "200 OK"
        headers = [("Content-type", "text/plain; charset=utf-8")]
        start_response(status, headers)
        return [body]

    def run_server(self):
        self.server = make_server(
            "", self.port, self.application, handler_class=QuietHandler
        )
        self.server.serve_forever()

    def start(self, input_json):
        self.input_json = input_json
        server_thread = threading.Thread(target=self.run_server)
        server_thread.setDaemon(True)
        server_thread.start()


'''
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass
        """
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        if "set_fzf_port" in params:
            succeeded = set_fzf_port(int(params["set_fzf_port"][0]))
        elif "filter" in params:
            if mode == "default":
                set_selector(params["filter"][0][1:-1])
                command = fzf_options.enter_filter_mode(selector, server_port)
                post_to_localhost(get_fzf_api_url(), data=command)
                set_mode("filter")
                return True
            elif mode == "filter":
                selected = params["filter"][0][1:-1]
                command = fzf_options.enter_default_mode(
                    selector, selected, server_port
                )
                post_to_localhost(get_fzf_api_url(), data=command)
                set_mode("default")
                return True
            else:
                return False
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
                input_text = fzf_options.get_input_text(
                    fzf_options.get_key_list(
                        fzf_options.get_select_condition_list(
                            fzf_options.collect_keys(input_json), selector, selected
                        )
                    )
                )
                self.wfile.write(bytes(input_text, "utf8"))
            succeeded = False
        else:
            succeeded = False
        if succeeded:
            self.send_response(200)
            self.end_headers()
        """

    def log_message(self, format, *args):
        # supress any log messages
        return


class ThreadedHTTPServer(threading.Thread):
    def run(self, port):
        self.httpd = HTTPServer(("", port), RequestHandler)
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()


@dataclass
class ControlServer:
    port: int
    server: ThreadedHTTPServer = field(default=None)

    def start(self):
        self.server = ThreadedHTTPServer(daemon=True)
        self.server.run(self.port)
        atexit.register(self.server.stop)
        self.server.start()
'''
