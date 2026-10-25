"""Current source-built CUA regressions with retained native storage evidence.

List transport outcomes, ordering holds and explicit action responses are
controlled. Native/model/media quality is not established by this fixture.
"""
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-19-verification-20261026';AUDIT=ROOT/'audit/iteration-19-verification-20261026'
s=importlib.util.spec_from_file_location('i19_verify_review',AUDIT/'review.py');review=importlib.util.module_from_spec(s);s.loader.exec_module(review)
ROUTES={'attempts','audio','prepare','reviews'}
class Iteration19Verify(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.o=json.loads((DATA/'observations.json').read_text());cls.c=cls.o['cases'];cls.base=json.loads((DATA/'baseline.json').read_text());cls.n=json.loads((ROOT/'data/iteration-19-saved-records-20261026/native-before.json').read_text());cls.events=[json.loads(l) for l in (DATA/'requests.jsonl').read_text().splitlines()]
 def test_initial_loading_positive(self):
  self.assertEqual(ROUTES,{x['route'] for x in self.c['initial']})
  for x in self.c['initial']:
   self.assertTrue(x['unread']['statuses']);self.assertEqual([],x['unread']['titles']);self.assertNotIn('No saved preparations yet',x['unread']['main']);self.assertNotIn('No attempts yet',x['unread']['main']);self.assertNotIn('No exercises yet',x['unread']['main'])
  self.assertIn('No saved preparations yet',self.base['audioUnread']['main']);self.assertIn('No saved preparations yet',self.base['prepareUnread']['main'])
 def test_initial_failure_negative(self):
  for x in self.c['initial']:
   self.assertTrue(x['failed']['alerts']);self.assertEqual([],x['failed']['titles']);self.assertNotIn('No saved preparations yet',x['failed']['main']);self.assertNotIn('No attempts yet',x['failed']['main']);self.assertNotIn('No exercises yet',x['failed']['main']);self.assertEqual(3,len(x['recovered']['titles']))
  r=self.c['audioFailed'];self.assertNotIn('No saved preparations yet',r['main']);self.assertIn('Saved audio is unavailable. Refresh to retry.',r['main'])
  events=[e for e in self.events if e['scenario']=='repaired-audio-unread' and e['event']=='request'];self.assertEqual([1,2,3],[e['ordinal'] for e in events])
 def test_empty_positive(self):
  self.assertEqual(ROUTES,{x['route'] for x in self.c['empty']})
  for x in self.c['empty']:
   self.assertEqual([],x['titles']);self.assertEqual([],x['statuses']);self.assertEqual([],x['alerts']);self.assertIn({'attempts':'No attempts yet','audio':'No saved preparations yet','prepare':'No saved preparations yet','reviews':'No exercises yet'}[x['route']],x['main'])
 def test_latest_read_positive(self):
  self.assertEqual(['Latest saved snapshot']*3,self.base['newerBeforeRelease']['titles']);self.assertEqual(['Earlier saved snapshot']*3,self.base['obsoleteAfterRelease']['titles'])
  self.assertEqual(ROUTES,{x['route'] for x in self.c['order']})
  for x in self.c['order']:
   self.assertTrue(x['pending']['statuses']);self.assertEqual(['Latest saved snapshot']*3,x['before']['titles']);self.assertEqual(['Latest saved snapshot']*3,x['after']['titles']);self.assertEqual([],x['after']['statuses'])
   events=[e['ordinal'] for e in self.events if e['scenario']=='repaired-order-'+x['route'] and e['event']=='response'];self.assertLess(events.index(3),events.index(2))
 def test_obsolete_failure_negative(self):
  self.assertEqual(ROUTES,{x['route'] for x in self.c['obsoleteError']})
  for x in self.c['obsoleteError']:
   self.assertEqual(['Latest saved snapshot']*3,x['titles']);self.assertNotIn('Refresh to retry.',x['main']);self.assertNotIn('Retry when the local service',x['main']);self.assertEqual([],x['statuses'])
 def test_latest_failure_negative(self):
  row=self.c['latestError'];self.assertEqual(['Insurance','Picnic','Café opening'],row['titles']);self.assertIn('Saved audio is unavailable. Refresh to retry.',row['main']);self.assertNotIn('Earlier saved snapshot',row['main'])
 def test_retention_recovery_positive(self):
  self.assertEqual(ROUTES,{x['route'] for x in self.c['retention']})
  for x in self.c['retention']:
   self.assertEqual(x['before']['titles'],x['failed']['titles']);self.assertEqual(x['before']['links'],x['failed']['links']);self.assertEqual(x['before']['titles'],x['recovered']['titles']);self.assertIn('unavailable',x['failed']['main']);self.assertNotIn('Saved audio is unavailable',x['recovered']['main']);self.assertNotIn('Saved attempts are unavailable',x['recovered']['main']);self.assertNotIn('Saved preparations are unavailable',x['recovered']['main']);self.assertNotIn('Exercises are unavailable',x['recovered']['main'])
 def test_pagination_positive(self):
  self.assertEqual({'attempts','audio','prepare'},{x['route'] for x in self.c['pagination']})
  for x in self.c['pagination']:
   self.assertEqual(1,len(x['before']['titles']));self.assertEqual(2,len(x['after']['titles']));self.assertEqual(0,x['more']);events=[e for e in self.events if e['scenario']=='pagination-'+x['route'] and e['event']=='request'];self.assertIn('cursor=page-two',events[-1]['query'])
 def test_action_independent_positive(self):
  self.assertTrue(self.c['generateEnabledDuringFailure']);self.assertEqual('Synthetic retained picnic request.',self.c['retainedTopic']);posts=[e for e in self.events if e['scenario']=='retained-error-prepare' and e['event']=='body'];self.assertEqual(1,len(posts));self.assertEqual('/api/v1/blueprints',posts[0]['path']);self.assertEqual('Synthetic retained picnic request.',posts[0]['body']['exercise_request']['topic']);self.assertNotIn('private backend detail',self.c['independentGeneration']['main'])
 def test_unreadable_negative(self):
  self.assertEqual(['Saved attempts are unavailable. Refresh to retry.'],self.c['unreadable']['alerts']);self.assertNotIn('private backend detail',self.c['unreadable']['main']);self.assertEqual([],self.c['unreadableRecovery']['alerts']);self.assertEqual(3,len(self.c['unreadableRecovery']['titles']));self.assertTrue(any('Tangerine display recovery' in x['message'] for x in self.c['console']));self.assertFalse(any('private backend detail' in x['message'] for x in self.c['console']))
 def test_layout_positive(self):
  self.assertEqual(12,len(self.c['layout']));self.assertEqual({'fonts':'loaded','sourceSans':True},self.c['fonts'])
  for row in self.c['layout']:
   self.assertEqual([],review.readability(row));self.assertIn('Source Sans 3',row['font']);self.assertEqual('24.65px',row['bodyLine']);self.assertEqual(['14px','14px'],[x['size'] for x in row['identities']]);self.assertNotEqual(*[x['text'] for x in row['identities']])
   for t in row['recordTitles']:self.assertLessEqual(t['scroll'],t['width']+1)
 def test_keyboard_positive(self):
  self.assertEqual(4,len(self.c['keyboard']))
  for x in self.c['keyboard']:self.assertEqual('3px',x['outline']);self.assertGreater(x['top'],0);self.assertLessEqual(x['bottom'],x['height']+1)
  self.assertTrue(self.c['navigationOpen']);self.assertTrue(self.c['navigationClosed']);self.assertIn('Attempt: '+self.n['ids']['attempts'][2],self.c['details']['main'])
 def test_resume_readback_positive(self):
  for row in [self.c['resume'],self.c['resumeReload']]:self.assertIn('Audio\ncomplete',row['main']);self.assertIn('2/2 audio pieces saved',row['main']);self.assertNotIn('Audio: The selected included',row['main'])
  rows=[e for e in self.events if e['scenario']=='controlled-resume-ui' and e['event']=='request' and e['method']=='POST'];self.assertEqual(1,len(rows));self.assertEqual('/api/v1/preparations/'+self.n['ids']['resume']+':resume',rows[0]['path'])
 def test_zero_dispatch_negative(self):
  posts=[e for e in self.events if e['event']=='request' and e['method']!='GET'];self.assertEqual(2,len(posts));self.assertEqual({'retained-error-prepare','controlled-resume-ui'},{e['scenario'] for e in posts});self.assertFalse(any(e['method']!='POST' for e in posts))
 def packet(self):return json.loads((AUDIT/'REVIEW.json').read_text())
 def errors(self,p,facts=None,native=None):return review.review_errors(p,facts or self.o,native or self.n)
 def test_review_positive(self):self.assertEqual([],self.errors(self.packet()))
 def test_ux_omission_negative(self):
  p=self.packet();p.pop('ui_ux');self.assertTrue(self.errors(p));p=self.packet();p['ui_ux']={'observations':['Build and screenshots passed'],'references':['data/iteration-19-verification-20261026/web-build-final.log']};self.assertTrue(self.errors(p))
 def test_typography_omission_negative(self):
  p=self.packet();p.pop('typography');self.assertTrue(self.errors(p));f=copy.deepcopy(self.o);f['cases']['layout'][0]['identities'][0]['size']='10px';self.assertTrue(self.errors(self.packet(),facts=f));f=copy.deepcopy(self.o);f['cases']['layout'][0]['overflow']=True;self.assertTrue(self.errors(self.packet(),facts=f))
 def test_evidence_mismatch_negative(self):
  n=copy.deepcopy(self.n);n['ids']['attempts'][0]='wrong-record';self.assertTrue(self.errors(self.packet(),native=n))
  for field,value in [('unexecuted_cases',['planned']),('reference_origin','candidate-generated gold'),('new_model_calls',50),('performance_campaigns','required')]:p=self.packet();p[field]=value;self.assertTrue(self.errors(p))
if __name__=='__main__':unittest.main(verbosity=2)
