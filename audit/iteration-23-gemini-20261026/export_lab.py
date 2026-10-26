"""Export existing I23 functional artifacts to the selected local Lab; zero inference."""
from pathlib import Path
import json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-23-gemini-20261026'
stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
for folder in ['live','repair','resume','controlled','context']:
 dest=stage/folder;dest.mkdir(exist_ok=True)
 for file in (OUT/folder).iterdir():
  if file.is_file() and file.suffix in ('.json','.jsonl','.wav') and not file.name.startswith('private'):shutil.copy2(file,dest/file.name)
 if (OUT/folder/'assets').exists():shutil.copytree(OUT/folder/'assets',dest/'assets',dirs_exist_ok=True)
for name in ['candidate-reconciliation.json','observations.json','answer-expectation.json','playback.json','requests.jsonl','native-write-responses.jsonl']:
 shutil.copy2(OUT/name,stage/name)
for name in ['services/api/internal/provider/execute.go','services/api/internal/app/provider_inference.go','specification/v2/prompts/extract-v1.txt','tests/native_gemini_test.go']:
 shutil.copy2(ROOT/name,stage/Path(name).name)
container='tangerine-local-llm-lab-1'
def call(args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr[:500])
 return p.stdout
call(['docker','exec',container,'mkdir','-p','/tmp/tangerine-i23'])
call(['docker','cp',str(stage)+'/.',container+':/tmp/tangerine-i23'])
code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I23 Gemini Free native text qualification'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'I23 functional Gemini Free qualification','tangerine.model':'gemini-3.1-flash-lite','tangerine.billing':'Free tier; no billing account observed','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded','tangerine.baseline_limit':'pre-fix panic leaves one missing receipt; retained failed baseline, not candidate acceptance'})
c.log_artifacts(r.info.run_id,'/tmp/tangerine-i23',artifact_path='qualification')
ledger=json.loads(pathlib.Path('/tmp/tangerine-i23/candidate-reconciliation.json').read_text())
for k,v in {'candidate_dispatches':ledger['independent_dispatches'],'candidate_native_receipts':ledger['native_receipts'],'total_hosted_dispatches':ledger['hosted_dispatches_total'],'baseline_orphan_receipts':1,'primary_score':100,'explanation_fraction':1,'export_inference_calls':0}.items():c.log_param(r.info.run_id,k,v)
for name in ['candidate-reconciliation.json','resume/result.json','live/key.json']:
 p=c.download_artifacts(r.info.run_id,'qualification/'+name,'/tmp/tangerine-i23-readback')
 assert json.loads(pathlib.Path(p).read_text())==json.loads((pathlib.Path('/tmp/tangerine-i23')/name).read_text())
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk('qualification');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'files':files,'export_inference_calls':0}))
'''
raw=call(['docker','exec',container,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
result=json.loads(next(x.split('=',1)[1] for x in raw.splitlines() if x.startswith('TANGERINE_RESULT=')))
(OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='files'})
