"""Literal expectations over actual controlled native and CUA observations.

The live Gemini qualification stays in test_completion_i23; these observations
prove terminal recovery and native/local resume only. No model is dispatched.
"""
import hashlib,json,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-23-verification-20261026'
def read(file):return json.loads((DATA/file).read_text())
def observations(file):return [json.loads(x) for x in (DATA/file).read_text().splitlines()]
def assert_pass(test,file,name):
 rows=observations(file)
 test.assertFalse(any(r.get('Action')=='fail' for r in rows))
 test.assertTrue(any(r.get('Action')=='pass' and r.get('Test')==name for r in rows),name)

class GeminiRecoveryEvidence(unittest.TestCase):
 def test_terminal_native_negative(self):
  for name in ['authentication','legacy_auth','payment','permission','legacy_permission','model','quota','unknown_client']:
   assert_pass(self,'green-provider.jsonl','TestGeminiTerminalRecoveryNegative/'+name)
  for name,want,calls in [('quota','LOCAL_BUDGET_EXCEEDED',1),('denied','CONSTRAINT_CONFLICT',1),('credentials','MISSING_CREDENTIALS',1),('unavailable','PROVIDER_FAILURE',2)]:
   row=read('controlled/error-'+name+'.json');self.assertEqual((want,calls),(row['code'],row['calls']))
   for field in ['canonical_asset_id','settings_asset_id']:
    self.assertIsNotNone(row['before'][field]);self.assertEqual(row['before'][field],row['after'][field])
   self.assertEqual('complete',row['after']['phase_states']['canonical_text']);self.assertEqual('failed',row['after']['phase_states']['mutation']);self.assertIsNone(row['after']['audio_asset_id'])
   assert_pass(self,'controlled/native.jsonl','TestNativeGeminiErrors/'+name)
 def test_transient_native_positive(self):
  assert_pass(self,'green-provider.jsonl','TestGeminiTransientRecoveryPositive')
  # The independent prior real503 and exact request retry remain valid.
  live=json.loads((ROOT/'data/iteration-23-gemini-20261026/live/dispatches.json').read_text())
  self.assertEqual([503,200],[x['http_status'] for x in live[1:3]])
  self.assertEqual(live[1]['request'],live[2]['request'])
 def test_browser_errors_positive(self):
  f=read('browser-facts.json');self.assertEqual('Keep my pending request',f['denial']['topic']);self.assertEqual('Keep my pending request',f['afterRefreshTopic']);self.assertFalse(f['denial']['disabled'])
  self.assertIn('Settings',f['credentials']);self.assertIn('allowance',f['allowance']);self.assertIn('Settings',f['reopenedFailure']);self.assertNotIn('When the service is available',f['reopenedFailure'])
  self.assertTrue(f['catalogueRecovered']);self.assertEqual(('true','false'),(f['menuOpen'],f['menuClosed']));self.assertEqual({'outline':'solid','tag':'BUTTON','text':'Refresh'},f['focus'])
 def test_browser_privacy_negative(self):
  f=read('browser-facts.json')
  for text in f['denial']['alerts']+[f['credentials'],f['allowance'],f['reopenedFailure']]:
   for forbidden in ['private','SQL','password','Buy credits','Traceback','PERMISSION_DENIED','CONSTRAINT_CONFLICT','MISSING_CREDENTIALS']:
    self.assertNotIn(forbidden,text)
  log=observations('requests.jsonl');self.assertFalse(any(x['event']=='forbidden_execution' for x in log))
  # Two terminal-message actions were controlled at HTTP only. Neither reached
  # native generation and neither was replayed by the browser's request owner.
  for scenario in ['credential-message','allowance-message']:
   posts=[x for x in log if x['event']=='request' and x['scenario']==scenario and x['method']=='POST']
   self.assertEqual(1,len(posts))
 def test_browser_resume_positive(self):
  before,after=read('browser/before.json'),read('browser/after.json')
  for field in ['id','canonical_asset_id','settings_asset_id']:
   self.assertEqual(before[field],after[field])
  self.assertEqual({'canonical_text':'complete','mutation':'complete','render':'complete'},after['phase_states']);self.assertIsNone(after['last_failure'])
  self.assertEqual(hashlib.sha256((DATA/'recovered.wav').read_bytes()).hexdigest(),after['audio_sha256'])
  f=read('browser-facts.json');self.assertFalse(f['playback']['paused']);self.assertGreater(f['playback']['currentTime'],0);self.assertEqual(28.875,f['playback']['duration'])
  with wave.open(str(DATA/'recovered.wav')) as a:self.assertEqual((1,24000,693000),(a.getnchannels(),a.getframerate(),a.getnframes()))
  d=read('browser/dispatches.json');self.assertEqual([('canonical',200),('mutation',403),('mutation',403),('mutation',200)],[(x['phase'],x['status']) for x in d])
  self.assertTrue(all(x['origin']=='controlled transport; no hosted dispatch' for x in d));self.assertEqual(d[1]['request']['model'],d[-1]['request']['model'])
  assert_pass(self,'browser/native.jsonl','TestNativeGeminiBrowserRecovery')
 def test_browser_reopen_positive(self):
  f=read('browser-facts.json');self.assertEqual(0,f['reopenedAlerts']);self.assertIn(read('browser/fixture.json')['preparation_id'],f['record'])
  for stage in ['Clean text','Mistakes','Audio']:self.assertIn(stage+'\ncomplete',f['reopened'])
  self.assertIn('4/4 audio pieces saved',f['reopened']);self.assertIn('Open the Library to listen and answer',f['reopened'])
 def test_layouts_positive(self):
  rows=read('layouts.json');self.assertEqual({1280,390,320},{r['width'] for r in rows})
  for r in rows:
   self.assertFalse(r['overflow']);self.assertFalse(r['resumeDisabled']);self.assertEqual(('17px','24.65px',True),(r['body'],r['lineHeight'],r['loaded']))
   self.assertTrue(all(float(a['size'].removesuffix('px'))>=14 for a in r['alerts']))

if __name__=='__main__':unittest.main(verbosity=2)
