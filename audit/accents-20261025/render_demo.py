"""Encode native browser frames and synchronize exact saved audio.

Original timestamps are retained in demo-frames.json and original.mp4. The short
demo removes long idle gaps, preserves playback speed, and labels that edit.
There are no simulated screens, replacement model responses or voice-overs.
"""
import json,os,subprocess,wave
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/accents-20261025'
v=json.loads((O/'demo-frames.json').read_text());frames=v['frames'];cues=v['cues'];start=frames[0]['timestamp'];end=frames[-1]['timestamp']+3
audio=[]
for cue in cues:
 if 'audio' not in cue:continue
 p=Path(cue['audio']);p=p if p.is_absolute() else R/p
 with wave.open(str(p)) as w:duration=w.getnframes()/w.getframerate()
 audio.append((cue['at'],cue['at']+duration,p))
wait=[]
for a,b in [('Generate exercise','Exercise saved with four local audio pieces'),('Submit answer for LLM checking','Score, detected and missed mistakes, LLM feedback')]:
 x=next(c['at'] for c in cues if c['label']==a)+1;y=next(c['at'] for c in cues if c['label']==b)-1
 wait.append((x,y,6/(y-x)))
breaks=sorted({start,end,*[f['timestamp'] for f in frames],*[x for a,b,_ in audio for x in [a,b]],*[x for a,b,_ in wait for x in [a,b]]})
mapped={start:0};segments=[];clock=0
for a,b in zip(breaks,breaks[1:]):
 mid=(a+b)/2;scale=1
 if not any(x<=mid<=y for x,y,_ in audio):scale=next((s for x,y,s in wait if x<=mid<=y),min(1,2/(b-a)))
 length=(b-a)*scale;segments.append((a,b,clock,length));clock+=length;mapped[b]=clock
def when(t):
 if t in mapped:return mapped[t]
 a,b,c,d=next(s for s in segments if s[0]<=t<=s[1]);return c+(t-a)*d/(b-a)
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
for short in [False,True]:
 name='demo' if short else 'original';listing=O/(name+'.concat');rows=[]
 for i,f in enumerate(frames):
  a=f['timestamp'];b=frames[i+1]['timestamp'] if i+1<len(frames) else end
  rows.extend(["file '/workspace/"+str(Path(f['path']).relative_to(R))+"'",f'duration {(when(b)-when(a)) if short else b-a:.6f}'])
 rows.append(rows[-2]);listing.write_text('\n'.join(rows)+'\n')
 args=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','concat','-safe','0','-i','/workspace/'+str(listing.relative_to(R))]
 for _,_,p in audio:args+=['-i','/workspace/'+str(p.relative_to(R))]
 filters=[]
 for i,(a,b,p) in enumerate(audio,1):filters.append(f'[{i}:a]adelay={round((when(a) if short else a-start)*1000)}:all=1[a{i}]')
 duration=when(end) if short else end-start
 filters.append(''.join(f'[a{i}]' for i in range(1,len(audio)+1))+f'amix=inputs={len(audio)}:normalize=0,apad,atrim=duration={duration:.6f}[audio]')
 label='REAL UI - idle waits shortened; exact stored audio synchronized' if short else 'REAL UI - original timing; exact stored audio synchronized'
 filters.append(f"[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,drawbox=x=0:y=692:w=iw:h=28:color=black@0.9:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{label}':x=12:y=698:fontsize=16:fontcolor=white[video]")
 args+=['-filter_complex',';'.join(filters),'-map','[video]','-map','[audio]','-fps_mode','vfr','-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-b:a','128k','-t',str(duration),'-movflags','+faststart','/workspace/'+str((O/(name+'.mp4')).relative_to(R))]
 p=subprocess.run(['docker','run','--rm','--network','none','--entrypoint','', '-v',str(R)+':/workspace','tangerine-local-speech:local',*args],env=ENV,cwd=R,capture_output=True,text=True,timeout=240)
 (O/(name+'-encode.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stderr[-1200:])
 print(json.dumps({'video':name,'seconds':duration,'frames':len(frames)}),flush=True)
(O/'video-edit.json').write_text(json.dumps({'original_seconds':end-start,'demo_seconds':when(end),'audio_origin':'Exact saved preview/dialogue WAVs, synchronized to recorded playback cues; not captured system audio','idle_edit':'Long generation/checking waits compressed to six seconds each; other idle frame holds capped at two seconds; audio playback unchanged','raw_frame_index':'demo-frames.json'},indent=2)+'\n')
