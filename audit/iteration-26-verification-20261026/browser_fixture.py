"""Actual I26 sheet with test-owned read/HTTP failures; no inference routes."""
import argparse
import copy
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'audit/iteration-26-acoustic-20261026/listening.py'
spec=importlib.util.spec_from_file_location('selected_listening_browser_owner',source)
listening=importlib.util.module_from_spec(spec);spec.loader.exec_module(listening)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
    output=args.out.resolve();output.mkdir(parents=True,exist_ok=True)
    rows=copy.deepcopy(json.loads((ROOT/'data/iteration-26-acoustic-20261026/gallery.json').read_text()))
    (output/'original-comparison.json').write_text(Path(rows[0]['comparison']).read_text())
    (output/'comparison.json').write_text('{private_backend_canary')
    rows[0]['comparison']=str(output/'comparison.json')
    (output/'original-gallery.json').write_text(json.dumps(rows))
    (output/'gallery.json').write_text('{private_backend_canary')
    parent=listening.handler(listening.selection_reader(output),output)
    events=[];lock=threading.Lock();counts={}
    class Observed(parent):
        def do_GET(self):
            path=urlsplit(self.path).path
            with lock:
                counts[path]=counts.get(path,0)+1;number=counts[path]
            transient=path=='/audio/linking/clean.wav' and number==1
            persistent=path=='/audio/linking/mutated.wav' and not (output/'media-available').exists()
            if transient or persistent:
                self.respond(503,b'private_backend_canary: controlled saved-media dependency failure','text/plain; charset=utf-8')
            else:super().do_GET()

        def respond(self,status,body,kind):
            super().respond(status,body,kind)
            with lock:
                events.append(dict(path=urlsplit(self.path).path,status=status,bytes=len(body)))
                target=output/'http-observations.json';temporary=output/'http-observations.partial'
                temporary.write_text(json.dumps(events,indent=2)+'\n');temporary.replace(target)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Observed)
    (output/'server.json').write_text(json.dumps(dict(port=server.server_port,origin='actual I26 source; controlled file/HTTP failures; saved real Kokoro clips',inference_calls=0),indent=2)+'\n')
    print('Selected listening recovery fixture on http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
    server.serve_forever()


if __name__=='__main__':main()
