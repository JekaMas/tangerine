"""Actual independent recognition and auditory transports; no text-only hearing."""
import base64,hashlib,io,json,os,pathlib,tempfile,time,urllib.request,urllib.error,wave
from dataclasses import asdict,is_dataclass
from diagnostic_audio import transcribe_complete
from model_setup import installed
from inference_capture import observe_method,values

def derivative(audio,rate):
 import subprocess,wave
 p=subprocess.run(['ffmpeg','-nostdin','-v','error','-i','pipe:0','-ar',str(rate),'-ac','1','-acodec','pcm_s16le','-f','wav','pipe:1'],input=audio,capture_output=True,timeout=30,check=True)
 with wave.open(io.BytesIO(p.stdout),'rb') as w:pcm=w.readframes(w.getnframes())
 out=io.BytesIO()
 with wave.open(out,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
 return out.getvalue()

def recognize(audio,capture=lambda value:None):
 root,manifest=installed('faster-whisper-local-en-v1')
 from faster_whisper import WhisperModel
 from importlib.metadata import version
 model=WhisperModel(str(root),device='cpu',compute_type='int8',local_files_only=True)
 actual=derivative(audio,16000)
 with tempfile.TemporaryDirectory(prefix='tangerine-asr-') as tmp:
  path=pathlib.Path(tmp)/'input.wav';path.write_bytes(actual)
  capture(dict(method='faster-whisper-local-en-v1',model_manifest=manifest,input_audio_base64=base64.b64encode(actual).decode(),input_sample_rate_hz=16000,device='cpu',compute_type='int8',parameters=dict(language='en',task='transcribe',beam_size=5,temperature=0,word_timestamps=True,initial_prompt=None,condition_on_previous_text=False,vad_filter=False)))
  events=[]
  # ffmpeg already produced the actual16kHz derivative. Pass its PCM to the
  # recognizer directly, avoiding a second decoder and PyAV-version coupling.
  import numpy as np
  with wave.open(io.BytesIO(actual),'rb') as source:samples=np.frombuffer(source.readframes(source.getnframes()),dtype='<i2').astype(np.float32)/32768
  with observe_method(model,'transcribe',events,capture_result=False):result=transcribe_complete(model,samples)
  result.update(model_visible_calls=events,segment_iterator_complete=True)
 result.update(model_manifest=manifest,library_version=version('faster-whisper'),device='cpu',compute_type='int8',input_audio_base64=base64.b64encode(actual).decode(),input_audio_sha256=hashlib.sha256(actual).hexdigest(),input_sample_rate_hz=16000,source_sample_rate_hz=24000,clock_transform=dict(numerator=3,denominator=2))
 return result

def decode_findings(text):
 # Tolerate prose/fences around an otherwise complete object; no model audit.
 decoder=json.JSONDecoder();start=text.find('{')
 if start<0:raise ValueError('DIAGNOSTIC_OUTPUT_INVALID')
 try:out,_=decoder.raw_decode(text[start:])
 except ValueError:raise ValueError('DIAGNOSTIC_OUTPUT_INVALID') from None
 if not isinstance(out,dict) or not isinstance(out.get('findings'),list):raise ValueError('DIAGNOSTIC_OUTPUT_INVALID')
 out.setdefault('schema_version','2.0.0');out.setdefault('summary','Audio diagnostic')
 for row in out['findings']:
  for key in ['clip_interval','proposed_ipa']:row.setdefault(key,None)
 return out

def auditory(profile,prompt,input,clips,timeout=260,capture=lambda value:None):
 content=json.dumps(input,ensure_ascii=False,sort_keys=True)
 started=time.time()
 if profile['provider']=='local_qwen25_omni':
  if profile['billing_mode']!='local':raise ValueError('PAID_USE_FORBIDDEN')
  selection='qwen25-omni-3b-audio-v1' if profile['model']=='Qwen/Qwen2.5-Omni-3B' else 'qwen25-omni-audio-v1'
  root,manifest=installed(selection)
  if manifest['repo']!=profile['model'] or manifest['revision']!=profile['revision']:raise ValueError('MODEL_BINDING_MISMATCH')
  import numpy as np,torch,soundfile as sf
  from transformers import Qwen2_5OmniConfig,Qwen2_5OmniForConditionalGeneration,Qwen2_5OmniProcessor
  from qwen_omni_utils import process_mm_info
  torch.set_num_threads(min(4,os.cpu_count() or 1))
  # This action produces text only. Do not allocate the unused speech decoder.
  config=Qwen2_5OmniConfig.from_pretrained(str(root),local_files_only=True);config.enable_audio_output=False
  model=Qwen2_5OmniForConditionalGeneration.from_pretrained(str(root),config=config,torch_dtype=torch.float32,attn_implementation='eager',local_files_only=True).to(profile['device'])
  processor=Qwen2_5OmniProcessor.from_pretrained(str(root),local_files_only=True)
  rate=int(processor.feature_extractor.sampling_rate)
  derivatives=[derivative(c,rate) for c in clips]
  with tempfile.TemporaryDirectory(prefix='tangerine-auditory-') as tmp:
   parts=[{'type':'text','text':content}]
   for i,clip in enumerate(derivatives):
    path=pathlib.Path(tmp)/('clip-'+str(i)+'.wav');path.write_bytes(clip)
    parts.extend([{'type':'text','text':'Target audio' if i==0 else 'Reference audio'},{'type':'audio','audio':str(path)}])
   conversation=[{'role':'system','content':[{'type':'text','text':prompt}]},{'role':'user','content':parts}]
   text=processor.apply_chat_template(conversation,add_generation_prompt=True,tokenize=False)
   audios,images,videos=process_mm_info(conversation,use_audio_in_video=False)
   encoded=processor(text=text,audio=audios,images=images,videos=videos,return_tensors='pt',padding=True,use_audio_in_video=False).to(profile['device'])
   encoded_context=values(dict(encoded));events=[]
   capture(dict(model_encoded_inputs=encoded_context,provider='local_qwen25_omni',model_manifest=manifest,model_visible_template=text,profile=profile,input_audio=[dict(sha256=hashlib.sha256(c).hexdigest(),base64=base64.b64encode(c).decode(),sample_rate_hz=rate) for c in derivatives],input_token_ids=encoded['input_ids'].cpu().tolist(),parameters=dict(device=profile['device'],dtype='float32',attention='eager',enable_audio_output=False,return_audio=False,do_sample=False,max_new_tokens=profile['max_output_tokens'])))
   try:
    with observe_method(model,'generate',events),torch.inference_mode():output=model.generate(**encoded,return_audio=False,do_sample=False,max_new_tokens=profile['max_output_tokens'])
   except Exception as error:
    capture(dict(provider='local_qwen25_omni',model_manifest=manifest,model_visible_template=text,profile=profile,model_encoded_inputs=encoded_context,model_visible_calls=events,failure_type=type(error).__name__))
    raise
   generated=output[:,encoded['input_ids'].shape[1]:]
   visible=processor.batch_decode(generated,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
  wire=dict(model_encoded_inputs=encoded_context,model_visible_calls=events,provider='local_qwen25_omni',model_manifest=manifest,model_visible_template=text,profile=profile,input_audio=[dict(sha256=hashlib.sha256(c).hexdigest(),base64=base64.b64encode(c).decode(),sample_rate_hz=rate,source_sample_rate_hz=24000) for c in derivatives],input_token_ids=encoded['input_ids'].cpu().tolist(),output_token_ids=generated.cpu().tolist(),output_text=visible,parameters=dict(device=profile['device'],dtype='float32',attention='eager',enable_audio_output=False,return_audio=False,do_sample=False,max_new_tokens=profile['max_output_tokens']))
 elif profile['provider']=='gemini_interactions':
  # Only an explicitly selected free/included binding can reach this adapter.
  if profile['billing_mode'] not in ['free_tier','included_subscription']:raise ValueError('PAID_USE_FORBIDDEN')
  key=os.environ.get('GEMINI_API_KEY')
  if not key:raise ValueError('MISSING_CREDENTIALS')
  parts=[dict(type='text',text=content)]
  for i,clip in enumerate(clips):parts.extend([dict(type='text',text='Target audio' if i==0 else 'Reference audio'),dict(type='audio',data=base64.b64encode(clip).decode(),mime_type='audio/wav')])
  request=dict(model=profile['model'],input=parts,store=False,stream=False,background=False,tools=[],system_instruction=prompt,generation_config=dict(max_output_tokens=profile['max_output_tokens']))
  raw=json.dumps(request,ensure_ascii=False,separators=(',',':')).encode()
  if len(raw)>=20000000:raise ValueError('INPUT_CAPACITY_EXCEEDED')
  req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',data=raw,headers={'Content-Type':'application/json','x-goog-api-key':key})
  capture(dict(provider='gemini_interactions',profile=profile,request=request))
  class NoRedirect(urllib.request.HTTPRedirectHandler):
   def redirect_request(self,*args,**kwargs):return None
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  try:
   with opener.open(req,timeout=timeout) as response:status=response.status;response_raw=response.read()
  except urllib.error.HTTPError as error:status=error.code;response_raw=error.read()
  try:result=json.loads(response_raw)
  except ValueError:result=None
  wire=dict(provider='gemini_interactions',profile=profile,request=request,http_status=status,response=result,response_text=response_raw.decode(errors='replace'))
  capture(wire)
  if not isinstance(result,dict) or status!=200 or result.get('status')!='completed':return dict(error='DIAGNOSTIC_PROVIDER_FAILED',wire=wire,started_at_unix=started,finished_at_unix=time.time())
  visible=''.join(c.get('text','') for step in result.get('steps',[]) if step.get('type')=='model_output' for c in step.get('content',[]) if c.get('type')=='text')
 else:raise ValueError('CAPABILITY_UNAVAILABLE')
 capture(wire)
 try:findings=decode_findings(visible)
 except ValueError:return dict(error='DIAGNOSTIC_OUTPUT_INVALID',wire=wire,started_at_unix=started,finished_at_unix=time.time())
 return dict(output=findings,wire=wire,started_at_unix=started,finished_at_unix=time.time())
