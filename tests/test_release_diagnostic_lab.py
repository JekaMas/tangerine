"""Read back captured actual native ASR/auditory packets from local MLflow."""
from pathlib import Path
import json,unittest,uuid
from release_lab import export_packets
R=Path(__file__).resolve().parents[1]
class ReleaseDiagnosticLabTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  native=json.loads((R/'data/iteration16/receipts/diagnostics-current.json').read_text())
  required={'TestNativeDiagnosticActualASRPositive','TestNativeDiagnosticActualAuditoryPositive'}
  assert native['status']=='passed' and required.issubset(native['observed_tests'])
  observations=native.get('observations') or [dict(root=native['root'],test=t) for t in required]
  packets={}
  for observation in observations:
   root=R/observation['root'];events=[json.loads(line) for line in (R/observation.get('go_events',str(root/'go-test.jsonl'))).read_text().splitlines() if line.startswith('{')]
   assert any(e.get('Action')=='pass' and e.get('Test')==observation['test'] for e in events)
   assert not any(e.get('Action')=='fail' and e.get('Test')==observation['test'] for e in events)
   for path in root.glob('diagnostic-*.json'):packets[json.loads(path.read_text())['operation']]=path
  assert required.issubset({o['test'] for o in observations})
  cls.root=R/'data/iteration16/lab'/('run-'+uuid.uuid4().hex[:10]);cls.result=export_packets(list(packets.values()),cls.root)
  (cls.root/'observation-sources.json').write_text(json.dumps(observations,indent=2))
 def test_native_lab_artifacts_positive(self):self.assertGreaterEqual(self.result['operations'],2);self.assertTrue(all(a['verified'] for i in self.result['items'] for a in i['exported']['artifacts']))
 def test_native_lab_traces_positive(self):self.assertTrue(all(t['state']=='exported' for i in self.result['items'] for t in i['exported']['trace_exports']));self.assertTrue(all(i['verified']['status']=='observed' and not i['verified']['discrepancies'] for i in self.result['items']))
 def test_export_no_inference_negative(self):self.assertEqual(self.result['model_calls'],0);self.assertTrue(all(i['exported']['provider_calls']==0 and i['verified']['provider_calls']==0 for i in self.result['items']))
 def test_missing_artifact_negative(self):self.assertIs(self.result['missing_rejected'],True)
if __name__=='__main__':unittest.main()
