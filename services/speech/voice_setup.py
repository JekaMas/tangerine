"""Explicit synthetic voice design/reference admission and saved clone conditioning."""
import contextlib, hashlib, io, json, os, pathlib, sys, tempfile, time
from model_setup import installed, ROOT
from audio import normalize
os.environ.setdefault('NUMBA_CACHE_DIR','/tmp/numba-cache')

def setup(request):
 import torch, soundfile as sf
 from qwen_tts import Qwen3TTSModel
 profile=request['profile_id'];voice=request['voice_id']
 for part in (profile,voice):
  if not part or '/' in part or part in ('.','..'):raise ValueError('INVALID_VOICE_ID')
 dest=ROOT/'voices'/profile/voice;dest.mkdir(parents=True,exist_ok=True)
 if (dest/'manifest.json').exists():
  manifest=json.loads((dest/'manifest.json').read_text())
  if manifest['request']!=request:raise ValueError('VOICE_ID_CONFLICT')
  return manifest
 text=request['reference_text'];origin=request['mode'];started=time.time()
 if origin=='design':
  root,design_manifest=installed('qwen-design-v1')
  model=Qwen3TTSModel.from_pretrained(str(root),device_map='cpu',dtype=torch.float32,attn_implementation='eager',local_files_only=True)
  audio,rate=model.generate_voice_design(text=text,language='English',instruct=request['voice_description'])
  buffer=io.BytesIO();sf.write(buffer,audio[0],rate,format='WAV',subtype='PCM_16');data=normalize(buffer.getvalue());del model
 elif origin=='local_reference':
  source=ROOT/request['reference_path'];source.resolve().relative_to(ROOT.resolve());data=normalize(source.read_bytes());design_manifest=None
 else:raise ValueError('INVALID_VOICE_MODE')
 (dest/'reference.wav').write_bytes(data);(dest/'reference.txt').write_text(text)
 root,base_manifest=installed('qwen-base-v1')
 model=Qwen3TTSModel.from_pretrained(str(root),device_map='cpu',dtype=torch.float32,attn_implementation='eager',local_files_only=True)
 prompt=model.create_voice_clone_prompt(ref_audio=str(dest/'reference.wav'),ref_text=text)
 torch.save(prompt,dest/'conditioning.tmp');os.replace(dest/'conditioning.tmp',dest/'conditioning.pt')
 files=[]
 for name in ('reference.wav','reference.txt','conditioning.pt'):
  b=(dest/name).read_bytes();files.append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'size':len(b)})
 manifest={'request':request,'profile_id':profile,'voice_id':voice,'origin':origin,'description':request.get('voice_description'),'locale':request['locale'],'reference_text':text,'files':files,'design_model':design_manifest,'base_model':base_manifest,'started_at':started,'finished_at':time.time()}
 (dest/'manifest.tmp').write_text(json.dumps(manifest,indent=2));os.replace(dest/'manifest.tmp',dest/'manifest.json')
 return manifest
if __name__=='__main__':
 try:
  request=json.load(sys.stdin)
  with contextlib.redirect_stdout(sys.stderr):result=setup(request)
  print(json.dumps(result))
 except Exception as e:
  code=str(e) if isinstance(e,ValueError) and str(e) in {'INVALID_VOICE_ID','VOICE_ID_CONFLICT','INVALID_VOICE_MODE','MODEL_SETUP_REQUIRED','AUDIO_FORMAT_INVALID','AUDIO_SILENT'} else 'VOICE_SETUP_FAILED'
  print(json.dumps({'error':code}));sys.exit(1)
