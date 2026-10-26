"""Read-only, loopback listening sheet for the finite Qwen comparison."""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
from urllib.parse import urlsplit
import wave

ROOT = Path(__file__).resolve().parents[2]
MATERIAL = ROOT / 'audit/iteration-24-azure-20261026/material.json'
FONT = ROOT / 'services/web/public/fonts/SourceSans3.ttf'


def read_saved(read, fallback=None):
    """Retry a failed local read once; existing playable media stays usable."""
    for attempt in range(2):
        try:
            return read()
        except (OSError, ValueError, EOFError, wave.Error) as error:
            logging.warning('Saved comparison read failed: %s (attempt %s)', type(error).__name__, attempt+1)
    return fallback


def duration(file):
    with wave.open(str(file), 'rb') as audio:
        return audio.getnframes()/audio.getframerate()


def page(output, origin='local'):
    material = read_saved(lambda: json.loads(MATERIAL.read_text()))
    progress = read_saved(lambda: json.loads((output/'state.json').read_text())) if (output/'state.json').exists() else None
    cards = []
    for variant, title, subtitle in [
            ('clean', 'Reference pronunciation', 'The saved original dialogue.'),
            ('mistakes', 'Requested pronunciation mistakes', 'The same dialogue with four phonetic respellings.')]:
        file = output/('qwen-'+variant+'.wav')
        if file.exists():
            seconds = read_saved(lambda: duration(file))
            caption = f'{seconds:.2f} seconds · complete four-turn recording' if seconds is not None else 'Saved recording · duration temporarily unavailable'
            content = f'<audio controls preload="metadata" src="/{file.name}" aria-label="{title}"></audio><p class="playback-status" role="status"></p><p>{caption}</p><a href="/{file.name}" download>Download WAV</a>'
        else:
            content = '<p>This complete recording is not ready. Saved pieces are retained.</p>'
        cards.append(f'<section><h2>{title}</h2><p>{subtitle}</p>{content}</section>')
    available = sum((output/('qwen-'+v+'.wav')).exists() for v in ('clean', 'mistakes'))
    if available == 2:
        status = 'Both complete recordings are available.'
    elif progress:
        status = progress['message']
    elif available:
        status = 'One complete recording is available. The comparison is incomplete.'
    else:
        status = 'The comparison is incomplete. No complete recording is available yet.'
    if progress is None and (output/'state.json').exists():
        status += ' Progress details are temporarily unavailable. Refresh saved recordings to try again.'
    if progress:
        status += f" {progress['completed_pieces']} of {progress['total_pieces']} pieces saved."
    note = 'Qwen3-TTS CustomVoice 0.6B · Ryan and Aiden · local inference.'
    if origin == 'controlled':
        note = 'Constructed playback fixture. This audio does not demonstrate Qwen speech or pronunciation.'
    transcript = ''.join('<p><strong>'+html.escape(r['speaker_id'])+':</strong> '+html.escape(r['canonical_text'])+'</p>' for r in material['turns']) if material else '<p>The saved transcript is temporarily unavailable. Refresh saved recordings to try again.</p>'
    targets = ''.join('<tr><td>'+html.escape(r['id']+' / '+r['speaker_id'])+'</td><td>'+html.escape(r['target']['word'])+'</td><td>'+html.escape(r['target']['description'])+'</td><td>'+html.escape(r['target']['respelling'])+'</td></tr>' for r in material['turns']) if material else '<tr><td colspan="4">The saved targets are temporarily unavailable. Refresh saved recordings to try again.</td></tr>'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine · Qwen dialogue comparison</title><style>
@font-face{{font-family:"Source Sans 3";src:url('/font.ttf') format('truetype');font-display:swap}}*{{box-sizing:border-box}}body{{margin:0;background:#f6f6f2;color:#25332d;font:17px/1.45 "Source Sans 3",sans-serif}}main{{max-width:1000px;margin:auto;padding:32px 24px}}h1{{font-size:36px;line-height:1.15;margin:18px 0 12px}}h2{{font-size:23px;line-height:1.25;margin:0 0 12px}}p{{max-width:72ch;margin:12px 0}}.intro{{max-width:65ch}}section,.notice{{background:white;border:1px solid #dce1d8;border-radius:14px;padding:24px;margin:20px 0}}.notice{{border-left:5px solid #a64b20}}.samples{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.samples section{{margin-bottom:0}}audio{{width:100%;margin:12px 0}}button{{font:inherit;border:1px solid #9ca99d;border-radius:8px;padding:10px 18px;background:white;color:inherit;cursor:pointer}}a{{color:#85421f}}button:focus-visible,a:focus-visible,summary:focus-visible,audio:focus-visible{{outline:3px solid #aa4c21;outline-offset:4px}}summary{{font-weight:600;cursor:pointer}}.table{{overflow-x:auto}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;padding:12px 10px;border-bottom:1px solid #dce1d8;vertical-align:top}}footer{{margin-top:24px;color:#4a5b50}}@media(max-width:680px){{main{{padding:24px 16px}}h1{{font-size:30px}}.samples{{display:block}}section,.notice{{padding:18px}}th,td{{padding:10px 8px}}}}@media(max-width:380px){{table{{font-size:15px}}}}
</style><main><a href="http://localhost:3000/">Tangerine workspace</a><h1>Qwen dialogue comparison</h1><p class="intro">Two voices, the same four saved turns, and four pronunciation targets.</p><p>{html.escape(note)}</p><div class="notice" role="status">{html.escape(status)}</div><button id="refresh" type="button">Refresh saved recordings</button><div class="samples">{''.join(cards)}</div><section><p><strong>Pronunciation approximation.</strong> The mistake version changes only the four selected spellings sent to Qwen. This model has no exact IPA control. A requested sound or stress change is not a confirmed audible mistake, and an accent alone is not an error.</p><details><summary>Requested mistakes and spellings</summary><div class="table"><table><thead><tr><th>Turn / speaker</th><th>Word</th><th>Requested deviation</th><th>Qwen spelling</th></tr></thead><tbody>{targets}</tbody></table></div></details></section><section><details><summary>Original dialogue</summary>{transcript}</details></section><footer><p>Playback and refresh read saved recordings and generate no new audio. The earlier 5.6-second preview is not a completed comparison.</p></footer></main><script>
document.getElementById('refresh').addEventListener('click',()=>location.reload());
document.querySelectorAll('audio').forEach(a=>{{
 let retried=false;const status=a.parentElement.querySelector('.playback-status');
 a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(b=>{{if(a!==b)b.pause()}}));
 a.addEventListener('loadedmetadata',()=>status.textContent='');
 a.addEventListener('error',()=>{{
  console.warn('Saved Qwen recording unavailable',{{attempt:retried?2:1}});
  if(!retried){{retried=true;status.textContent='Retrying the saved recording. No new audio is generated.';setTimeout(()=>a.load(),1000)}}
  else status.textContent='The saved recording could not be played. Refresh saved recordings and try again. No new audio is generated.';
 }});
}});
</script></html>'''


def handler(output, origin='local'):
    class Player(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/':
                body, kind = page(output, origin).encode(), 'text/html; charset=utf-8'
            elif path == '/font.ttf':
                body, kind = read_saved(FONT.read_bytes), 'font/ttf'
            elif path in ('/qwen-clean.wav', '/qwen-mistakes.wav') and (output/path[1:]).is_file():
                body, kind = read_saved((output/path[1:]).read_bytes), 'audio/wav'
            else:
                self.respond(404, b'This saved comparison resource is not available.', 'text/plain; charset=utf-8')
                return
            if body is None:
                self.respond(503, b'The saved file is temporarily unavailable. Refresh saved recordings to try again.', 'text/plain; charset=utf-8')
            else:
                self.respond(200, body, kind)

        def respond(self, status, body, kind):
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass
    return Player


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--origin', choices=['local', 'controlled'], default='local')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(args.output, args.origin))
    print('Listening on http://127.0.0.1:'+str(server.server_port)+'/', flush=True)
    server.serve_forever()
