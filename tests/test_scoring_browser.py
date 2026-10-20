"""Observed native UI values; independent literal expectations."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class ScoringBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration11/browser'/('run-'+uuid.uuid4().hex[:12]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/scoring-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_INTERPRETATION_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=600)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native scoring browser failed: '+str(evidence/'driver.stderr'))
  cls.values=json.loads((evidence/'observations.json').read_text())['values']
 def test_scores_positive(self):self.assertEqual(self.values['test_scores_positive'],{'primary':'Primary score: 100.0 / 100','optional':True,'recommendation':True})
 def test_retry_positive(self):self.assertEqual(self.values['test_retry_positive'],{'primary':'Primary score: 100.0 / 100','recommendation':True})
 def test_feedback_failure_negative(self):self.assertEqual(self.values['test_feedback_failure_negative'],{'primary':'Primary score: 100.0 / 100','answer':'Use opens.','disabled':True})
 def test_privacy_negative(self):self.assertFalse(self.values['test_privacy_negative'])
 def test_write_failure_negative(self):self.assertEqual(self.values['test_write_failure_negative'],{'answer':'Use opens.','disabled':True,'primary':'Primary score: 100.0 / 100'})
 def test_write_recovery_positive(self):self.assertEqual(self.values['test_write_recovery_positive'],'Primary score: 100.0 / 100')
if __name__=='__main__':unittest.main()
