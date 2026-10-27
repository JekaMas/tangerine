"""Read-only developer comparison over the actual native-rendered WAVs."""
import argparse,html,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--port',type=int,default=52759);a=p.parse_args();evidence=ROOT/a.evidence
rows=[('obstructive','source-1.wav','Safety instruction — source'),('obstructive','mixed.wav','Obstructive interruption — mixed'),('cooperative_backchannel','source-1.wav','Invited backchannel — source'),('cooperative_backchannel','mixed.wav','Cooperative backchannel — mixed')]
font=ROOT/'services/web/public/fonts/SourceSans3.ttf'
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/font.ttf' and font:self.send(200,'font/ttf',font.read_bytes());return
  for n,(kind,name,label) in enumerate(rows):
   if self.path==f'/audio/{n}.wav':self.send(200,'audio/wav',(evidence/kind/name).read_bytes());return
  if self.path!='/':self.send(404,'text/plain',b'Not found');return
  cards=[]
  for n,(kind,name,label) in enumerate(rows):
   c=json.loads((evidence/kind/'progress.json').read_text())['composition'];o=c['overlaps'][0]
   note='The safety instruction must remain audible; B should wait.' if kind=='obstructive' else 'A explicitly invites a brief acknowledgment; the main message remains audible.'
   cards.append(f'<section><h2>{html.escape(label)}</h2><p>{note}</p><audio id="clip{n}" controls preload="metadata" aria-label="{html.escape(label)}" src="/audio/{n}.wav"></audio><p class="caption">'+('Original single speaker recording.' if name.startswith('source') else f'Saved production composition. Selected overlap: {o["final_start"]/24000:.2f}–{o["final_end"]/24000:.2f}s.')+'</p></section>')
  page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine — simultaneous speech comparison</title><style>@font-face{font-family:Source Sans 3;src:url('/font.ttf')}*{box-sizing:border-box}body{font-family:'Source Sans 3',sans-serif;font-size:17px;line-height:1.45;margin:0;background:#faf8f3;color:#29251e}main{max-width:1000px;margin:40px auto;padding:0 24px}h1{font-size:32px;line-height:1.15;margin:10px 0 18px}h2{font-size:21px;margin:0 0 10px}p{max-width:72ch}.caption{font-size:14px;color:#62594d}section{border:1px solid #d6cbb8;border-radius:12px;background:white;padding:22px;margin:18px 0}audio{width:100%;max-width:700px}a{color:#9b3c10}audio:focus-visible{outline:3px solid #9b3c10;outline-offset:4px}</style><main><p class="caption">TANGERINE · ITERATION 32 · ACTUAL LOCAL RECORDINGS</p><h1>Simultaneous speech and word masking</h1><p>Compare the retained local source with the waveform mixed by Tangerine’s production composer. Two distinct local voices contribute during the overlap. These are authored development scenes; no hosted service or paid credits were used.</p>'''+''.join(cards)+'''<p class="caption">Independent local recognition omitted the safety warning in the obstructive mix and retained the museum message in the cooperative mix. This is finite machine evidence, not universal perceptual qualification.</p></main></html>'''
  self.send(200,'text/html; charset=utf-8',page.encode())
 def send(self,status,mime,body):self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'http://127.0.0.1:{server.server_port}/',flush=True);server.serve_forever()
