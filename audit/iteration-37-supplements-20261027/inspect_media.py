"""Encode one actual continuous Chrome source session with an honest caption."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027'
IMAGE='tangerine-local-speech:local'
def media(args):
 r=subprocess.run(['docker','run','--pull=never','--rm','--network','none','-v',str(OUT)+':/evidence','-v',str(ROOT/'services/web/public/fonts/SourceSans3.ttf')+':/font.ttf:ro','--entrypoint',args[0],IMAGE,*args[1:]],capture_output=True,text=True,timeout=120)
 if r.returncode:raise RuntimeError(r.stderr[-1600:])
 return r.stdout
video=next((OUT/'browser/video').glob('*.webm'))
(OUT/'video-title.txt').write_text('Tangerine: acquired speech and dialogue sources')
(OUT/'video-caption.txt').write_text('Actual saved sources. Silent. Labelled read fixtures; no models or synthesis.')
filter='pad=1280:820:0:50:color=0x192b39,drawtext=fontfile=/font.ttf:textfile=/evidence/video-title.txt:fontcolor=white:fontsize=24:x=22:y=12,drawtext=fontfile=/font.ttf:textfile=/evidence/video-caption.txt:fontcolor=white:fontsize=20:x=22:y=783'
media(['ffmpeg','-nostdin','-y','-i','/evidence/'+str(video.relative_to(OUT)),'-vf',filter,'-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','/evidence/speech-supplements-demo.mp4'])
probe=json.loads(media(['ffprobe','-v','error','-show_streams','-show_format','-of','json','/evidence/speech-supplements-demo.mp4']))
duration=float(probe['format']['duration']);frames=[]
for i,fraction in enumerate([.15,.5,.85]):
 seconds=duration*fraction;target='video-frame-'+str(i)+'.png';media(['ffmpeg','-nostdin','-y','-ss',str(seconds),'-i','/evidence/speech-supplements-demo.mp4','-frames:v','1','/evidence/'+target]);frames.append(dict(path=target,seconds=seconds))
(OUT/'media-observations.json').write_text(json.dumps(dict(probe=probe,frames=frames,source=str(video.relative_to(OUT)),silent=True,cut=False,scope='Actual acquired-source browsing, named views, retained files, finite playback, recovery and reopen. Some read failures/empty/window pages are labelled fixtures; not a generated exercise, inference or acoustic-mistake qualification.'),indent=2)+'\n')
print(json.dumps(dict(seconds=duration,frames=len(frames))))
