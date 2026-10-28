"""Observe the actual saved I26 sheet; no inference, synthesis or user services."""
import importlib.util,json,os,subprocess,threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/completion-leftovers-20261028/i26'
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    path=ROOT/'audit/iteration-26-acoustic-20261026/listening.py'
    spec=importlib.util.spec_from_file_location('i26_actual_sheet',path)
    owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    rows=json.loads((ROOT/'data/iteration-26-acoustic-20261026/gallery.json').read_text())
    parent=owner.handler(rows,ROOT/'data/iteration-26-acoustic-20261026')
    events=[]
    class Observed(parent):
        def respond(self,status,body,kind):
            events.append(dict(method=self.command,path=self.path,status=status))
            super().respond(status,body,kind)
    server=ThreadingHTTPServer(('127.0.0.1',0),Observed)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:
        env={**os.environ,'TANGERINE_PLAYWRIGHT_MODULE':str(NODE.parent.parent/'node_modules/playwright'),'I26_URL':'http://127.0.0.1:'+str(server.server_port),'I26_OUTPUT':str(OUT)}
        with (OUT/'browser.log').open('w') as log:
            result=subprocess.run([str(NODE),str(ROOT/'tests/completion_leftovers_i26.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=180)
        (OUT/'exit-code').write_text(str(result.returncode)+'\n')
        return result.returncode
    finally:
        (OUT/'requests.json').write_text(json.dumps(events,indent=2)+'\n')
        server.shutdown();server.server_close();worker.join(timeout=5)

if __name__=='__main__':raise SystemExit(main())
