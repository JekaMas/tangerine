"""One necessary paired opinion on stored I22 speech, existing Gemini Free binding.
No synthesis, benchmark, paid route, retry, model sweep or quality-gate dispatch.
"""
from pathlib import Path
import base64,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-22-elevenlabs-20261026/live'
if (OUT/'auditory-response.json').exists():raise SystemExit('Reuse retained opinion; no duplicate call')
prompt='''Listen to the two actual short audio clips. Clip A is the first supplied audio, clip B is the second. They are two versions of the same word. Independently describe the initial consonant in each: is it a sustained sibilant /s/, a dental fricative /θ/, or unclear? The word spelling and the order do not identify the intended pronunciation. Listen to the actual sound; do not infer a pronunciation from a label or expected English. Return one JSON object with findings containing exactly unit_id A and B, feature="initial consonant", status="supported" or "uncertain", proposed_ipa="sɪŋk" or "θɪŋk" or null, and a brief description of the acoustic basis. Use uncertain for unclear evidence. This is a model listening opinion, not independent linguistic gold.'''
packet=dict(profile=dict(id='existing-gemini-free-auditory',provider='gemini_interactions',model='gemini-3.1-flash-lite',billing_mode='free_tier',max_output_tokens=1500),prompt=prompt,input=dict(clips=[dict(unit_id='A',target_phrase='one English word'),dict(unit_id='B',target_phrase='one English word')]),clips=[base64.b64encode((OUT/f).read_bytes()).decode() for f in ['target.wav','reference.wav']])
(OUT/'auditory-request.json').write_text(json.dumps(packet))
code="""import sys,json,base64;sys.path.insert(0,'/app');from diagnostic_models import auditory
p=json.load(sys.stdin);print(json.dumps(auditory(p['profile'],p['prompt'],p['input'],[base64.b64decode(x) for x in p['clips']],260)))"""
r=subprocess.run(['docker','exec','-i','tangerine-local-speech-1','python','-c',code],input=json.dumps(packet),text=True,capture_output=True,timeout=280)
(OUT/'auditory-stdout.txt').write_text(r.stdout);(OUT/'auditory-stderr.txt').write_text(r.stderr)
if r.returncode:raise SystemExit('Auditory observation unavailable; retain native failure, no fallback')
x=json.loads(r.stdout);(OUT/'auditory-response.json').write_text(json.dumps(x))
print(json.dumps({'output':x.get('output'),'error':x.get('error'),'http_status':x.get('wire',{}).get('http_status')}))
