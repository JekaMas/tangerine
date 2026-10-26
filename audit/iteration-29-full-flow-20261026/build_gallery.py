"""Build a static local evidence viewer from explicit synthetic observations."""
from pathlib import Path
from html import escape
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/iteration-29-full-flow-20261026'
SHARE = OUT / 'share'
PREP = 'bc740ead-ff03-455f-805b-0fb4c7babcf1'


def main():
    key = json.loads((OUT / 'keys' / (PREP + '.json')).read_text())
    expected = json.loads((OUT / 'answer-expectation.json').read_text())
    shutil.copy2(ROOT / 'services/web/public/fonts/SourceSans3.ttf', SHARE / 'SourceSans3.ttf')
    pictures = SHARE / 'pictures'
    pictures.mkdir(exist_ok=True)
    names = [('Library', 'fault-library-final-repeated-refresh.png'),
             ('New exercise', 'request-ready.png'), ('Saved attempts', 'layout-attempts-1280.png'),
             ('Saved audio', 'layout-audio-final-1280.png'), ('Listen and results', 'result-final-video.png'),
             ('Optional review', 'layout-reviews-1280.png'), ('Reports', 'layout-reports-1280.png'),
             ('Sources', 'empty-sources-desktop.png'), ('Settings', 'settings-desktop.png'),
             ('Recovery', 'recovery-desktop.png'), ('Cleanup preview', 'layout-cleanup-1280.png')]
    for _, name in names:
        shutil.copy2(OUT / 'pictures' / name, pictures / name)
    screens = ''.join('<figure><a href="pictures/' + name + '"><img loading="lazy" alt="Observed ' + escape(label) +
                      ' screen" src="pictures/' + name + '"></a><figcaption>' + escape(label) + '</figcaption></figure>' for label, name in names)
    turns = ''.join('<li><p class="eyebrow">Speaker ' + escape(t['speaker_id']) + '</p><p><strong>Clean:</strong> ' +
                    escape(t['canonical_text']) + '</p><p><strong>Spoken:</strong> ' + escape(t['surface_text']) + '</p></li>' for t in key['utterances'])
    units = ''.join('<li><strong>' + escape(u['primary_taxonomy_id']) + '</strong> — ' + escape(u['rationale']) + '</li>' for u in key['units'])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tangerine — observed flow</title><style>
@font-face{font-family:Source Sans;src:url(SourceSans3.ttf)}*{box-sizing:border-box}
body{margin:0;background:#f6f7fb;color:#1e2d39;font:18px/1.5 'Source Sans',sans-serif}
main{max-width:1060px;margin:auto;padding:42px 24px 80px}h1{font-size:clamp(34px,6vw,52px);line-height:1.12;letter-spacing:-.025em;margin:8px 0 20px}
h2{font-size:28px;line-height:1.2;margin:32px 0 16px}p{max-width:75ch;margin:12px 0}
.eyebrow{color:#92420e;font-weight:650;font-size:15px;letter-spacing:.04em}.notice{border-left:4px solid #b74b10;padding:18px 22px;background:#fff4e9;border-radius:8px}
section,details{background:#fff;border:1px solid #dfe3e8;border-radius:12px;padding:24px;margin:26px 0}
video,audio{width:100%;display:block;margin:18px 0}video{background:#14232e}a{color:#95400d;text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid #376d98;outline-offset:4px}
summary{cursor:pointer;font-size:23px;font-weight:650}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:20px}
figure{margin:0}img{width:100%;height:auto;border:1px solid #dfe3e8;border-radius:6px}figcaption{margin:6px 0 14px;font-weight:600}
ol{padding-left:24px}li{padding-left:4px;margin:16px 0}.score{font-size:36px;font-weight:700;font-variant-numeric:tabular-nums}.muted{color:#52616d}
@media(max-width:450px){main{padding:24px 16px 48px}section,details{padding:18px}h2{font-size:25px}}
</style><main><p class="eyebrow">TANGERINE · ITERATION 29 · ACTUAL FUNCTIONAL OBSERVATIONS</p>
<h1>From an idea to a listening exercise</h1><p>A real 94-word dialogue, two local voices, two injected text mistakes and a saved learner answer.</p>
<div class="notice"><strong>The complete-flow acceptance remains open.</strong><p>Generation, audio, checking, scoring and reopening succeeded. Gemini Free repeatedly returned a high-demand error for comments and recommendations. The video shows that unavailable stage; it does not substitute a successful result.</p></div>
<section><h2>Watch the observed flow</h2><video controls preload="metadata" poster="pictures/result-final-video.png" src="tangerine-observed-flow.mp4"></video>
<p class="muted">Edited 3-minute recording from actual browser frames. Cuts compress waiting and disclose the in-run repair. Key and arithmetic cards are editorial explanations. The actual stored WAV is overlaid on the listening segment; this is not a continuous live microphone recording.</p>
<p><a href="tangerine-observed-flow.mp4" download>Download the video</a> · <a href="exercise.wav" download>Download the original recording</a></p>
<h2>The saved exercise audio</h2><audio controls preload="metadata" src="exercise.wav"></audio><p>29.65 seconds. American Heart and British Emma, synthesized locally with Kokoro. This run selects grammar and collocation mistakes; it makes no pronunciation-realization claim.</p></section>
<section><h2>The observed result</h2><p class="score">60 / 100</p><p>One of two mistakes found; one missed; no false positives. The supplied optional explanation scored 100% separately.</p>
<p>Independent expected arithmetic: 100 × (45 × 2/3 + 30 × 1/2) / 75 = 60. Only detection and correction contribute to this exercise's primary score.</p><p><strong>Constructed partial developer answer:</strong></p><blockquote>''' + escape(expected['answer']) + '''</blockquote>
<p class="muted">The same immutable answer, key, audio and score survived reopening and feedback-only retries. Comments and recommendations are still unavailable. No paid credits or overage were used.</p></section>
<details><summary>Inspect the saved text and mutation key</summary><p>This is an LLM-generated candidate key, not independently annotated linguistic gold.</p><ol>''' + turns + '''</ol><h2>The two intended mistakes</h2><ul>''' + units + '''</ul></details>
<details><summary>Inspect the eleven actual routes</summary><p>Actual saved screenshots. Some show scrolled sections. Cleanup is a preview; saved exercise data were retained. The isolated Sources page shows its intentionally empty workspace.</p><div class="grid">''' + screens + '''</div></details>
<p class="muted">Local evidence viewer. No account, external request, inference or synthesis occurs on this page.</p></main></html>'''
    (SHARE / 'index.html').write_text(page)
    print('Static local viewer created; 11 route pictures, existing video/audio; zero new inference')


if __name__ == '__main__':
    main()
