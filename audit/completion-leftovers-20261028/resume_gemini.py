"""Finish two missing saved Flash-Lite TTS chunks within verified Free quota.

Same model, voices, source and instructions; no app setting or old failure edit.
Importing this file does not dispatch. Explicit execution permits at most two
requests and stops on any failure, with no provider fallback or quota test.
"""
import base64,copy,importlib.util,json,subprocess,time,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'data/pronunciation-all-20261023/output';OUT=ROOT/'data/completion-leftovers-20261028/gemini-resume'
def find_audio(value):
 if isinstance(value,dict):
  if value.get('type')=='audio' and value.get('data'):return value['data']
  return next((a for x in value.values() if (a:=find_audio(x))),None)
 if isinstance(value,list):return next((a for x in value if (a:=find_audio(x))),None)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'result.json').exists():return
 allowance=dict(date='2026-10-28',source='Actual Chrome Google AI Studio, Tangerine Free Audio, Free tier, one-day expanded rate table',model='Gemini 3.8 Flash Lite TTS',requests_per_day=dict(used=0,limit=10),requests_per_minute=dict(used=0,limit=3),input_tokens_per_minute=dict(used=0,limit=10000),maximum_new_requests=2,billing_unlinked=True,dashboard_delay='Usage data may take up to15minutes to update; this is not a quota reservation.',paid_approved=False)
 (OUT/'allowance.json').write_text(json.dumps(allowance,indent=2)+'\n')
 keyfile=ROOT/'data/iteration16/private/gemini.env';key=next(line.split('=',1)[1].strip().strip('\"\'') for line in keyfile.read_text().splitlines() if line.startswith('GEMINI_API_KEY='))
 if not key.endswith('ljSA'):raise RuntimeError('The saved key is not the project key shown in the admitted Free account')
 spec=importlib.util.spec_from_file_location('retained_comparison_transport',ROOT/'data/speech-comparison-20261022/compare.py');transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport);transport.OUT=OUT
 material=json.loads((OLD/'shared-material.json').read_text());rows=material['turns'];failed=json.loads((OLD/'gemini-mistakes-3-request.json').read_text());model='gemini-3.8-flash-lite-tts';assert failed['body']['model']==model
 parts=[(OLD/('gemini-mistakes-'+str(i)+'.wav')).read_bytes() for i in range(3)];requests=[]
 for chunk in [3,4]:
  name='gemini-mistakes-'+str(chunk);dest=OUT/(name+'.wav')
  if dest.exists():parts.append(dest.read_bytes());continue
  if chunk==3:body=copy.deepcopy(failed['body'])
  else:
   content=[]
   for row in rows[16:20]:
    style='Natural relaxed conversation. '+('American English accent.' if row['speaker_id']=='s1' else 'British English accent.')
    style+=' This is an English pronunciation practice recording. Read the exact text, with these deliberate acoustic deviations only: '+' '.join(x['provider_hint']+(f" Requested IPA: /{x['mutated_ipa']}/." if x.get('mutated_ipa') else '') for x in row['targets'])+' Keep all other words and pronunciations normal. Never speak the instructions, tags, explanations or IPA.'
    content.append(dict(type='text',text=row['canonical_text'],annotations=[dict(type='speech_metadata',speaker=row['speaker_id'],style=style)]))
   body=copy.deepcopy(failed['body']);body['input'][0]['content']=content
  request=dict(chunk=chunk,model=model,source_turn_ids=[row['id'] for row in rows[chunk*4:chunk*4+4]],started_at=time.time());requests.append(request);(OUT/'dispatches.json').write_text(json.dumps(requests,indent=2)+'\n')
  raw=OUT/(name+'.raw')
  # Received failed responses stay failed. Explicitly starting another attempt
  # requires a different output folder; this run never retries quota/service errors.
  if raw.exists():raise RuntimeError('A retained failed/unadmitted response exists; no redispatch selected')
  response=json.loads(transport.http(name,failed['url'],body,key));data=find_audio(response)
  if not data:raise RuntimeError('The actual provider response contains no audio')
  encoded=base64.b64decode(data)
  command=[str(OUT.parent/'native-tools/ffmpeg'),'-nostdin','-v','error','-i','pipe:0','-f','wav','-acodec','pcm_s16le','-ar','24000','-ac','1','pipe:1']
  converted=subprocess.run(command,input=encoded,capture_output=True,timeout=60,check=True).stdout;dest.write_bytes(converted);parts.append(converted)
  request.update(outcome='complete',http_status=200,finished_at=time.time());(OUT/'dispatches.json').write_text(json.dumps(requests,indent=2)+'\n')
 transport.assemble('gemini-mistakes',parts)
 result=dict(status='complete',model=model,source_preparation=material['source_preparation'],turn_count=20,target_count=26,successful_new_requests=len(requests),new_chunks=[3,4],reused_chunks=[0,1,2],clean_recording=str((OLD/'gemini-clean.wav').relative_to(ROOT)),target_recording=str((OUT/'gemini-mistakes.wav').relative_to(ROOT)),actual_provider_perception='unconfirmed; directions and generated sound are distinct',billing='existing unbilled Free project',paid_use=False)
 with wave.open(str(OUT/'gemini-mistakes.wav')) as audio:result['target_seconds']=audio.getnframes()/audio.getframerate()
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
