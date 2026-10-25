"""Literal expectations over the shipped pure form request; zero inference."""
from pathlib import Path
import json,subprocess,unittest
R=Path(__file__).resolve().parents[1];NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class AccentRequest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
  import {blueprintRequest} from './services/web/app/prepare/request.js';
  const f={topic:'Travel',speakers:2,words:70,level:'B1',families:['lexis'],categories:[],severities:[],amount:'exact',mutationCount:'2',voices:['melo_en_au','melo_en_in'],advanced:''};
  const req=over=>blueprintRequest({...f,...over});
  console.log(JSON.stringify({pair:req({}),one:req({speakers:1}),restored:req({speakers:2}),three:req({speakers:3}),automatic:req({voices:['','']}),advanced:req({advanced:JSON.stringify({speakers:[{id:'custom',voice_profile_id:'bf_emma'}],exercise_request:{speaker_count:1}})})}));
  """
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=R,capture_output=True,text=True,timeout=15)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_speaker_choices_positive(self):self.assertEqual(self.v['pair']['exercise_request']['speaker_voice_ids'],['melo_en_au','melo_en_in'])
 def test_speaker_restore_positive(self):self.assertEqual([self.v['restored']['exercise_request']['speaker_voice_ids'],self.v['three']['exercise_request']['speaker_voice_ids']],[['melo_en_au','melo_en_in'],['melo_en_au','melo_en_in',None]])
 def test_advanced_speakers_positive(self):
  self.assertEqual([self.v['advanced']['exercise_request']['speaker_count'],self.v['advanced']['speakers'][0]['voice_profile_id']],[1,'bf_emma']);self.assertNotIn('speaker_voice_ids',self.v['advanced']['exercise_request'])
 def test_auto_negative(self):self.assertNotIn('speaker_voice_ids',self.v['automatic']['exercise_request']);self.assertNotIn('provider_profile_id',self.v['automatic'])
 def test_active_count_negative(self):self.assertEqual(self.v['one']['exercise_request']['speaker_voice_ids'],['melo_en_au'])
if __name__=='__main__':unittest.main()
