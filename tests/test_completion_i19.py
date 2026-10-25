"""Literal I19 oracles over actual native storage and source-built CUA receipts.

External model/speech outputs are constructed transport packets. These tests
reuse the retained interaction without dispatching another provider operation.
"""
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-19-saved-records-20261026'
AUDIT=ROOT/'audit/iteration-19-saved-records-20261026'
spec=importlib.util.spec_from_file_location('i19_review',AUDIT/'review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
class CompletionI19(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.o=json.loads((DATA/'observations.json').read_text());cls.c=cls.o['cases']
  cls.n=json.loads((DATA/'native-before.json').read_text());cls.a=json.loads((DATA/'native-after.json').read_text())
  cls.events=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]
 def article(self,view,title):return next(r for r in self.c[view]['articles'] if r['title']==title)
 def test_failure_positive(self):
  for view in ['nativeFailures','refreshedFailures']:
   self.assertIn('Mistakes: Generation reached its time limit.',self.article(view,'Picnic')['text'])
   self.assertIn('Clean text: The selected provider could not complete',self.article(view,'Insurance')['text'])
   self.assertIn('1/2 audio pieces saved',self.article(view,'Café opening')['text'])
   for r in self.c[view]['articles']:self.assertIn('retained',r['text']);self.assertIn('resume this exercise explicitly',r['text']);self.assertNotIn('service_unavailable',r['text'])
 def test_recovery_positive(self):
  self.assertEqual(self.n['first_piece_asset'],self.a['first_piece_asset'])
  self.assertEqual([2,3],[self.n['speech_dispatches_before'],self.a['speech_dispatches_after']])
  self.assertTrue(self.a['preparation']['audio_available']);self.assertIsNone(self.a['preparation']['last_failure'])
  for view in ['resumed','resumedReload']:
   r=self.article(view,'Café opening');self.assertEqual([],r['alerts']);self.assertIn('Audio\ncomplete',r['text']);self.assertIn('2/2 audio pieces saved',r['text'])
  d=DATA/'harness-fixed';b=json.loads((d/'native-before.json').read_text());a=json.loads((d/'native-after.json').read_text())
  passes={e.get('Test') for e in map(json.loads,(d/'native.jsonl').read_text().splitlines()) if e['Action']=='pass'};self.assertIn('TestI19HistoryBrowserFixture',passes)
  self.assertEqual(b['first_piece_asset'],a['first_piece_asset']);self.assertEqual([2,3],[b['speech_dispatches_before'],a['speech_dispatches_after']]);self.assertTrue(a['preparation']['audio_available'])
  ui=json.loads((d/'ui-complete.json').read_text());self.assertIn('2/2 audio pieces saved',ui['text']);self.assertEqual([],ui['alerts'])
  posts=[e for e in self.events if e['method']=='POST'];self.assertEqual(1,len(posts));self.assertEqual('/api/v1/preparations/'+self.n['ids']['resume']+':resume',posts[0]['path'])
 def test_empty_reason_negative(self):
  rows=next(r for r in self.c['widths'] if r['route']=='audio' and r['width']==320)['articles']
  for row in rows:
   self.assertTrue(row['alerts']);self.assertIn('Mistakes: This preparation did not complete.',row['text']);self.assertNotIn('private backend detail',row['text'])
  self.assertIn('Check the request and Settings before trying again.',rows[0]['text'])
 def test_read_only_negative(self):
  self.assertTrue(self.events)
  self.assertFalse(any(e['method']!='GET' and not (e['method']=='POST' and e['scenario']=='explicit-resume' and e['path'].endswith(':resume')) for e in self.events))
  row=self.article('nativeAudio','Café opening');self.assertEqual([],row['alerts']);self.assertNotIn('could not complete',row['text']);self.assertTrue(all(x['paused'] for x in self.c['nativeAudio']['audio']))
 def test_records_positive(self):
  rows=self.c['nativeAttempts']['articles'];self.assertEqual(['Insurance','Picnic','Picnic'],[r['title'] for r in rows])
  self.assertEqual(['Draft','Completed','Draft'],[[x.strip() for x in r['text'].splitlines() if x.strip()][1].split(' · ')[0] for r in rows])
  self.assertEqual({f'/listen?attempt={i}' for i in self.n['ids']['attempts']},{r['links'][0]['href'] for r in rows})
  self.assertEqual('/listen?attempt='+self.n['ids']['attempts'][0],self.c['openedNative']['url']);self.assertEqual('A'*170,self.c['openedAnswer']);self.assertIn('Picnic. Identify',self.c['openedNative']['main'])
 def test_legacy_positive(self):
  rows=self.c['legacyAttempts']['articles'];self.assertEqual('Untitled exercise',rows[2]['title']);self.assertIsNone(rows[2]['excerpt'])
  audio=next(r for r in self.c['widths'] if r['route']=='audio' and r['width']==320)
  self.assertIn('Date unavailable',audio['main']);self.assertTrue(audio['articles'][2]['title'].startswith('A very long exercise topic'))
  for r in rows:self.assertTrue(r['links'][0]['href'].startswith('/listen?attempt=12345678-1111-4111-8111-'))
 def test_same_title_negative(self):
  base=json.loads((DATA/'baseline-observations.json').read_text())
  self.assertEqual(base['attempts'][0],base['attempts'][1])
  for route in ['attempts','audio','prepare','reviews']:
   row=next(r for r in self.c['widths'] if r['route']==route and r['width']==320)
   records=row['reviews'] if route=='reviews' else row['articles']
   identities=[r['identity'] for r in records[:2]]
   self.assertEqual(['Record: 12345678-1111-4111-8111-000000000001','Record: 12345678-1111-4111-8111-000000000002'],identities)
   self.assertNotEqual(*identities)
 def test_narrow_metadata_negative(self):
  self.assertEqual(12,len(self.c['widths']))
  for row in self.c['widths']:self.assertEqual([],review.readability_errors(row));self.assertIn('Source Sans 3',row['body']['font'])
  for prefix in ['attempt','audio','prepare']:
   a,b=self.c[prefix+'ListFailure'],self.c[prefix+'ListRecovery'];self.assertTrue(a['alerts']);self.assertFalse(a['overflow']);self.assertEqual([r['title'] for r in a['articles']],[r['title'] for r in b['articles']]);self.assertNotIn('private backend detail',a['main']);self.assertNotIn('TEST_LIST_FAILURE',a['main'])
   self.assertNotIn('unavailable. Refresh to retry.',b['main'])
  self.assertEqual(['My retained picnic request.']*2,[self.c['retainedTopicFailure'],self.c['retainedTopicRecovery']])
 def test_list_projection_positive(self):
  n=self.n;ids=n['ids'];a=next(a for a in n['attempts'] if a['id']==ids['attempts'][0]);self.assertEqual('Picnic',a['exercise_title']);self.assertEqual('A'*160+'…',a['answer_excerpt']);self.assertEqual('2026-10-25T12:30:00Z',a['started_at'])
  for item in n['preparations']['items']:
   if item['id'] in ids['failures']:self.assertEqual('2026-10-25T12:30:00Z',item['created_at'])
  for item in n['library']:self.assertEqual('2026-10-25T12:30:00Z',item['created_at'])
  self.assertEqual('Changed',next(x for x in n['library'] if x['id']==ids['picnic'])['title'])
  for rows in [n['attempts'],n['library'],n['preparations']['items']]:
   for row in rows:self.assertFalse({'canonical_text','surface_text','units','mutation_manifest','answer_key','settings_asset_id'}&row.keys())
  passes={e.get('Test') for e in map(json.loads,(DATA/'native.jsonl').read_text().splitlines()) if e['Action']=='pass'}
  self.assertTrue({'TestI19HistoryBrowserFixture/NativeProjection','TestI19HistoryBrowserFixture/NativePagination'}<=passes)
  readback={e.get('Test') for e in map(json.loads,(DATA/'persisted-readback.jsonl').read_text().splitlines()) if e['Action']=='pass'};self.assertIn('TestI19HistoryPersistedReadback',readback)
 def test_legacy_projection_negative(self):
  rows=self.c['legacyPagination']['articles'];self.assertEqual(4,len(rows));self.assertEqual(4,len({r['links'][0]['href'] for r in rows}));self.assertEqual('Insurance',rows[-1]['title'])
  self.assertTrue(any('cursor=legacy-next' in e.get('query','') for e in self.events))
  self.assertIn('Date unavailable',next(r for r in self.c['widths'] if r['route']=='reviews')['main'])
 def test_review_retained_positive(self):
  self.assertTrue(self.c['reviewFailure']['alerts']);self.assertEqual(self.c['nativeReview']['reviews'],self.c['reviewFailure']['reviews']);self.assertEqual(self.c['reviewFailure']['reviews'],self.c['reviewRecovery']['reviews']);self.assertEqual([],self.c['reviewRecovery']['alerts'])
  ids={x['href'] for x in self.c['nativeReview']['reviews']};self.assertIn(self.c['selectedReview']['url'],ids)
  self.assertIn('No exercises yet',self.c['emptyReview']['main']);self.assertIn('Exercises are unavailable',self.c['initialReviewFailure']['main']);self.assertNotIn('No exercises yet',self.c['initialReviewFailure']['main']);self.assertEqual(2,len(self.c['initialReviewRecovery']['reviews']))
 def test_keyboard_positive(self):
  for r in self.c['keyboard']:self.assertEqual('3px',r['outline']);self.assertGreater(r['top'],r['header']);self.assertLess(r['bottom'],r['height']+1)
  self.assertIn('Attempt: 12345678-1111-4111-8111-000000000001',self.c['detailsExpanded']['main']);self.assertIn('/cleanup?subject=12345678-1111-4111-8111-000000000001',[x['href'] for x in self.c['detailsExpanded']['articles'][0]['links']])
 def test_restart_sibling_positive(self):
  passes={e.get('Test') for e in map(json.loads,(DATA/'restart-sibling.jsonl').read_text().splitlines()) if e['Action']=='pass'};self.assertIn('TestNativeSpeechRestartPositive',passes)
 def test_bounded_retry_negative(self):
  for scenario in ['review-failure-final','legacy-attempt-list-failed','legacy-audio-list-failed','legacy-prepare-list-failed','initial-review-failure']:
   rows=[e for e in self.events if e['scenario']==scenario];self.assertEqual([1,2,3],[r['occurrence'] for r in rows]);self.assertTrue(all(e['method']=='GET' for e in rows))
 def packet(self):return json.loads((AUDIT/'REVIEW.json').read_text())
 def errors(self,p,o=None,n=None):return review.review_errors(p,o or self.o,n or self.n)
 def test_review_positive(self):self.assertEqual([],self.errors(self.packet()))
 def test_ux_omission_negative(self):
  p=self.packet();p.pop('ui_ux');self.assertTrue(self.errors(p));p=self.packet();p['ui_ux']={'observations':[],'references':['data/iteration-19-saved-records-20261026/web-build-final.log']};self.assertTrue(self.errors(p))
 def test_typography_omission_negative(self):
  p=self.packet();p.pop('typography');self.assertTrue(self.errors(p));o=copy.deepcopy(self.o);o['cases']['widths'][0]['identityType'][0]['size']='10px';self.assertTrue(self.errors(self.packet(),o=o))
 def test_evidence_mismatch_negative(self):
  n=copy.deepcopy(self.n);n['ids']['attempts'][0]='wrong-record';self.assertTrue(self.errors(self.packet(),n=n))
  for field,value in [('unexecuted_cases',['planned']),('reference_origin','candidate-generated gold'),('new_model_calls',50),('performance_campaigns','required')]:p=self.packet();p[field]=value;self.assertTrue(self.errors(p))
if __name__=='__main__':unittest.main(verbosity=2)
