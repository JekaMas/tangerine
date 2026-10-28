"""Actual saved Qwen pair, existing read-only player, Chrome pointer/keyboard."""
import importlib.util,json,os,subprocess,threading
from http.server import ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/completion-leftovers-20261028/qwen-browser';PAIR=OUT.parent/'qwen-mps-float32-cpu-codec'
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
def main():
 if not (PAIR/'result.json').exists():raise RuntimeError('Both complete native variants are required before playback acceptance')
 OUT.mkdir(parents=True,exist_ok=True);spec=importlib.util.spec_from_file_location('qwen_saved_player',ROOT/'audit/iteration-25-qwen-20261026/player.py');owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
 parent=owner.handler(PAIR);events=[]
 class Observed(parent):
  def respond(self,status,body,kind):events.append(dict(method=self.command,path=self.path,status=status));super().respond(status,body,kind)
 server=ThreadingHTTPServer(('127.0.0.1',0),Observed);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  env={**os.environ,'QWEN_URL':'http://127.0.0.1:'+str(server.server_port),'QWEN_OUTPUT':str(OUT),'TANGERINE_PLAYWRIGHT_MODULE':str(NODE.parent.parent/'node_modules/playwright')}
  with (OUT/'browser.log').open('w') as log:r=subprocess.run([str(NODE),str(ROOT/'tests/completion_leftovers_qwen.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=180)
  (OUT/'exit-code').write_text(str(r.returncode)+'\n');return r.returncode
 finally:
  (OUT/'requests.json').write_text(json.dumps(events,indent=2)+'\n');server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':raise SystemExit(main())
