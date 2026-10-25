"""Literal current CUA/media oracles; controlled HTTP is not new native grading."""
import copy,importlib.util,json,unittest
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/iteration-20-results-replay-20261026';AUDIT=ROOT/'audit/iteration-20-results-replay-20261026'
s=importlib.util.spec_from_file_location('i20_review',AUDIT/'review.py');review=importlib.util.module_from_spec(s);s.loader.exec_module(review)
ANSWER='I heard “two ticket”. Use “two tickets”.\nThe plural is required after two.'
class CompletionI20(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.facts=json.loads((DATA/'observations.json').read_text());cls.c=cls.facts['cases'];cls.n=json.loads((DATA/'native-attempt.json').read_text());cls.score=json.loads((DATA/'native-results.json').read_text())['score'];cls.events=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]
 def test_current_result_positive(self):
  c=self.c['complete'];self.assertEqual('Primary score: 60.0 / 100',c['score']);self.assertIn('Found 1 of 2 mistakes · 1 missed · 0 false positives',c['summary']);self.assertIn('Optional explanation: 100.0%',c['summary']);self.assertLess(c['scoreY'],c['savedY']);self.assertTrue(c['savedClosed']);self.assertEqual(self.n['answer_text'],self.c['savedAnswer']['answer']);self.assertTrue(self.c['savedAnswer']['readOnly']);self.assertFalse(self.c['savedAnswer']['disabled']);self.assertEqual('en',self.c['savedAnswer']['language'])
  expected=100*(45*Fraction(2,3)+30*Fraction(1,2))/75;self.assertEqual(Fraction(60),expected);self.assertEqual({'denominator':'1','numerator':'60'},self.score['composite']['exact_value_0_100']);self.assertEqual(self.n['attempt_id'],self.score['attempt_id'])
 def test_draft_positive(self):
  self.assertFalse(self.c['draftInitial']['readOnly']);self.assertIsNone(self.c['draftInitial']['score']);self.assertIn('Draft saved.',self.c['draftSaved']['statuses']);self.assertEqual(ANSWER,self.c['draftReopened']['answer']);self.assertFalse(self.c['draftReopened']['readOnly']);self.assertIsNone(self.c['checking']['score']);self.assertTrue(any('Answer saved. Checking findings, corrections' in x for x in self.c['checking']['statuses']))
  for key in ['submitted','submittedReload']:self.assertEqual(ANSWER,self.c[key]['answer']);self.assertTrue(self.c[key]['readOnly']);self.assertFalse(self.c[key]['disabled'])
 def test_uncertain_negative(self):
  c=self.c['uncertain'];self.assertEqual('Primary score: uncertain',c['score']);self.assertNotIn('/ 100',c['score']);self.assertIn('Optional explanation: not applicable',c['summary']);self.assertIn('detection.f1: 66.7%',c['main']);self.assertIn('Some findings remain uncertain',c['main'])
 def test_optional_reason_negative(self):
  c=self.c['absent'];self.assertEqual('Primary score: 60.0 / 100',c['score']);self.assertIn('Optional explanation: not applicable',c['summary']);self.assertIn('Missing explanations do not reduce your primary score.',c['summary']);self.assertNotIn('Optional explanation: 0',c['summary'])
 def test_replay_positive(self):
  a,b=self.c['replayStart']['audio'],self.c['replayEnd']['audio'];self.assertFalse(a['paused']);self.assertGreaterEqual(a['current'],9.59);self.assertLess(a['current'],10.59);self.assertTrue(b['paused']);self.assertGreaterEqual(b['current'],14.839);self.assertLess(b['current'],15.239);self.assertEqual(a['src'],b['src']);self.assertEqual(25.875,a['duration']);self.assertIn('0:09.59–0:14.84',self.c['complete']['passages'][0].replace('\n',''))
 def test_recurring_positive(self):
  self.assertEqual(6,self.c['complete']['replayCount']);self.assertEqual(6,len(self.c['occurrences']));starts=[9.59,15.5,17.5,19,21,23.5]
  for row,start in zip(self.c['occurrences'],starts):self.assertGreaterEqual(row['audio']['current'],start);self.assertLess(row['audio']['current'],start+1);self.assertFalse(row['audio']['paused']);self.assertEqual(self.c['replayStart']['audio']['src'],row['audio']['src'])
  self.assertIn('This pattern is scored once.',self.c['complete']['main']);self.assertIn('Found 1 of 2 mistakes',self.c['complete']['summary'])
 def test_autoplay_negative(self):
  for key in ['complete','noAutoplayExpanded','returned']:self.assertTrue(self.c[key]['audio']['paused']);self.assertEqual(0,self.c[key]['audio']['current'])
 def test_audio_failure_negative(self):
  a,b=self.c['mediaFailure'],self.c['mediaRecovery'];self.assertTrue(any('Saved audio is temporarily unavailable' in x for x in a['alerts']));self.assertEqual(self.n['answer_text'],a['answer']);self.assertEqual('Primary score: 60.0 / 100',a['score']);self.assertEqual(6,a['replayCount']);self.assertNotIn('private backend detail',a['main']);self.assertEqual([],b['alerts']);self.assertFalse(b['audio']['paused']);self.assertGreaterEqual(b['audio']['current'],15.5);self.assertEqual(a['audio']['src'].split('?')[0],b['audio']['src'].split('?')[0]);self.assertIn('playback_revision=1',b['audio']['src'])
 def test_range_stop_positive(self):
  b=self.c['secondEnd']['audio'];self.assertTrue(b['paused']);self.assertGreaterEqual(b['current'],16.5);self.assertLess(b['current'],16.9);self.assertTrue(self.c['replacedEnd']['audio']['paused']);self.assertGreaterEqual(self.c['replacedEnd']['audio']['current'],24.5);self.assertLess(self.c['replacedEnd']['audio']['current'],24.9)
 def test_range_interrupt_negative(self):
  a,b=self.c['manualSeek']['audio'],self.c['manualAfter']['audio'];self.assertEqual(0,a['current']);self.assertFalse(a['paused']);self.assertGreater(b['current'],14.839);self.assertFalse(b['paused']);self.assertGreaterEqual(self.c['replacedStart']['audio']['current'],23.5);self.assertFalse(self.c['replacedStart']['audio']['paused']);self.assertIn('Passage timing unavailable. Use the full recording above.',self.c['complete']['main'])
 def test_results_recovery_positive(self):
  a,b=self.c['resultsFailure'],self.c['resultsRecovery'];self.assertIn('Your answer is saved. Findings are temporarily unavailable. Refresh to retry.',a['alerts']);self.assertEqual(a['score'],b['score']);self.assertEqual(a['answer'],b['answer']);self.assertEqual(6,a['replayCount']);self.assertEqual([],b['alerts']);self.assertNotIn('private backend detail',a['main'])
 def test_navigation_keyboard_positive(self):
  k=self.c['keyboard'];self.assertEqual('3px',k['outline']);self.assertGreater(k['top'],0);self.assertLessEqual(k['bottom'],k['height']);self.assertEqual(['true','false'],[self.c['navigationOpen'],self.c['navigationClosed']]);self.assertEqual('Prepare an exercise',self.c['nextPracticeHeading']);self.assertIn({'text':'Optional reconsideration and history','href':'/reviews?attempt='+self.n['attempt_id']},self.c['complete']['links'])
 def test_layout_positive(self):
  rows=self.c['layouts'];self.assertEqual(12,len(rows));self.assertEqual({(s,w) for s in ['completed','uncertain','draft','checking'] for w in [1280,390,320]},{(x['state'],x['width']) for x in rows})
  for x in rows:
   self.assertEqual(['17px','24.65px'],[x['bodySize'],x['bodyLine']]);self.assertTrue(x['sourceSans']);self.assertEqual('loaded',x['fonts']);self.assertFalse(x['overflow']);self.assertIn('Source Sans 3',x['font'])
   for b in x['buttons']:self.assertGreaterEqual(b['height'],44);self.assertGreaterEqual(float(b['font'].removesuffix('px')),13)
 def test_score_group_positive(self):
  rows=self.c['scoreGroups'];self.assertEqual({'completed','maximum','unavailable'},{x['state'] for x in rows})
  for row in rows:
   self.assertFalse(row['overflow'])
   if row['state']=='unavailable':self.assertEqual('Primary score: not applicable',row['score']);self.assertIsNone(row['value'])
   else:
    v=row['value'];self.assertEqual('nowrap',v['whiteSpace']);self.assertLessEqual(v['width'],v['parentWidth']);self.assertLessEqual(v['height'],float(v['line'].removesuffix('px'))+1);self.assertEqual('100.0 / 100' if row['state']=='maximum' else '60.0 / 100',v['text'])
 def test_zero_dispatch_negative(self):
  actions=[x for x in self.events if x['event']=='request' and x['method']!='GET'];writes=[x for x in actions if not x['path'].endswith('/playback')];self.assertEqual(['PUT','POST'],[x['method'] for x in writes]);self.assertEqual([self.n['results_path'].removesuffix('/results')+'/answer',self.n['results_path'].removesuffix('/results')+':submit'],[x['path'] for x in writes]);self.assertTrue(all(x['path'].endswith(('/playback','/answer',':submit')) for x in actions));self.assertFalse(any(x['event']=='fixture_error' for x in self.events))
  events=[x['body'] for x in self.events if x['event']=='body' and x['path'].endswith('/playback')];self.assertTrue({'play','pause','seek'}<={x['kind'] for x in events});self.assertEqual({self.n['attempt_id']},{x['attempt_id'] for x in events})
 def packet(self):return json.loads((AUDIT/'REVIEW.json').read_text())
 def errors(self,p,facts=None,native=None):return review.review_errors(p,facts or self.facts,native or self.n)
 def test_review_positive(self):self.assertEqual([],self.errors(self.packet()))
 def test_ux_omission_negative(self):
  p=self.packet();p.pop('ui_ux');self.assertTrue(self.errors(p));p=self.packet();p['ui_ux']={'observations':['build and screenshots'],'references':['data/iteration-20-results-replay-20261026/web-build.log']};self.assertTrue(self.errors(p))
 def test_typography_omission_negative(self):
  p=self.packet();p.pop('typography');self.assertTrue(self.errors(p));f=copy.deepcopy(self.facts);f['cases']['layouts'][0]['bodySize']='10px';self.assertTrue(self.errors(self.packet(),facts=f));f=copy.deepcopy(self.facts);f['cases']['layouts'][0]['overflow']=True;self.assertTrue(self.errors(self.packet(),facts=f))
 def test_evidence_mismatch_negative(self):
  n=copy.deepcopy(self.n);n['attempt_id']='other-attempt';self.assertTrue(self.errors(self.packet(),native=n))
  for name,value in [('unexecuted_cases',['planned']),('reference_origin','candidate gold'),('new_model_calls',50),('performance_campaigns','required')]:p=self.packet();p[name]=value;self.assertTrue(self.errors(p))
if __name__=='__main__':unittest.main(verbosity=2)
