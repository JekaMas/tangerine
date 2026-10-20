"""Actual UI observations with independent literal expectations and real dependencies."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class InterpretationBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration10/browser'/('run-'+uuid.uuid4().hex[:12]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/interpretation-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_INTERPRETATION_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=600)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native interpretation browser failed: '+str(evidence/'driver.stderr'))
  cls.observed=json.loads((evidence/'observations.json').read_text())
 def test_submit_positive(self):self.assertEqual(self.observed['values']['test_submit_positive'],{'answer':'Use opens.','disabled':True,'findings':True,'optional':True})
 def test_history_positive(self):self.assertEqual(self.observed['values']['test_history_positive'],'Use opens.')
 def test_private_negative(self):self.assertFalse(self.observed['values']['test_private_negative'])
 def test_immutable_negative(self):self.assertEqual(self.observed['values']['test_immutable_negative'],'Use opens.')
 def test_retry_positive(self):self.assertTrue(self.observed['values']['test_retry_positive'])
 def test_failure_negative(self):self.assertEqual(self.observed['values']['test_failure_negative'],{'answer':'Use opens.','disabled':True,'retry':True})
 def test_media_recovery_positive(self):self.assertTrue(self.observed['values']['test_media_recovery_positive'])
 def test_media_failure_negative(self):self.assertEqual(self.observed['values']['test_media_failure_negative'],{'answer':'Use opens.','disabled':True})
if __name__=='__main__':unittest.main()
