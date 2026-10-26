"""Edit retained real generation and current real checking for the SAME case.

Cuts, source-frame gaps, the new explicit checking configuration and the
separately synchronized actual saved WAV are disclosed. No model execution.
"""
from pathlib import Path
import datetime,json,shutil
import build_media as encoder

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'data/iteration-29-full-flow-20261026'
DATA=ROOT/'data/iteration-29-saved-case-flow-20261026'
encoder.DATA=DATA
encoder.SHARE=DATA/'share'
encoder.SHARE.mkdir(exist_ok=True)

def epoch(value):return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()

def main():
    native=json.loads((DATA/'call-reconciliation.json').read_text())
    assert native['complete_flow'], 'Do not edit missing recommendations into a complete demo'
    observations=json.loads((DATA/'ui-observations.json').read_text())
    by={r['name']:r for r in observations}
    frames=json.loads((DATA/'video-frames.json').read_text())
    unique={}
    for row in frames:unique.setdefault((row['sequence'],row['source_timestamp']),row)
    frames=sorted(unique.values(),key=lambda r:r['source_timestamp'])
    playback=epoch(json.loads((DATA/'playback-action.json').read_text())['at'])
    old_receipt=json.loads((OLD/'media-receipt.json').read_text())
    timeline=[];clock=0.;audio_start=None
    def add(file,duration,kind,**facts):
        nonlocal clock
        timeline.append(dict(file=file,duration=duration,output_start=clock,kind=kind,**facts));clock+=duration
    def card(name,title,body,duration):
        add(encoder.card(name,title,body),duration,'explicit editorial data/disclosure card')
    def clip(start,end,label):
        nonlocal audio_start
        # Include the preceding genuine frame for a still interval; never
        # fabricate product state or interpolate a browser's progress display.
        rows=[r for r in frames if start<=r['source_timestamp']<=end]
        before=[r for r in frames if r['source_timestamp']<start]
        if before:rows.insert(0,before[-1])
        for i,row in enumerate(rows):
            at=max(start,row['source_timestamp'])
            next_at=min(end,rows[i+1]['source_timestamp']) if i+1<len(rows) else end
            if next_at<=at:continue
            duration=next_at-at
            if at<=playback<next_at:audio_start=clock+(playback-at)
            if not (at<playback+29.65 and next_at>playback):duration=min(duration,3.)
            add(row['file'],max(.04,duration),'actual current CUA frame',source_timestamp=row['source_timestamp'],label=label)
    card('complete-intro','Tangerine: actual complete exercise flow',
         'Actual Gemini Free generation/mutations; installed local Kokoro speech.\n'
         'The SAME saved case is answered with an explicitly selected local checker.\n'
         'New attempt: gpt-oss:20b. The older Gemini attempt remains unchanged.\n\n'
         'Edited actual CUA footage: cuts, waits compressed and frame gaps.\n'
         'Matching saved WAV separately synchronized during full playback.\n'
         'Developer answer is deliberately partial; expectation predates grading.\n'
         'Original failures, raw frames, native context and replies are retained.\n'
         'This is a finite functional example, not linguistic or acoustic gold.',9)
    (DATA/'reused-generation').mkdir(exist_ok=True)
    for i,row in enumerate(old_receipt['timeline']):
        if row.get('label')!='actual request and generation; waits compressed':continue
        file='reused-generation/'+str(i).zfill(5)+'.jpg'
        shutil.copy2(OLD/row['file'],DATA/file)
        add(file,row['duration'],'reused actual generation CUA frame',source_timestamp=row['source_timestamp'],label='same actual preparation; no regeneration')
    shutil.copy2(OLD/'card-key.png',DATA/'same-saved-key.png')
    add('same-saved-key.png',12,'editorial view of actual saved clean text and candidate key')
    card('complete-binding','Explicit new attempt; existing work is reused',
         'The generated case, clean/mutated text, key and stored WAV are identical.\n'
         'No old attempt was switched to a different model.\n'
         'A new ordinary listening attempt freezes local gpt-oss:20b checking.\n\n'
         'The failed installed-local generation experiments are retained separately.\n'
         'They are not used as successful generation or substituted into this case.\n'
         'No purchased credits, paid fallback, overage or model download.',8)
    clip(epoch(by['saved-case-library-recovered']['at'])-1,playback+29.9,'actual saved-case navigation and full stored playback')
    card('complete-oracle','Independent expectation recorded before submission',
         'Constructed answer detects book -> books and gives the correct reason.\n'
         'The do -> make collocation error is deliberately omitted.\n\n'
         'Frozen task: detection and correction; explanation is optional.\n'
         'TP=1, FN=1, FP=0; detection F1=2/3; correction recall=1/2.\n'
         '100*(45*(2/3)+30*(1/2))/75 = 60/100.\n'
         'The supplied correct optional explanation is separately 100%.',9)
    clip(playback+29.9,epoch(by['answer-submitted']['at'])+2,'actual answer, save/reload and submission')
    card('complete-repair','Actual recovery; original failures remain retained',
         'The saved answer survives incomplete model output and a stage deadline.\n'
         'A source-span defect is repaired: valid coordinates retain the actual\n'
         'answer when a duplicate model quote omits double quotation marks.\n'
         'Words, negation, apostrophes and ambiguous locations cannot be guessed.\n\n'
         'The same frozen local attempt resumes through the production owner.\n'
         'No key, audio, numerical result or model response is substituted.',9)
    clip(epoch(by['checking-source-repair-retry']['at'])-1,epoch(by['comments-desktop']['at'])+2,'actual source-built retry, native score and live feedback; waits compressed')
    clip(epoch(by['missed-passage-playing']['at'])-1,epoch(by['explicit-local-settings-settled']['at'])+2,'actual finite replay, refresh, saved navigation, reopening and explicit local settings')
    clip(epoch(by['final-feedback-1280']['at'])-1,epoch(by['final-result-current']['at'])+2,'actual current typography, line breaks and stored complete result')
    card('complete-outro','Observed result and proof boundary',
         'Actual native result:60/100; optional explanation100%; one found/one missed.\n'
         'LLM comments and practice recommendation are saved and reopened.\n'
         'All eleven routes retain their inspected UI/error/keyboard/typography scope.\n\n'
         'Primary score, source key and stored audio stay associated with this attempt.\n'
         'Read/reopen/export adds zero inference; candidate language/accent labels\n'
         'are not independent gold or a claim that every provider is available.\n'
         'Cuts, compressed waits, original-frame gaps and synchronized WAV disclosed.',10)
    assert audio_start is not None
    with (DATA/'complete.ffconcat').open('w') as f:
        f.write('ffconcat version 1.0\n')
        for row in timeline:f.write("file '/evidence/"+row['file']+"'\nduration "+str(row['duration'])+'\n')
        f.write("file '/evidence/complete-outro.png'\n")
    (DATA/'complete-banner.txt').write_text('Actual edited CUA | same saved case; explicit new local checker | waits/cuts/frame gaps disclosed | saved WAV synchronized')
    audio='assets/'+native['audio_asset_id']+'.wav';shutil.copy2(DATA/audio,encoder.SHARE/'exercise.wav')
    vf="scale=1280:660:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:0:color=0x172b3d,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile=/evidence/complete-banner.txt:expansion=none:fontcolor=white:fontsize=17:x=15:y=688"
    encoder.run(['ffmpeg','-v','error','-y','-safe','0','-f','concat','-i','/evidence/complete.ffconcat','-i','/evidence/'+audio,'-vf',vf,'-filter_complex','[1:a]adelay='+str(round(audio_start*1000))+':all=1,apad[a]','-map','0:v','-map','[a]','-r','24','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart','/evidence/share/tangerine-complete-flow.mp4'])
    probe=json.loads(encoder.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json','/evidence/share/tangerine-complete-flow.mp4']))
    receipt={k:native[k] for k in ['attempt_id','case_version_id','audio_asset_id','source_key_id']}
    receipt.update(video='share/tangerine-complete-flow.mp4',audio='share/exercise.wav',edits_disclosed=True,separate_saved_audio_disclosed=True,omitted_stages=[],complete_flow=True,audio_output_start_seconds=audio_start,output_seconds_planned=clock,probe=probe,timeline=timeline,recording_limits=['Edited source frames; cuts, compressed waits and frame gaps, not uninterrupted realtime','Original generation and new local checking are the SAME saved case; explicit new attempt, not fallback','Candidate key and model prose are not independent linguistic/acoustic gold'])
    (DATA/'media-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print({'seconds':probe['format']['duration'],'audio_start':audio_start,'timeline_entries':len(timeline)})

if __name__=='__main__':main()
