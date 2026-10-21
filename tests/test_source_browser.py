"""Literal independent browser expectations through real local source owners."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]
class SourceBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  evidence=ROOT/'data/iteration13/browser'/('run-'+uuid.uuid4().hex[:10]);evidence.mkdir(parents=True)
  p=subprocess.run([str(ROOT/'tests/source-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_SOURCE_EVIDENCE':str(evidence)},capture_output=True,text=True,timeout=800)
  (evidence/'driver.stdout').write_text(p.stdout);(evidence/'driver.stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Native source browser failed: '+str(evidence/'driver.stderr'))
  cls.values=json.loads((evidence/'observations.json').read_text())['values']
 def test_cards_positive(self):self.assertEqual(self.values['test_cards_positive'],11)
 def test_missing_negative(self):self.assertTrue(self.values['test_missing_negative'])
 def test_unsafe_negative(self):self.assertTrue(self.values['test_unsafe_negative'])
 def test_preview_positive(self):self.assertTrue(self.values['test_preview_positive'])
 def test_preview_negative(self):self.assertTrue(self.values['test_preview_negative'])
 def test_import_positive(self):self.assertTrue(self.values['test_import_positive'])
 def test_scope_negative(self):self.assertTrue(self.values['test_scope_negative'])
 def test_rows_positive(self):self.assertTrue(self.values['test_rows_positive'])
 def test_restart_positive(self):self.assertTrue(self.values['test_restart_positive'])
 def test_failure_negative(self):self.assertTrue(self.values['test_failure_negative'])
 def test_recovery_positive(self):self.assertTrue(self.values['test_recovery_positive'])
 def test_unbound_negative(self):self.assertTrue(self.values['test_unbound_negative'])
 def test_no_execution_negative(self):self.assertEqual(self.values['test_no_execution_negative'],'undefined')
 def test_remote_positive(self):self.assertTrue(self.values['test_remote_positive'])
 def test_remote_negative(self):self.assertTrue(self.values['test_remote_negative'])
if __name__=='__main__':unittest.main()
