import atexit
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

fzf_port = None
input_json = None


def set_fzf_port(port):
    global fzf_port
    fzf_port = port
    return True


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        if "set_fzf_port" in params:
            succeeded = set_fzf_port(int(params["set_fzf_port"][0]))
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
    global input_json
    input_json = j

    server = ThreadedHTTPServer(daemon=True)
    port = server.bind_socket()
    atexit.register(server.stop)
    server.start()
    return port
