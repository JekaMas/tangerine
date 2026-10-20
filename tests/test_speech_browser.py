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
 def test_refresh_positive(self):self.assertEqual(self.observed['values']['test_refresh_positive'],1);self.assertTrue(self.observed['recovery_observed'])
 def test_dependency_negative(self):self.assertEqual(self.observed['values']['test_dependency_negative'],'Saved preparations are unavailable. Refresh to retry.')
 def test_audio_failure_negative(self):self.assertEqual(self.observed['values']['test_audio_failure_negative'],'Saved audio is temporarily unavailable. Refresh and retry playback; saved text and audio are retained.');self.assertTrue(self.observed['recovery_observed'])
if __name__=='__main__':unittest.main()
