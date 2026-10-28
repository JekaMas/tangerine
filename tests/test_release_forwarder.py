"""Actual local HTTP case semantics; only the upstream reply is a fixture."""
import importlib.util
import http.client
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


class ReleaseForwarder(unittest.TestCase):
    def run_request(self,header,origin):
        class Upstream(BaseHTTPRequestHandler):
            def do_PUT(self):
                body=self.rfile.read(int(self.headers.get('content-length','0'))).decode()
                payload=json.dumps(dict(host=self.headers['host'],origin=self.headers['origin'],body=body)).encode()
                self.send_response(200);self.send_header('X-Tangerine-Instance','literal-instance')
                self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
            def log_message(self,*args):pass
        upstream=ThreadingHTTPServer(('127.0.0.1',0),Upstream)
        spec=importlib.util.spec_from_file_location('release_forwarder',ROOT/'audit/iteration-30-release-20261027/readiness_forwarder.py')
        owner=importlib.util.module_from_spec(spec)
        with patch.dict(os.environ,dict(I30_WEB_PORT='1')):spec.loader.exec_module(owner)
        owner.TARGET='http://127.0.0.1:'+str(upstream.server_port)
        owner.BROWSER=True;owner.BROWSER_ORIGIN='http://localhost:54321'
        forward=ThreadingHTTPServer(('127.0.0.1',0),owner.Forward)
        threads=[threading.Thread(target=s.serve_forever,daemon=True) for s in [upstream,forward]]
        for worker in threads:worker.start()
        try:
            connection=http.client.HTTPConnection('127.0.0.1',forward.server_port,timeout=5)
            connection.request('PUT','/api/v1/configuration',body='literal-body',headers={header:origin})
            response=connection.getresponse();result=(response.status,response.getheader('X-Tangerine-Instance'),json.load(response))
            connection.close();return result
        finally:
            for server in [forward,upstream]:server.shutdown();server.server_close()
            for worker in threads:worker.join(timeout=5)

    def test_case_insensitive_origin_positive(self):
        for header in ['Origin','origin','oRiGiN']:
            self.assertEqual((200,'literal-instance',dict(host='localhost:3000',origin='http://localhost:3000',body='literal-body')),
                             self.run_request(header,'http://localhost:54321'))

    def test_unrelated_origin_not_rewritten_negative(self):
        for origin in ['http://example.invalid','http://localhost:54322']:
            self.assertEqual(origin,self.run_request('origin',origin)[2]['origin'])


if __name__=='__main__':unittest.main(verbosity=2)
