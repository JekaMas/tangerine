"""Edit actual CUA frames and separately mux the matching saved WAV. No inference.

Original frames/timestamps remain untouched. Cards are explicitly editorial data
views, never fabricated product screens. No uninterrupted-live-run claim.
"""
from pathlib import Path
import datetime,json,subprocess,textwrap,shutil

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/iteration-29-full-flow-20261026'
SHARE=DATA/'share';SHARE.mkdir(exist_ok=True)
IMAGE='tangerine-local-speech:local'

def run(args):
    p=subprocess.run(['docker','run','--rm','--network','none','-v',str(DATA)+':/evidence','--entrypoint',args[0],IMAGE,*args[1:]],capture_output=True,text=True)
    with (DATA/'media-build.log').open('a') as f:f.write(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError('Media encoding failed; inspect media-build.log')
    return p.stdout

def card(name,title,body):
    (DATA/(name+'-title.txt')).write_text(title)
    (DATA/(name+'-body.txt')).write_text(body)
    filt="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile=/evidence/"+name+"-title.txt:expansion=none:fontsize=34:fontcolor=0xe87524:x=55:y=45,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile=/evidence/"+name+"-body.txt:expansion=none:fontsize=23:line_spacing=8:fontcolor=white:x=55:y=115"
    run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=0x172b3d:s=1280x720','-vf',filt,'-frames:v','1','/evidence/'+name+'.png'])
    return name+'.png'

def ts(s):return datetime.datetime.fromisoformat('2026-10-26T'+s+'+00:00').timestamp()

def main():
    raw=json.loads((DATA/'video-frames.json').read_text())
    # Repeated event reads are retained in the original log, but not replayed
    # twice in the edited video. Sort by original source time, not retrieval time.
    unique={}
    for r in raw:unique.setdefault((r['sequence'],r['metadata']['timestamp']),r)
    frames=sorted(unique.values(),key=lambda r:r['metadata']['timestamp'])
    facts=json.loads((DATA/'browser-observations.json').read_text())
    play=next(a for a in facts['actions'] if a['action']=='play stored exercise audio')
    playback=datetime.datetime.fromisoformat(play['at'].replace('Z','+00:00')).timestamp()
    key=json.loads((DATA/'keys/bc740ead-ff03-455f-805b-0fb4c7babcf1.json').read_text())
    intro=card('card-intro','Tangerine: actual local/free exercise',
        'Real Gemini Free text/mutations and installed local Kokoro audio.\n'
        'Two speakers, B1, about 90 words, two minor mistakes.\n\n'
        'Edited demonstration: waits shortened and repair work omitted.\n'
        'Original CUA frames, failures, native context and replies are retained.\n'
        'The matching saved WAV is separately synchronized during playback.\n'
        'The learner answer is a constructed partial developer answer.\n\n'
        'Recommendations remain blocked by actual provider unavailability.\n'
        'This video is evidence of the observed partial flow, not I29 acceptance.')
    dialogue='\n\n'.join(textwrap.fill(t['speaker_id']+': '+t['canonical_text'],82) for t in key['utterances'])
    keycard=card('card-key','Actual saved clean text and mutation key',dialogue+'\n\nInjected: books -> book; make -> do. Exactly two minor mistakes.\nDeveloper key inspection; candidate key, not independent linguistic gold.')
    expected=card('card-expectation','Independent expectation before scoring',
        'Constructed answer: identify book -> books and explain many + plural.\n'
        'The collocation mistake is deliberately omitted.\n\n'
        'Frozen task: detection and correction; classification=false.\n'
        'TP=1, FN=1, FP=0. Detection F1=2/3; correction recall=1/2.\n'
        '100*(45*(2/3)+30*(1/2))/75 = 60/100.\n'
        'A correct supplied optional explanation is separately 100%.\n\n'
        'An earlier arithmetic draft included classification; its correction\n'
        'from the frozen task input was saved before any numeric result existed.')
    recovery=card('card-recovery','The same saved attempt after repairs',
        'The answer and audio were retained through actual provider failures.\n'
        'Source-span diagnostics and redundant attachment handling were repaired.\n'
        'An explicit retry resumed the unfinished interpretation.\n\n'
        'Native score:60/100. One found, one missed, zero false positives.\n'
        'Recommendations did not complete: Gemini returned high-demand 503\n'
        'responses and deadlines. The saved score remains usable.\n\n'
        'The next footage reopens this same attempt. No score/audio substitution.')
    outro=card('card-outro','Observed result and remaining dependency',
        'All eleven routes: empty/populated, keyboard, read errors and recovery.\n'
        'Actual exercise: 94 words, four local speech pieces, 29.65 s WAV.\n'
        'Exact score 60/100; optional explanation 100%; reopened without inference.\n\n'
        'Required recommendations remain unavailable from the selected Free model.\n'
        'Full-flow acceptance is INCOMPLETE. Original failures remain visible.\n'
        'No paid provider calls, overage, model sweep or performance campaign.\n\n'
        'Edited CUA footage and editorial cards; saved WAV muxed separately.\n'
        'Read the accompanying report and exact native artifact relationships.')
    timeline=[];output_time=0.;audio_start=None
    def add(path,duration,kind,**meta):
        nonlocal output_time
        timeline.append({'file':path,'duration':duration,'output_start':output_time,'kind':kind,**meta});output_time+=duration
    def clip(start,end,label):
        nonlocal audio_start
        rows=[r for r in frames if start<=r['metadata']['timestamp']<=end]
        for i,r in enumerate(rows):
            at=r['metadata']['timestamp'];next_at=rows[i+1]['metadata']['timestamp'] if i+1<len(rows) else min(end,at+2)
            duration=max(.04,next_at-at)
            in_audio=at<=playback+29.65 and next_at>=playback
            if not in_audio:duration=min(duration,3.)
            if at<=playback<next_at:audio_start=output_time+(playback-at)
            add('frames/'+str(r['index']).zfill(5)+'.jpg',duration,'original CUA frame',sequence=r['sequence'],source_timestamp=at,label=label)
    add(intro,8,'editorial disclosure card')
    clip(ts('16:32:00'),ts('16:34:46'),'actual request and generation; waits compressed')
    add(keycard,12,'editorial view of the actual saved clean text/key')
    clip(ts('16:35:03'),ts('16:36:21.7'),'actual library and full stored playback')
    add(expected,8,'editorial view of the independent frozen expectation')
    clip(ts('16:36:21.7'),ts('16:37:49'),'actual draft, submission and retained failure')
    add(recovery,9,'editorial repair/failure disclosure')
    final=[r for r in frames if r.get('label')=='actual-final-result-after-reopen']
    if not final:raise AssertionError('No actual final result footage')
    clip(final[0]['metadata']['timestamp'],final[-1]['metadata']['timestamp'],'actual saved result reopened')
    add(outro,10,'editorial incomplete-verdict card')
    if audio_start is None:raise AssertionError('The recorded full playback is absent')
    with (DATA/'video.ffconcat').open('w') as f:
        f.write('ffconcat version 1.0\n')
        for row in timeline:f.write("file '/evidence/"+row['file']+"'\nduration "+str(row['duration'])+'\n')
        f.write("file '/evidence/"+outro+"'\n")
    banner='Edited actual CUA footage | waits/cuts disclosed | saved audio separately synchronized | I29 incomplete'
    (DATA/'video-banner.txt').write_text(banner)
    audio='assets/'+key['audio']['asset_id']+'.wav';shutil.copy2(DATA/audio,SHARE/'exercise.wav')
    filt="scale=1280:660:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:0:color=0x172b3d,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile=/evidence/video-banner.txt:expansion=none:fontcolor=white:fontsize=18:x=20:y=687"
    run(['ffmpeg','-v','error','-y','-safe','0','-f','concat','-i','/evidence/video.ffconcat','-i','/evidence/'+audio,'-vf',filt,'-filter_complex','[1:a]adelay='+str(round(audio_start*1000))+':all=1,apad[a]','-map','0:v','-map','[a]','-r','24','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart','/evidence/share/tangerine-observed-flow.mp4'])
    probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json','/evidence/share/tangerine-observed-flow.mp4']))
    receipt={'attempt_id':'8db4a113-d8b6-430c-9bb1-eaec2fc19ff5','case_version_id':'3029a559-14ca-4992-a984-b1c02cb067c4','audio_asset_id':key['audio']['asset_id'],'video':'share/tangerine-observed-flow.mp4','audio':'share/exercise.wav','source_frames':len(raw),'unique_source_events':len(frames),'edits_disclosed':True,'separate_saved_audio_disclosed':True,'audio_output_start_seconds':audio_start,'output_seconds_planned':output_time,'omitted_stages':['successful recommendation generation: provider unavailable'],'complete_flow':False,'probe':probe,'timeline':timeline,'recording_limits':['CDP frame/event gaps and a recorder timeout are retained; this is an edited observation, not uninterrupted realtime','Repeated event reads deduplicated by source sequence/timestamp; originals retained','Cards are editorial views of actual data and explicit limitations, not product screenshots','No independent ASR/accent or complete phonological qualification is claimed']}
    (DATA/'media-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print({'duration':probe['format']['duration'],'audio_start':audio_start,'source_frames':len(raw),'unique':len(frames)})

if __name__=='__main__':main()
