"""Native installed Playwright/Chrome transport; no DOM/network substitution."""
import json,os,select,signal,subprocess,time
from pathlib import Path
class Browser:
 def __init__(self,profile,initial_url='http://localhost:3000/'):
  bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
  node=Path(os.getenv('TANGERINE_TEST_NODE',str(bundled/'bin/node')))
  module=Path(os.getenv('TANGERINE_TEST_PLAYWRIGHT_MODULE',str(bundled/'node_modules/playwright')))
  if not node.is_file() or not (module/'package.json').is_file():raise RuntimeError('TEST_BROWSER_REQUIRED: configure existing Node/Playwright paths; this test never installs them')
  env={**os.environ,'TANGERINE_TEST_PLAYWRIGHT_MODULE':str(module)};self.seq=0
  self.process=subprocess.Popen([str(node),str(Path(__file__).with_name('browser_playwright.cjs')),str(profile),initial_url or ''],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True)
  try:
   ready=self.read();
   if not ready.get('ready'):raise RuntimeError(ready.get('error','Native browser not ready'))
   self.driver_version=ready['driver_version']
  except BaseException:self.close();raise
 def read(self):
  if not select.select([self.process.stdout],[],[],30)[0]:raise TimeoutError('Native browser command exceeded 30 seconds')
  line=self.process.stdout.readline()
  if not line:raise RuntimeError('Native browser transport exited')
  return json.loads(line)
 def call(self,method,params=None):
  self.seq+=1;self.process.stdin.write(json.dumps({'id':self.seq,'method':method,'params':params or {}})+'\n');self.process.stdin.flush();r=self.read()
  if r.get('id')!=self.seq:raise RuntimeError('Native browser response identity mismatch')
  if 'error' in r:raise RuntimeError(r['error'])
  return r['result']
 def evaluate(self,js):
  self.seq+=1;self.process.stdin.write(json.dumps({'id':self.seq,'method':'evaluate','expression':js})+'\n');self.process.stdin.flush();r=self.read()
  if r.get('id')!=self.seq:raise RuntimeError('Native browser response identity mismatch')
  if 'error' in r:raise RuntimeError(r['error'])
  return r['result']
 def wait(self,text):
  for _ in range(100):
   dom=self.evaluate('document.documentElement.outerHTML') or ''
   if text in dom:return dom
   time.sleep(.1)
  raise AssertionError('Native browser did not render '+text)
 def refresh(self):self.evaluate("document.querySelector('button').click()")
 def close(self):
  if hasattr(self,'process'):
   if self.process.poll() is None:
    try:self.call('close')
    except (OSError,RuntimeError,TimeoutError):pass
   if self.process.poll() is None:
    try:os.killpg(self.process.pid,signal.SIGTERM);self.process.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(self.process.pid,signal.SIGKILL);self.process.wait()
   for pipe in (self.process.stdin,self.process.stdout,self.process.stderr):pipe.close()
