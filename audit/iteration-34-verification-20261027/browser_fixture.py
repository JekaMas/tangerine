"""Isolated UI outcomes over the existing source-built frontend; no API forwarding.

Native I34 failure packets are retained inputs. UI-only completion is constructed
and never claims new native generation, synthesis, scoring or persistence.
"""
import argparse
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'data/iteration-34-verification-20261027/browser'
NATIVE = ROOT/'data/iteration-34-local-generation-20261027'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=0)
    parser.add_argument('--frontend',default='http://127.0.0.1:53039')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    # Public read only; captures catalogue/voice options, no key or user record.
    if not (OUT/'options.json').exists():
        with urllib.request.urlopen('http://127.0.0.1:3000/api/v1/preparation-options',timeout=10) as r:
            (OUT/'options.json').write_bytes(r.read())
    options=json.loads((OUT/'options.json').read_text())
    control=OUT/'control.json'
    if not control.exists(): control.write_text('{"scenario":"empty","mode":"empty"}\n')
    counts={};lock=threading.Lock();scenario='';saved=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,status,body,kind='application/json'):
            raw=body if isinstance(body,bytes) else json.dumps(body).encode()
            self.send_response(status);self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store')
            self.end_headers()
            try:self.wfile.write(raw)
            except (BrokenPipeError,ConnectionResetError):pass
        def do_GET(self):self.route()
        def do_POST(self):self.route()
        def route(self):
            nonlocal scenario,saved
            path=urlsplit(self.path).path
            if not path.startswith('/api/'):
                # Static source-built web only. All /api paths terminate below.
                with urllib.request.urlopen(urllib.request.Request(args.frontend+self.path,headers={'Host':'localhost:3000'}),timeout=20) as r:
                    self.send(r.status,r.read(),r.headers.get('Content-Type','text/html'))
                return
            rule=json.loads(control.read_text());mode=rule['mode']
            with lock:
                if scenario!=rule['scenario']:
                    scenario=rule['scenario'];counts.clear();saved=[]
                key=self.command+' '+path;counts[key]=counts.get(key,0)+1;n=counts[key]
            payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or b'{}')
            row=dict(scenario=scenario,method=self.command,path=path,occurrence=n,body=payload,
                     idempotency_key=self.headers.get('Idempotency-Key'),forwarded=False)
            status=200;body={};delay=0
            if self.command=='GET' and path in ['/api/v1/preparations','/api/v1/preparation-options']:
                status=503 if mode=='unavailable' or mode=='transient' and n==1 else 200
                body=dict(code='PRIVATE_BACKEND_CANARY',message='SQL/password/private trace') if status!=200 else (
                    options if path.endswith('preparation-options') else dict(items=saved,next_cursor=None))
            elif self.command=='GET' and path=='/api/v1/configuration':
                body=dict(configuration=dict(configuration_sha256='a'*64))
            elif self.command=='POST' and path=='/api/v1/blueprints':
                body=dict(id='b452f4fe-a1a4-4df0-a71a-9a44b50526f8',**payload)
            elif self.command=='POST' and path=='/api/v1/candidates:generate':
                before=json.loads((NATIVE/'controlled/failure-runner-before.json').read_text())
                before['last_failure']['message']='PRIVATE_BACKEND_CANARY: SQL password/private trace'
                saved=[before];delay=1
                status=503;body=dict(code='PROVIDER_FAILURE',message='PRIVATE_BACKEND_CANARY',preparation=before)
                if mode=='malformed':body=b'<html>PRIVATE_BACKEND_CANARY: password SQL</html>'
            elif self.command=='POST' and path.endswith(':resume'):
                after=copy.deepcopy(json.loads((NATIVE/'controlled/failure-runner-after.json').read_text())['preparation'])
                # UI-only completed outcome. Native I34 recovery is mutation-only
                # and remains separately evidenced. No fake audio file is served.
                after['phase_states']['render']='complete';after['audio_available']=True
                saved=[after];body=dict(preparation=after);delay=.7
            else:status=404;body=dict(code='PRIVATE_BACKEND_CANARY')
            row['status']=status
            with lock:
                with (OUT/'requests.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            time.sleep(delay)
            self.send(status,body,'text/html' if isinstance(body,bytes) else 'application/json')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    (OUT/'server.json').write_text(json.dumps(dict(port=server.server_port,frontend=args.frontend,
        origin='Actual existing source-built web; retained native failure packet; controlled UI-only recovery/completion.',
        new_inference_calls=0,new_synthesis_calls=0,api_forwarding=False),indent=2)+'\n')
    print('I34 UI fixture http://127.0.0.1:'+str(server.server_port)+'/prepare',flush=True)
    server.serve_forever()


if __name__=='__main__':main()
