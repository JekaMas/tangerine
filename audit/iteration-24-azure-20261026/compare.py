"""Finite native Azure comparison; existing F0 access only, no provider fallback.

No inference on import. An actual live run follows the recorded F0 resource
observation; an account_tier label alone never establishes live eligibility.
"""
import base64,json,logging,sys,time,urllib.error,wave
from time import sleep
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

SAFE_ERRORS={'PROVIDER_FAILED','PROVIDER_QUOTA','MISSING_CREDENTIALS','PAID_USE_FORBIDDEN','VOICE_UNAVAILABLE','AUDIO_SILENT','AUDIO_FORMAT_INVALID','CAPABILITY_UNAVAILABLE'}

def failure_facts(error):
 return dict(error=str(error) if isinstance(error,ValueError) and str(error) in SAFE_ERRORS else 'COMPARISON_INTERRUPTED',error_type=type(error).__name__,http_status=getattr(error,'http_status',None))

def recovery_message(error):
 code=failure_facts(error)['error'];status=getattr(error,'http_status',None)
 if isinstance(error,KeyboardInterrupt):message='The comparison stopped at your request. Resume when ready.'
 elif code=='MISSING_CREDENTIALS' or status in (401,403):message='Azure access needs attention. Check the selected F0 resource, key and region before resuming.'
 elif code=='PROVIDER_QUOTA':message='The free allowance or request limit is unavailable. Wait for its reset before resuming.'
 elif code=='PAID_USE_FORBIDDEN':message='This resource is not eligible for the free-only comparison. Configure an existing F0 resource before resuming.'
 elif code in ('VOICE_UNAVAILABLE','CAPABILITY_UNAVAILABLE'):message='The selected voice or pronunciation control is unavailable. Check the resource capabilities before resuming.'
 elif code in ('AUDIO_SILENT','AUDIO_FORMAT_INVALID'):message='Azure returned an unusable recording. Check the selected voice and pronunciation settings before resuming.'
 else:message='The comparison could not finish yet. Check the local connection and comparison setup, then resume.'
 return message+' Saved text and completed recordings are retained. No provider was switched.'

def retry_delay(error):
 status=getattr(error,'http_status',None)
 if status==429:return getattr(error,'retry_after',None)
 if status in (408,500,502,503,504):
  delay=getattr(error,'retry_after',None);return 1 if delay is None else delay
 if status is None and isinstance(error,(urllib.error.URLError,TimeoutError,ConnectionError)):return 1
 return None

def state(out,phase,message,completed):
 save(out/'state.json',(json.dumps(dict(state=phase,message=message,completed_pieces=completed),indent=2)+'\n').encode())

def render_piece(plan,turn,out,deadline,completed):
 for attempt in range(1,4):
  remaining=deadline-time.monotonic()
  if remaining<=0:raise TimeoutError()
  try:return backends.render(plan['profile'],turn,remaining)
  except (Exception,KeyboardInterrupt) as error:
   delay=retry_delay(error);will_retry=attempt<3 and delay is not None and delay<deadline-time.monotonic()
   logging.warning('Azure comparison failure %s',json.dumps(dict(**failure_facts(error),attempt=attempt,retrying=will_retry)))
   if not will_retry:raise
   state(out,'retrying','A temporary service or connection problem occurred. Retrying the current piece; saved recordings remain available.',completed)
   sleep(delay)

def execute(plan,out,timeout=270):
 """Resume admitted pieces; changed settings belong to a different run folder."""
 out=Path(out);out.mkdir(parents=True,exist_ok=True);deadline=time.monotonic()+timeout
 completed=sum((out/(t['variant']+'-'+t['id']+'.wav')).exists() for t in plan['turns'])
 state(out,'rendering','Rendering the remaining pieces. Saved recordings remain available.',completed)
 try:
  for variant in ['clean','mistakes']:
   turns=[t for t in plan['turns'] if t['variant']==variant]
   for turn in turns:
    name=variant+'-'+turn['id'];audio=out/(name+'.wav')
    if audio.exists():continue
    response=out/(name+'-response.json')
    if response.exists():result=json.loads(response.read_text())
    else:
     result=render_piece(plan,turn,out,deadline,completed)
     save(response,(json.dumps(result,indent=2)+'\n').encode())
    save(audio,base64.b64decode(result['audio_base64']));completed+=1
    state(out,'rendering','Rendering the remaining pieces. Saved recordings remain available.',completed)
   destination=out/('azure-'+variant+'.wav')
   if not destination.exists():assemble([out/(variant+'-'+t['id']+'.wav') for t in turns],destination)
 except (Exception,KeyboardInterrupt) as error:
  state(out,'paused',recovery_message(error),completed);raise
 state(out,'complete','Both recordings are available.',completed)
 return dict(status='complete',variants=['azure-clean.wav','azure-mistakes.wav'],source_preparation=plan['source_preparation'])

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--resource',type=Path,required=True);args=parser.parse_args()
 try:return run(args)
 except (Exception,KeyboardInterrupt) as error:
  logging.warning('Azure comparison stopped %s',json.dumps(failure_facts(error)))
  message=recovery_message(error)
  print(json.dumps(dict(status='paused',message=message)))
  return 130 if isinstance(error,KeyboardInterrupt) else 1

def run(args):
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
  except (Exception,KeyboardInterrupt) as error:row.update(failure_facts(error));raise
  finally:
   row['finished_at']=time.time();save(journal,(json.dumps(observed,indent=2)+'\n').encode())
 backends.transport=observe
 try:result=execute(plan,args.out)
 finally:backends.transport=native_transport
 save(args.out/'result.json',(json.dumps(result,indent=2)+'\n').encode())
 print(json.dumps(result))
 return 0

if __name__=='__main__':sys.exit(main())
