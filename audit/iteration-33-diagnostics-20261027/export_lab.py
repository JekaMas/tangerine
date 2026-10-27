"""Export exact saved research to the existing local Lab, with zero inference."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'data/iteration-33-diagnostics-20261027'
CONTAINER = 'tangerine-local-llm-lab-1'


def call(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr[-1500:])
    return result.stdout


def main():
    stage = OUT/'lab-export'; stage.mkdir(exist_ok=True)
    shutil.copy2(OUT/'reconciliation.json', stage/'reconciliation.json')
    (stage/'native').mkdir(exist_ok=True)
    for suite in ['category','category-evidence','diagnostic']:
        for suffix in ['.json','.log']:
            shutil.copy2(OUT/'native'/(suite+suffix),stage/'native'/(suite+suffix))
    rows = json.loads((OUT/'reconciliation.json').read_text())['sets']
    for row in rows:
        original = ROOT/row['original_response']
        target = stage/'original'/row['id']; target.mkdir(parents=True,exist_ok=True)
        for name in ['response.json','readmitted-response.json','frozen.json','withheld.json','comparison.json','dispatch.json']:
            if (original.parent/name).exists():
                shutil.copy2(original.parent/name,target/name)
        for clip in row['clips']:
            media = stage/'media'/row['id']/(clip['role']+'.wav')
            media.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/clip['audio_path'],media)
    shutil.copy2(ROOT/'data/connected-speech-20261023/output/physical-reconciliation.json',stage/'original-physical.json')
    sources = ['services/speech/diagnostic_models.py','services/speech/diagnostic_context.py',
               'services/speech/category_validation.py','services/speech/diagnostic_runtime.py',
               'specification/v2/prompts/audio-category-probe-v1.txt',
               'specification/v2/prompts/audio-judge-v1.txt',
               'audit/iteration-26-acoustic-20261026/selection.json',
               'audit/iteration-26-acoustic-20261026/observe.py',
               'audit/iteration-33-diagnostics-20261027/reconcile.py',
               'tests/test_saved_audio_diagnostics.py']
    for name in sources:
        target = stage/'source'/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    remote = '/tmp/tangerine-iteration33-diagnostics'
    call(['docker','exec',CONTAINER,'mkdir','-p',remote])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
    # The allowlist excludes environment files and credentials. Only retained
    # noncredential model bodies, saved media, exact native tests and code enter.
    code = '''import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-iteration33-diagnostics');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I33 - saved audio diagnostic repair';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'Five retained sets; ambiguity, pause/F0 and native context repair', 'tangerine.reference_origin':'Authored original fixtures; mixed model replies are not perceptual gold', 'tangerine.new_inference':'0','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='evidence')
for k,v in {'actual_new_model_calls':0,'actual_new_synthesis_calls':0,'retained_original_i26_calls':4,'retained_original_linking_calls':1,'export_inference_calls':0,'selected_sets':5}.items():c.log_param(r.info.run_id,k,v)
names=['reconciliation.json','native/category.log','native/diagnostic.log','original/weak-form/response.json','original/intonation-function/frozen.json','media/thought-group/mutated.wav','media/intonation-function/acceptable.wav','source/services/speech/diagnostic_models.py','source/specification/v2/prompts/audio-judge-v1.txt']
readback=pathlib.Path('/tmp/tangerine-iteration33-readback');readback.mkdir(exist_ok=True);checked=[]
for name in names:
 p=pathlib.Path(c.download_artifacts(r.info.run_id,'evidence/'+name,'/tmp/tangerine-iteration33-download'));assert p.read_bytes()==(root/name).read_bytes()
 target=readback/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());checked.append(name)
files=[]
def walk(path):
 for x in c.list_artifacts(r.info.run_id,path):
  if x.is_dir:walk(x.path)
  else:files.append(x.path)
walk('evidence');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,status=c.get_run(r.info.run_id).info.status,artifact_files=len(files),readback=True,checked=checked,actual_new_model_calls=0,actual_new_synthesis_calls=0,export_inference_calls=0)))
'''
    raw = call(['docker','exec',CONTAINER,'python','-c',code])
    (OUT/'lab-export.log').write_text(raw)
    result = json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')))
    call(['docker','cp',CONTAINER+':/tmp/tangerine-iteration33-readback/.',str(OUT/'lab-readback')])
    (OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'audit/iteration-33-diagnostics-20261027/MLFLOW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
