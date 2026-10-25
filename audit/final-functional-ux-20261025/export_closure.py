"""Append the repaired starter's zero-call evidence, preserving the first export."""
from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'data/final-functional-ux-20261025'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(ROOT/'data/local-preview/docker-config')}
def docker(*args):
 p=subprocess.run(['docker',*args],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=240)
 if p.returncode:(OUT/'mlflow-closure-failure.log').write_text(p.stdout+p.stderr);raise RuntimeError('Local closure export failed; native evidence is retained')
 return p.stdout
stage=OUT/'lab-closure';stage.mkdir(exist_ok=True)
for p in OUT.iterdir():
 if p.name.startswith(('lab-','mlflow')):continue
 if p.is_dir():shutil.copytree(p,stage/p.name,dirs_exist_ok=True)
 else:shutil.copyfile(p,stage/p.name)
shutil.copytree(HERE,stage/'audit',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['services/web/app/reports/starters.js','services/web/app/reports/StarterForms.js','services/web/app/audio/page.js','services/web/app/styles/prepare.css','tests/test_final_functional_helpers.py','tests/test_final_functional_browser.py']:
 q=stage/'sources'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,q)
remote='/tmp/tangerine-final-functional-ux-closure-20261025';docker('exec','tangerine-local-llm-lab-1','mkdir','-p',remote);docker('cp',str(stage)+'/.','tangerine-local-llm-lab-1:'+remote)
run=json.loads((HERE/'MLFLOW.json').read_text())['run_id']
code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient('http://127.0.0.1:5000');run=RUN;root='/tmp/tangerine-final-functional-ux-closure-20261025';c.log_artifacts(run,root,artifact_path='closure');dest='/tmp/fx-closure-readback'
def read(name):return json.loads(pathlib.Path(c.download_artifacts(run,'closure/'+name,dest)).read_text())
r=read('audit/RECONCILIATION.json');assert r['cases']==253 and len(r['cases_observed'])==253 and not r['missing'];config=read('starter-configuration-final.json');assert config['stage_profiles']['case_generation']=='local-generation' and config['stage_profiles']['claim_mapping']=='chatgpt-plan-responses-v1';assert read('starter-input-final.json')['category_ids']==['grammar.verbs.subject_verb_agreement'];e=read('starter-experiment-final.json');assert e['status']=='planned' and all(x['status']=='not_run' and not x['receipt_ids'] for x in e['rows']);c.set_tag(run,'tangerine.final_selected_cases','253');c.set_tag(run,'tangerine.final_binding','Exact selected category + explicit experiment generation profile; workspace unchanged');c.log_metric(run,'selected_software_passes',253,step=1);print(json.dumps({'run_id':run,'selected_cases':253,'new_inference_calls':0,'artifact_namespace':'closure','readback':'253 observations, exact native category, selected local generation binding, preserved Pro mapping and unexecuted experiment'}))
'''.replace('RUN',repr(run))
raw=docker('exec','tangerine-local-llm-lab-1','python','-c',code);(OUT/'mlflow-closure.log').write_text(raw);result=json.loads(next(x for x in reversed(raw.splitlines()) if x.startswith('{')));p=HERE/'MLFLOW.json';v=json.loads(p.read_text());v['closure']=result;p.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(result))
