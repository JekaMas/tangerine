"""Internal speech runtime foundation. No fabricated synthesis endpoint."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import hmac
import shutil
import subprocess


def binary_available(name):
    path = shutil.which(name)
    if path is None:
        return False
    result = subprocess.run([path, "-version"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=5, check=False)
    return result.returncode == 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health/live":
            status, body = 200, {"status": "alive"}
        elif self.path == "/health/ready":
            if not os.environ.get("SPEECH_INTERNAL_TOKEN") or not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + os.environ["SPEECH_INTERNAL_TOKEN"]):
                self.send_error(403)
                return
            ready = binary_available("ffmpeg") and binary_available("ffprobe")
            status, body = (200 if ready else 503), {"status": "ready" if ready else "unavailable"}
        else:
            status, body = 404, {"error": "not_implemented"}
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        # Request bodies, paths, headers and provider secrets are never logged.
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8090), Handler).serve_forever()
