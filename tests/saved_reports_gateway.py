"""Local controlled transport around the source-built web/native fixture.

The browser is driven only by CUA. Faults replace HTTP transport, never report
arithmetic/storage. No model, speech, financial or user-workspace write can pass.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http.client
import json
from pathlib import Path
import threading

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-28-reports-20261026'
STACK=json.loads((DATA/'browser-stack.json').read_text())
LOCK=threading.Lock()
CONTROL={'name':'initial','failures':{}}
STAMP=None


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self): self.forward()
    def do_POST(self): self.forward()
    def forward(self):
        global STAMP,CONTROL
        body=self.rfile.read(int(self.headers.get('Content-Length',0)))
        with LOCK:
            control=DATA/'browser-control.json'
            if control.exists() and control.stat().st_mtime_ns!=STAMP:
                STAMP=control.stat().st_mtime_ns
                CONTROL=json.loads(control.read_text())
            name=CONTROL.get('name','initial')
            key=self.command+' '+self.path.split('?')[0]
            remaining=CONTROL.get('failures',{}).get(key,0)
            fail=remaining!=0
            if remaining>0: CONTROL['failures'][key]=remaining-1
        forbidden=self.command!='GET' and self.path!='/api/v1/reports/empirical'
        if forbidden:
            status,raw,headers=403,b'{"error":"forbidden_test_execution"}',{'Content-Type':'application/json'}
        elif fail:
            status,raw,headers=503,b'{"error":"private backend detail; synthetic dependency failure"}',{'Content-Type':'application/json'}
        else:
            upstream=http.client.HTTPConnection('127.0.0.1',int(STACK['web_port']),timeout=280)
            headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','connection','accept-encoding','origin','content-length']}
            headers['Host']='localhost:3000'
            if self.command!='GET':headers['Origin']='http://localhost:3000'
            upstream.request(self.command,self.path,body=body,headers=headers)
            response=upstream.getresponse();status=response.status;raw=response.read();headers=dict(response.getheaders());upstream.close()
        self.send_response(status)
        for k,v in headers.items():
            if k.lower() not in ['connection','transfer-encoding','content-length','content-encoding']:
                self.send_header(k,v)
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        if self.path.startswith('/api/'):
            event=dict(scenario=name,method=self.command,path=self.path,status=status,forbidden=forbidden)
            try:event['response']=json.loads(raw)
            except (ValueError,UnicodeDecodeError):pass
            if body:
                try:event['body']=json.loads(body)
                except (ValueError,UnicodeDecodeError):event['body']='malformed constructed input'
            with LOCK:
                with (DATA/'browser-requests.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')


if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    (DATA/'browser-gateway.json').write_text(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port)))+'\n')
    server.serve_forever()
