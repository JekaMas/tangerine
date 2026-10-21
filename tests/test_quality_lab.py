"""Actual installed local MLflow readback/export, with no model inference.
The selected local-model record contains independently observed wire requests.
"""
from pathlib import Path
import json,os,subprocess,unittest
R=Path(__file__).resolve().parents[1]
class QualityLab(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.binding=json.loads((R/'audit/iteration-14-empirical-20261021/RUNTIME-BINDINGS.json').read_text())
  selected=R/'data/iteration14/local/selected.json'
  cls.root=R/(json.loads(selected.read_text())['evidence_root'] if selected.exists() else cls.binding['local_evidence']);cls.packet=json.loads((cls.root/'actual-local/quality-export.json').read_text());cls.command=['docker','exec','-i',cls.binding['lab_container'],'python','/tangerine/lab.py']
 @classmethod
 def sdk(cls,action,packet,offline=False):
  command=cls.command
  if offline:command=command[:3]+['-e','MLFLOW_TRACKING_URI=http://127.0.0.1:9',*command[3:]]
  return subprocess.run(command+[action],input=json.dumps(packet),capture_output=True,text=True,cwd=R,timeout=90)
 def test_correspondence_positive(self):
  p=subprocess.run(['python3','-B',str(R/'audit/iteration-14-empirical-20261021/local_reconcile.py'),str(self.root.relative_to(R))],env={**os.environ,'TANGERINE_QUALITY_LAB_CONTAINER':self.binding['lab_container']},cwd=R,capture_output=True,text=True,timeout=180)
  self.assertEqual(p.returncode,0,p.stderr);value=json.loads(p.stdout);self.assertEqual((value['actual_dispatches'],value['native_receipts'],value['context_snapshots'],value['span_count']),(4,4,4,4));self.assertEqual(value['independent_verdict_packets'],2)
 def test_missing_copy_negative(self):
  p=self.sdk('verify',{'artifacts':[{'run':'missing-native-copy','artifact':'native/absent.json','sha256':'0'*64}]});self.assertNotEqual(p.returncode,0);value=json.loads(p.stdout);self.assertEqual(value['status'],'incomplete');self.assertEqual(value['provider_calls'],0);self.assertEqual(value['discrepancies'],['missing Lab artifact native/absent.json'])
 def test_unavailable_negative(self):
  original=(self.root/'actual-local/dispatch-observations.jsonl').read_bytes();p=self.sdk('quality-sync',self.packet,True);self.assertNotEqual(p.returncode,0);self.assertIn('native data retained',p.stderr);self.assertEqual((self.root/'actual-local/dispatch-observations.jsonl').read_bytes(),original)
 def test_export_recovery_positive(self):
  before=(self.root/'actual-local/dispatch-observations.jsonl').read_bytes();first=self.sdk('quality-sync',self.packet);self.assertEqual(first.returncode,0,first.stderr);a=json.loads(first.stdout);second=self.sdk('quality-sync',self.packet);self.assertEqual(second.returncode,0,second.stderr);b=json.loads(second.stdout);self.assertEqual(a['run'],b['run']);self.assertEqual([v['run'] for v in a['native_exports']],[v['run'] for v in b['native_exports']]);self.assertEqual(a['provider_calls'],0);self.assertEqual((self.root/'actual-local/dispatch-observations.jsonl').read_bytes(),before)
if __name__=='__main__':unittest.main()
