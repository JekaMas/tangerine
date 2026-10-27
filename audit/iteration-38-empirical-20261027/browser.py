"""Actual owned API/web/Chrome report flow; labelled read/write transport faults."""
import http.client,json,os,subprocess,sys,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-38-empirical-20261027'
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
MODULE=NODE.parent.parent/'node_modules/playwright'
def cmd(args):return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
def main(coverage=False,visual=False):
 store=ROOT/('data/iteration-36-jfleg-20261027' if coverage else 'data/iteration-35-official-l2-20261027');name=json.loads((store/'stack.json').read_text())['name'];folder=OUT/('coverage-visual' if visual else 'coverage-browser' if coverage else 'browser');folder.mkdir(parents=True,exist_ok=True)
 cmd(['docker','start',name+'-postgres',name+'-media'])
 for suffix in ['i38-api','i38-web']:subprocess.run(['docker','rm',name+'-'+suffix],capture_output=True)
 cmd(['docker','run','--pull=never','-d','--name',name+'-i38-api','--network',name,'--network-alias','i38-api','--env-file',str(store/'private-runtime.env'),'-e','APP_ORIGIN=http://localhost:3000','-e','API_INTERNAL_TOKEN=i38-owned-report-token','-v',str(OUT)+':/evidence:ro','--entrypoint','/evidence/tangerine','tangerine-i28-go','serve'])
 network=name+'-i38-ui'
 if subprocess.run(['docker','network','inspect',network],capture_output=True).returncode:cmd(['docker','network','create',network])
 cmd(['docker','run','--pull=never','-d','--name',name+'-i38-web','--network',network,'--env-file',str(store/'private-runtime.env'),'-e','APP_ORIGIN=http://localhost:3000','-e','API_INTERNAL_TOKEN=i38-owned-report-token','-e','API_INTERNAL_URL=http://i38-api:8080','-p','127.0.0.1::3000','tangerine-i38-web'])
 cmd(['docker','network','connect',name,name+'-i38-web'])
 port=int(cmd(['docker','inspect','-f','{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}',name+'-i38-web']))
 state={'mode':'normal','remaining':0};requests=[];lock=threading.Lock()
 class Gateway(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):self.forward()
  def do_POST(self):self.forward()
  def forward(self):
   data=self.rfile.read(int(self.headers.get('Content-Length',0)))
   if self.path=='/__test/mode' and self.command=='POST':
    with lock:state.update(json.loads(data))
    self.send_response(200);self.end_headers();self.wfile.write(b'{}');return
   key=self.command+' '+self.path.split('?')[0]
   source=key=='GET /api/v1/reports/source-populations';write=key=='POST /api/v1/reports/empirical';scenario='normal';fail=False;empty=False
   with lock:
    scenario=state['mode'];fail=source and scenario=='unavailable' or write and scenario=='save_failure' or source and scenario=='transient' and state['remaining']>0
    if source and scenario=='transient' and fail:state['remaining']-=1
    empty=source and scenario=='empty'
   if source and scenario=='loading':time.sleep(.7)
   forbidden=self.command!='GET' and not write
   if forbidden:status,body,headers=403,b'{"error":"forbidden_test_execution"}',[('Content-Type','application/json')]
   elif empty:status,body,headers=200,b'[]',[('Content-Type','application/json')]
   elif fail:status,body,headers=503,b'{"error":"I38_PRIVATE_DATABASE_CANARY","detail":"internal traceback"}',[('Content-Type','application/json')]
   else:
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=275)
    try:
     heads={'Host':'localhost:3000','Accept':self.headers.get('Accept','*/*'),'Content-Type':self.headers.get('Content-Type','')}
     if self.command!='GET':heads['Origin']='http://localhost:3000'
     connection.request(self.command,self.path,body=data,headers=heads);response=connection.getresponse();status=response.status;headers=response.getheaders();body=response.read()
    finally:connection.close()
   if self.path.startswith('/api/'):
    event={'method':self.command,'path':self.path,'scenario':scenario,'status':status,'forbidden':forbidden}
    if write and data:event['body']=json.loads(data)
    if write and status==201:event['saved_report']=json.loads(body)
    with lock:requests.append(event)
   self.send_response(status)
   for k,v in headers:
    if k.lower() not in ['transfer-encoding','connection','content-length','content-encoding','keep-alive']:self.send_header(k,v)
   self.send_header('Content-Length',str(len(body)));self.end_headers()
   try:self.wfile.write(body)
   except (BrokenPipeError,ConnectionResetError):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Gateway);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 for _ in range(120):
  try:
   c=http.client.HTTPConnection('127.0.0.1',port,timeout=2);c.request('GET','/reports',headers={'Host':'localhost:3000'});r=c.getresponse();r.read();c.close()
   if r.status==200:break
  except OSError:pass
  time.sleep(.1)
 else:raise RuntimeError('Owned browser did not start')
 try:
  env={**os.environ,'I38_URL':'http://127.0.0.1:'+str(server.server_port),'I38_BROWSER_EVIDENCE':str(folder),'I38_EXISTING_REQUESTS':str(OUT/'coverage-browser/requests.json'),'TANGERINE_PLAYWRIGHT_MODULE':str(MODULE)}
  with (folder/'stdout.log').open('w') as stdout,(folder/'stderr.log').open('w') as stderr:r=subprocess.run([str(NODE),str(ROOT/('tests/imported_reports_visual.cjs' if visual else 'tests/imported_reports_coverage_browser.cjs' if coverage else 'tests/imported_reports_browser.cjs'))],cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=360)
 finally:
  (folder/'requests.json').write_text(json.dumps(requests,indent=2)+'\n');server.shutdown();server.server_close();thread.join(timeout=5)
  for suffix in ['i38-web','i38-api']:cmd(['docker','stop',name+'-'+suffix])
 (folder/'exit-code').write_text(str(r.returncode));return r.returncode
if __name__=='__main__':sys.exit(main('--coverage' in sys.argv or '--coverage-visual' in sys.argv,'--coverage-visual' in sys.argv))
