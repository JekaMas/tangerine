"""Retain the actual continuous browser session, with an explicit proof caption."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-37-verification-20261027'

def media(args):
    result=subprocess.run(['docker','run','--pull=never','--rm','--network','none',
        '-v',str(OUT)+':/evidence','-v',str(ROOT/'services/web/public/fonts/SourceSans3.ttf')+':/font.ttf:ro',
        '--entrypoint',args[0],'tangerine-local-speech:local',*args[1:]],capture_output=True,text=True,timeout=120)
    if result.returncode:raise RuntimeError(result.stderr[-1800:])
    return result.stdout

def main():
    video=next((OUT/'media-final/video').glob('*.webm'))
    (OUT/'video-title.txt').write_text('Tangerine: saved-source playback and recovery')
    (OUT/'video-caption.txt').write_text('Actual saved recordings; controlled read failures. Silent. No models or synthesis.')
    filter='pad=1280:820:0:50:color=0x192b39,drawtext=fontfile=/font.ttf:textfile=/evidence/video-title.txt:fontcolor=white:fontsize=24:x=22:y=12,drawtext=fontfile=/font.ttf:textfile=/evidence/video-caption.txt:fontcolor=white:fontsize=20:x=22:y=783'
    media(['ffmpeg','-nostdin','-y','-i','/evidence/'+str(video.relative_to(OUT)),'-vf',filter,'-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','/evidence/source-recovery-demo.mp4'])
    probe=json.loads(media(['ffprobe','-v','error','-show_streams','-show_format','-of','json','/evidence/source-recovery-demo.mp4']))
    duration=float(probe['format']['duration']);frames=[]
    for i,fraction in enumerate([.15,.5,.85]):
        seconds=duration*fraction;name='video-frame-'+str(i)+'.png'
        media(['ffmpeg','-nostdin','-y','-ss',str(seconds),'-i','/evidence/source-recovery-demo.mp4','-frames:v','1','/evidence/'+name])
        frames.append(dict(path=name,seconds=seconds))
    (OUT/'media-observations.json').write_text(json.dumps(dict(probe=probe,frames=frames,source=str(video.relative_to(OUT)),silent=True,cut=False,
        scope='Continuous real source playback/recovery verification; viewport resizing is letterboxed. Controlled read failures and a saved native DRAL-window selection are labelled. Not a generation/scoring flow or acoustic-quality evaluation.',
        original_audio='data/iteration-37-supplements-20261027/dral-original-dialogue-fragment.wav',audio_origin='Unchanged retained CC0 source bytes; separately retained, not dubbed into the silent video.'),indent=2)+'\n')
    print(json.dumps(dict(seconds=duration,inspected_frame_targets=len(frames))))

if __name__=='__main__':main()
