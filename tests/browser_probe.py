"""Native Chrome DevTools driver for the production page; no DOM/network stubs."""
import base64, json, os, signal, socket, struct, subprocess, time, urllib.request
from urllib.parse import urlparse
class Browser:
 def __init__(self,profile):
  self.process=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+str(profile),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
  try:
   deadline=time.monotonic()+30;port=None;page=None
   while time.monotonic()<deadline:
    p=profile/'DevToolsActivePort'
    lines=p.read_text().splitlines() if p.exists() else []
    # Chrome creates this file before its port/path contents are complete.
    if len(lines)>=2 and lines[0].isdigit() and lines[1].startswith('/devtools/browser/'):
     port=int(lines[0])
     try:
      with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list',timeout=2) as response:pages=json.load(response)
      page=next((x for x in pages if x.get('type')=='page' and x.get('webSocketDebuggerUrl')),None)
      if page:break
     except (OSError,ValueError):pass
    if self.process.poll() is not None:raise RuntimeError('Chrome exited before its debugger became ready')
    time.sleep(.1)
   if page is None:raise TimeoutError('Chrome debugger did not become ready within 30 seconds')
   url=urlparse(page['webSocketDebuggerUrl'])
   self.sock=socket.create_connection((url.hostname,url.port),timeout=30);key=base64.b64encode(os.urandom(16)).decode();self.sock.sendall(f'GET {url.path} HTTP/1.1\r\nHost: {url.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode());response=b''
   while not response.endswith(b'\r\n\r\n'):response+=self.sock.recv(1)
   if not response.startswith(b'HTTP/1.1 101 '):raise RuntimeError('Chrome socket handshake failed')
   self.seq=0;self.call('Page.enable');self.call('Page.navigate',{'url':'http://localhost:3000/'})
  except BaseException:self.close();raise
 def read(self,n):
  b=b''
  while len(b)<n:
   part=self.sock.recv(n-len(b))
   if not part:raise RuntimeError('Chrome socket closed')
   b+=part
  return b
 def call(self,method,params=None):
  self.seq+=1;message=json.dumps({'id':self.seq,'method':method,'params':params or {}}).encode();mask=os.urandom(4);n=len(message);header=b'\x81'+(bytes([n|128]) if n<126 else b'\xfe'+struct.pack('!H',n) if n<65536 else b'\xff'+struct.pack('!Q',n));self.sock.sendall(header+mask+bytes(v^mask[i%4] for i,v in enumerate(message)))
  while True:
   h=self.read(2);length=h[1]&127
   if length==126:length=struct.unpack('!H',self.read(2))[0]
   elif length==127:length=struct.unpack('!Q',self.read(8))[0]
   mask2=self.read(4) if h[1]&128 else None;payload=self.read(length)
   if mask2:payload=bytes(v^mask2[i%4] for i,v in enumerate(payload))
   if h[0]&15!=1:continue
   response=json.loads(payload)
   if response.get('id')==self.seq:
    if 'error' in response:raise RuntimeError(response['error'])
    return response['result']
 def evaluate(self,js):return self.call('Runtime.evaluate',{'expression':js,'returnByValue':True})['result'].get('value')
 def wait(self,text):
  for _ in range(100):
   dom=self.evaluate('document.documentElement.outerHTML') or ''
   if text in dom:return dom
   time.sleep(.1)
  raise AssertionError('Native browser did not render '+text)
 def refresh(self):self.evaluate("document.querySelector('button').click()")
 def close(self):
  if hasattr(self,'sock'):self.sock.close()
  if hasattr(self,'process'):
   try:os.killpg(self.process.pid,signal.SIGTERM);self.process.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(self.process.pid,signal.SIGKILL);self.process.wait()
