"""Static, local viewer for the actual complete case. No provider calls."""
from pathlib import Path
from html import escape
import json,shutil

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/iteration-29-saved-case-flow-20261026';SHARE=DATA/'share'

def main():
    SHARE.mkdir(exist_ok=True)
    shutil.copy2(DATA/'complete-intro.png',SHARE/'complete-intro.png')
    shutil.copy2(ROOT/'services/web/public/fonts/SourceSans3.ttf',SHARE/'SourceSans3.ttf')
    names=['final-result-current','final-feedback-1280','final-feedback-390','final-feedback-320']
    for name in names:shutil.copy2(DATA/'pictures'/(name+'.png'),SHARE/(name+'.png'))
    result=json.loads((DATA/'attempts/a5f608ea-6719-4682-9f86-d6330a4707b2-result.json').read_text())
    comments=''.join('<article><h3>'+escape(i['kind'])+'</h3><p class="prose">'+escape(i['text'])+'</p></article>' for i in result['feedback']['items'])
    pictures=''.join('<figure><a href="'+n+'.png"><img loading="lazy" alt="Actual '+n.replace('-',' ')+'" src="'+n+'.png"></a><figcaption>'+n.replace('-',' ')+'</figcaption></figure>' for n in names)
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tangerine · Actual complete flow</title><style>
@font-face{font-family:Source Sans;src:url(SourceSans3.ttf)}*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#1e2d39;font:18px/1.45 'Source Sans',sans-serif}main{max-width:1050px;margin:auto;padding:40px 24px 70px}h1{font-size:42px;line-height:1.12;letter-spacing:-.02em}h2{font-size:27px;margin-top:30px}h3{font-size:20px}p{max-width:75ch}.eyebrow{color:#934411;font-size:15px;font-weight:650;letter-spacing:.04em}section,details{padding:24px;background:white;border:1px solid #dce3e9;border-radius:12px;margin:24px 0}.score{font-size:38px;font-weight:650}.prose{white-space:pre-wrap}video,audio{display:block;width:100%;margin:18px 0}video{background:#172b3d;aspect-ratio:16/9;object-fit:contain}a{color:#934411;text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid #376d98;outline-offset:3px}summary{font-size:22px;font-weight:650;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:24px}figure{margin:0}img{width:100%;border:1px solid #dce3e9}figcaption{margin-top:8px}article{border-top:1px solid #dce3e9;padding-top:12px;margin-top:20px}@media(max-width:450px){main{padding:24px 16px}section,details{padding:18px}h1{font-size:34px}}
</style><main><p class="eyebrow">TANGERINE · ITERATION 29 · ACTUAL FUNCTIONAL EVIDENCE</p><h1>From a topic to saved feedback</h1>
<p>Two speakers, two text mistakes, a stored recording, an answer, exact scores and actual LLM recommendations.</p>
<section><h2>Watch the real flow</h2><video id="completed-video" controls preload="metadata" poster="complete-intro.png" src="tangerine-complete-flow.mp4"></video>
<p>Edited actual CUA footage. Cuts, compressed waits and source-frame gaps are disclosed. The matching saved WAV is synchronized separately. Editorial cards show the actual key and independent arithmetic; they are not fabricated product screens.</p>
<p>Gemini Free generated the saved text and mutations; local Kokoro produced the speech. A new ordinary attempt explicitly selected local gpt-oss:20b checking. The same case/key/audio are reused; the old unavailable Gemini attempt is preserved.</p>
<p><a href="tangerine-complete-flow.mp4" download>Download the complete-flow video</a> · <a href="exercise.wav" download>Download the actual stored audio</a></p><audio id="saved-audio" controls preload="metadata" src="exercise.wav"></audio>
<p>29.65 seconds · American Heart and British Emma · Two textual mistakes. This recording does not qualify controlled pronunciation or establish independent accent accuracy.</p></section>
<section><h2>The observed result</h2><p class="score">60 / 100</p><p>One found, one missed, zero false positives. Optional explanation: 100% separately.</p><p>Independent pre-submission expectation: 100 × (45 × 2/3 + 30 × 1/2) / 75 = 60. The deliberately partial developer answer and every failed/successful native call remain retained.</p>'''+comments+'''</section>
<details><summary>Current interface pictures</summary><div class="grid">'''+pictures+'''</div></details>
<section><h2>Scope and records</h2><p>All eleven routes retain their inspected desktop/narrow, keyboard and safe error/recovery scope. Current result and typography changes have fresh pictures and clicks. Read/reopen/export adds zero inference.</p><p>The key remains an LLM candidate and prose is model output, not independently annotated linguistic gold. Unsuccessful local generation experiments and the unavailable older Gemini feedback are retained; they are not presented as universal provider qualification.</p><p><a href="http://127.0.0.1:8773/">Earlier partial-flow evidence</a> · <a href="VERIFY-REPORT.md">Verification report</a></p></section>
<p>Local static viewer. No login, external request, inference or synthesis.</p></main></html>'''
    (SHARE/'index.html').write_text(html)
    report=ROOT/'audit/iteration-29-full-flow-20261026/VERIFY-REPORT.md'
    shutil.copy2(report,SHARE/'VERIFY-REPORT.md')
    print('Complete actual flow viewer created; no inference')

if __name__=='__main__':main()
