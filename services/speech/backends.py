"""Frozen speech bindings; no fallback, runtime downloads, or paid dispatch."""
import contextlib, base64, hashlib, io, json, os, pathlib, subprocess, sys, time, urllib.error, urllib.parse, urllib.request, uuid, xml.etree.ElementTree as ET
from audio import admit, normalize, wav_bytes, quality, measure
from model_setup import installed
from inference_capture import observe_method

CACHE={}
os.environ.setdefault('NUMBA_CACHE_DIR','/tmp/numba-cache')

def billing(profile):
 provider=profile['provider'];mode=profile.get('billing_mode','unknown')
 if provider.startswith('local_') and mode=='local':return
 if mode not in ('free_tier','included_subscription') or profile.get('overage_disabled') is not True:raise ValueError('PAID_USE_FORBIDDEN')
 if provider=='azure_speech' and profile.get('account_tier')!='F0':raise ValueError('PAID_USE_FORBIDDEN')
 if provider=='openai_tts':raise ValueError('PAID_USE_FORBIDDEN')

def ssml(turn):
 root=ET.Element('speak',{'version':'1.0','xmlns':'http://www.w3.org/2001/10/synthesis','xml:lang':turn['locale']})
 voice=ET.SubElement(root,'voice',{'name':turn['voice_id']})
 for op in turn['operations']:
  if op['kind']=='text':
   child=ET.SubElement(voice,'s');child.text=op['text']
  elif op['kind']=='phoneme':ET.SubElement(voice,'phoneme',{'alphabet':'ipa','ph':op['ipa']}).text=op['text']
  elif op['kind']=='pause':ET.SubElement(voice,'break',{'time':str(op['duration_ms'])+'ms'})
  elif op['kind']=='prosody':
   attributes={}
   for key,attribute,suffix in [('rate_percent','rate','%'),('pitch_semitones','pitch','st'),('volume_db','volume','dB')]:
    if op.get(key) is not None:attributes[attribute]=f"{op[key]:+g}{suffix}"
   if op.get('contour'):attributes['contour']=' '.join(f"({p['position_percent']}%,{p['pitch_semitones']:+g}st)" for p in op['contour'])
   ET.SubElement(voice,'prosody',attributes).text=op['text']
  else:raise ValueError('CAPABILITY_UNAVAILABLE')
 return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def transport(url,body,headers,timeout):
 request=urllib.request.Request(url,data=body,headers=headers)
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPRedirectHandler())
 # A redirect must never carry a credential to another host.
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):return None
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
 try:
  with opener.open(request,timeout=timeout) as response:return response.read(),response.status
 except urllib.error.HTTPError as e:
  raise ValueError('PROVIDER_QUOTA' if e.code==429 else 'PROVIDER_FAILED') from None

def kokoro(profile,turn):
 root,manifest=installed('kokoro-local-en-v1')
 sys.path.insert(0,str(root/'g2p'));os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
 from kokoro import KModel,KPipeline
 from misaki import en
 if 'model' not in CACHE:
  weight=next(r['path'] for r in manifest['files'] if r['path'].endswith('.pth'))
  CACHE['model']=KModel(repo_id=manifest['repo'],config=str(root/'config.json'),model=str(root/weight)).to('cpu').eval()
 code={'en-US':'a','en-GB':'b'}[turn['locale']]
 if code not in CACHE:
  pipe=KPipeline(lang_code=code,repo_id=manifest['repo'],model=CACHE['model'],device='cpu')
  # Interpret literal text, never Misaki's embedded pronunciation markup.
  pipe.g2p.preprocess=lambda text:(text,text.split(),{})
  CACHE[code]=pipe
 pipe=CACHE[code];voice=str(root/'voices'/(turn['voice_id']+'.pt'));frames=[];tokens=[];offset=0
 import numpy as np
 model_calls=[]
 with observe_method(CACHE['model'],'forward_with_tokens',model_calls,capture_result=False):
  for op in turn['operations']:
   if op['kind']=='pause':frames.append(np.zeros(op['duration_ms']*24,dtype=np.float32));offset+=op['duration_ms']*24;continue
   if op['kind']!='text':raise ValueError('CAPABILITY_UNAVAILABLE')
   results = pipe.generate_from_tokens(turn['compiled_phonemes'],voice=voice,speed=profile.get('voice_settings',{}).get('speed') or 1) if turn.get('compiled_phonemes') else pipe(op['text'],voice=voice,speed=profile.get('voice_settings',{}).get('speed') or 1)
   for result in results:
    if result.audio is None or not result.phonemes:raise ValueError('SYNTHESIS_FAILED')
    frames.append(result.audio.numpy());tokens.append({'graphemes':result.graphemes,'phonemes':result.phonemes,'start_sample':offset,'sample_count':len(result.audio),'pred_dur':result.output.pred_dur.tolist()});offset+=len(result.audio)
 if not frames:raise ValueError('SYNTHESIS_FAILED')
 samples=np.concatenate(frames)
 if not np.isfinite(samples).all():raise ValueError('AUDIO_FORMAT_INVALID')
 pcm=(np.clip(samples,-1,1)*32767).astype('<i2').tobytes()
 return wav_bytes(pcm),{'model_manifest':manifest,'decoder':tokens,'model_visible_calls':model_calls},None

def espeak(profile,turn):
 pcm=bytearray();calls=[]
 for op in turn['operations']:
  if op['kind']=='pause':pcm.extend(b'\0\0'*(op['duration_ms']*24));continue
  if op['kind']!='text':raise ValueError('CAPABILITY_UNAVAILABLE')
  args=['espeak-ng','--stdout','-v',turn['voice_id'],'--stdin']
  p=subprocess.run(args,input=op['text'].encode(),capture_output=True,timeout=60,check=False)
  if p.returncode:raise ValueError('SYNTHESIS_FAILED')
  pcm.extend(normalize(p.stdout)[44:]);calls.append({'argv':args,'text':op['text']})
 return wav_bytes(pcm),{'calls':calls,'engine':'espeak-ng','version':subprocess.run(['espeak-ng','--version'],capture_output=True,timeout=5,check=False).stdout.decode()},p.stdout

def hosted(profile,turn,timeout):
 if profile['provider']=='azure_speech':
  body=ssml(turn);key=os.environ.get('AZURE_SPEECH_KEY');url=profile.get('endpoint')
  if not key or not url:raise ValueError('MISSING_CREDENTIALS')
  headers={'Ocp-Apim-Subscription-Key':key,'Content-Type':'application/ssml+xml','X-Microsoft-OutputFormat':'riff-24khz-16bit-mono-pcm'}
 elif profile['provider']=='elevenlabs':
  if any(op['kind']!='text' for op in turn['operations']):raise ValueError('CAPABILITY_UNAVAILABLE')
  text=''.join(op['text'] for op in turn['operations']);model=profile['model'];base=profile.get('endpoint') or 'https://api.elevenlabs.io'
  if model in ('eleven_v3','eleven_v4'):
   payload={'inputs':[{'text':text,'voice_id':turn['voice_id']}],'model_id':model};url=base+'/v1/text-to-dialogue?output_format=mp3_44100_128'
  else:
   payload={'text':text,'model_id':model,'voice_settings':{k:v for k,v in profile.get('voice_settings',{}).items() if v is not None}};url=base+'/v1/text-to-speech/'+urllib.parse.quote(turn['voice_id'],safe='')+'?output_format=mp3_44100_128'
  body=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode();key=os.environ.get('ELEVENLABS_API_KEY')
  if not key:raise ValueError('MISSING_CREDENTIALS')
  headers={'xi-api-key':key,'Content-Type':'application/json'}
 else:raise ValueError('CAPABILITY_UNAVAILABLE')
 raw,status=transport(url,body,headers,timeout)
 return normalize(raw),{'url':url,'body_base64':base64.b64encode(body).decode(),'http_status':status},raw

def qwen(profile,turn):
 from qwen_tts import Qwen3TTSModel
 import numpy as np,torch
 text=''.join(op['text'] for op in turn['operations'] if op['kind']=='text')
 if len(turn['operations'])!=1 or turn['operations'][0]['kind']!='text':raise ValueError('CAPABILITY_UNAVAILABLE')
 custom=profile.get('adapter_version')=='qwen-custom-v1'
 root,manifest=installed('qwen-custom-v1' if custom else 'qwen-base-v1')
 conditioning=None;conditioning_manifest=None
 if not custom:
  conditioning=ROOT_CONDITION/profile['id']/turn['voice_id']
  try:
   prompt=torch.load(conditioning/'conditioning.pt',map_location='cpu',weights_only=False)
   conditioning_manifest=json.loads((conditioning/'manifest.json').read_text())
  except FileNotFoundError:raise ValueError('VOICE_SETUP_REQUIRED') from None
 key=str(root)
 if key not in CACHE:CACHE[key]=Qwen3TTSModel.from_pretrained(str(root),device_map='cpu',dtype=torch.float32,attn_implementation='eager',local_files_only=True)
 model=CACHE[key]
 inputs=[]
 with observe_method(model,'_tokenize_texts',inputs),observe_method(model.model,'generate',inputs,capture_result=False):
  if custom:audio,rate=model.generate_custom_voice(text=text,language='English',speaker=turn['voice_id'],instruct=turn.get('accent_description') or '')
  else:audio,rate=model.generate_voice_clone(text=text,language='English',voice_clone_prompt=prompt)
 import soundfile as sf
 output=io.BytesIO();sf.write(output,audio[0],rate,format='WAV',subtype='PCM_16')
 return normalize(output.getvalue()),{'model_manifest':manifest,'speaker':turn['voice_id'],'instruction':turn.get('accent_description'),'conditioning_manifest':conditioning_manifest,'model_visible_calls':inputs},None

ROOT_CONDITION=pathlib.Path(os.environ.get('TANGERINE_MODEL_DIR','/models'))/'voices'

def render(profile,turn,timeout=260):
 billing(profile)
 permitted={v['id']:v for v in profile['voices']}
 if turn['voice_id'] not in permitted or permitted[turn['voice_id']]['locale']!=turn['locale']:raise ValueError('VOICE_UNAVAILABLE')
 start=time.time();provider=profile['provider'];receipt_id=str(uuid.uuid4())
 if provider=='local_kokoro':audio,native,raw=kokoro(profile,turn)
 elif provider=='local_espeak_ng':audio,native,raw=espeak(profile,turn)
 elif provider=='local_qwen3_tts':audio,native,raw=qwen(profile,turn)
 else:audio,native,raw=hosted(profile,turn,timeout)
 pcm=admit(audio)
 warnings=measure(pcm)
 return {'audio_base64':base64.b64encode(audio).decode(),'sample_count':len(pcm)//2,'quality':warnings,'receipt':{'id':receipt_id,'provider':provider,'model':native['model_manifest']['repo'] if 'model_manifest' in native else native.get('version'),'requested_model':profile.get('model'),'voice_id':turn['voice_id'],'locale':turn['locale'],'requested_accent':permitted[turn['voice_id']].get('accent_description'),'observed_accent':None,'billing_mode':profile['billing_mode'],'duration_ms':int((time.time()-start)*1000),'input':{'profile':profile,'turn':turn},'native':native,'raw_response_base64':base64.b64encode(raw).decode() if raw else None,'audio_sha256':hashlib.sha256(audio).hexdigest()}}


def plan(profile,render_plan):
 billing(profile)
 pieces=[];context={}
 if profile['provider']=='local_kokoro':
  root,manifest=installed('kokoro-local-en-v1');context=manifest
  sys.path.insert(0,str(root/'g2p'))
  from kokoro import KPipeline
  pipes={}
 for turn in render_plan['turns']:
  selected=next((v for v in profile['voices'] if v['id']==turn['voice_id'] and v['locale']==turn['locale']),None)
  if selected is None:raise ValueError('VOICE_UNAVAILABLE')
  text=''.join(op['text'] for op in turn['operations'] if op['kind']=='text')
  if any(op['kind']!='text' for op in turn['operations']):raise ValueError('CAPABILITY_UNAVAILABLE')
  chunks=[]
  if profile['provider']=='local_kokoro':
   code={'en-US':'a','en-GB':'b'}[turn['locale']]
   if code not in pipes:
    pipe=KPipeline(lang_code=code,repo_id=manifest['repo'],model=False)
    pipe.g2p.preprocess=lambda text:(text,text.split(),{})
    pipes[code]=pipe
   pipe=pipes[code];_,tokens=pipe.g2p(text)
   for graphemes,phones,tokens in pipe.en_tokenize(tokens):
    if not phones or len(phones)>510:raise ValueError('INPUT_CAPACITY_EXCEEDED')
    chunks.append((graphemes,phones))
  else:
   rest=text
   while len(rest)>2000:
    end=rest.rfind(' ',0,2001)
    if end<=0:raise ValueError('INPUT_CAPACITY_EXCEEDED')
    chunks.append((rest[:end],None));rest=rest[end:]
   if rest:chunks.append((rest,None))
  if not chunks:raise ValueError('SYNTHESIS_FAILED')
  for index,(surface,phones) in enumerate(chunks):
   piece=dict(turn);piece['operations']=[{'kind':'text','text':surface}]
   piece['gap_after_ms']=turn['gap_after_ms'] if index==len(chunks)-1 else 0
   if phones:piece['compiled_phonemes']=phones
   piece['accent_description']=selected.get('accent_description')
   pieces.append(piece)
 return {'pieces':pieces,'model_context':context}

if __name__=='__main__':
 try:
  packet=json.load(sys.stdin)
  with contextlib.redirect_stdout(sys.stderr):
   if packet.get('action')=='plan':result=plan(packet['profile'],packet['plan'])
   elif packet.get('action')=='quality':result=measure(base64.b64decode(packet['pcm_base64']),packet['planned_pause_intervals'])
   else:result=render(packet['profile'],packet['turn'],packet.get('timeout_seconds',260))
  print(json.dumps(result))
 except Exception as e:
  # Raw library/provider exceptions may contain credentials or private text.
  code=str(e) if isinstance(e,ValueError) and str(e) in {'PAID_USE_FORBIDDEN','PROVIDER_QUOTA','PROVIDER_FAILED','MISSING_CREDENTIALS','CAPABILITY_UNAVAILABLE','VOICE_UNAVAILABLE','VOICE_SETUP_REQUIRED','MODEL_SETUP_REQUIRED','INPUT_CAPACITY_EXCEEDED','AUDIO_FORMAT_INVALID','AUDIO_SILENT','SYNTHESIS_FAILED'} else 'SYNTHESIS_FAILED'
  print(json.dumps({'error':code}));sys.exit(1)
