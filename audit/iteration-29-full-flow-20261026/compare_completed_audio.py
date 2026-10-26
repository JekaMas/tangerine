"""Compare the selected separately synchronized WAV with decoded video audio.

This proves file correspondence only, not acoustic or linguistic quality.
"""
from pathlib import Path
import json,subprocess

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/iteration-29-saved-case-flow-20261026'

def main():
    start=json.loads((DATA/'media-receipt.json').read_text())['audio_output_start_seconds']
    # Run the existing installed encoder/numpy runtime. No host dependencies.
    code='''import json,wave,subprocess,numpy as np
from pathlib import Path
p=Path('/evidence')
start=START
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(round(start,3)),'-i',str(p/'share/tangerine-complete-flow.mp4'),'-t','29.65','-ar','24000','-ac','1','-c:a','pcm_s16le',str(p/'video-audio-window.wav')],check=True)
def load(path):
 with wave.open(str(path),'rb') as w:return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
a,b=load(p/'share/exercise.wav'),load(p/'video-audio-window.wav')
scores=[]
for lag in range(-48,49):
 left,right=(a[lag:],b[:len(b)-lag]) if lag>=0 else (a[:len(a)+lag],b[-lag:])
 scores.append((float(np.corrcoef(left,right)[0,1]),lag))
correlation,lag=max(scores)
r={'source_samples':len(a),'video_decoded_samples':len(b),'correlation':float(np.corrcoef(a,b)[0,1]),'aligned_correlation':correlation,'codec_alignment_lag_samples':lag,'alignment_search_samples':[-48,48],'method':'Decode separately synchronized saved-audio window at '+str(round(start,3))+' seconds; compare at24k mono PCM','alignment_scope':'Codec/demux window alignment within2ms, not an acoustic or linguistic judgment','new_model_calls':0}
(p/'audio-video-match.json').write_text(json.dumps(r,indent=2)+'\\n');print(json.dumps(r))
'''.replace('START',repr(start))
    p=subprocess.run(['docker','run','--rm','--network','none','-v',str(DATA)+':/evidence','--entrypoint','python','tangerine-local-speech:local','-c',code],capture_output=True,text=True)
    (DATA/'audio-compare.log').write_text(p.stdout+p.stderr)
    if p.returncode:raise SystemExit('Audio correspondence check failed; inspect retained log')
    print(p.stdout.strip())

if __name__=='__main__':main()
