"""Local Lab readback of constructed/native preparation; no Azure/model calls."""
import json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-24-azure-20261026';stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
shutil.copytree(OUT/'controlled',stage/'controlled',dirs_exist_ok=True)
for name in ['access-inventory.json','browser-facts.json','layouts.json','red-contracts.log','green-contracts-final.log','green-cli.log','siblings.log','informational-final.json']:
 shutil.copy2(OUT/name,stage/name)
for name in ['services/speech/backends.py','audit/iteration-24-azure-20261026/compare.py','audit/iteration-24-azure-20261026/player.py','audit/iteration-24-azure-20261026/material.json','audit/iteration-24-azure-20261026/REPORT.md','audit/iteration-24-azure-20261026/PRESERVATION.json','audit/iteration-24-azure-20261026/SOURCE.json','tests/test_azure_comparison.py','tests/test_completion_i24.py']:
 shutil.copy2(ROOT/name,stage/Path(name).name)
container='tangerine-local-llm-lab-1'
def call(args):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return r.stdout
call(['docker','exec',container,'mkdir','-p','/tmp/tangerine-i24'])
call(['docker','cp',str(stage)+'/.',container+':/tmp/tangerine-i24'])
retained=OUT/'lab-readback.json'
run_id=json.loads(retained.read_text())['run_id'] if retained.exists() else ''
code='''import json,pathlib,sys
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000');name='Tangerine I24 Azure - controlled preparation; actual access blocked'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.get_run(sys.argv[1]) if sys.argv[1] else c.create_run(eid,tags={'tangerine.scope':'Native SSML/policy/resume and constructed transport fixtures','tangerine.origin':'Controlled responses/PCM only; NOT Azure audio','tangerine.live_status':'Blocked: Microsoft passkey and actual F0 resource/key/region unavailable','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded'})
prefix='final-preparation'
c.log_artifacts(r.info.run_id,'/tmp/tangerine-i24',artifact_path=prefix)
for k,v in {'azure_synthesis_calls':0,'model_calls':0,'export_inference_calls':0,'live_recordings':0}.items():c.log_param(r.info.run_id,k,v)
for name in ['controlled/plan.json','controlled/result.json','access-inventory.json','informational-final.json','SOURCE.json']:
 p=c.download_artifacts(r.info.run_id,prefix+'/'+name,'/tmp/tangerine-i24-readback');assert json.loads(pathlib.Path(p).read_text())==json.loads((pathlib.Path('/tmp/tangerine-i24')/name).read_text())
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk(prefix);c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'files':files,'actual_azure_calls':0,'export_inference_calls':0,'qualification':'blocked; controlled preparation only'}))
'''
raw=call(['docker','exec',container,'python','-c',code,run_id]);(OUT/'lab-export.log').write_text(raw)
result=json.loads(next(x.split('=',1)[1] for x in raw.splitlines() if x.startswith('TANGERINE_RESULT=')));(OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='files'})
