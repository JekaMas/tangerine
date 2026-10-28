"""Read-only current Gemini pair and actual Chrome; no model dispatch."""
import html,importlib.util,json,os,subprocess,threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2];PAIR=ROOT/'data/completion-leftovers-20261028/gemini-current-api';OUT=PAIR.parent/'gemini-browser';NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
def main():
 OUT.mkdir(parents=True,exist_ok=True);plan=json.loads((PAIR/'plan.json').read_text());result=json.loads((PAIR/'result.json').read_text());assert result['status']=='complete'
 spec=importlib.util.spec_from_file_location('saved_media_owner',ROOT/'audit/iteration-25-qwen-20261026/player.py');media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)
 targets=''.join('<tr><td>'+str(i+1)+'</td><td>'+html.escape(t['word'])+'</td><td>'+html.escape(t['description'])+'</td></tr>' for i,t in enumerate(plan['source_material']['targets']))
 turns=''.join('<p><strong>'+('Speaker 1 · Kore' if t['speaker_id']=='s1' else 'Speaker 2 · Puck')+':</strong> '+html.escape(t['canonical_text'])+'</p>' for t in plan['source_material']['turns'])
 cards=''.join('<section><h2>'+label+'</h2><audio controls preload="metadata" src="/gemini-'+v+'.wav" aria-label="'+label+'"></audio><p>'+str(result[v+'_seconds'])+' seconds · complete 20-turn recording</p></section>' for v,label in [('clean','Reference pronunciation'),('mistakes','Requested pronunciation contrasts')])
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine · Gemini speech comparison</title><style>@font-face{font-family:"Source Sans 3";src:url('/font.ttf')}*{box-sizing:border-box}body{margin:0;background:#f6f6f2;color:#25332d;font:17px/1.45 "Source Sans 3",sans-serif}main{max-width:1000px;margin:auto;padding:32px 24px}h1{font-size:36px;line-height:1.15}h2{font-size:23px;line-height:1.25}p{max-width:72ch}section,.notice{background:white;border:1px solid #dce1d8;border-radius:14px;padding:24px;margin:20px 0}.samples{display:grid;grid-template-columns:1fr 1fr;gap:20px}audio{width:100%}button{font:inherit;min-height:44px;padding:10px 18px;cursor:pointer}summary{font-weight:600;cursor:pointer}button:focus-visible,audio:focus-visible,summary:focus-visible{outline:3px solid #aa4c21;outline-offset:4px}.table{overflow:auto}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px 10px;border-bottom:1px solid #dce1d8;vertical-align:top}@media(max-width:680px){main{padding:24px 16px}.samples{display:block}h1{font-size:30px}section,.notice{padding:18px}}</style><main><h1>Gemini pronunciation comparison</h1><p>Two speakers, the same 20 saved turns and 26 pronunciation targets. Kore and Puck; American/British accent directions.</p><p class="notice">Both complete recordings are available. This is a new complete comparison; the earlier recordings are retained separately.</p><button type="button" id="refresh">Refresh saved recordings</button><div class="samples">'''+cards+'''</div><section><p>Pronunciation directions request contrasts; they do not confirm every sound. Accents and legitimate contextual variants are not errors. These saved samples were made within your Free allowance.</p><details><summary>Pronunciation targets</summary><div class="table"><table><thead><tr><th>Target</th><th>Word or passage</th><th>Requested deviation</th></tr></thead><tbody>'''+targets+'''</tbody></table></div></details></section><section><details><summary>Original dialogue</summary>'''+turns+'''</details></section><p>Playback and Refresh read saved files; no generation or payment occurs.</p></main><script>document.getElementById('refresh').addEventListener('click',()=>location.reload());document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()})));</script></html>'''
 (OUT/'comparison.html').write_text(page)
 parent=media.handler(PAIR);events=[]
 class View(parent):
  def do_GET(self):
   path=urlsplit(self.path).path
   if path=='/':self.respond(200,page.encode(),'text/html; charset=utf-8')
   elif path=='/font.ttf':self.respond(200,media.FONT.read_bytes(),'font/ttf')
   elif path in ['/gemini-clean.wav','/gemini-mistakes.wav']:
    body=media.read_saved((PAIR/path[1:]).read_bytes)
    self.respond(200 if body else 503,body or b'The saved recording is temporarily unavailable. Refresh to retry.','audio/wav' if body else 'text/plain')
   else:self.respond(404,b'This saved comparison resource is not available.','text/plain')
  def respond(self,status,body,kind):events.append(dict(method=self.command,path=self.path,status=status));super().respond(status,body,kind)
 server=ThreadingHTTPServer(('127.0.0.1',0),View);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  env={**os.environ,'QWEN_URL':'http://127.0.0.1:'+str(server.server_port),'QWEN_OUTPUT':str(OUT),'TANGERINE_PLAYWRIGHT_MODULE':str(NODE.parent.parent/'node_modules/playwright')}
  with (OUT/'browser.log').open('w') as log:r=subprocess.run([str(NODE),str(ROOT/'tests/completion_leftovers_gemini.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=180)
  (OUT/'exit-code').write_text(str(r.returncode)+'\n');return r.returncode
 finally:
  (OUT/'requests.json').write_text(json.dumps(events,indent=2)+'\n');server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':raise SystemExit(main())
