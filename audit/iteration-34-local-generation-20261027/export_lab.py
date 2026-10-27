"""Publish this finite actual local experiment to the already running local Lab.

Explicit allowlist: native model bodies, contexts, outcomes and selected source.
Never include runtime env files, API keys or user-workspace data. No inference.
"""
from pathlib import Path
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-34-local-generation-20261027'
CONTAINER='tangerine-local-llm-lab-1'

def call(args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    if p.returncode:raise RuntimeError(p.stderr[-1500:])
    return p.stdout

def main():
    result=json.loads((OUT/'comparison.json').read_text())
    stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
    shutil.copy2(OUT/'comparison.json',stage/'comparison.json')
    for name in ['PLAN.json','REPAIR-PLAN.json','FINAL-PLAN.json','REPAIRED-PLAN.json','DEADLINE-PROFILE-PLAN.json','QWEN-REPAIRED-PLAN.json']:
        shutil.copy2(HERE/name,stage/name)
    for directory in ['', 'repair', 'final', 'repaired', 'deadline-profile', 'qwen-repaired','projection-replay']:
        target=stage/'native'/(directory or 'baseline');target.mkdir(parents=True,exist_ok=True)
        source=OUT/directory
        for f in source.glob('*.json'):
            if f.name.startswith('private'):continue
            shutil.copy2(f,target/f.name)
        for f in ['native.jsonl','native.stderr','native-exit-code','resources.jsonl']:
            shutil.copy2(source/f,target/f)
        shutil.copytree(source/'assets',target/'assets',dirs_exist_ok=True)
    for name in ['specification/v2/prompts/canonical-v1.txt','specification/v2/prompts/generate-v1.txt',
                 'services/api/internal/app/mutation_shape.go','services/api/internal/app/mutation_projection.go',
                 'services/api/internal/app/mutation_correction_projection.go',
                 'services/api/internal/app/mutation_local_projection_test.go','tests/native_local_generation_test.go',
                 'tests/native_local_generation_failures_test.go','audit/iteration-34-local-generation-20261027/compare.py']:
        target=stage/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    for name in ['projection-red.jsonl','projection-green.jsonl','surface-red.jsonl','projection-stable.jsonl','correction-red.jsonl','go-final.jsonl']:
        shutil.copy2(OUT/name,stage/name)
    shutil.copytree(OUT/'baseline-source',stage/'baseline-source',dirs_exist_ok=True)
    remote='/tmp/tangerine-i34-local-generation'
    call(['docker','exec',CONTAINER,'mkdir','-p',remote])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
    code='''import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-i34-local-generation');result=json.loads((root/'comparison.json').read_text());c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I34 - bounded installed-local generation repair';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
runs=[];download=pathlib.Path('/tmp/tangerine-i34-readback');download.mkdir(exist_ok=True)
for i,a in enumerate(result['alternatives']):
 r=c.create_run(eid,tags={'tangerine.alternative':a['id'],'tangerine.origin':'Actual installed-local replies; authored independent literal targets','tangerine.scope':'Finite functional repair; no model sweep or population benchmark','tangerine.paid_use':'forbidden'})
 model=next(x['model'] for x in result['rows'] if x['alternative']==a['id'])
 for k,v in {'model':model,'selected_requests':a['requests'],'admitted_requests':a['admitted'],'qualified_fixed_population':a['qualified'],'local_api_charge_usd':0,'electricity':'unmeasured','new_calls_for_export':0}.items():c.log_param(r.info.run_id,k,v)
 for k,v in a['measured'].items():c.log_metric(r.info.run_id,k,v)
 for k,v in a['quality'].items():
  if v is not None:c.log_metric(r.info.run_id,'strict_target_'+k,v)
 c.log_artifacts(r.info.run_id,str(root),artifact_path='evidence')
 checks=['comparison.json','source/specification/v2/prompts/generate-v1.txt','source/services/api/internal/app/mutation_projection.go','source/services/api/internal/app/mutation_correction_projection.go']
 c.set_tag(r.info.run_id,'tangerine.execution','retained_reply_projection_replay' if a['id']=='projection-replay' else 'actual_local_inference')
 c.log_param(r.info.run_id,'actual_new_inference_calls',a['measured']['dispatches'])
 directory={'plain':'baseline','schema':'baseline','repair-plain':'repair','final-plain':'final','repaired-plain':'repaired','deadline-profile-plain':'deadline-profile','qwen-repaired-plain':'qwen-repaired','projection-replay':'projection-replay'}[a['id']]
 checks += ['native/'+directory+'/dispatches.json','native/'+directory+'/documents.json']
 for artifact in checks:
  f=pathlib.Path(c.download_artifacts(r.info.run_id,'evidence/'+artifact,'/tmp/tangerine-i34-download-'+str(i)))
  assert f.read_bytes()==(root/artifact).read_bytes()
  if i==len(result['alternatives'])-1:
   p=download/artifact;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(f.read_bytes())
 c.set_terminated(r.info.run_id);runs.append(dict(alternative=a['id'],run_id=r.info.run_id,status=c.get_run(r.info.run_id).info.status,checked=checks))
print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=eid,runs=runs,readback=True,actual_model_calls=result['dispatch_count'],export_inference_calls=0,api_charge_usd=0)))
'''
    raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
    value=json.loads(next(l.split('=',1)[1] for l in raw.splitlines() if l.startswith('TANGERINE_RESULT=')))
    (OUT/'lab-readback').mkdir(exist_ok=True)
    call(['docker','cp',CONTAINER+':/tmp/tangerine-i34-readback/.',str(OUT/'lab-readback')])
    for p in [OUT/'lab-readback.json',HERE/'MLFLOW.json']:p.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value))

if __name__=='__main__':main()
