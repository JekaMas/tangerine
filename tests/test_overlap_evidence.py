"""Independent finite I32 recording/timing evidence, no inference or runtime gate."""
import copy,hashlib,json,math,struct,sys,unittest,wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audit/iteration-32-overlap-20261027"))
from observed_go import receipt_errors
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/iteration-32-overlap-20261027'
SELECTED=OUT/'selected'
def read(path):return json.loads(path.read_text())
def samples(path):
 with wave.open(str(path),'rb') as w:
  if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,24000):raise AssertionError('wrong actual PCM format')
  raw=w.readframes(w.getnframes());return struct.unpack('<'+'h'*(len(raw)//2),raw)
def rounded(x):return math.floor(x+.5) if x>=0 else math.ceil(x-.5)
def expected_samples(progress,source):
 c=progress['composition'];expected=[0.0]*c['sample_count']
 for t in c['tracks']:
  for i in range(t['source_start'],t['source_end']):expected[t['final_start']+i-t['source_start']]+=source[t['piece_id']][i]*t['gain']
 return tuple(rounded(x) for x in expected)
def scene(kind):
 directory=SELECTED/kind;p=read(directory/'progress.json')
 source={v['id']:samples(directory/f'source-{i+1}.wav') for i,v in enumerate(p['pieces'])}
 return directory,p,source,samples(directory/'mixed.wav')
def observed_ids():
 packet=read(OUT/'OBSERVATIONS.json');result=set()
 for cohort in packet['cohorts']:
  errors=receipt_errors(cohort)
  if errors:raise AssertionError(errors)
  result.update(cohort['test_ids'])
 return result
class OverlapEvidence(unittest.TestCase):
 def require_native(self,names):
  found=observed_ids();self.assertTrue({'tangerine.local/api/internal/app::'+n for n in names}<=found)
 def test_admission_positive(self):
  self.require_native(['TestOverlapAdmissionPositive','TestOverlapCooperativePositive','TestOverlapManifestPositive','TestOverlapFrozenPlanPositive'])
 def test_admission_negative(self):
  self.require_native(['TestOverlapAdmissionNegative/same-speaker','TestOverlapAdmissionNegative/wrong-unit','TestOverlapAdmissionNegative/forward-target','TestOverlapAdmissionNegative/false-error','TestOverlapAdmissionNegative/bad-scope','TestOverlapAdmissionNegative/missing-intent','TestOverlapSchemaNegative','TestOverlapCanonicalNegative'])
 def test_arithmetic_positive(self):
  self.require_native(['TestOverlapArithmeticPositive','TestOverlapSequentialPositive','TestOverlapSourceMapPositive'])
 def test_clipping_cancellation_negative(self):
  self.require_native(['TestOverlapClippingNegative','TestOverlapCancellationNegative','TestOverlapPublicFailureNegative'])
 def test_native_clocks_positive(self):
  self.require_native(['TestOverlapSplitTargetPositive','TestOverlapLaterTurnPositive','TestOverlapKeyPositive','TestOverlapAcousticKeySiblingPositive','TestOverlapWordsPositive'])
 def test_missing_native_timing_negative(self):
  self.require_native(['TestOverlapTimingNegative','TestOverlapFutureNativeClockNegative'])

 def test_actual_samples_positive(self):
  for kind in ['obstructive','cooperative_backchannel']:
   d,p,source,mixed=scene(kind)
   with self.subTest(kind=kind):
    self.assertEqual(mixed,expected_samples(p,source));self.assertEqual(len(mixed),p['composition']['sample_count'])
    self.assertTrue(all(any(n!=0 for n in values) for values in source.values()))
    a,b=p['composition']['pieces'];self.assertLess(b['final_start'],a['final_end'])
    shared=range(max(a['final_start'],b['final_start']),min(a['final_end'],b['final_end']))
    self.assertTrue(any(source[a['piece_id']][i-a['final_start']] and source[b['piece_id']][i-b['final_start']] for i in shared))
 def test_wrong_offset_negative(self):
  _,p,source,mixed=scene('obstructive');c=copy.deepcopy(p);t=next(t for t in c['composition']['tracks'] if t['piece_id']==c['pieces'][1]['id']);t['final_start']+=1;c['composition']['sample_count']+=1
  self.assertNotEqual(mixed,expected_samples(c,source))
 def test_source_and_key_clocks_positive(self):
  for kind in ['obstructive','cooperative_backchannel']:
   d,p,source,mixed=scene(kind);key=read(d/'key.json');o=p['composition']['overlaps'][0];target=p['pieces'][0]
   phrase='Do not touch' if kind=='obstructive' else 'visit the museum'
   u=key['utterances'][0];start=u['surface_text'].index(phrase);end=start+len(phrase)
   words=target['word_intervals'];first=next(w for w in words if w['start_cp']==start);last=next(w for w in words if w['end_cp']==end)
   self.assertEqual(o['final_start'],first['start']);self.assertEqual(o['final_end'],min(last['end'],p['composition']['pieces'][1]['final_end']))
   interval=key['units'][0]['audio_intervals'][0];self.assertEqual(interval,dict(start_ms=o['final_start']//24,end_ms=(o['final_end']+23)//24))
   other=key['utterances'][1]['audio_interval'];placement=p['composition']['pieces'][1];self.assertEqual(other,dict(start_ms=placement['final_start']//24,end_ms=(placement['final_end']+23)//24))
   mapping=read(d/'sample-map.json');self.assertEqual(mapping['output_audio_sha256'],hashlib.sha256((d/'mixed.wav').read_bytes()).hexdigest())
   self.assertTrue(all('mix_gain' in r for r in mapping['rows'] if r['kind']!='gap'))
   for row in mapping['rows']:
    if row['kind']=='gap':continue
    piece=next(x for x in p['pieces'] if x['id']==row['piece_id']);place=next(x for x in p['composition']['pieces'] if x['piece_id']==row['piece_id'])
    self.assertEqual(piece['audio_sha256'],row['source_audio_sha256']);self.assertEqual(row['final_start']-row['source_start'],place['final_start'])
 def test_sequential_counterexample_negative(self):
  _,p,source,mixed=scene('obstructive');a,b=p['pieces'];self.assertNotEqual(mixed,source[a['id']]+source[b['id']]);key=read(SELECTED/'obstructive/key.json');self.assertLess(key['utterances'][1]['audio_interval']['start_ms'],len(source[a['id']])//24)
 def test_local_recognition_contrast_positive(self):
  for kind in ['obstructive','cooperative_backchannel']:
   d,p,source,mixed=scene(kind);original=read(d/'source-1.wav.asr.json');altered=read(d/'mixed.wav.asr.json')
   for row in [original,altered]:self.assertTrue(row['segment_iterator_complete']);self.assertEqual(row['device'],'cpu');self.assertEqual(row['parameters']['initial_prompt'],None);self.assertTrue(row['model_visible_calls'])
   clean=original['hypothesis'].lower();target=altered['hypothesis'].lower()
   if kind=='obstructive':self.assertIn('do not touch the wire',clean);self.assertNotIn('do not touch',target);self.assertIn('want to speak now',target)
   else:self.assertIn('visit the museum tomorrow morning',clean);self.assertIn('visit the museum tomorrow morning',target)
 def test_cooperative_score_negative(self):
  control=read(SELECTED/'cooperative_backchannel/score.json')['counts'];self.assertEqual([control[k] for k in ['true_errors','tp','fp','fn']],[0,0,0,0]);target=read(SELECTED/'obstructive/score.json')['counts'];self.assertEqual([target[k] for k in ['true_errors','tp','fp','fn']],[1,1,0,0])
 def test_resume_positive(self):
  d,p,_,_=scene('obstructive');before=read(d/'interrupted-progress.json');self.assertEqual(before['composition'],p['composition']);self.assertIsNone(before['assembled_asset_id']);self.assertEqual([x['asset_id'] for x in before['pieces']],[x['asset_id'] for x in p['pieces']]);self.assertTrue(read(d/'observation.json')['resume_tested'])
 def test_no_repeated_inference_negative(self):
  for kind in ['obstructive','cooperative_backchannel']:self.assertEqual(read(SELECTED/kind/'observation.json')['new_local_recordings'],0)
 def test_lab_positive(self):
  row=read(OUT/'lab-readback.json');self.assertTrue(row['readback']);self.assertEqual(row['status'],'FINISHED');self.assertEqual(row['export_inference_calls'],0);self.assertGreater(row['artifact_files'],10)
 def test_preservation_positive(self):
  gap=Path('/Users/jekamas/projects/0xatelerix/tangerine/audit/spec-fullness-20261008/GAPS.md');self.assertEqual(hashlib.sha256(gap.read_bytes()).hexdigest(),'78f8cfa15fdc0215d92f6045d2f0f6e53b391030e543050ee1b09ed65776db65')
  for row in read(ROOT/'audit/iteration-32-overlap-20261027/PRESERVATION.json')['registries']:
   self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])
 def test_context_positive(self):
  for kind in ['obstructive','cooperative_backchannel']:
   raw=(SELECTED/kind/'text-context-true.json').read_text();self.assertIn('overlap_intents',raw);self.assertIn('target_scope',raw);self.assertIn('canonical_script',raw)
 def test_browser_positive(self):
  facts=read(OUT/'browser-observations.json');self.assertEqual({(1280,720),(390,844),(320,740)},{(r['width'],r['height']) for r in facts['layouts']})
  for row in facts['layouts']:self.assertFalse(row['overflow']);self.assertEqual(row['size'],'17px');self.assertEqual(row['lineHeight'],'24.65px');self.assertEqual(row['caption'],'14px')
  self.assertTrue(any(any(a['id']=='clip3' and not a['paused'] and a['time']>0 and a['error'] is None for a in row) for row in facts['playback']))
 def test_native_range_positive(self):
  self.require_native(['TestNativeOverlapObstructive','TestNativeOverlapCooperative'])
  for kind in ['obstructive','cooperative_backchannel']:
   d,p,source,mixed=scene(kind);r=read(d/'observation.json')['stored_range'];o=p['composition']['overlaps'][0]
   self.assertEqual((r['start_byte'],r['end_byte_exclusive'],r['status']),(44+2*o['final_start'],44+2*o['final_end'],206))
 def test_impossible_range_negative(self):
  for kind in ['obstructive','cooperative_backchannel']:self.assertEqual(read(SELECTED/kind/'observation.json')['stored_range']['invalid_status'],416)
 def test_quality_nonblocking_positive(self):
  self.require_native(['TestNativeSpeechQualityMeasuredPositive','TestNativeSpeechQualityWarningPositive','TestNativeSpeechQualityUnavailableNegative','TestNativeSpeechQualityMalformedNegative'])
 def test_listening_browser_positive(self):
  facts=read(OUT/'listening-browser.json');self.assertEqual({(1280,720),(390,844),(320,740)},{(r['width'],r['height']) for r in facts['layouts']})
  for row in facts['layouts']:self.assertFalse(row['overflow']);self.assertIn('Source Sans 3',row['font']);self.assertEqual(row['size'],'17px');self.assertEqual(row['lineHeight'],'24.65px');self.assertEqual(row['caption'],'15px')
  obs={r['kind']:r for r in facts['observations']}
  for kind,start,end,limit in [('masked-passage-stop',1.9,2.45,2.8),('cooperative-passage-stop',2.875,3.75,4.1)]:
   row=obs[kind];self.assertTrue(row['paused']);self.assertIsNone(row['error']);self.assertGreaterEqual(row['time'],end);self.assertLess(row['time'],limit)
  row=obs['keyboard-replay'];self.assertEqual(row['focus'],'Replay passage 1.1');self.assertEqual(row['outline'],'3px');self.assertFalse(row['paused']);self.assertGreaterEqual(row['time'],1.9);self.assertLess(row['time'],2.45)
  row=obs['cooperative-full-playback'];self.assertTrue(row['ended']);self.assertEqual(row['time'],5.325);self.assertIsNone(row['error'])
 def test_transient_read_recovery_positive(self):
  events=[readline for line in (OUT/'listening-requests.jsonl').read_text().splitlines() if (readline:=json.loads(line))['method']=='GET' and readline['path']=='/api/v1/attempts/11111111-1111-4111-8111-111111111132']
  self.assertEqual([e['status'] for e in events],[200,503,503,200,503,503,503,200])
  obs={r['kind']:r for r in read(OUT/'listening-browser.json')['observations']}
  for kind in ['transient-read-recovered','keyboard-refresh-recovered']:
   row=obs[kind];self.assertEqual(row['alerts'],[]);self.assertEqual(row['status'],['Saved state refreshed.']);self.assertTrue(row['paused']);self.assertEqual(row['answer'],'B interrupts the warning. B should wait until A finishes.');self.assertEqual(row['score'],'Primary score: 100.0 / 100')
  self.assertEqual(obs['keyboard-refresh-recovered']['outline'],'3px')
 def test_technical_error_negative(self):
  row=next(r for r in read(OUT/'listening-browser.json')['observations'] if r['kind']=='persistent-read-guidance')
  self.assertEqual(row['alerts'],['Saved attempt is unavailable. Your text is retained. Refresh to retry.']);self.assertTrue(row['refresh']);self.assertEqual(row['score'],'Primary score: 100.0 / 100');self.assertEqual(row['answer'],'B interrupts the warning. B should wait until A finishes.');self.assertTrue(row['paused'])
  self.assertNotIn('PRIVATE_NATIVE_CANARY',' '.join(row['alerts']))
 def test_ordinary_playback_no_dispatch_negative(self):
  events=[json.loads(line) for line in (OUT/'listening-requests.jsonl').read_text().splitlines()]
  self.assertTrue(events)
  self.assertTrue(all(e['method']=='GET' or (e['method']=='POST' and '/playback' in e['path']) for e in events))
  obs=next(r for r in read(OUT/'listening-browser.json')['observations'] if r['kind']=='cooperative-open-no-autoplay');self.assertTrue(obs['paused']);self.assertEqual(obs['time'],0);self.assertIn('Found 0 of 0 mistakes',obs['counts'])
  for id,kind in [('11111111-1111-4111-8111-111111111132','obstructive'),('22222222-2222-4222-8222-222222222232','cooperative_backchannel')]:
   sha=hashlib.sha256((SELECTED/kind/'mixed.wav').read_bytes()).hexdigest();self.assertTrue(any(e.get('served_sha256')==sha and id in e['path'] for e in events))
 def test_video_positive(self):
  frames=read(OUT/'verify-frames.json');description=read(OUT/'video-description.json');probe=read(OUT/'video-probe.json')
  self.assertEqual(len(frames),42);self.assertEqual(description['frame_count'],len(frames));self.assertTrue(all((OUT/f'verify-frames/frame-{i:05d}.jpg').stat().st_size>1000 for i in range(len(frames))))
  stream=next(s for s in probe['streams'] if s['codec_type']=='video');self.assertEqual((stream['width'],stream['height']),(1280,844));self.assertEqual(stream['codec_name'],'h264');self.assertGreater(float(probe['format']['duration']),10)
 def test_video_claims_negative(self):
  probe=read(OUT/'video-probe.json');self.assertFalse([s for s in probe['streams'] if s['codec_type']=='audio'])
  description=read(OUT/'video-description.json');self.assertIn('Silent browser video',description['audio']);self.assertIn('not a new generated full flow',description['ui_boundary']);self.assertIn('static waits',description['cuts'])
 def test_frozen_failure_policy_positive(self):
  self.require_native(['TestOverlapFixedFailureNegative','TestOverlapRecoverableFailurePositive','TestOverlapFixedFailureResponseNegative','TestNativeOverlapMissingTimingRecovery'])
  d=SELECTED/'obstructive-missing-timing';p=read(d/'preparation.json');progress=read(d/'progress.json')
  self.assertEqual(p['phase_states']['render'],'failed');self.assertFalse(p['last_failure']['retryable']);self.assertEqual(p['last_failure']['code'],'CAPABILITY_UNQUALIFIED');self.assertEqual(len(progress['pieces']),2);self.assertTrue(all(x['state']=='complete' and x['asset_id'] for x in progress['pieces']))
 def test_frozen_failure_retry_negative(self):
  p=read(SELECTED/'obstructive-missing-timing/preparation.json');self.assertNotIn('ALIGNMENT_UNAVAILABLE',p['last_failure']['message']);self.assertIn('compatible speech voice',p['last_failure']['message']);self.assertIsNone(p['audio_asset_id'])
 def test_fixed_recovery_browser_positive(self):
  facts=read(OUT/'recovery-browser.json');self.assertEqual({(route,w) for route in ['/prepare','/audio'] for w in [1280,390,320]},{(r['route'],r['width']) for r in facts['views']})
  for row in facts['views']:self.assertFalse(row['overflow']);self.assertEqual(row['size'],'17px');self.assertEqual(row['lineHeight'],'24.65px');self.assertIn('Source Sans 3',row['font']);self.assertEqual(len(row['articles']),3)
  actions={r['kind']:r for r in facts['actions']};self.assertEqual(actions['new-exercise-link']['hash'],'#main-content');self.assertEqual(actions['new-exercise-link']['topic'],'My retained safety conversation');self.assertEqual(actions['keyboard-topic-focus']['label'],'Topic');self.assertEqual(actions['keyboard-topic-focus']['value'],'A preserved topic for the next exercise');self.assertEqual(actions['keyboard-topic-focus']['outline'],'3px')
 def test_fixed_recovery_no_resume_negative(self):
  for row in read(OUT/'recovery-browser.json')['views']:
   for a in row['articles'][:2]:
    self.assertEqual(a['buttons'],[]);self.assertEqual(a['links'][0]['text'],'Prepare a new exercise');self.assertIn('compatible voice or different speech settings',a['alerts'][0]);self.assertNotIn('Ready to assemble',a['text']);self.assertNotIn('PRIVATE_NATIVE_CANARY',a['text'])
   transient=row['articles'][2];self.assertEqual(transient['buttons'],[dict(text='Resume exercise' if row['route']=='/prepare' else 'Resume audio',disabled=False)]);self.assertIn('resume this exercise explicitly',transient['alerts'][0])
 def test_recovery_video_positive(self):
  desc=read(OUT/'recovery-video-description.json');frames=read(OUT/'recovery-frames.json');probe=read(OUT/'recovery-video-probe.json');self.assertEqual(desc['frame_count'],25);self.assertEqual(len(frames),25);self.assertFalse([s for s in probe['streams'] if s['codec_type']=='audio']);self.assertIn('read-only HTTP boundary',desc['boundary']);self.assertGreater(float(probe['format']['duration']),5)
 def test_native_owner_positive(self):
  packet=read(OUT/'OBSERVATIONS.json')
  for cohort in packet['cohorts']:
   self.assertEqual(cohort['exit_code'],0)
   raw=ROOT/cohort['stdout'];self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),cohort['stdout_sha256'])
   events=[json.loads(line) for line in raw.read_text().splitlines() if line.startswith('{')]
   if cohort['kind']=='contracts-lab':
    self.assertTrue({e['Package'] for e in events}<= {'tangerine.local/api/internal/contracts','tangerine.local/api/internal/lab'});self.assertTrue(all(not k.startswith('services/api/internal/app/') for k in cohort['source_sha256']));self.assertTrue(cohort['original_non_dependency_bindings'])
   self.assertFalse([e for e in events if e['Action'] in ['fail','skip']]);observed={e['Package']+'::'+e['Test'] for e in events if e.get('Test') and e['Action']=='pass'}
   self.assertEqual(set(cohort['test_ids']),observed)
   for name,digest in cohort['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
 def test_reuse_mismatch_negative(self):
  packet=read(OUT/'OBSERVATIONS.json')
  for kind in ['exit','population','source']:
   cohort=copy.deepcopy(packet['cohorts'][0])
   if kind=='exit':cohort['exit_code']=1
   elif kind=='population':cohort['test_ids'].pop()
   else:cohort['source_sha256'][next(iter(cohort['source_sha256']))]='0'*64
   self.assertTrue(receipt_errors(cohort),kind)
if __name__=='__main__':unittest.main()
