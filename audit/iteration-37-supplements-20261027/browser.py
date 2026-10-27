"""Retained-source UI fixture: real services/Chrome; controlled GET failures only."""
import http.client,json,os,subprocess,sys,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027';HERE=Path(__file__).resolve().parent
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
MODULE=NODE.parent.parent/'node_modules/playwright'

def command(args):return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
def main(program=None,folder=None,image='tangerine-i37-web'):
 name=json.loads((OUT/'stack.json').read_text())['name'];fixture=json.loads((OUT/'elrd-fixture.json').read_text());visual='--visual-only' in sys.argv;folder=Path(folder) if folder else OUT/('browser-visual' if visual else 'browser');folder.mkdir(parents=True,exist_ok=True)
 if not fixture.get('import_id'):raise RuntimeError('Actual completed supplement fixture is required')
 # These are separate owned services. The user's localhost3000 containers remain running.
 subprocess.run(['docker','rm',name+'-api',name+'-web'],capture_output=True)
 command(['docker','run','--pull=never','-d','--name',name+'-api','--network',name,'--network-alias','api','--env-file',str(OUT/'private-runtime.env'),'-v',str(OUT)+':/evidence:ro','--entrypoint','/evidence/tangerine','tangerine-i28-go','serve'])
 if subprocess.run(['docker','network','inspect',name+'-ui'],capture_output=True).returncode:command(['docker','network','create',name+'-ui'])
 command(['docker','run','--pull=never','-d','--name',name+'-web','--network',name+'-ui','--env-file',str(OUT/'private-runtime.env'),'-e','API_INTERNAL_URL=http://api:8080','-p','127.0.0.1::3000',image])
 command(['docker','network','connect',name,name+'-web'])
 port=int(command(['docker','inspect','-f','{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}',name+'-web']))
 state={'mode':'normal','remaining':0};observed=[];lock=threading.Lock()
 class Gateway(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_POST(self):
   if self.path=='/__test/mode':
    value=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
    with lock:state.update(value)
    self.send_response(200);self.end_headers();self.wfile.write(b'{}');return
   self.send_response(405);self.end_headers()
  def do_GET(self):
   failure=False;scenario='normal';delay=0
   if '/examples' in self.path or '/files' in self.path:
    with lock:
     scenario=state['mode'];failure=(scenario=='unavailable' and '/examples' in self.path) or (scenario=='files_unavailable' and '/files' in self.path) or scenario=='transient' and state['remaining']>0
     if scenario=='transient' and failure:state['remaining']-=1
     if scenario=='loading':delay=.6
   if delay:time.sleep(delay)
   if scenario=='recording_window' and '/examples' in self.path:status=200;headers=[('Content-Type','application/json')];body=json.dumps({'items':[json.loads((OUT/'window-source-row.json').read_text())],'next_cursor':''}).encode()
   elif scenario=='empty' and '/examples' in self.path:status=200;headers=[('Content-Type','application/json')];body=b'{"items":[],"next_cursor":""}'
   elif failure:status=503;headers=[('Content-Type','application/json')];body=b'{"error":"INTERNAL_CANARY_DO_NOT_SHOW","detail":"private backend traceback"}'
   else:
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=45)
    try:
     connection.request('GET',self.path,headers={'Host':'localhost:3000','Accept':self.headers.get('Accept','*/*'),'Range':self.headers.get('Range','')})
     response=connection.getresponse();status=response.status;headers=response.getheaders()
     if '/sources/assets/' in self.path:
      self.send_response(status)
      for k,v in headers:
       if k.lower() not in ['transfer-encoding','connection','keep-alive','content-encoding']:self.send_header(k,v)
      self.end_headers();written=0
      try:
       while chunk:=response.read(32768):self.wfile.write(chunk);written+=len(chunk)
      except (BrokenPipeError,ConnectionResetError):pass
      with lock:observed.append({'path':self.path,'status':status,'scenario':'actual_saved_media','method':'GET','request_range':self.headers.get('Range'),'bytes_forwarded':written})
      return
     body=response.read()
    finally:connection.close()
   if self.path.startswith('/api/'):
    with lock:observed.append({'path':self.path,'status':status,'scenario':scenario,'method':'GET'})
   self.send_response(status)
   for k,v in headers:
    if k.lower() not in ['transfer-encoding','content-length','connection','keep-alive','content-encoding']:self.send_header(k,v)
   self.send_header('Content-Length',str(len(body)));self.end_headers()
   try:self.wfile.write(body)
   except (BrokenPipeError,ConnectionResetError):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Gateway);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 url='http://127.0.0.1:'+str(server.server_port)
 for _ in range(100):
  try:
   c=http.client.HTTPConnection('127.0.0.1',port,timeout=2);c.request('GET','/sources',headers={'Host':'localhost:3000'});r=c.getresponse();r.read();c.close()
   if r.status==200:break
  except OSError:pass
  time.sleep(.1)
 else:raise RuntimeError('Owned browser fixture did not become ready')
 result=None
 try:
  env={**os.environ,'TANGERINE_SUPPLEMENT_BROWSER_URL':url,'TANGERINE_SUPPLEMENT_EVIDENCE':str(folder),'TANGERINE_SUPPLEMENT_DATA':str(OUT),'TANGERINE_PLAYWRIGHT_MODULE':str(MODULE)}
  with (folder/'stdout.log').open('w') as stdout,(folder/'stderr.log').open('w') as stderr:result=subprocess.run([str(NODE),str(ROOT/(program or 'tests/supplement_browser.cjs'))],cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=360)
 finally:
  (folder/'requests.json').write_text(json.dumps(observed,indent=2)+'\n');server.shutdown();server.server_close();thread.join(timeout=5)
  for suffix in ['web','api']:command(['docker','stop',name+'-'+suffix])
 if result is None:raise RuntimeError('Native browser did not finish')
 (folder/'exit-code').write_text(str(result.returncode));return result.returncode
if __name__=='__main__':sys.exit(main())
