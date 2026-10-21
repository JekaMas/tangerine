"""Read back captured actual native ASR/auditory packets from local MLflow."""
from pathlib import Path
import json,unittest,uuid
from release_lab import export_packets
R=Path(__file__).resolve().parents[1]
class ReleaseDiagnosticLabTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  native=json.loads((R/'data/iteration16/receipts/diagnostics-current.json').read_text())
  assert native['status']=='passed' and {'TestNativeDiagnosticActualASRPositive','TestNativeDiagnosticActualAuditoryPositive'}.issubset(native['observed_tests'])
  cls.root=R/'data/iteration16/lab'/('run-'+uuid.uuid4().hex[:10]);cls.result=export_packets(sorted((R/native['root']).glob('diagnostic-*.json')),cls.root)
 def test_native_lab_artifacts_positive(self):self.assertGreaterEqual(self.result['operations'],2);self.assertTrue(all(a['verified'] for i in self.result['items'] for a in i['exported']['artifacts']))
 def test_native_lab_traces_positive(self):self.assertTrue(all(t['state']=='exported' for i in self.result['items'] for t in i['exported']['trace_exports']));self.assertTrue(all(i['verified']['status']=='observed' and not i['verified']['discrepancies'] for i in self.result['items']))
 def test_export_no_inference_negative(self):self.assertEqual(self.result['model_calls'],0);self.assertTrue(all(i['exported']['provider_calls']==0 and i['verified']['provider_calls']==0 for i in self.result['items']))
 def test_missing_artifact_negative(self):self.assertIs(self.result['missing_rejected'],True)
if __name__=='__main__':unittest.main()
