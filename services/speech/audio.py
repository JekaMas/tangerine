"""Actual WAV admission and sample-exact assembly; quality warnings are advisory."""
import array, io, struct, subprocess, sys, wave

RATE=24000

def wav_bytes(pcm):
 out=io.BytesIO()
 with wave.open(out,'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm)
 return out.getvalue()

def admit(data):
 with wave.open(io.BytesIO(data),'rb') as w:
  if (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype()) != (1,2,RATE,'NONE'):raise ValueError('AUDIO_FORMAT_INVALID')
  expected=w.getnframes();pcm=w.readframes(expected)
 if expected==0 or len(pcm)!=expected*2 or len(data)<44:raise ValueError('AUDIO_FORMAT_INVALID')
 if not any(pcm):raise ValueError('AUDIO_SILENT')
 return pcm

def normalize(data):
 p=subprocess.run(['ffmpeg','-nostdin','-v','error','-i','pipe:0','-f','wav','-acodec','pcm_s16le','-ar','24000','-ac','1','pipe:1'],input=data,capture_output=True,timeout=60,check=False)
 if p.returncode:raise ValueError('AUDIO_FORMAT_INVALID')
 # FFmpeg streaming WAV uses unknown-size headers; decode and write a finite RIFF.
 with wave.open(io.BytesIO(p.stdout),'rb') as w:pcm=w.readframes(w.getnframes())
 final=wav_bytes(pcm);admit(final);return final

def assemble(pieces):
 out=bytearray();intervals=[]
 for piece in pieces:
  pcm=admit(piece['audio']);start=len(out)//2;out.extend(pcm);end=len(out)//2
  intervals.append({'piece_id':piece['id'],'start_sample':start,'end_sample':end,'gap_end_sample':end+piece['gap_after_ms']*24})
  out.extend(b'\0\0'*(piece['gap_after_ms']*24))
 if not intervals:raise ValueError('AUDIO_FORMAT_INVALID')
 return wav_bytes(out),intervals


def quality(pcm):
 """Mechanical observations only. No ASR, accent assertion or release gate."""
 values=array.array('h');values.frombytes(pcm)
 if sys.byteorder!='little':values.byteswap()
 peak=max(abs(v) for v in values)/32768
 rms=(sum(v*v for v in values)/len(values))**.5/32768
 warnings=[]
 if peak>=.9999:warnings.append('clipping_risk')
 if rms<.01:warnings.append('low_level')
 return {'peak_full_scale':peak,'rms_full_scale':rms,'sample_count':len(values),'warnings':warnings,'observed_accent':None,'speech_intelligibility':None}


def measure(pcm,planned=()):
 import math,re,shutil,hashlib
 result=quality(pcm);n=result['sample_count'];values=array.array('h');values.frombytes(pcm)
 if sys.byteorder!='little':values.byteswap()
 silent=[]
 for start in range(0,n,240):
  end=min(start+480,n);rms=math.sqrt(sum(v*v for v in values[start:end])/(end-start))/32768
  if rms<=10**(-45/20):
   if silent and start<=silent[-1][1]:silent[-1][1]=end
   else:silent.append([start,end])
 unwanted=[]
 for start,end in silent:
  remaining=[[start,end]]
  for a,b in planned:
   next_ranges=[]
   for c,d in remaining:
    if b<=c or a>=d:next_ranges.append([c,d])
    else:
     if c<a:next_ranges.append([c,a])
     if b<d:next_ranges.append([b,d])
   remaining=next_ranges
  unwanted+=remaining
 result.update(silence_intervals=silent,planned_pause_intervals=list(planned),unwanted_silence_intervals=unwanted)
 if any(b-a>=48000 for a,b in unwanted):result['warnings'].append('unwanted_silence')
 command=['ffmpeg','-nostdin','-v','info','-f','s16le','-ar','24000','-ac','1','-i','pipe:0','-filter_complex','ebur128=peak=true','-f','null','-']
 if n<9600:result.update(integrated_lufs=None,true_peak_dbtp=None,loudness_state='not_measurable');result['warnings'].append('loudness_not_measurable');return result
 process=subprocess.run(command,input=pcm,capture_output=True,timeout=60,check=False)
 summary=process.stderr.decode(errors='replace').rsplit('Summary:',1)[-1];integrated=re.search(r'I:\s*([-+0-9.]+) LUFS',summary);peak=re.search(r'Peak:\s*([-+0-9.]+) dBFS',summary)
 version=subprocess.run(['ffmpeg','-version'],capture_output=True,timeout=5,check=False).stdout.decode(errors='replace')
 binary=shutil.which('ffmpeg')
 result.update(integrated_lufs=float(integrated[1]) if integrated and process.returncode==0 else None,true_peak_dbtp=float(peak[1]) if peak and process.returncode==0 else None,loudness_state='measured' if integrated and peak and process.returncode==0 else 'not_measurable',method={'id':'ffmpeg-ebur128-v1','command':command,'version_and_build':version,'binary_sha256':hashlib.sha256(open(binary,'rb').read()).hexdigest()})
 if result['integrated_lufs'] is None:result['warnings'].append('loudness_not_measurable')
 elif not -20<=result['integrated_lufs']<=-16:result['warnings'].append('loudness_outside_target')
 if result['true_peak_dbtp'] is not None and result['true_peak_dbtp']>-1:result['warnings'].append('true_peak_outside_target')
 return result
