"""Real custom audio-profile Settings, source build and DB; zero inference."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class CustomAudioProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=R/'data/iteration16/custom-audio-profile'/('run-'+uuid.uuid4().hex[:10]);cls.root.mkdir(parents=True)
  env=dict(os.environ,TANGERINE_RELEASE_EVIDENCE=str(cls.root))
  env.setdefault('TANGERINE_RELEASE_SOURCE_FOCUS','custom-audio-profile')
  env.setdefault('TANGERINE_TEST_VIDEO_DIR',str(cls.root/'videos'))
  p=subprocess.run([str(R/'tests/release-current-source')],cwd=R,env=env,capture_output=True,text=True,timeout=1800)
  (cls.root/'stdout').write_text(p.stdout);(cls.root/'stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Actual custom-profile Settings fixture failed: '+str(cls.root))
  cls.values=json.loads((cls.root/'observations.json').read_text())
  cls.receipt=json.loads((cls.root/'receipt.json').read_text())
  (R/'data/iteration16/custom-audio-profile-current.json').write_text(json.dumps(dict(status='observed',root=str(cls.root.relative_to(R)))))
  (R/'data/iteration16/release/current-source.json').write_text(json.dumps(dict(status='observed',root=str(cls.root.relative_to(R)))))
 def test_custom_profile_positive(self):
  self.assertEqual(self.values['test_custom_profile_positive'],dict(setup_commands=['scripts/tangerine model-setup qwen25-omni-3b-audio-v1'],saved_profile='custom-local-audio-judge',displayed_profile='custom-local-audio-judge',label='Qwen/Qwen2.5-Omni-3B · local · saved custom profile'))
  self.assertEqual(self.receipt['model_calls'],0)
 def test_custom_profile_disable_negative(self):
  self.assertEqual(self.values['test_custom_profile_disable_negative'],dict(saved_profile=None,displayed_profile='',llm_profiles_preserved=True))
  self.assertEqual(self.receipt['model_calls'],0)
 def test_saved_binding_positive(self):
  self.assertEqual(self.values['test_saved_binding_positive'],dict(setup_commands=['scripts/tangerine model-setup qwen25-omni-audio-v1'],saved_model='Qwen/Qwen2.5-Omni-7B',displayed_profile='qwen-omni-3b',label='Qwen/Qwen2.5-Omni-7B · local'))
  self.assertEqual(self.receipt['model_calls'],0)
 def test_current_source_positive(self):
  images=json.loads((self.root/'architecture.json').read_text())
  self.assertEqual(len(images),5);self.assertEqual({row['architecture'] for row in images},{'arm64'})
  self.assertEqual(self.receipt['model_calls'],0);self.assertTrue(Path(self.receipt['source_archive']).is_file())
if __name__=='__main__':unittest.main()
