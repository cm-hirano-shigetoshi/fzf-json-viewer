import atexit
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

input_json = None


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = json.dumps(input_json)
        self.wfile.write(bytes(message, "utf8"))

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
