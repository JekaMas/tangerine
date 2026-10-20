"""Actual UI observations with independent literal expectations and real dependencies."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class ListeningBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration9/browser'/('run-'+uuid.uuid4().hex[:12]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/listening-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_LISTENING_BROWSER_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=600)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native listening browser failed: '+str(evidence/'driver.stderr'))
  cls.observed=json.loads((evidence/'observations.json').read_text())
 def test_listening_positive(self):self.assertIs(self.observed['values']['test_listening_positive'],True);self.assertFalse(self.observed['network_substitution'])
 def test_draft_positive(self):self.assertEqual(self.observed['values']['test_draft_positive'],{'answer':'  The verb needs agreement.\nОшибка: goes. 🟠  ','language':'ru'})
 def test_submit_positive(self):self.assertEqual(self.observed['values']['test_submit_positive'],{'answer':'  The verb needs agreement.\nОшибка: goes. 🟠  ','disabled':True,'history_readback':'  The verb needs agreement.\nОшибка: goes. 🟠  '})
 def test_empty_positive(self):self.assertEqual(self.observed['values']['test_empty_positive'],{'answer':'','disabled':True})
 def test_private_negative(self):self.assertIs(self.observed['values']['test_private_negative'],False)
 def test_conflict_negative(self):self.assertEqual(self.observed['values']['test_conflict_negative'],'  The verb needs agreement.\nОшибка: goes. 🟠  ')
 def test_database_recovery_negative(self):self.assertTrue(self.observed['database_recovered']);self.assertEqual(self.observed['values']['test_database_recovery_negative'],'  The verb needs agreement.\nОшибка: goes. 🟠  ')
 def test_audio_recovery_negative(self):self.assertTrue(self.observed['media_recovered']);self.assertEqual(self.observed['values']['test_audio_recovery_negative'],'  The verb needs agreement.\nОшибка: goes. 🟠  ')
 def test_remote_submission_positive(self):self.assertEqual(self.observed['values']['test_remote_submission_positive'],{'answer':'Submitted in another window. Ошибка.','disabled':True,'language':'en'})
 def test_unsent_recovery_negative(self):self.assertEqual(self.observed['values']['test_unsent_recovery_negative'],{'answer':'Unsubmitted local text 🟠','languageRetained':True})
if __name__=='__main__':unittest.main()
