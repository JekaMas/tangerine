"""Fixed speech failures and recoverable siblings through shared UI owners."""
from pathlib import Path
import json,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class OverlapRecovery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
  import {fixedSpeechFailure,failureMessage} from './services/web/app/prepare/failureMessage.js';
  import {preparationResponse} from './services/web/app/prepare/response.js';
  import {requestError} from './services/web/app/requestError.js';
  const rows={};
  for(const [kind,code,retryable] of [['clip','PROVIDER_OUTPUT_INVALID',false],['timing','CAPABILITY_UNQUALIFIED',false],['temporary','INFRASTRUCTURE_UNAVAILABLE',true],['cancelled','DEADLINE_EXCEEDED',true],['credential','MISSING_CREDENTIALS',false]]){
    const preparation={phase_states:{canonical_text:'complete',mutation:'complete',render:'failed'},last_failure:{code,retryable,message:'PRIVATE_NATIVE_CANARY'}};
    let immediate='';try{await preparationResponse(new Response(JSON.stringify({code,preparation,message:'PRIVATE_NATIVE_CANARY'}),{status:422}));}catch(e){immediate=requestError(e);}
    rows[kind]={fixed:fixedSpeechFailure(preparation),saved:failureMessage(preparation),immediate,complete:failureMessage({...preparation,audio_available:true})};
  }
  rows.canonical=fixedSpeechFailure({phase_states:{canonical_text:'failed',render:'not_started'},last_failure:{code:'PROVIDER_OUTPUT_INVALID',retryable:false}});
  console.log(JSON.stringify(rows));
  """
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=15)
  if p.returncode:raise AssertionError(p.stderr)
  cls.rows=json.loads(p.stdout)
 def test_fixed_settings_positive(self):
  expected='Audio: This recording cannot be completed with its saved speech settings. Saved text, mutations and completed audio pieces are retained. Prepare a new exercise with a compatible voice or different speech settings. Saved preparations keep their original settings.'
  for kind in ['clip','timing']:self.assertTrue(self.rows[kind]['fixed']);self.assertEqual(self.rows[kind]['saved'],expected)
 def test_immediate_saved_agree_positive(self):
  for kind in ['clip','timing']:self.assertEqual(self.rows[kind]['saved'],self.rows[kind]['immediate'])
 def test_transient_resume_positive(self):
  for kind in ['temporary','cancelled']:self.assertFalse(self.rows[kind]['fixed']);self.assertIn('resume this exercise explicitly',self.rows[kind]['saved'])
 def test_credential_not_blocked_negative(self):
  self.assertFalse(self.rows['credential']['fixed']);self.assertIn('Check Settings, then resume',self.rows['credential']['saved']);self.assertFalse(self.rows['canonical'])
 def test_backend_details_negative(self):
  for kind in ['clip','timing','temporary','cancelled','credential']:
   self.assertNotIn('PRIVATE_NATIVE_CANARY',self.rows[kind]['saved']);self.assertNotIn('PRIVATE_NATIVE_CANARY',self.rows[kind]['immediate']);self.assertEqual(self.rows[kind]['complete'],'')
if __name__=='__main__':unittest.main(verbosity=2)
