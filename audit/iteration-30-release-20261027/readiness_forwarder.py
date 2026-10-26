"""Test-owned network forwarder for the unmodified Linux public-readiness probe.

The launcher runs in a Docker CLI container. Its localhost:3000 probe forwards
the exact request/status/body to the actual separately published web service.
This avoids the user's occupied host port. It supplies no application reply.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import urllib.error
import urllib.request

TARGET = 'http://host.docker.internal:' + os.environ['I30_WEB_PORT']
CLIENT = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BROWSER = os.environ.get('I30_BROWSER_GATEWAY') == '1'
BROWSER_ORIGIN = os.environ.get('I30_BROWSER_ORIGIN', '')


class Forward(BaseHTTPRequestHandler):
    def forward(self):
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in {'host', 'connection', 'content-length'}}
        if BROWSER:
            headers['Host'] = 'localhost:3000'
            if headers.get('Origin') == BROWSER_ORIGIN:
                headers['Origin'] = 'http://localhost:3000'
        data = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        request = urllib.request.Request(TARGET + self.path, method=self.command,
                                         data=data if data else None, headers=headers)
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
            for key, value in response.headers.items():
                if key.lower() not in {'connection', 'transfer-encoding', 'content-length'}:
                    self.send_header(key, value)
            length = response.headers.get('Content-Length', '0') if self.command == 'HEAD' else str(len(body))
            self.send_header('Content-Length', length)
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)

    do_GET = do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = forward

    def log_message(self, *_):
        pass  # Do not log the private internal readiness header.


ThreadingHTTPServer(('0.0.0.0', 8088) if BROWSER else ('127.0.0.1', 3000), Forward).serve_forever()
