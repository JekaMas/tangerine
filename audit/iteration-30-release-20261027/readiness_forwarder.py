"""Test-owned network forwarder for the unmodified Linux public-readiness probe.

The launcher runs in a Docker CLI container. Its localhost:3000 probe forwards
the exact request/status/body to the actual separately published web service.
This avoids the user's occupied host port. It supplies no application reply.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.error
import urllib.request

TARGET = 'http://host.docker.internal:' + os.environ['I30_WEB_PORT']
CLIENT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class Forward(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urllib.request.Request(TARGET + self.path,
                                         headers={k: v for k, v in self.headers.items() if k.lower() != 'host'})
        try:
            response = CLIENT.open(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        except OSError:
            self.send_error(503, 'Owned web service is not ready')
            return
        with response:
            body = response.read()
            self.send_response(response.code)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/octet-stream'))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *_):
        pass  # Do not log the private internal readiness header.


HTTPServer(('127.0.0.1', 3000), Forward).serve_forever()
