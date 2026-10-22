"""Actual final arm64 source and new saved precision through Chrome; no inference."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class CurrentSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=R/'data/iteration16/release'/('current-arm64-'+uuid.uuid4().hex[:10]);cls.root.mkdir(parents=True)
  env=dict(os.environ,TANGERINE_RELEASE_EVIDENCE=str(cls.root),TANGERINE_TEST_VIDEO_DIR=str(cls.root/'videos'))
  p=subprocess.run([str(R/'tests/release-current-source')],cwd=R,env=env,capture_output=True,text=True,timeout=2000)
  (cls.root/'stdout').write_text(p.stdout);(cls.root/'stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Current source failure: '+str(cls.root))
  cls.values=json.loads((cls.root/'observations.json').read_text())
  pointer=R/'data/iteration16/release/current-source.json'
  settings=R/'data/iteration16/release/settings-current.json'
  if os.environ.get('TANGERINE_RELEASE_SOURCE_FOCUS')=='startup' and pointer.exists() and not settings.exists():settings.write_text(pointer.read_text())
  pointer.write_text(json.dumps(dict(root=str(cls.root.relative_to(R)),receipt=json.loads((cls.root/'receipt.json').read_text())),indent=2))
 def test_current_arm64_source_positive(self):self.assertIs(self.values['test_current_arm64_source_positive'],True)
 def test_current_architecture_negative(self):self.assertIs(self.values['test_current_architecture_negative'],True)
 def test_current_precision_ui_positive(self):self.assertIs(self.values['test_current_precision_ui_positive'],True)
 def test_current_precision_negative(self):self.assertIs(self.values['test_current_precision_negative'],True)
if __name__=='__main__':unittest.main()
