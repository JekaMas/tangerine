"""Independent literal expectations on real Chrome/API/PostgreSQL/MinIO."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class ReviewBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration12/browser'/('run-'+uuid.uuid4().hex[:12]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/review-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_INTERPRETATION_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=800)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native review browser failed: '+str(evidence/'driver.stderr'))
  cls.values=json.loads((evidence/'observations.json').read_text())['values']
 def test_rights_negative(self):self.assertTrue(self.values['test_rights_negative'])
 def test_rights_recovery_positive(self):self.assertTrue(self.values['test_rights_recovery_positive'])
 def test_case_positive(self):self.assertTrue(self.values['test_case_positive'])
 def test_modality_negative(self):self.assertTrue(self.values['test_modality_negative'])
 def test_dispute_positive(self):self.assertEqual(self.values['test_dispute_positive'],{'statement':'Please check café agreement. Keep my exact statement.','primary':'Primary score: 100.0 / 100'})
 def test_failure_negative(self):self.assertEqual(self.values['test_failure_negative'],{'failed':True,'statement':'Please check café agreement. Keep my exact statement.','primary':'Primary score: 100.0 / 100'})
 def test_retry_positive(self):self.assertTrue(self.values['test_retry_positive'])
 def test_selection_failure_negative(self):self.assertEqual(self.values['test_selection_failure_negative'],{'failed':True,'primary':'Primary score: 100.0 / 100'})
 def test_selection_positive(self):self.assertTrue(self.values['test_selection_positive'])
 def test_key_positive(self):self.assertEqual(self.values['test_key_positive'],{'key':True,'primary':'Primary score: 100.0 / 100'})
 def test_history_negative(self):self.assertEqual(self.values['test_history_negative'],'Primary score: 100.0 / 100')
 def test_atomic_negative(self):self.assertEqual(self.values['test_atomic_negative'],{'failed':True,'primary':'Primary score: 100.0 / 100'})
 def test_recovery_positive(self):self.assertEqual(self.values['test_recovery_positive'],{'complete':True,'primary':'Primary score: 100.0 / 100'})
 def test_privacy_negative(self):self.assertFalse(self.values['test_privacy_negative'])
if __name__=='__main__':unittest.main()
