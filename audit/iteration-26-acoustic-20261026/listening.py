"""Read-only selected target/control sheet. Playback and Refresh never infer."""
import argparse
import html
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


observer=load('selected_probe_observer',HERE/'observe.py')
# The existing saved-media owner supplies one read retry, safe HTTP responses
# and the local font. No comparison-specific synthesis or insurance UI is used.
media=load('saved_comparison_media',ROOT/'audit/iteration-25-qwen-20261026/player.py')
LABELS={'clean':'Clean reference','mutated':'Requested mistake',
        'acceptable':'Valid contextual variant','misleading_metadata':'Clean control · false claim withheld'}
CAPTIONS={'confirmed':'Confirmed in this model check',
          'not_realized':'The model did not confirm this target',
          'uncertain':'Uncertain · keep the observations separate',
          'not_run':'Listening observation not performed'}


def materialize(output):
    target=output/'gallery.json'
    if target.exists():return json.loads(target.read_text())
    selection=json.loads((HERE/'selection.json').read_text());rows=[]
    retained=ROOT/selection['retained_linking']
    rows.append(dict(id='linking',title='Linking',probe=json.loads((retained/'withheld.json').read_text()),
                     comparison=str(retained/'comparison.json'),physical=None,origin='Retained complete four-control observation'))
    for row in selection['cases']:
        saved=output/'selected'/row['id']/'frozen.json'
        frozen=json.loads(saved.read_text()) if saved.exists() else observer.prepare(row['id'])
        rows.append(dict(id=row['id'],title=row['id'].replace('-',' ').capitalize(),probe=frozen['probe'],
                         comparison=str(output/'selected'/row['id']/'comparison.json'),physical=frozen['physical'],origin=row['repair']))
    observer.save(target,rows)
    return rows


def selection_reader(output):
    """Admit the saved selection once; a failed read can recover on Refresh."""
    saved=None
    def read():
        nonlocal saved
        if saved is None:saved=media.read_saved(lambda:materialize(output))
        return saved or []
    return read


def page(rows):
    escape=lambda value:html.escape(str(value))
    cards=[]
    for row in rows:
        path=Path(row['comparison'])
        result=media.read_saved(lambda:json.loads(path.read_text())) if path.exists() else None
        contexts={c['unit_id']:c['public_context'] for c in row['probe']['clips']}
        private={c['role']:c for c in row['probe']['withheld']}
        status=CAPTIONS[(result or {}).get('audio_confirmation','not_run')] if result is not None else 'Saved listening observation unavailable'
        notes=''
        if result is None:
            notes+='<p>The saved listening observation could not be loaded. Refresh saved observations to try again. The recordings remain available; no model call is needed to play them.</p>'
        if result and result.get('error'):
            notes+='<p>Listening confirmation was unavailable. The saved recordings remain available. Refresh saved observations to read any completed result.</p>'
        if result and result.get('false_alarms'):
            count=result['false_alarms']
            notes+='<p>The listening model incorrectly flagged '+escape(count)+' correct '+('control' if count==1 else 'controls')+'. That prevents confirmation.</p>'
        if result and result.get('physical_auditory_conflict'):
            notes+='<p>The waveform supports a change, while the listening observation does not confirm the intended perception. Both observations are retained.</p>'
        players=[]
        for role,label in LABELS.items():
            clip=private[role]
            observation=next((c for c in (result or {}).get('cases',[]) if c['role']==role),None)
            reason=' '.join(f.get('reason') or f.get('description') or '' for f in (observation or {}).get('findings',[]))
            allowed='<p><strong>Allowed context:</strong> '+escape(contexts[clip['unit_id']])+'</p>' if role=='acceptable' else ''
            explanation='<details class="model-note"><summary>Saved listening observation</summary><p>'+escape(reason)+'</p></details>' if reason else ''
            source='/audio/'+row['id']+'/'+role+'.wav'
            players.append('<article><h3>'+escape(label)+'</h3>'+allowed+'<audio controls preload="metadata" aria-label="'+escape(row['title']+' · '+label)+'" src="'+source+'"></audio><p class="playback-status" role="status"></p><a download href="'+source+'">Download WAV</a>'+explanation+'</article>')
        physical=''
        if row.get('physical'):
            physical='<details><summary>Saved waveform observations</summary><p>These measurements establish the scoped acoustic change. Meaning and perceived correctness remain separate.</p><pre>'+escape(json.dumps(row['physical']['observations'],ensure_ascii=False,indent=2))+'</pre></details>'
        voice=row['probe']['binding']
        speaker={'af_heart':'Heart','bm_george':'George'}.get(voice.get('voice'),voice.get('voice'))
        locale={'en-US':'American English','en-GB':'British English'}.get(voice.get('locale'),voice.get('locale'))
        cards.append('<section id="'+row['id']+'"><h2>'+escape(row['title'])+'</h2><p class="status">'+escape(status)+'</p>'+notes+'<p><strong>Target context:</strong> '+escape(contexts[private['clean']['unit_id']])+'</p><p class="source">Local Kokoro · '+escape(speaker)+' · '+escape(locale)+'</p><div class="players">'+''.join(players)+'</div>'+physical+'</section>')
    links=''.join('<a href="#'+r['id']+'">'+escape(r['title'])+'</a>' for r in rows)
    summary='Five selected saved examples, with their correct controls and actual listening observations.' if rows else 'No saved comparison is available yet. Existing Tangerine practice and recordings remain available; refresh after the local examples are available.'
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine · Selected acoustic checks</title><style>
@font-face{font-family:"Source Sans 3";src:url('/font.ttf')}*{box-sizing:border-box}body{margin:0;background:#f6f6f2;color:#25332d;font:17px/1.45 "Source Sans 3",sans-serif}main{max-width:1120px;margin:auto;padding:32px 24px}h1{font-size:36px;line-height:1.15;max-width:26ch;margin:20px 0 12px}h2{font-size:26px;line-height:1.2;margin:0 0 12px}h3{font-size:20px;line-height:1.25;margin:0 0 10px}p{max-width:75ch}nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin:24px 0}a{color:#85421f}button{font:inherit;padding:10px 16px;min-height:44px;background:white;border:1px solid #9ca99d;border-radius:8px;color:inherit;cursor:pointer}section{margin:28px 0;padding:24px;background:white;border:1px solid #dce1d8;border-radius:14px}.status{font-weight:600;background:#fff0d8;color:#704200;padding:10px 14px;border-radius:8px;width:fit-content}.source{color:#4a5b50}.players{display:grid;grid-template-columns:1fr 1fr;gap:20px}article{padding:18px;border:1px solid #dce1d8;border-radius:10px}audio{width:100%;margin:10px 0}.model-note{margin-top:18px}summary{cursor:pointer;font-weight:600}details{margin-top:20px}pre{font:14px/1.45 monospace;white-space:pre-wrap;overflow-wrap:anywhere}button:focus-visible,a:focus-visible,audio:focus-visible,summary:focus-visible{outline:3px solid #aa4c21;outline-offset:4px}.intro{max-width:70ch}footer{margin:30px 0;color:#4a5b50}@media(max-width:680px){main{padding:24px 16px}h1{font-size:30px}section{padding:18px}.players{grid-template-columns:1fr}}
</style><main><a href="http://localhost:3000/">Tangerine workspace</a><h1>What the recordings support</h1><p class="intro">'''+summary+''' Local Kokoro speech; Gemini Free model observations are evidence on these examples, not universal perceptual gold.</p><p class="intro">A pronunciation can fail a narrow drill and remain correct in another context. Uncertainty stays visible and does not stop ordinary practice.</p><button id="refresh" type="button">Refresh saved observations</button><nav aria-label="Selected examples">'''+links+'</nav>'+''.join(cards)+'''<footer>Playback and Refresh read saved files. They generate no audio and make no model calls.</footer></main><script>
document.getElementById('refresh').addEventListener('click',()=>location.reload());
document.querySelectorAll('audio').forEach(a=>{
 let retried=false;const status=a.parentElement.querySelector('.playback-status');
 a.addEventListener('play',()=>document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()}));
 a.addEventListener('loadedmetadata',()=>status.textContent='');
 a.addEventListener('error',()=>{console.warn('Saved acoustic clip unavailable',{attempt:retried?2:1});if(!retried){retried=true;status.textContent='Retrying the saved clip. No new audio is generated.';setTimeout(()=>a.load(),1000)}else status.textContent='The saved clip could not be played. Refresh saved observations to try again. Other recordings remain available.'});
});
</script></html>'''


def handler(rows,output):
    class Listening(media.handler(output)):
        def do_GET(self):
            path=urlsplit(self.path).path
            if path!='/' and not path.startswith('/audio/'):
                super().do_GET();return
            current=rows() if callable(rows) else rows
            allowed={'/audio/'+row['id']+'/'+clip['role']+'.wav':ROOT/clip['audio_path'] for row in current for clip in row['probe']['withheld']}
            if path=='/':self.respond(200,page(current).encode(),'text/html; charset=utf-8')
            elif path in allowed:
                raw=media.read_saved(allowed[path].read_bytes)
                if raw is None:self.respond(503,b'The saved clip is temporarily unavailable. Refresh saved observations to try again.','text/plain; charset=utf-8')
                else:self.respond(200,raw,'audio/wav')
            else:super().do_GET()
    return Listening


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--port',type=int,default=8772);args=parser.parse_args()
    rows=selection_reader(args.out)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler(rows,args.out))
    print('Read-only selected listening sheet on http://127.0.0.1:'+str(server.server_port)+'/',flush=True);server.serve_forever()
