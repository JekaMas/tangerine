"""The presentation owner exposes authored recovery guidance and hides technical exceptions."""
from pathlib import Path
import json,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1];NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class RequestError(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""import {requestError,userError} from './services/web/app/requestError.js'; console.log(JSON.stringify({network:requestError(new TypeError('Failed to fetch')),custom:requestError(new TypeError('NetworkError'),'Library unavailable. Refresh to retry.'),native:requestError(userError('The selected model is unavailable.')),bug:requestError(new TypeError('Cannot read property id')),missing:requestError(null)}));"""
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=10)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_network_positive(self):self.assertEqual(self.v['network'],'This step could not be completed. Your input is retained. Refresh saved state before trying again.')
 def test_context_positive(self):self.assertEqual(self.v['custom'],'Library unavailable. Refresh to retry.')
 def test_native_error_negative(self):self.assertEqual(self.v['native'],'The selected model is unavailable.')
 def test_nontransport_type_error_negative(self):self.assertEqual(self.v['bug'],self.v['network'])
 def test_unknown_outcome_negative(self):self.assertNotIn('Nothing was erased',self.v['network']);self.assertEqual(self.v['missing'],self.v['network'])
if __name__=='__main__':unittest.main(verbosity=2)
