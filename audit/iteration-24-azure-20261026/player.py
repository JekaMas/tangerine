"""Loopback comparison player. Public dialogue/WAVs only; no credentials served."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse,html,json,wave
ROOT=Path(__file__).resolve().parents[2]
FONT=ROOT/'services/web/public/fonts/SourceSans3.ttf'
MATERIAL=Path(__file__).with_name('material.json')

def page(output,origin):
 material=json.loads(MATERIAL.read_text());players=[]
 for variant,label in [('clean','Correct pronunciation'),('mistakes','Four requested pronunciation mistakes')]:
  file=output/('azure-'+variant+'.wav')
  if file.exists():
   with wave.open(str(file),'rb') as a:duration=a.getnframes()/a.getframerate()
   content=f'<audio controls preload="metadata" aria-label="{label}" src="/{file.name}"></audio><p>{duration:.2f} seconds</p><a download href="/{file.name}">Download WAV</a>'
  else:content='<p class="pending">Waiting for Azure F0 access. No recording has been generated.</p>'
  players.append(f'<section><h2>{label}</h2>{content}</section>')
 status='Both recordings are available.' if all((output/f'azure-{v}.wav').exists() for v in ['clean','mistakes']) else 'Comparison incomplete. Complete Microsoft sign-in and configure an existing Azure F0 Speech resource, key and region. Completed pieces are retained.'
 note='Controlled protocol fixture audio; this does not demonstrate Azure voices or pronunciation.' if origin=='controlled' else 'Azure Speech F0 comparison. Voice labels and IPA are requests; acoustic realization remains unknown until observed.'
 rows=''.join('<tr><td>'+html.escape(r['id']+' / '+r['speaker_id'])+'</td><td>'+html.escape(r['target']['word'])+'</td><td>'+html.escape(r['target']['description'])+'</td><td>/'+html.escape(r['target']['mutated_ipa'])+'/</td></tr>' for r in material['turns'])
 text=''.join('<p><strong>'+html.escape(r['speaker_id'])+':</strong> '+html.escape(r['canonical_text'])+'</p>' for r in material['turns'])
 return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine · Azure speech comparison</title><style>
 @font-face{{font-family:"Source Sans 3";src:url('/font.ttf') format('truetype');font-display:swap}}*{{box-sizing:border-box}}body{{margin:0;background:#f5f6fa;color:#24302c;font:17px/1.45 "Source Sans 3",sans-serif}}main{{max-width:980px;margin:auto;padding:32px 20px}}h1{{font-size:34px;line-height:1.15;margin:8px 0 16px}}h2{{font-size:22px}}p{{max-width:72ch}}section,.notice{{background:white;border:1px solid #d9dfe1;border-radius:12px;padding:24px;margin:20px 0}}.notice{{border-left:4px solid #a95026}}.samples{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}audio{{width:100%}}button{{font:inherit;border:1px solid #bac5cb;background:white;border-radius:8px;padding:10px 18px;color:inherit;cursor:pointer}}button:focus-visible,a:focus-visible,summary:focus-visible{{outline:3px solid #a95026;outline-offset:4px}}a{{color:#7e3e1f}}summary{{font-weight:600;cursor:pointer}}.table{{overflow-x:auto}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #d9dfe1;vertical-align:top}}.pending{{color:#65583c}}@media(max-width:640px){{main{{padding:24px 16px}}h1{{font-size:29px}}.samples{{display:block}}section,.notice{{padding:18px}}th,td{{padding:8px}}}}@media(max-width:380px){{table{{font-size:15px}}}}
 </style><main><a href="http://localhost:3000/">Tangerine workspace</a><h1>Azure speech comparison</h1><p>Two speakers, the same four saved turns, and four pronunciation targets.</p><p>{html.escape(note)}</p><div class="notice" role="status">{status}</div><button onclick="location.reload()">Refresh saved recordings</button><div class="samples">{''.join(players)}</div><section><details><summary>Requested mistakes</summary><p>Speaker1: requested American Jenny. Speaker2: requested British Ryan. An accent alone is not an error.</p><div class="table"><table><thead><tr><th>Turn / speaker</th><th>Word</th><th>Requested deviation</th><th>Requested IPA</th></tr></thead><tbody>{rows}</tbody></table></div></details></section><section><details><summary>Original dialogue</summary>{text}</details></section><p>Refresh and playback perform no synthesis. No paid tier, trial or provider fallback is selected.</p></main><script>document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(b=>{{if(a!==b)b.pause()}})))</script></html>'''

def handler(output,origin):
 class Player(BaseHTTPRequestHandler):
  def do_GET(self):
   path=urlsplit(self.path).path
   if path=='/':body=page(output,origin).encode();kind='text/html; charset=utf-8'
   elif path=='/font.ttf':body=FONT.read_bytes();kind='font/ttf'
   elif path in ['/azure-clean.wav','/azure-mistakes.wav'] and (output/path[1:]).is_file():body=(output/path[1:]).read_bytes();kind='audio/wav'
   else:self.send_error(404);return
   self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 return Player

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--port',type=int,default=0);p.add_argument('--origin',choices=['live','controlled'],default='live');a=p.parse_args()
 server=ThreadingHTTPServer(('127.0.0.1',a.port),handler(a.output,a.origin));print('Listening on http://127.0.0.1:'+str(server.server_address[1])+'/',flush=True);server.serve_forever()
