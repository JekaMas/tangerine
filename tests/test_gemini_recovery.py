"""Production message owners with literal errors, not hosted qualification."""
import json, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'

class GeminiRecovery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script=r'''
  import {preparationResponse} from './services/web/app/prepare/response.js';
  import {failureMessage} from './services/web/app/prepare/failureMessage.js';
  import {requestError} from './services/web/app/requestError.js';
  const rows={};
  for(const code of ['MISSING_CREDENTIAL','MISSING_CREDENTIALS','CONSTRAINT_CONFLICT','LOCAL_BUDGET_EXCEEDED','PROVIDER_FAILURE','UNKNOWN']){
    let immediate;
    try{await preparationResponse(new Response(JSON.stringify({code,message:'private SQL password=secret'}),{status:503}));}catch(e){immediate=requestError(e);}
    const base={phase_states:{canonical_text:'complete',mutation:'failed',render:'not_started'},last_failure:{code,message:'private traceback',retryable:true}};
    rows[code]={immediate,saved:failureMessage(base),complete:failureMessage({...base,audio_available:true})};
  }
  console.log(JSON.stringify(rows));
  '''
  r=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=15)
  if r.returncode:raise AssertionError(r.stderr)
  cls.rows=json.loads(r.stdout)
 def test_credentials_actionable_positive(self):
  for code in ['MISSING_CREDENTIAL','MISSING_CREDENTIALS']:
   self.assertIn('Settings',self.rows[code]['immediate'])
   self.assertIn('credential',self.rows[code]['saved'])
 def test_access_actionable_positive(self):
  for key in ['immediate','saved']:
   self.assertIn('Settings',self.rows['CONSTRAINT_CONFLICT'][key])
   self.assertNotIn('When the service is available',self.rows['CONSTRAINT_CONFLICT'][key])
 def test_allowance_no_purchase_positive(self):
  for key in ['immediate','saved']:
   self.assertIn('allowance',self.rows['LOCAL_BUDGET_EXCEEDED'][key])
   self.assertNotIn('Buy',self.rows['LOCAL_BUDGET_EXCEEDED'][key])
 def test_diagnostics_private_negative(self):
  for row in self.rows.values():
   for key in ['immediate','saved']:
    for secret in ['private','SQL','password','traceback']:
     self.assertNotIn(secret,row[key])
 def test_complete_unblocked_positive(self):
  self.assertTrue(all(row['complete']=='' for row in self.rows.values()))
 def test_transient_retains_resume_negative(self):
  self.assertIn('Saved text, mutations and completed audio pieces are retained',self.rows['PROVIDER_FAILURE']['saved'])
  self.assertIn('resume this exercise explicitly',self.rows['PROVIDER_FAILURE']['saved'])

if __name__=='__main__':unittest.main(verbosity=2)
