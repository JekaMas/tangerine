"""Independent expectations over actual shipped pure request code; no inference."""
from pathlib import Path
import json,subprocess,unittest
R=Path(__file__).resolve().parents[1];NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class RecurringRequest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
  import {blueprintRequest} from './services/web/app/prepare/request.js';
  const f={topic:'Travel',speakers:2,words:50,level:'B1',families:['grammar'],categories:[],severities:[],amount:'auto',mutationCount:'',voices:[],recurring:[{enabled:true,instruction:' Drop plural endings '},{enabled:true,percent:95,instruction:''}],advanced:''};
  const r=o=>blueprintRequest({...f,...o});let error='';try{r({amount:'exact',mutationCount:'1'})}catch(e){error=e.message}
  console.log(JSON.stringify({profiles:r({}),one:r({speakers:1}),restored:r({speakers:2}),disabled:r({recurring:[{enabled:false}]}),zero:r({amount:'exact',mutationCount:'0'}),low:r({amount:'low'}),advanced:r({advanced:JSON.stringify({exercise_request:{recurring_errors:[]}})}),error}));
  """
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=R,capture_output=True,text=True,timeout=15)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_profiles_positive(self):self.assertEqual(self.v['profiles']['exercise_request']['recurring_errors'],[{'speaker_number':1,'target_percent':85,'instruction':'Drop plural endings'},{'speaker_number':2,'target_percent':95,'instruction':None}])
 def test_retention_positive(self):self.assertEqual(len(self.v['one']['exercise_request']['recurring_errors']),1);self.assertEqual(self.v['restored']['exercise_request']['recurring_errors'][1]['target_percent'],95)
 def test_legacy_negative(self):self.assertNotIn('recurring_errors',self.v['disabled']['exercise_request']);self.assertIsNone(self.v['disabled']['exercise_request']['mutation_count'])
 def test_override_positive(self):self.assertEqual(self.v['advanced']['exercise_request']['recurring_errors'],[])
 def test_count_negative(self):self.assertIn('at least 2',self.v['error']);self.assertEqual(self.v['zero']['exercise_request']['mutation_count'],0);self.assertEqual(self.v['low']['exercise_request']['mutation_count'],2)
if __name__=='__main__':unittest.main()
