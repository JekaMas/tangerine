"""Test-owned HTTP observation/fault transport around the real Next/native UI.

No browser automation, arithmetic, model reply substitution or account changes.
Only explicit real-flow steps can dispatch models; UI-only checks cannot do so.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import http.client,json,threading,time,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-29-full-flow-20261026'
STACK=json.loads((DATA/'stack.json').read_text())
LOCK=threading.Lock();STAMP=None
CONTROL={'name':'empty-route-review','allow_model_calls':False,'failures':{}}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):self.forward()
 def do_POST(self):self.forward()
 def do_PUT(self):self.forward()
 def forward(self):
  global STAMP,CONTROL
  body=self.rfile.read(int(self.headers.get('Content-Length',0)))
  with LOCK:
   path=DATA/'control.json'
   if path.exists() and path.stat().st_mtime_ns!=STAMP:
    STAMP=path.stat().st_mtime_ns;CONTROL=json.loads(path.read_text())
   name=CONTROL.get('name','initial');key=self.command+' '+self.path.split('?')[0]
   display_fixture=CONTROL.get('display_fixture')
   response_fixture=CONTROL.get('response_fixture')
   saved_feedback=response_fixture in ['saved_feedback_unavailable','constructed_feedback_complete'] and key=='POST /api/v1/attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5:retry-feedback'
   remaining=CONTROL.get('failures',{}).get(key,0);fail=remaining!=0
   if remaining>0:CONTROL['failures'][key]=remaining-1
   model_write=self.command=='POST' and (self.path.endswith(('candidates:generate',':submit',':retry',':retry-feedback',':render',':resume',':run',':reconsider','/measurements')))
   forbidden=model_write and not CONTROL.get('allow_model_calls',False) and not saved_feedback
  started=time.time()
  if saved_feedback:
   # UI retry-notice regression only: replay the exact actual saved native
   # unavailable-result envelope. No native write or model reply is simulated.
   status,raw,headers=200,(DATA/'attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5-result.json').read_bytes(),{'Content-Type':'application/json'}
   if response_fixture=='constructed_feedback_complete':
    value=json.loads(raw);value['feedback_status']='complete';value['retry_operation']=None
    value['feedback']={'items':[{'kind':'recommendation','status':'final','text':'Constructed UI fixture: practise make a plan and make it fun.'}],'origin':'constructed_ui_transport_fixture'}
    raw=json.dumps(value).encode()
  elif forbidden:status,raw,headers=403,b'{"error":"test_owned_model_dispatch_disabled"}',{'Content-Type':'application/json'}
  elif fail:status,raw,headers=503,b'{"error":"private backend canary; test-owned dependency unavailable"}',{'Content-Type':'application/json'}
  else:
   upstream=http.client.HTTPConnection('127.0.0.1',int(STACK['web_port']),timeout=280)
   headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','connection','accept-encoding','origin','content-length']}
   headers['Host']='localhost:3000'
   if self.command!='GET':headers['Origin']='http://localhost:3000'
   upstream.request(self.command,self.path,body=body,headers=headers)
   response=upstream.getresponse();status=response.status;raw=response.read();headers=dict(response.getheaders());upstream.close()
   # Labelled presentation counterexample only. The real stored preparation,
   # audio/key and model replies are unchanged and are never replaced in the
   # actual-flow evidence. No render action follows this controlled read.
   if display_fixture=='audio_unassembled' and key=='GET /api/v1/preparations' and status==200:
    value=json.loads(raw)
    for item in value['items']:
     item['audio_available']=False;item['phase_states']['render']='interrupted'
    raw=json.dumps(value).encode()
  self.send_response(status)
  for k,v in headers.items():
   if k.lower() not in ['connection','transfer-encoding','content-length','content-encoding']:self.send_header(k,v)
  self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  if self.path.startswith('/api/'):
   event={'scenario':name,'method':self.command,'path':self.path,'status':status,'forbidden':forbidden,'controlled_display_fixture':display_fixture,'controlled_response_fixture':response_fixture,'started_at_unix':started,'finished_at_unix':time.time()}
   content_type=next((v for k,v in headers.items() if k.lower()=='content-type'),'')
   if content_type.startswith('application/json'):
    try:event['response']=json.loads(raw)
    except (ValueError,UnicodeDecodeError):pass
   else:event['bytes']=len(raw)
   if body:
    try:event['body']=json.loads(body)
    except (ValueError,UnicodeDecodeError):event['body_bytes']=len(body)
   with LOCK:
    with (DATA/'requests.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')

if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 0),Handler)
 (DATA/'gateway.json').write_text(json.dumps({'url':'http://127.0.0.1:'+str(server.server_port)})+'\n')
 server.serve_forever()
