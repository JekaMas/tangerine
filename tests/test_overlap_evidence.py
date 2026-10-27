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
 def test_native_owner_positive(self):
  packet=read(OUT/'OBSERVATIONS.json')
  for cohort in packet['cohorts']:
   self.assertEqual(cohort['exit_code'],0)
   raw=ROOT/cohort['stdout'];self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),cohort['stdout_sha256'])
   events=[json.loads(line) for line in raw.read_text().splitlines() if line.startswith('{')]
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
