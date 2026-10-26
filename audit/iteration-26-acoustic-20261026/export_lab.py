"""Export this finite saved experiment to the existing local Lab; zero inference."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-26-acoustic-20261026'
CONTAINER='tangerine-local-llm-lab-1'


def call(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    if result.returncode:
        (OUT/'lab-failure.log').write_text(result.stdout+result.stderr)
        raise SystemExit('The local Lab export did not finish. Saved observations remain available.')
    return result.stdout


def main():
    stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
    # Explicit allowlist: OUT also contains the ignored native credential file.
    for name in ['browser-observations.json','clean.json','SOURCE.json','native-runtime.json']:
        shutil.copy2(OUT/name,stage/name)
    shutil.copytree(OUT/'selected',stage/'selected',dirs_exist_ok=True)
    for name in ['desktop.png','mobile-390.png','mobile-320.png','weak-form.png','intonation-function.png']:
        shutil.copy2(OUT/name,stage/name)
    sources=['services/speech/category_validation.py','services/speech/diagnostic_runtime.py',
             'services/speech/diagnostic_models.py','services/speech/diagnostic_server.py',
             'specification/v2/prompts/audio-category-probe-v1.txt',
             'audit/iteration-25-qwen-20261026/player.py','tests/test_selected_acoustic.py',
             'tests/test_completion_i26.py','tests/test_category_validation.py','tests/test_category_evidence.py']
    sources += [str(p.relative_to(ROOT)) for p in HERE.iterdir() if p.suffix in {'.py','.json','.md'} and p.name not in {'MLFLOW.json','STATUS.json'}]
    for name in sources:
        target=stage/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    rows=json.loads((OUT/'gallery.json').read_text())
    retained=ROOT/json.loads((HERE/'selection.json').read_text())['retained_linking']
    for name in ['withheld.json','readmitted-response.json','comparison.json']:
        target=stage/'retained-linking'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(retained/name,target)
    for row in rows:
        for clip in row['probe']['withheld']:
            target=stage/'media'/row['id']/(clip['role']+'.wav');target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/clip['audio_path'],target)
    remote='/tmp/tangerine-i26-acoustic'
    call(['docker','exec',CONTAINER,'mkdir','-p',remote])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
    previous=OUT/'lab-readback.json'
    run_id=json.loads(previous.read_text())['run_id'] if previous.exists() else ''
    code='''import json,pathlib,sys
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-i26-acoustic');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I26 - selected saved acoustic controls'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.get_run(sys.argv[1]) if sys.argv[1] else c.create_run(eid,tags={'tangerine.scope':'Five saved four-control sets; four new finite free-tier observations','tangerine.reference_origin':'Authored local drill contexts; model agreement is not perceptual gold','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded','tangerine.original_cv_run':'153b4dc65bab4210925db0e15214aa47'})
source=json.loads((root/'SOURCE.json').read_text());prefix='source-'+source['commit'][:7]
c.log_artifacts(r.info.run_id,str(root),artifact_path=prefix)
for key,value in {'actual_new_model_calls':4,'new_synthesis_calls':0,'export_inference_calls':0,'selected_sets':5,'confirmed_model_checks':2,'uncertain_or_unconfirmed':3,'retained_cv_test_ids':518}.items():c.log_param(r.info.run_id,key,value)
checked=[]
names=['clean.json','SOURCE.json','browser-observations.json','sources/audit/iteration-26-acoustic-20261026/REUSE.json']
names += [str(p.relative_to(root)) for p in (root/'selected').glob('*/*.json')]
for name in names:
 p=pathlib.Path(c.download_artifacts(r.info.run_id,prefix+'/'+name,'/tmp/tangerine-i26-readback'));assert json.loads(p.read_text())==json.loads((root/name).read_text());checked.append(name)
for saved in (root/'media').glob('*/*.wav'):
 name=str(saved.relative_to(root));p=pathlib.Path(c.download_artifacts(r.info.run_id,prefix+'/'+name,'/tmp/tangerine-i26-readback'));assert p.read_bytes()==saved.read_bytes();checked.append(name)
files=[]
def walk(path):
 for item in c.list_artifacts(r.info.run_id,path):
  if item.is_dir:walk(item.path)
  else:files.append(item.path)
walk(prefix);c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,artifact_prefix=prefix,source_commit=source['commit'],status=c.get_run(r.info.run_id).info.status,readback=True,checked=checked,files=files,actual_new_model_calls=4,new_synthesis_calls=0,export_inference_calls=0,qualification='Finite mixed model observations; browser activation remains unverified; no I26 acceptance')))
'''
    raw=call(['docker','exec',CONTAINER,'python','-c',code,run_id]);(OUT/'lab-export.log').write_text(raw)
    result=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')))
    previous.write_text(json.dumps(result,indent=2)+'\n')
    summary={key:value for key,value in result.items() if key not in {'files','checked'}}
    summary['checked_artifacts']=len(result['checked']);summary['artifact_files']=len(result['files'])
    (HERE/'MLFLOW.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':main()
