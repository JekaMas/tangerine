"""Private synthesis transport. New inputs enter once; accepted stored audio is reused."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64, hmac, json, os, shutil, subprocess, sys, socket, select, threading, queue, signal, time

def binary_available(name):
 path=shutil.which(name)
 if path is None:return False
 return subprocess.run([path,'-version'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5,check=False).returncode==0

class Handler(BaseHTTPRequestHandler):
 def authorized(self):
  token=os.environ.get('SPEECH_INTERNAL_TOKEN','')
  return bool(token) and hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+token)
 def send(self,status,body):
  data=json.dumps(body,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if self.path=='/health/live':self.send(200,{'status':'alive'});return
  if not self.authorized():self.send(403,{'error':'internal_access_required'});return
  if self.path=='/health/ready':
   ready=binary_available('ffmpeg') and binary_available('ffprobe');self.send(200 if ready else 503,{'status':'ready' if ready else 'unavailable'})
  elif self.path=='/internal/v1/models':
   from model_setup import MODELS,installed
   rows=[]
   for name in MODELS:
    try:_,manifest=installed(name);rows.append({'profile_id':name,'status':'ready','revision':manifest['revision']})
    except ValueError:rows.append({'profile_id':name,'status':'setup_required'})
   self.send(200,{'profiles':rows,'espeak_ng':bool(shutil.which('espeak-ng'))})
  else:self.send(404,{'error':'not_implemented'})
 def do_POST(self):
  if not self.authorized():self.send(403,{'error':'internal_access_required'});return
  if self.path not in ('/internal/v1/piece','/internal/v1/plan','/internal/v1/quality'):self.send(404,{'error':'not_implemented'});return
  try:
   if self.headers.get('Content-Type')!='application/json':raise ValueError('INVALID_JSON')
   raw=self.rfile.read(int(self.headers.get('Content-Length','0')));packet=json.loads(raw)
   if self.path in ('/internal/v1/plan','/internal/v1/quality'):packet['action']='plan' if self.path.endswith('/plan') else 'quality';raw=json.dumps(packet).encode()
   timeout=min(270,max(1,float(packet.get('timeout_seconds',260))))
   # A process belongs to the foreground request and is killed on its deadline.
   p=subprocess.Popen([sys.executable,'-B',os.path.join(os.path.dirname(__file__),'backends.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
   completed=queue.Queue()
   def drain():completed.put(p.communicate(raw))
   thread=threading.Thread(target=drain,daemon=True);thread.start();deadline=time.monotonic()+timeout
   try:
    while True:
     try:stdout,stderr=completed.get(timeout=.1);break
     except queue.Empty:pass
     if time.monotonic()>=deadline:raise subprocess.TimeoutExpired(p.args,timeout)
     if select.select([self.connection],[],[],0)[0] and self.connection.recv(1,socket.MSG_PEEK)==b'':raise ConnectionAbortedError()
    result=json.loads(stdout)
    self.send(200 if p.returncode==0 else 422,result)
   finally:
    if p.poll() is None:os.killpg(p.pid,signal.SIGKILL)
    thread.join(timeout=5)
  except (ConnectionAbortedError,BrokenPipeError,ConnectionResetError):pass
  except subprocess.TimeoutExpired:self.send(504,{'error':'SPEECH_TIMEOUT'})
  except (ValueError,KeyError,TypeError,OverflowError):self.send(400,{'error':'INVALID_JSON'})
 def log_message(self,*_args):pass

if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8090),Handler).serve_forever()
