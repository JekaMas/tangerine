"""Literal independent browser expectations through real local source owners."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class QualityBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration14/browser'/('run-'+uuid.uuid4().hex[:10]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/quality-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_QUALITY_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=800)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native source browser failed: '+str(evidence/'driver.stderr'))
  cls.values=json.loads((evidence/'observations.json').read_text())['values']
 def test_empty_positive(self):self.assertTrue(self.values['test_empty_positive'])
 def test_report_positive(self):self.assertTrue(self.values['test_report_positive'])
 def test_missing_negative(self):self.assertTrue(self.values['test_missing_negative'])
 def test_plan_positive(self):self.assertTrue(self.values['test_plan_positive'])
 def test_no_fake_execution_negative(self):self.assertFalse(self.values['test_no_fake_execution_negative'])
 def test_run_positive(self):self.assertTrue(self.values['test_run_positive'])
 def test_audio_unknown_negative(self):self.assertTrue(self.values['test_audio_unknown_negative'])
 def test_reload_positive(self):self.assertTrue(self.values['test_reload_positive'])
 def test_failure_negative(self):self.assertTrue(self.values['test_failure_negative'])
 def test_recovery_positive(self):self.assertTrue(self.values['test_recovery_positive'])
 def test_bad_input_negative(self):self.assertTrue(self.values['test_bad_input_negative'])
if __name__=='__main__':unittest.main()
