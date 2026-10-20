"""Typed native browser observations against independent literal UI expectations."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class SpeechBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration7/browser'/('run-'+uuid.uuid4().hex[:12]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/speech-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_SPEECH_BROWSER_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=900)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native browser observation failed; inspect '+str(evidence/'driver.stderr'))
  cls.observed=json.loads((evidence/'observations.json').read_text())
 def test_playback_positive(self):self.assertIs(self.observed['values']['test_playback_positive'],True);self.assertFalse(self.observed['network_substitution'])
 def test_refresh_positive(self):self.assertEqual(self.observed['values']['test_refresh_positive'],1);self.assertTrue(self.observed['recovery_observed']);self.assertEqual(self.observed['refresh_requests']['after'],self.observed['refresh_requests']['before']+1)
 def test_dependency_negative(self):self.assertEqual(self.observed['values']['test_dependency_negative'],'Saved preparations are unavailable. Refresh to retry.')
 def test_audio_failure_negative(self):self.assertEqual(self.observed['values']['test_audio_failure_negative'],'Saved audio is temporarily unavailable. Refresh and retry playback; saved text and audio are retained.');self.assertTrue(self.observed['recovery_observed'])
 def test_acoustic_progress_positive(self):self.assertIs(self.observed['values']['test_acoustic_progress_positive'],True)
 def test_acoustic_profile_positive(self):self.assertEqual(self.observed['values']['test_acoustic_profile_positive'],{'saved_profile':True,'selected_profile':'kokoro-controlled-v1'});self.assertTrue(self.observed['recovery_observed'])
 def test_acoustic_private_key_negative(self):self.assertIs(self.observed['values']['test_acoustic_private_key_negative'],False)
 def test_acoustic_reference_negative(self):self.assertIs(self.observed['values']['test_acoustic_reference_negative'],False);self.assertFalse(self.observed['network_substitution'])
if __name__=='__main__':unittest.main()
