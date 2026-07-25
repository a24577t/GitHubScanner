"""Scripted stdlib HTTP server standing in for a GitHub API endpoint.

A script maps a path (without query string) to a list of responses, consumed
in order; the last response repeats. Every request is recorded so tests can
assert on methods used and headers sent.
"""
import contextlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Recorder:
    def __init__(self):
        self.requests = []


def response(status, body, headers=None):
    if isinstance(body, (dict, list)):
        body = json.dumps(body)
    return {"status": status, "body": body, "headers": headers or {}}


@contextlib.contextmanager
def serve(script):
    """Yield (base_url, recorder) for a scripted server; shuts down on exit."""
    recorder = Recorder()
    remaining = {path: list(responses) for path, responses in script.items()}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def _handle(self):
            path = self.path.split("?")[0]
            with lock:
                recorder.requests.append(
                    {
                        "method": self.command,
                        "path": self.path,
                        "headers": dict(self.headers),
                    }
                )
                scripted = remaining.get(path)
                if not scripted:
                    resp = response(404, {"message": "no script for " + path})
                else:
                    resp = scripted.pop(0) if len(scripted) > 1 else scripted[0]
            body = resp["body"].encode("utf-8")
            self.send_response(resp["status"])
            for name, value in resp["headers"].items():
                self.send_header(name, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = _handle
        do_POST = _handle
        do_PUT = _handle
        do_PATCH = _handle
        do_DELETE = _handle

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", recorder
    finally:
        server.shutdown()
        server.server_close()
