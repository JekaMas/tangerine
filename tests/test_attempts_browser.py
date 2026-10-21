"""Actual saved-history failure/Refresh/reopen through real DB, API and Chrome."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class AttemptsBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=R/'data/iteration16/attempts'/('run-'+uuid.uuid4().hex[:10]);cls.root.mkdir(parents=True)
  env=dict(os.environ,TANGERINE_LISTENING_BROWSER_EVIDENCE=str(cls.root),TANGERINE_LISTENING_TEST_FOCUS='attempts')
  p=subprocess.run([str(R/'tests/listening-browser')],cwd=R,env=env,capture_output=True,text=True,timeout=600)
  (cls.root/'stdout').write_text(p.stdout);(cls.root/'stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Actual attempts browser failed: '+str(cls.root))
  cls.observed=json.loads((cls.root/'observations.json').read_text())
 def test_attempts_failure_negative(self):
  self.assertEqual(self.observed['values']['test_attempts_failure_negative'],dict(error=True,savedLink=True));self.assertIs(self.observed['network_substitution'],False)
 def test_attempts_recovery_positive(self):
  self.assertEqual(self.observed['values']['test_attempts_recovery_positive'],dict(sameAttempt=True,answer='Use opens.'));self.assertIs(self.observed['database_recovered'],True)
if __name__=='__main__':unittest.main()
