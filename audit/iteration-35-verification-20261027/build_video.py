"""Two actual Chrome sessions, joined with explicit cut and silent-video disclosure."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-35-verification-20261027/browser'
def media(command):
 p=subprocess.run(['docker','run','--pull=never','--rm','--network=none','-v',str(OUT)+':/evidence','-v',str(ROOT/'services/web/public/fonts/SourceSans3.ttf')+':/font.ttf:ro','--entrypoint',command[0],'tangerine-local-speech:local',*command[1:]],capture_output=True,text=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr[-1800:])
 return p.stdout
first=next((OUT/'after-cache-before-oracle-repair').glob('*.webm'));second=next((OUT/'videos').glob('*.webm'))
(OUT/'video-title.txt').write_text('Tangerine: full official L2-ARCTIC import and recovery')
(OUT/'video-disclosure.txt').write_text('Actual Chrome on retained data. Cut between sessions. Silent; no new import, models or speech.')
filter="[0:v]fps=24,setsar=1[v0];[1:v]fps=24,setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0,pad=1280:820:0:50:color=0x192b39,drawtext=fontfile=/font.ttf:textfile=/evidence/video-title.txt:fontcolor=white:fontsize=24:x=22:y=12,drawtext=fontfile=/font.ttf:textfile=/evidence/video-disclosure.txt:fontcolor=white:fontsize=20:x=22:y=783[v]"
media(['ffmpeg','-nostdin','-y','-i','/evidence/'+str(first.relative_to(OUT)),'-i','/evidence/'+str(second.relative_to(OUT)),'-filter_complex',filter,'-map','[v]','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','/evidence/official-source-recovery.mp4'])
probe=json.loads(media(['ffprobe','-v','error','-show_streams','-show_format','-of','json','/evidence/official-source-recovery.mp4']))
for seconds in [3,7,11]:media(['ffmpeg','-nostdin','-y','-ss',str(seconds),'-i','/evidence/official-source-recovery.mp4','-frames:v','1','/evidence/video-frame-'+str(seconds)+'.png'])
(OUT/'video.json').write_text(json.dumps(dict(probe=probe,clips=[str(first.relative_to(OUT)),str(second.relative_to(OUT))],origin='Actual installed Chrome on native full imported data, two sessions joined with visible disclosure; no synthetic successful data or audio.',silent=True,cut=True),indent=2)+'\n')
print(json.dumps(dict(seconds=probe['format']['duration'],clips=2)))
