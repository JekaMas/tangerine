"""Actual selected local MLflow SDK artifact; no genuine LLM calls or inference claim."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class RecoveryLabTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  pointer=R/'data/iteration15/receipts/native-current.json'
  if not pointer.exists():raise AssertionError('Current native recovery receipt is required; no older fallback')
  receipt=json.loads(pointer.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
  if receipt['exit_code']!=0 or receipt['source_revision']!=head:raise AssertionError('Current native recovery source/result does not match')
  native=R/receipt['control_artifact'];packet=json.loads(native.read_text())
  if (packet['independent_fixture_dispatches'],packet['native_receipts'],packet['native_snapshots'],packet['actual_llm_inference_calls'])!=(2,2,2,0):raise AssertionError('Constructed boundary/native join mismatch')
  cls.path=R/'data/iteration15/lab'/('run-'+uuid.uuid4().hex[:10]);cls.path.mkdir(parents=True)
  script=r'''
import hashlib,json,pathlib,tempfile
import mlflow
from mlflow import MlflowClient
root=pathlib.Path('/lab');source=pathlib.Path('/native/control-native.json');packet=json.loads(source.read_text())
mlflow.set_tracking_uri('sqlite:////lab/mlflow.db');client=MlflowClient();experiment=client.create_experiment('Tangerine iteration15 deterministic recovery',artifact_location='file:///lab/artifacts')
with mlflow.start_run(experiment_id=experiment,tags={'tangerine.proof':'deterministic_control_only','tangerine.source_revision':json.loads(pathlib.Path('/native/receipt.json').read_text())['source_revision'],'tangerine.model_observation':'constructed upstream; no real inference'}) as run:
 mlflow.log_metrics({'actual_llm_inference_calls':0,'constructed_dispatches':packet['independent_fixture_dispatches'],'native_receipts':packet['native_receipts'],'native_snapshots':packet['native_snapshots'],'native_speech_receipts':packet['native_speech_receipts'],'constructed_speech_dispatches':packet['independent_speech_dispatches']});mlflow.log_artifact(str(source));run_id=run.info.run_id
with tempfile.TemporaryDirectory() as folder:
 downloaded=pathlib.Path(client.download_artifacts(run_id,'control-native.json',folder));same=downloaded.read_bytes()==source.read_bytes()
actual=client.get_run(run_id);missing=False
try:
 with tempfile.TemporaryDirectory() as folder:client.download_artifacts(run_id,'missing-required-copy.json',folder)
except Exception:missing=True
result={'status':'observed','mlflow_version':mlflow.__version__,'run_id':run_id,'experiment_id':experiment,'tracking_uri':'sqlite:////lab/mlflow.db','artifact_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'artifact_path':'control-native.json','artifact_exact':same,'missing_artifact_rejected':missing,'metrics':actual.data.metrics,'run_status':actual.info.status,'proof':'Actual MLflow SDK/SQLite artifact readback for deterministic control evidence; no genuine LLM quality/inference/hosted qualification.'};(root/'result.json').write_text(json.dumps(result,indent=2));assert same and missing and result['metrics']['actual_llm_inference_calls']==0
'''
  (cls.path/'record.py').write_text(script);(cls.path/'control-native.json').write_bytes(native.read_bytes());(cls.path/'receipt.json').write_text(json.dumps(receipt))
  command=['docker','run','--rm','--network','none','-v',str(cls.path)+':/lab','-v',str(cls.path)+':/native:ro','--entrypoint','python','tangerine-mlflow-upstream:3.17.0','-B','/lab/record.py']
  p=subprocess.run(command,cwd=R,env=os.environ,capture_output=True,text=True,timeout=150);(cls.path/'stdout').write_text(p.stdout);(cls.path/'stderr').write_text(p.stderr)
  if p.returncode:raise AssertionError('Actual MLflow record failed: '+str(cls.path))
  cls.result=json.loads((cls.path/'result.json').read_text());(R/'data/iteration15/receipts/lab-current.json').write_text(json.dumps({'result':str((cls.path/'result.json').relative_to(R)),'source_revision':head},indent=2))
 def test_export_positive(self):self.assertTrue(self.result['artifact_exact']);self.assertEqual(self.result['run_status'],'FINISHED')
 def test_control_correspondence_positive(self):self.assertEqual(self.result['metrics'],{'actual_llm_inference_calls':0,'constructed_dispatches':2,'native_receipts':2,'native_snapshots':2,'native_speech_receipts':1,'constructed_speech_dispatches':1})
 def test_missing_copy_negative(self):self.assertTrue(self.result['missing_artifact_rejected'])
