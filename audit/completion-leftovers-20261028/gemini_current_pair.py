"""New explicit current-API comparison: same source/model/voices, mode omitted.

Two finite Free requests; no model sweep, fallback, old-plan rewrite or retry.
The rejected legacy conversational-mode request remains a failed observation.
"""
import base64,importlib.util,json,os,sys,time,wave
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'data/pronunciation-all-20261023/output';OUT=ROOT/'data/completion-leftovers-20261028/gemini-current-api'
def audio_outputs(value):
 if isinstance(value,dict):
  if value.get('type')=='audio' and value.get('data'):return [value['data']]
  return [a for x in value.values() for a in audio_outputs(x)]
 if isinstance(value,list):return [a for x in value for a in audio_outputs(x)]
 return []
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'result.json').exists():return
 source=json.loads((OLD/'shared-material.json').read_text());rows=source['turns'];model='gemini-3.8-flash-lite-tts'
 key=None
 spec=importlib.util.spec_from_file_location('actual_free_transport',ROOT/'data/speech-comparison-20261022/compare.py');transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport);transport.OUT=OUT
 plan=dict(schema_version='current-interactions-20261028',model=model,source_preparation=source['source_preparation'],source_material=source,voices=[dict(speaker='s1',voice='Kore'),dict(speaker='s2',voice='Puck')],billing='existing verified Free project; no billing link',mode='omitted: rejected by current API, not equivalent to legacy explicit conversational cadence',maximum_new_requests=2,legacy_failure='data/completion-leftovers-20261028/gemini-resume/gemini-mistakes-3.raw',provider_reference='https://ai.google.dev/api/interactions-api')
 if (OUT/'plan.json').exists():
  plan=json.loads((OUT/'plan.json').read_text());source=plan['source_material'];rows=source['turns'];model=plan['model']
 else:(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 dispatches=json.loads((OUT/'dispatches.json').read_text()) if (OUT/'dispatches.json').exists() else []
 for variant in ['clean','mistakes']:
  name='gemini-'+variant;destination=OUT/(name+'.wav')
  if destination.exists():continue
  content=[]
  for row in rows:
   style='Natural relaxed conversation. '+('American English accent.' if row['speaker_id']=='s1' else 'British English accent.')
   if variant=='mistakes':style+=' This is an English pronunciation practice recording. Read the exact text, with these deliberate acoustic deviations only: '+' '.join(t['provider_hint']+(f" Requested IPA: /{t['mutated_ipa']}/." if t.get('mutated_ipa') else '') for t in row['targets'])+' Keep all other words and pronunciations normal. Never speak the instructions, tags, explanations or IPA.'
   content.append(dict(type='text',text=row['canonical_text'],annotations=[dict(type='speech_metadata',speaker=row['speaker_id'],style=style)]))
  body=dict(model=model,input=[dict(type='user_input',content=content)],response_format=dict(type='audio'),generation_config=dict(speech_config=dict(speakers=plan['voices'])))
  raw=OUT/(name+'.raw')
  if raw.exists():
   receipt=json.loads((OUT/(name+'-receipt.json')).read_text())
   if receipt['http_status']!=200:raise RuntimeError('A retained failed response exists; no redispatch selected')
   response=json.loads(raw.read_text());row=next(r for r in dispatches if r['variant']==variant)
  else:
   if key is None:
    key=next(line.split('=',1)[1].strip().strip('\"\'') for line in (ROOT/'data/iteration16/private/gemini.env').read_text().splitlines() if line.startswith('GEMINI_API_KEY='))
    if not key.endswith('ljSA'):raise RuntimeError('Selected project key does not match admitted Free account')
   row=dict(variant=variant,started_at=time.time(),outcome='started');dispatches.append(row);(OUT/'dispatches.json').write_text(json.dumps(dispatches,indent=2)+'\n')
   try:response=json.loads(transport.http(name,'https://generativelanguage.googleapis.com/v1beta/interactions',body,key))
   except Exception as error:
    row.update(outcome='failed',failure_type=type(error).__name__,finished_at=time.time());(OUT/'dispatches.json').write_text(json.dumps(dispatches,indent=2)+'\n');raise
  encoded=audio_outputs(response)
  if len(encoded)!=1:raise RuntimeError('Actual audio output structure needs explicit projection; no partial dialogue is admitted')
  # The production normalization owner rewrites FFmpeg's streaming unknown-size
  # RIFF header as finite PCM. Capturing its pipe output directly is insufficient.
  sys.path.insert(0,str(ROOT/'services/speech'));from audio import normalize
  with patch.dict(os.environ,dict(PATH=str(OUT.parent/'native-tools')+os.pathsep+os.environ['PATH'])):
   converted=normalize(base64.b64decode(encoded[0]))
  destination.write_bytes(converted)
  if row['outcome']!='complete':
   row.update(outcome='complete',http_status=200,finished_at=time.time());(OUT/'dispatches.json').write_text(json.dumps(dispatches,indent=2)+'\n')
 result=dict(status='complete',model=model,source_preparation=source['source_preparation'],source_turns=20,requested_targets=26,successful_new_requests=len(dispatches),billing='verified Free project',paid_use=False,mode='omitted in both complete variants; original mode-present recordings/failures retained separately',perceived_realization='not established by successful synthesis')
 for variant in ['clean','mistakes']:
  with wave.open(str(OUT/('gemini-'+variant+'.wav'))) as audio:result[variant+'_seconds']=audio.getnframes()/audio.getframerate()
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
