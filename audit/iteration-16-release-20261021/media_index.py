"""Index actual retained browser/model media; no generated illustration or audio edit."""
from pathlib import Path
import base64,json,os,struct,subprocess,wave
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;D=R/'data/iteration16'
load=lambda p:json.loads(p.read_text())
live=R/load(D/'release/live-current.json')['root'];prior=Path(load(live/'retained-observations.json')['source']);current=R/load(D/'release/current-source.json')['root']
settings_pointer=D/'release/settings-current.json';settings=R/load(settings_pointer)['root'] if settings_pointer.exists() else current
portable_pointer=D/'release/portable-current.json';portable=R/load(portable_pointer)['root'] if portable_pointer.exists() else None
attempts=D/'attempts/run-498170c8d8'
roots={'speech':R/'data/iteration7/browser/run-16fdff2d1dc5','listening':R/'data/iteration9/browser/run-f15b42d86f1b','interpretation':R/'data/iteration10/browser/run-f105d75c23d4','scoring':R/'data/iteration11/browser/run-922f48e71445','review':R/'data/iteration12/browser/run-9cdd7962284c','sources':R/'data/iteration13/browser/run-69bcea2bd5','reports':R/'data/iteration14/browser/run-a21836ff35','recovery':R/'data/iteration15/workspace/run-ead277e23e','actual-main':prior,'actual-continuation':live,'current-source':current,'current-settings':settings,'attempts':attempts}
if portable:roots['portable']=portable
rows=[('Library','/',(portable/'test_portable_library_positive.png') if portable else prior/'test_library_positive.png','Actual restored populated Library on amd64; the original empty Library and generation path remain captured in the main-flow video.' if portable else 'Actual empty Library before generation; populated Listen-and-answer navigation is captured in the actual main-flow video.'),('Prepare','/prepare',prior/'test_generation_positive.png','Actual installed local LLM clean→mutations/key with one explicitly saved Resume.'),('Saved audio','/audio',roots['speech']/'test_playback_positive.png','Actual native Kokoro/control/storage; text-key upstream is constructed.'),('Listen/results','/listen',prior/'test_primary_score_positive.png','Actual local LLM interpretation/native100/comments; optional explanation absent.'),('Saved attempts','/attempts',(portable/'attempts-history.png') if portable else attempts/'attempts-history.png','Actual stored history; separate owned real DB outage/Refresh/reopen.'),('Reviews','/reviews',live/'test_review_positive.png','Actual local reconsideration/dispute and unchanged supported primary score.'),('Sources','/sources',roots['sources']/'test_rows_positive.png','Real importer/DB/UI with labelled constructed native source records.'),('Reports/Lab','/reports',roots['reports']/'test_report_positive.png','Real source/attempt/experiment owners; constructed reporting population.'),('Settings','/settings',settings/'test_current_precision_ui_positive.png','Actual source save/reload of CPU/int8/qnnpack/repetition binding; no inference.'),('Recovery','/recovery',roots['recovery']/'test_switch_back_positive.png','Actual native maintenance, restore/switch and saved-data readback.'),('Cleanup','/cleanup',roots['recovery']/'test_cleanup_preview_positive.png','Actual owned records, preview/confirmation rejection/application; no user data erased.')]
media=[]
for title,route,path,boundary in rows:
 if not path.is_file():raise ValueError('Missing route picture: '+str(path))
 width,height=struct.unpack('>II',path.read_bytes()[16:24]);media.append(dict(screen=title,route=route,picture=str(path.relative_to(R)),width=width,height=height,proof_boundary=boundary))
videos={}
for directory in [D/'frontend/final-videos',prior/'videos',live/'videos',current/'videos',settings/'videos',*([portable/'videos'] if portable else [])]:
 for path in directory.glob('browser-*.json'):
  meta=load(path)
  for v in meta['videos']:
   video=Path(v);assert video.is_file();videos[str(video.relative_to(R))]=dict(path=str(video.relative_to(R)),origin=str(path.relative_to(R)),silent_video=meta['silent_video'],driver=meta['driver'])
# One native metadata read per selected video. This is a final artifact usability
# observation, not a runtime stored-data audit or another browser/model run.
program='''import json,pathlib,subprocess,sys
out={}
for name in json.loads(sys.argv[1]):
 p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json','/repo/'+name],capture_output=True,text=True,check=True);x=json.loads(p.stdout);assert any(s['codec_type']=='video' for s in x['streams']);assert float(x['format']['duration'])>0;out[name]=x
print(json.dumps(out))'''
previous=load(A/'MEDIA.json') if (A/'MEDIA.json').exists() else {}
retained={v['path']:v['ffprobe'] for v in previous.get('videos',[]) if 'ffprobe' in v}
to_probe=[name for name in videos if name not in retained]
p=subprocess.run(['docker','run','--rm','--network','none','-v',str(R)+':/repo:ro','--entrypoint','python3','tangerine-i16-speech-arm64:local','-B','-c',program,json.dumps(to_probe)],env=os.environ,capture_output=True,text=True,timeout=120)
if p.returncode:raise AssertionError(p.stderr)
probes={**retained,**json.loads(p.stdout)}
for path,row in videos.items():row['ffprobe']=probes[path]
audio_paths=[prior/'played.wav',D/'frontend/audio/qwen-custom.wav',D/'frontend/audio/qwen-base.wav']
if portable:audio_paths.append(portable/'actual-amd64-speech.wav')
# Exact already-observed native source/result pairs; no resynthesis or edit.
acoustic=R/'data/iteration8/native/tangerine-acoustic-21b85f0167e6'
for control in ['pause_insert','vowel_duration','vot_edit','phone_pair','pitch_duration','pitch_range']:
 for side in ['source','result']:audio_paths.append(acoustic/('acoustic-'+control+'-'+side+'.wav'))
audios=[]
for path in audio_paths:
 with wave.open(str(path),'rb') as w:audios.append(dict(path=str(path.relative_to(R)),sample_rate_hz=w.getframerate(),channels=w.getnchannels(),sample_count=w.getnframes(),duration_seconds=w.getnframes()/w.getframerate()))
all_pictures=[]
for key,root in roots.items():
 for path in sorted(root.glob('*.png')):all_pictures.append(dict(group=key,path=str(path.relative_to(R))))
result=dict(origin='Actual local browser/runtime/model artifacts; individual constructed/actual boundaries retained.',screens=media,pictures=all_pictures,videos=list(videos.values()),audio=audios,video_audio_note='Play the exact WAV separately. Native Chrome WebM captures are silent; no fabricated/muxed audio track.',portable_status='passed' if portable else 'not_qualified')
(A/'MEDIA.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Local release evidence','',result['origin'],'','| Screen | Route | Picture | Evidence boundary |','|---|---|---|---|']
for row in media:lines.append('| '+row['screen']+' | '+row['route']+' | [Open picture]('+str(R/row['picture'])+') | '+row['proof_boundary']+' |')
lines+=['','Exact audio files:','']
for row in audios:lines.append('- ['+Path(row['path']).name+']('+str(R/row['path'])+') — '+str(round(row['duration_seconds'],3))+' seconds, '+str(row['sample_rate_hz'])+' Hz.')
lines+=['','Actual browser recordings (silent; exact WAVs above):','']
for row in videos.values():lines.append('- ['+Path(row['path']).name+']('+str(R/row['path'])+') — '+str(round(float(row['ffprobe']['format']['duration']),3))+' seconds.')
lines+=['','All '+str(len(all_pictures))+' pictures and native metadata are indexed in [MEDIA.json]('+str(A/'MEDIA.json')+').','']
(A/'EVIDENCE.md').write_text('\n'.join(lines));print(json.dumps(dict(screens=len(media),pictures=len(all_pictures),videos=len(videos),audio=len(audios),portable=result['portable_status'])))
