"""Encode the actual uncut verification session; no TTS/model is invoked."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-36-verification-20261027'
def media(args):
 command=['docker','run','--pull=never','--rm','--network','none','-v',str(OUT)+':/evidence','-v',str(ROOT/'services/web/public/fonts/SourceSans3.ttf')+':/font.ttf:ro','--entrypoint',args[0],'tangerine-local-speech:local',*args[1:]]
 result=subprocess.run(command,capture_output=True,text=True,timeout=120)
 if result.returncode:raise RuntimeError(result.stderr[-1600:])
 return result.stdout
video=next((OUT/'browser-green/video').glob('*.webm'))
(OUT/'video-title.txt').write_text('Tangerine: JFLEG refresh, downloads and partial-source examples')
(OUT/'video-caption.txt').write_text('Actual Chrome. Silent, uncut. Controlled delays/failures. Constructed partial/empty sources.')
filter='pad=1280:820:0:50:color=0x192b39,drawtext=fontfile=/font.ttf:textfile=/evidence/video-title.txt:fontcolor=white:fontsize=24:x=22:y=12,drawtext=fontfile=/font.ttf:textfile=/evidence/video-caption.txt:fontcolor=white:fontsize=20:x=22:y=783'
media(['ffmpeg','-nostdin','-y','-i','/evidence/'+str(video.relative_to(OUT)),'-vf',filter,'-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','/evidence/jfleg-verification.mp4'])
probe=json.loads(media(['ffprobe','-v','error','-show_streams','-show_format','-of','json','/evidence/jfleg-verification.mp4']))
duration=float(probe['format']['duration']);frames=[]
for index,fraction in enumerate([.2,.5,.8]):
 target='video-frame-'+str(index)+'.png';seconds=duration*fraction
 media(['ffmpeg','-nostdin','-y','-ss',str(seconds),'-i','/evidence/jfleg-verification.mp4','-frames:v','1','/evidence/'+target]);frames.append(dict(path=target,seconds=seconds))
(OUT/'media-observations.json').write_text(json.dumps(dict(probe=probe,frames=frames,source=str(video.relative_to(OUT)),silent=True,cut=False,scope='Actual browser reading the retained full import; controlled response order/download failures and constructed partial/empty imports. No source download, full re-import, generated exercise, inference or speech.'),indent=2)+'\n')
print(json.dumps(dict(seconds=duration,frames=len(frames))))
