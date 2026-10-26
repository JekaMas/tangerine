"""Finite native Azure comparison; existing F0 access only, no provider fallback.

No inference on import. An actual live run follows the recorded F0 resource
observation; an account_tier label alone never establishes live eligibility.
"""
import base64,json,os,sys,time,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'services/speech'))
import backends

VOICES={'s1':('en-US-JennyNeural','en-US'),'s2':('en-GB-RyanNeural','en-GB')}
SOURCE=Path(__file__).with_name('material.json')

def build_plan(material,resource):
 region=resource['location'];tier=resource['sku']['name']
 profile=dict(id='azure-f0-comparison',provider='azure_speech',adapter_version='azure-standard-v1',model='neural',billing_mode='free_tier',account_tier=tier,overage_disabled=True,endpoint=f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',voices=[dict(id=v,locale=l) for v,l in VOICES.values()],voice_settings={})
 turns=[]
 for variant in ['clean','mistakes']:
  for row in material['turns']:
   text=row['canonical_text'];target=row['target'];a,b=target['start'],target['end'];voice,locale=VOICES[row['speaker_id']]
   operations=[dict(kind='text',text=text[:a]),dict(kind='phoneme',text=target['word'],ipa=target['reference_ipa' if variant=='clean' else 'mutated_ipa']),dict(kind='text',text=text[b:])]
   turns.append(dict(variant=variant,id=row['id'],utterance_id=row['id'],speaker_id=row['speaker_id'],voice_id=voice,locale=locale,gap_after_ms=300,operations=operations))
 return dict(source_preparation=material['source_preparation'],source_material=material,resource=resource,profile=profile,turns=turns)

def save(path,raw):
 temporary=path.with_suffix(path.suffix+'.partial');temporary.write_bytes(raw);temporary.replace(path)

def assemble(files,destination):
 temporary=destination.with_suffix('.wav.partial')
 with wave.open(str(temporary),'wb') as out:
  out.setparams((1,2,24000,0,'NONE','not compressed'))
  for file in files:
   with wave.open(str(file),'rb') as audio:out.writeframes(audio.readframes(audio.getnframes()))
   out.writeframes(b'\0\0'*7200)
 temporary.replace(destination)

def execute(plan,out,timeout=270):
 """Resume admitted pieces; changed settings belong to a different run folder."""
 out=Path(out);out.mkdir(parents=True,exist_ok=True);deadline=time.monotonic()+timeout
 for turn in plan['turns']:
  name=turn['variant']+'-'+turn['id'];audio=out/(name+'.wav')
  if audio.exists():continue
  remaining=deadline-time.monotonic()
  if remaining<=0:raise TimeoutError('Comparison interrupted; completed pieces are retained.')
  response=out/(name+'-response.json')
  if response.exists():result=json.loads(response.read_text())
  else:
   result=backends.render(plan['profile'],turn,remaining)
   save(response,(json.dumps(result,indent=2)+'\n').encode())
  save(audio,base64.b64decode(result['audio_base64']))
 for variant in ['clean','mistakes']:
  destination=out/('azure-'+variant+'.wav')
  if not destination.exists():assemble([out/(variant+'-'+t['id']+'.wav') for t in plan['turns'] if t['variant']==variant],destination)
 return dict(status='complete',variants=['azure-clean.wav','azure-mistakes.wav'],source_preparation=plan['source_preparation'])

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--resource',type=Path,required=True);args=parser.parse_args()
 # Missing access stops before any synthesis, never silently selects another service.
 if not os.environ.get('AZURE_SPEECH_KEY'):raise SystemExit('Azure F0 key and resource region are required. No provider call was made.')
 args.out.mkdir(parents=True,exist_ok=True);saved=args.out/'plan.json'
 if saved.exists():plan=json.loads(saved.read_text())
 else:
  plan=build_plan(json.loads(SOURCE.read_text()),json.loads(args.resource.read_text()))
  save(saved,(json.dumps(plan,indent=2)+'\n').encode())
 journal=args.out/'dispatches.json';observed=json.loads(journal.read_text()) if journal.exists() else []
 native_transport=backends.transport
 def observe(url,body,headers,timeout):
  row=dict(url=url,body_base64=base64.b64encode(body).decode(),credential_header_present=bool(headers.get('Ocp-Apim-Subscription-Key')),started_at=time.time(),origin='actual Azure HTTP transport')
  observed.append(row);save(journal,(json.dumps(observed,indent=2)+'\n').encode())
  try:
   raw,status=native_transport(url,body,headers,timeout)
   row.update(http_status=status,raw_response_base64=base64.b64encode(raw).decode())
   return raw,status
  except ValueError as error:row['error']=str(error);raise
  finally:
   row['finished_at']=time.time();save(journal,(json.dumps(observed,indent=2)+'\n').encode())
 backends.transport=observe
 try:result=execute(plan,args.out)
 finally:backends.transport=native_transport
 save(args.out/'result.json',(json.dumps(result,indent=2)+'\n').encode())
 print(json.dumps(result))

if __name__=='__main__':main()
