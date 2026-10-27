"""Bind current source-player/proxy observations at the stable checkpoint only."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-37-verification-20261027'

def main():
    paths=[
        'services/web/app/sources/NativeExamples.js',
        'services/web/app/sources/sourcePlayback.js',
        'services/web/app/api/[...path]/route.js',
        'tests/source_playback.test.mjs','tests/source_proxy_range.test.mjs',
        'tests/supplement_media_browser.cjs','tests/supplement_range_browser.cjs',
        'tests/supplement_recovery_visual.cjs',
    ]
    for relative in ['media-final/observations.json','keyboard-visual/observations.json','range-green/observations.json','source-playback.log','source-proxy-green.log','web-build-final.log','media-observations.json']:
        paths.append(str((OUT/relative).relative_to(ROOT)))
    bindings=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]
    result=dict(entry_commit='895cb51afdc1ec9c22c57c086eb0fcebce8d930f',bindings=bindings,
        actual_local_owners='Next/Go/PostgreSQL/private MinIO, installed Chrome; same admitted source recordings.',
        controlled_boundary='Only media HTTP failures and actual saved DRAL-window row selection; event fixtures substitute an HTML media object.',
        reuse='All51 native Go race observations/imports and unchanged source-read/layout observations retain their original receipts. Only media and proxy behavior was invalidated.',
        limits='No data re-admission, source script, model, synthesis, acoustic-quality claim, purchase, deployment, PBT or publication.')
    (HERE/'EVIDENCE.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
