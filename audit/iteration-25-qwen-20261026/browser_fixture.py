"""Test-owned playback/recovery views. Constructed PCM; zero model calls."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
import wave

spec = importlib.util.spec_from_file_location('qwen_fixture_player', Path(__file__).with_name('player.py'))
player = importlib.util.module_from_spec(spec)
spec.loader.exec_module(player)


def setup(output):
    for name in ['empty', 'partial', 'complete', 'transient', 'failure', 'read_failure']:
        directory = output/name
        directory.mkdir(parents=True, exist_ok=True)
        (directory/'state.json').write_text(json.dumps(dict(
            state='complete' if name in ['complete', 'transient', 'failure'] else 'paused',
            message='Both complete recordings are available.' if name in ['complete', 'transient', 'failure'] else 'The comparison stopped. Saved text and completed pieces are retained. Resume explicitly when ready.',
            completed_pieces=8 if name in ['complete', 'transient', 'failure'] else 4 if name == 'partial' else 0,
            total_pieces=8)))
        if name == 'read_failure':
            (directory/'state.json').write_text('{unfinished')
        for variant in (['clean', 'mistakes'] if name in ['complete', 'transient', 'failure'] else ['clean'] if name in ['partial', 'read_failure'] else []):
            with wave.open(str(directory/('qwen-'+variant+'.wav')), 'wb') as audio:
                audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                audio.writeframes(b''.join(struct.pack('<h', int(4000*math.sin(i*.06))) for i in range(144000)))


def handler(output):
    counts = {}
    class Fixture(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            parts = path.strip('/').split('/')
            state = parts[0]
            if path == '/font.ttf':
                body, kind = player.FONT.read_bytes(), 'font/ttf'
            elif state in ['empty', 'partial', 'complete', 'transient', 'failure', 'read_failure']:
                if len(parts) == 1 or parts[1] == '':
                    body = player.page(output/state, 'controlled').replace('src="/qwen-', 'src="/'+state+'/qwen-').replace('href="/qwen-', 'href="/'+state+'/qwen-').encode()
                    kind = 'text/html; charset=utf-8'
                elif len(parts) == 2 and parts[1] in ['qwen-clean.wav', 'qwen-mistakes.wav'] and (output/state/parts[1]).exists():
                    counts[path] = counts.get(path, 0)+1
                    (output/'http-observations.json').write_text(json.dumps(dict(counts=counts, model_calls=0), indent=2))
                    if state == 'failure' or state == 'transient' and counts[path] == 1:
                        self.send_response(503); self.send_header('Content-Length', '0'); self.end_headers(); return
                    body, kind = (output/state/parts[1]).read_bytes(), 'audio/wav'
                else:
                    self.send_error(404); return
            else:
                self.send_error(404); return
            self.send_response(200); self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'no-store')
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *args):
            pass
    return Fixture


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8771)
    args = parser.parse_args()
    setup(args.output)
    http = ThreadingHTTPServer(('127.0.0.1', args.port), handler(args.output))
    print('Controlled player on http://127.0.0.1:'+str(http.server_port)+'/empty/', flush=True)
    http.serve_forever()
