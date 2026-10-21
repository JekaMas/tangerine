"""Actual amd64 native services and arm64 recording/result portability."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class ReleasePortableTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  source=json.loads((R/'data/iteration16/release/live-current.json').read_text());assert source['receipt']['status']=='passed'
  cls.root=R/'data/iteration16/release'/('amd64-'+uuid.uuid4().hex[:10]);cls.root.mkdir(parents=True)
  env=dict(os.environ,TANGERINE_RELEASE_SOURCE_EVIDENCE=str(R/source['root']),TANGERINE_RELEASE_EVIDENCE=str(cls.root),TANGERINE_TEST_VIDEO_DIR=str(cls.root/'videos'))
  p=subprocess.run([str(R/'tests/release-portable')],cwd=R,env=env,capture_output=True,text=True,timeout=2200)
  (cls.root/'stdout').write_text(p.stdout);(cls.root/'stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Actual cross-architecture release failed; evidence: '+str(cls.root))
  cls.values=json.loads((cls.root/'observations.json').read_text());(R/'data/iteration16/release/portable-current.json').write_text(json.dumps(dict(root=str(cls.root.relative_to(R)),receipt=json.loads((cls.root/'receipt.json').read_text())),indent=2))
 def check(self,name):self.assertIs(self.values[name],True)
 def test_portable_source_positive(self):self.check('test_portable_source_positive')
 def test_incomplete_source_negative(self):self.check('test_incomplete_source_negative')
 def test_amd64_start_positive(self):self.check('test_amd64_start_positive')
 def test_amd64_architecture_positive(self):self.check('test_amd64_architecture_positive')
 def test_amd64_architecture_negative(self):self.check('test_amd64_architecture_negative')
 def test_amd64_synthesis_positive(self):self.check('test_amd64_synthesis_positive')
 def test_cross_arch_restore_positive(self):self.check('test_cross_arch_restore_positive')
 def test_restore_collision_negative(self):self.check('test_restore_collision_negative')
 def test_portable_library_positive(self):self.check('test_portable_library_positive')
 def test_portable_result_positive(self):self.check('test_portable_result_positive')
 def test_portable_audio_positive(self):self.check('test_portable_audio_positive')
 def test_amd64_restart_positive(self):self.check('test_amd64_restart_positive')
 def test_portable_no_inference_negative(self):self.check('test_portable_no_inference_negative')
if __name__=='__main__':unittest.main()
