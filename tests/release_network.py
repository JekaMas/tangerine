"""Test-owned reverse network bridge; no application/model response substitution.

Host can reach Docker's published loopback ports while Docker currently cannot
reach host/public addresses. Host agents open outbound tunnels to this private
container. Public dependency TLS remains end to end. The only inference target
is the installed loopback Ollama, with an explicit local-model allowlist.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import hashlib,json,os,queue,select,socket,sys,threading,time,uuid
PUBLIC={'pypi.org','files.pythonhosted.org','download.pytorch.org','download-r2.pytorch.org','download.pytorch.com','huggingface.co','github.com','objects.githubusercontent.com','release-assets.githubusercontent.com'}
MODELS={'gpt-oss:20b','tangerine-qwen35-9b-i6-20261020'}
JOBS=queue.Queue()

def pipe(a,b,initial=b'',capture=None):
 if initial:b.sendall(initial)
 while True:
  ready,_,_=select.select([a,b],[],[],300)
  if not ready:return
  for source in ready:
   try:
    data=source.recv(65536)
    if not data:return
    target=b if source is a else a
    if capture and source is b:capture.write(data);capture.flush()
    target.sendall(data)
   except OSError:return

class Bridge(BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass
 def do_CONNECT(self):
  host,_,port=self.path.rpartition(':')
  allowed=host in PUBLIC or host.endswith('.hf.co') or host.endswith('.xethub.hf.co')
  if not allowed or port!='443':self.send_error(403);return
  self.transfer({'host':host,'port':443,'kind':'dependency'})
 def do_POST(self):
  if self.path!='/v1/responses':self.send_error(403);return
  raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
  try:body=json.loads(raw)
  except ValueError:self.send_error(400);return
  if body.get('model') not in MODELS or self.headers.get('Authorization'):self.send_error(403);return
  ident=uuid.uuid4().hex
  prefix=b'POST /v1/responses HTTP/1.1\r\nHost: 127.0.0.1:11434\r\nContent-Type: application/json\r\nConnection: close\r\nContent-Length: '+str(len(raw)).encode()+b'\r\n\r\n'+raw
  self.transfer({'host':'127.0.0.1','port':11434,'kind':'local_model','id':ident,'model':body['model'],'request_sha256':hashlib.sha256(raw).hexdigest()},prefix)
 def transfer(self,metadata,prefix=b''):
  metadata['prefix_length']=len(prefix)
  job={'metadata':metadata,'prefix':prefix,'client':self.connection,'ready':threading.Event(),'closed':threading.Event()};JOBS.put(job)
  if not job['ready'].wait(30):self.send_error(503);return
  if metadata['kind']=='dependency':self.send_response(200,'Connection established');self.end_headers()
  job['client_ready'].set();job['closed'].wait();self.close_connection=True
 def do_GET(self):
  if self.path!='/bridge/agent':self.send_error(404);return
  try:job=JOBS.get(timeout=120)
  except queue.Empty:self.send_response(204);self.send_header('Content-Length','0');self.end_headers();return
  job['client_ready']=threading.Event()
  metadata=json.dumps(job['metadata'],separators=(',',':')).encode().hex()
  self.send_response(101,'Switching Protocols');self.send_header('Connection','Upgrade');self.send_header('Upgrade','tangerine-test-network');self.send_header('X-Tangerine-Target',metadata);self.end_headers();self.wfile.write(job['prefix']);self.wfile.flush();job['ready'].set()
  try:
   if job['client_ready'].wait(30):pipe(job['client'],self.connection)
  finally:job['closed'].set();self.close_connection=True

def read_job(connection):
 header=bytearray()
 while b'\r\n\r\n' not in header:
  chunk=connection.recv(4096)
  if not chunk:raise OSError('bridge closed')
  header.extend(chunk)
 header,remainder=bytes(header).split(b'\r\n\r\n',1)
 if not header.startswith(b'HTTP/1.1 101'):return None,b''
 target=next(line.split(b': ',1)[1] for line in header.split(b'\r\n') if line.lower().startswith(b'x-tangerine-target:'))
 metadata=json.loads(bytes.fromhex(target.decode()));needed=metadata.get('prefix_length',0)
 initial=bytearray(remainder)
 while len(initial)<needed:
  chunk=connection.recv(min(65536,needed-len(initial)))
  if not chunk:raise OSError('bridge prefix incomplete')
  initial.extend(chunk)
 return metadata,bytes(initial)

def agent(port,directory):
 directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
 def work():
  while True:
   try:
    with socket.create_connection(('127.0.0.1',port),timeout=150) as bridge:
     bridge.sendall(b'GET /bridge/agent HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
     metadata,prefix=read_job(bridge)
     if metadata is None:continue
     with socket.create_connection((metadata['host'],metadata['port']),timeout=30) as upstream:
      bridge.settimeout(None);upstream.settimeout(None)
      if metadata['kind']=='local_model':
       ident=metadata['id'];(directory/(ident+'-request.json')).write_bytes(prefix.split(b'\r\n\r\n',1)[1]);metadata.update(billing_mode='local',fixture_response=False,dispatched=True)
       with (directory/(ident+'-response.http')).open('wb') as capture:pipe(bridge,upstream,prefix,capture)
       (directory/(ident+'-dispatch.json')).write_text(json.dumps(metadata,indent=2))
      else:pipe(bridge,upstream,prefix)
   except (OSError,ValueError,StopIteration):time.sleep(.2)
 workers=[threading.Thread(target=work,daemon=True) for _ in range(12)]
 for worker in workers:worker.start()
 print(json.dumps({'status':'ready','workers':len(workers),'paid_routes':False}),flush=True)
 for worker in workers:worker.join()

if __name__=='__main__':
 if sys.argv[1]=='server':ThreadingHTTPServer(('0.0.0.0',8088),Bridge).serve_forever()
 else:agent(int(sys.argv[2]),sys.argv[3])
