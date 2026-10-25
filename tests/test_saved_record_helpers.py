"""Literal JS presentation expectations; no IO/retry/LLM is owned here."""
import json, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class SavedRecordHelpers(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=subprocess.run([str(NODE),'--input-type=module','-e',"""
   import {recordTitle,needsRecordIdentity} from './services/web/app/savedRecord.js';
   import {failureMessage} from './services/web/app/prepare/failureMessage.js';
   const a={id:'12345678-0000-4000-8000-000000000001',exercise_title:'Picnic',started_at:'2026-10-25T12:30:00Z'};
   const b={...a,id:'12345678-0000-4000-8000-000000000002'};
   const rows=[a,b,{...a,id:'other',exercise_title:'Insurance'}];
   const msg=(phase,code,retryable=true)=>failureMessage({phase_states:{[phase]:'failed'},last_failure:code?{code,retryable,message:'private backend detail'}:null});
   console.log(JSON.stringify({collisions:rows.map(x=>needsRecordIdentity(x,rows,'started_at')),one:needsRecordIdentity(a,[a],'started_at'),different:needsRecordIdentity(a,[a,{...b,started_at:'2026-10-26T12:30:00Z'}],'started_at'),legacy:needsRecordIdentity({id:'a'},[{id:'a'},{id:'b'}],'created_at'),titles:[recordTitle({title:'Library title'}),recordTitle({exercise_title:'Heard',title:'Later'}),recordTitle({id:'a'})],messages:[msg('mutation','DEADLINE_EXCEEDED'),msg('canonical_text','PROVIDER_FAILURE'),msg('render','MISSING_CREDENTIALS',false),msg('mutation',null),msg('render','UNKNOWN',false)],cleared:[failureMessage({audio_available:true,last_failure:{code:'PROVIDER_FAILURE'}}),failureMessage({phase_states:{render:'complete'},last_failure:{code:'PROVIDER_FAILURE'}}),failureMessage({})]}));
  """],cwd=ROOT,capture_output=True,text=True,timeout=15)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_collision_positive(self):self.assertEqual([True,True,False],self.v['collisions']);self.assertTrue(self.v['legacy'])
 def test_distinct_negative(self):self.assertFalse(self.v['one']);self.assertFalse(self.v['different'])
 def test_original_title_positive(self):self.assertEqual(['Library title','Heard','Untitled exercise'],self.v['titles'])
 def test_phase_positive(self):
  for message,prefix in zip(self.v['messages'],['Mistakes:','Clean text:','Audio:','Mistakes:','Audio:']):self.assertTrue(message.startswith(prefix));self.assertIn('retained',message);self.assertNotIn('private backend',message)
 def test_credential_positive(self):self.assertIn('credential in Settings',self.v['messages'][2]);self.assertIn('Check Settings',self.v['messages'][2])
 def test_unknown_negative(self):self.assertIn('did not complete',self.v['messages'][3]);self.assertIn('Check the request',self.v['messages'][4])
 def test_stale_negative(self):self.assertEqual(['','',''],self.v['cleared'])
if __name__=='__main__':unittest.main(verbosity=2)
