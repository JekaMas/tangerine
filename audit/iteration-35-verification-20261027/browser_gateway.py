"""GET-only gateway over the actual I35 API/web; controlled transient errors only."""
import json,subprocess,secrets,time,urllib.request,urllib.error,sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Lock
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-35-verification-20261027'
NATIVE=ROOT/'data/iteration-35-official-l2-20261027'
NAME='tangerine-i35-verify'
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True,check=True);return p.stdout.strip()
def setup():
 env=OUT/'private-runtime.env'
 if not env.exists():
  env.write_text((NATIVE/'private-runtime.env').read_text()+'API_INTERNAL_TOKEN='+secrets.token_hex(32)+'\nAPP_ORIGIN=http://localhost:3000\nSPEECH_URL=http://not-configured.invalid:8090\n');env.chmod(0o600)
 cmd(['docker','run','--pull=never','-d','--name',NAME+'-api','--network','tangerine-i35-26fd12b0','--network-alias','i35-verify-api','--env-file',str(env),'-v',str(OUT)+':/evidence:ro','--entrypoint','/evidence/tangerine','tangerine-i28-go','serve'])
 cmd(['docker','run','--pull=never','-d','--name',NAME+'-web','--network','tangerine-i35-26fd12b0','--env-file',str(env),'-e','API_INTERNAL_URL=http://i35-verify-api:8080','-p','127.0.0.1::3000','tangerine-i35-verify-web'])
 port=cmd(['docker','port',NAME+'-web','3000/tcp']).split(':')[-1]
 (OUT/'stack.json').write_text(json.dumps(dict(api=NAME+'-api',web=NAME+'-web',web_port=int(port),database_reused='tangerine-i35-26fd12b0-postgres',media_reused='tangerine-i35-26fd12b0-media',image=cmd(['docker','image','inspect','tangerine-i35-verify-web','--format','{{.Id}}']),scope='Only GET source application handlers, unchanged I30 Sources frontend; no import or provider dispatch.'),indent=2)+'\n')
 return 'http://127.0.0.1:'+port

def main():
 OUT.mkdir(parents=True,exist_ok=True);browser=OUT/'browser';browser.mkdir(exist_ok=True)
 target='http://127.0.0.1:'+str(json.loads((OUT/'stack.json').read_text())['web_port']) if '--reuse' in sys.argv else setup()
 for _ in range(120):
  try:
   with urllib.request.urlopen(urllib.request.Request(target+'/sources',headers={'Host':'localhost:3000'}),timeout=5) as r:
    if r.status==200:break
  except (OSError,urllib.error.URLError):time.sleep(.25)
 else:raise RuntimeError('Owned frontend unavailable; inspect container logs')
 control=browser/'control.json';control.write_text('{"scenario":"initial","mode":"normal"}\n')
 counts={};scenario='';lock=Lock()
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_POST(self):self.block_write()
  def do_PUT(self):self.block_write()
  def do_DELETE(self):self.block_write()
  def block_write(self):
   self.send_response(405);self.end_headers()
  def do_GET(self):
   nonlocal scenario
   rule=json.loads(control.read_text());path=self.path.split('?')[0]
   with lock:
    if rule['scenario']!=scenario:counts.clear();scenario=rule['scenario']
    counts[path]=counts.get(path,0)+1;n=counts[path]
   mode=rule['mode'];headers={};injected=False
   if path.startswith('/api/') and not (path=='/api/v1/sources' or path.startswith('/api/v1/source-releases/') or path.startswith('/api/v1/imports/') or path.startswith('/api/v1/sources/assets/')):
    status=405;body=b'{}';headers['Content-Type']='application/json'
   elif path=='/api/v1/sources' and (mode=='unavailable' or mode=='transient' and n==1):
    injected=True;status=503;body=b'{"error":"PRIVATE_BACKEND_CANARY","message":"SQL/private password trace"}';headers['Content-Type']='application/json'
   else:
    if path.startswith('/api/') and mode=='loading':time.sleep(.7)
    request=urllib.request.Request(target+self.path,headers={'Host':'localhost:3000',**({'Range':self.headers['Range']} if self.headers.get('Range') else {})})
    try:response=urllib.request.urlopen(request,timeout=90)
    except urllib.error.HTTPError as error:response=error
    with response as r:
     status=r.status;body=r.read();headers={k:v for k,v in r.headers.items() if k.lower() in ['content-type','content-disposition','content-range','accept-ranges','etag']}
   if path.startswith('/api/'):
    with lock:
     with (browser/'requests.jsonl').open('a') as f:f.write(json.dumps(dict(scenario=rule['scenario'],method='GET',path=self.path,status=status,bytes=len(body),injected=injected,at=time.time()))+'\n')
   self.send_response(status)
   for k,v in headers.items():self.send_header(k,v)
   self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers()
   try:self.wfile.write(body)
   except (BrokenPipeError,ConnectionResetError):pass
 old=browser/'server.json';port=int(json.loads(old.read_text())['url'].rsplit(':',1)[1]) if '--reuse' in sys.argv else 0
 server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
 (browser/'server.json').write_text(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port),upstream=target,scope='Actual complete I35 data. GET only; transient/unavailable responses controlled outside real application. No provider/synthesis/import dispatch.'),indent=2)+'\n')
 print('Owned Sources browser gateway ready',flush=True)
 server.serve_forever()
if __name__=='__main__':main()
