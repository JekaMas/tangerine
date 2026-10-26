"""Export controlled native/UI recovery artifacts to the existing local Lab."""
import json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-23-verification-20261026'
stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
for folder in ['controlled','browser']:
 dest=stage/folder;dest.mkdir(exist_ok=True)
 for f in (OUT/folder).iterdir():
  if f.is_file() and f.suffix in ['.json','.jsonl'] and not f.name.startswith('private'):shutil.copy2(f,dest/f.name)
 if (OUT/folder/'assets').exists():shutil.copytree(OUT/folder/'assets',dest/'assets',dirs_exist_ok=True)
for name in ['browser-facts.json','layouts.json','requests.jsonl','native-write-responses.jsonl','recovered.wav','green-provider.jsonl']:
 shutil.copy2(OUT/name,stage/name)
for name in ['services/api/internal/provider/gemini.go','tests/native_gemini_test.go','tests/native_gemini_recovery_test.go']:
 shutil.copy2(ROOT/name,stage/Path(name).name)
container='tangerine-local-llm-lab-1'
def call(args):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return r.stdout
call(['docker','exec',container,'mkdir','-p','/tmp/tangerine-i23-verify'])
call(['docker','cp',str(stage)+'/.',container+':/tmp/tangerine-i23-verify'])
code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I23 verification - controlled error recovery'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'Controlled Gemini errors; native checkpoint/local speech/UI recovery','tangerine.origin':'Constructed/replayed HTTP dependency; no hosted qualification','tangerine.reused_live_run':'b83631af099449d1baed0ca39881a0f6','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,'/tmp/tangerine-i23-verify',artifact_path='recovery')
for k,v in {'hosted_dispatches_this_verification':0,'export_inference_calls':0,'speech_origin':'actual local Kokoro'}.items():c.log_param(r.info.run_id,k,v)
for name in ['browser/after.json','browser-facts.json','controlled/error-denied.json']:
 p=c.download_artifacts(r.info.run_id,'recovery/'+name,'/tmp/tangerine-i23-verify-readback')
 assert json.loads(pathlib.Path(p).read_text())==json.loads((pathlib.Path('/tmp/tangerine-i23-verify')/name).read_text())
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk('recovery');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'files':files,'export_inference_calls':0,'hosted_dispatches_this_verification':0}))
'''
raw=call(['docker','exec',container,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
result=json.loads(next(l.split('=',1)[1] for l in raw.splitlines() if l.startswith('TANGERINE_RESULT=')))
(OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='files'})
