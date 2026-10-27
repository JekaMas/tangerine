"""Edited actual Chrome frames, with explicit waits/cuts and fixture disclosure."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-34-verification-20261027/browser'


def main():
    frames=json.loads((OUT/'video-frames.json').read_text())
    lines=[];timeline=[];clock=0
    for index,row in enumerate(frames):
        elapsed=(frames[index+1]['at']-row['at'])/1000 if index+1<len(frames) else 3
        duration=min(4,max(2,elapsed))
        lines += ["file 'frames/"+row['file']+"'",'duration '+str(duration)]
        timeline.append(dict(label=row['label'],start=clock,duration=duration,original_gap=elapsed))
        clock+=duration
    lines.append("file 'frames/"+frames[-1]['file']+"'")
    (OUT/'video.concat').write_text('\n'.join(lines)+'\n')
    (OUT/'video-title.txt').write_text('Tangerine I34: preparation and recovery UI')
    (OUT/'video-disclosure.txt').write_text('Edited Chrome observations; controlled HTTP; no new generation or audio. Cuts compress waits.')
    command=['docker','run','--pull=never','--rm','--network=none','-v',str(OUT)+':/evidence',
        '-v',str(ROOT/'services/web/public/fonts/SourceSans3.ttf')+':/font.ttf:ro',
        '-w','/evidence','--entrypoint','ffmpeg','tangerine-local-speech:local',
        '-nostdin','-y','-f','concat','-safe','0','-i','video.concat',
        '-vf',"scale=1280:800:force_original_aspect_ratio=decrease,pad=1280:900:(ow-iw)/2:(oh-ih)/2:color=0x192b39,setsar=1,drawtext=fontfile=/font.ttf:textfile=video-title.txt:fontcolor=white:fontsize=24:x=24:y=10,drawtext=fontfile=/font.ttf:textfile=video-disclosure.txt:fontcolor=white:fontsize=20:x=24:y=866",
        '-r','24','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','preparation-recovery.mp4']
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    (OUT/'video-encode.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Video encoding failed; see video-encode.log')
    result=subprocess.run(['docker','run','--pull=never','--rm','--network=none','-v',str(OUT)+':/evidence:ro',
        '--entrypoint','ffprobe','tangerine-local-speech:local','-v','error','-show_streams','-show_format','-of','json','/evidence/preparation-recovery.mp4'],capture_output=True,text=True,timeout=30,check=True)
    probe=json.loads(result.stdout)
    (OUT/'video-probe.json').write_text(json.dumps(dict(probe=probe,timeline=timeline,
        actual_browser_frames=len(frames),origin='Actual CUA Chrome screenshots; cuts and compressed waits; not continuous screen capture.',
        synthetic_outcomes='All HTTP writes controlled; completion is UI-only, no audio or native generation claimed.',
        new_model_calls=0,new_synthesis_calls=0,silent=True),indent=2)+'\n')
    print(json.dumps(dict(frames=len(frames),seconds=probe['format']['duration'],exit_code=0)))


if __name__=='__main__':main()
