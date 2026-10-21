"""One private foreground diagnostic action over actual saved audio."""
import base64,hashlib,io,json,os,pathlib,time,uuid,wave
from decimal import Decimal
from audio import admit,wav_bytes,measure
from diagnostic_audio import clip_windows,complete_judge_measurements,wer
from diagnostic_models import auditory,recognize

def checkpoint(wire):
 path=os.environ.get('TANGERINE_DIAGNOSTIC_CAPTURE')
 if path:
  target=pathlib.Path(path);temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(wire));temporary.replace(target)

def plan(packet):
 pcm=admit(base64.b64decode(packet['audio_base64']));n=len(pcm)//2
 intervals=[(r['start'],r['end']) for r in packet.get('intervals',[])] or [(0,n)]
 windows=clip_windows(intervals,n,min(10,packet.get('max_clip_seconds',10))*24000)
 clips=[]
 for a,b in windows:
  raw=wav_bytes(pcm[a*2:b*2]);clips.append(dict(source_interval=dict(start=a,end=b),audio_base64=base64.b64encode(raw).decode()))
 return dict(clips=clips,sample_count=n)

def execute(packet):
 audio=base64.b64decode(packet['audio_base64']);pcm=admit(audio);sha=packet.get('audio_sha256') or packet.get('input',{}).get('audio_sha256');method=packet['method_id'];started=time.time()
 if method in ['ffmpeg-ebur128-v1','praat-ac-v1']:
  if method=='ffmpeg-ebur128-v1':
   raw=measure(pcm);fields=[('integrated_lufs','LUFS'),('true_peak_dbtp','dBTP')];version=method
  else:
   import numpy as np
   from acoustic_measurements import features
   raw=features(np.frombuffer(pcm,dtype='<i2').astype(float)/32768);version='praat-'+raw['praat_version']+'-ac-v1'
   fields=[('lexical_stress','category'),('nuclear_stress','category'),('f0_range_semitones','semitones'),('f0_slope_semitones_per_second','semitones_per_second'),('syllable_duration_ratio','ratio'),('rhythm','category'),('boundary','category'),('weak_form','category'),('linking','category'),('assimilation','category'),('elision','category')]
  rows=[]
  for feature,unit in fields:
   value=raw.get(feature) if method=='ffmpeg-ebur128-v1' else raw.get('prosody',{}).get(feature)
   rows.append(dict(id=str(uuid.uuid4()),audio_sha256=sha,method_id=method,method_version=version,feature=feature,interval=dict(start=0,end=len(pcm)//2,sample_rate_hz=24000),status='observed' if value is not None else 'not_measurable',numeric_value=None if value is None else format(Decimal(str(value)),'f'),categorical_value=None,unit=unit,evidence_asset_ids=[],reason=None if value is not None else raw.get('prosody',{}).get('reason') if feature.startswith('f0_') else 'requires_auditory_or_native_annotation' if method=='praat-ac-v1' else 'measurement_unavailable'))
  return dict(measurements=rows,native=raw,receipt=dict(model=None,started_at_unix=started,finished_at_unix=time.time(),inference_calls=0))
 if method=='faster-whisper-local-en-v1':
  # The recognizer accepts only audio; reference comparison occurs afterwards.
  raw=recognize(audio,checkpoint);comparison=wer(packet.get('reference_text',''),raw['hypothesis']);raw['comparison']=comparison
  rows=[dict(id=str(uuid.uuid4()),audio_sha256=sha,method_id=method,method_version='faster-whisper-'+raw['library_version']+'-lexical-v1',feature='WER',interval=dict(start=0,end=len(pcm)//2,sample_rate_hz=24000),status='observed' if comparison['exact_ratio'] is not None else 'not_measurable',numeric_value=comparison['decimal'],categorical_value=None,unit='ratio',evidence_asset_ids=[],reason=comparison['reason'])]
  return dict(measurements=rows,native=raw,receipt=dict(model=raw['model_manifest']['repo'],started_at_unix=started,finished_at_unix=time.time(),inference_calls=1))
 if method not in ['qwen25-omni-audio-v1','gemini-audio-v1']:raise ValueError('CAPABILITY_UNAVAILABLE')
 clips=[audio]
 if packet.get('reference_audio_base64'):clips.append(base64.b64decode(packet['reference_audio_base64']))
 result=auditory(packet['profile'],packet['prompt'],packet['input'],clips,packet.get('timeout_seconds',260),checkpoint)
 if result.get('error'):return result
 selected=set(packet['input']['units']);features=set(packet['input']['features'])
 if any(r.get('unit_id') not in selected or r.get('feature') not in features for r in result['output']['findings']):result['error']='DIAGNOSTIC_OUTPUT_INVALID';return result
 result['measurements']=complete_judge_measurements(result['output'],packet['input'],method)
 result['receipt']=dict(model=packet['profile']['model'],started_at_unix=started,finished_at_unix=time.time(),inference_calls=1)
 return result
