"""Export the scoped verification to the existing local Lab; no inference."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-33-verification-20261027'
OLD=ROOT/'data/iteration-33-diagnostics-20261027'
CONTAINER='tangerine-local-llm-lab-1'
REMOTE='/tmp/tangerine-i33-verification'


def call(args):
    return subprocess.run(args,cwd=ROOT,check=True,capture_output=True,text=True,timeout=120).stdout


def main():
    # This is the previous explicit noncredential evidence allowlist, not a
    # repository/environment upload. Original inputs remain distinguishable.
    stage=OUT/'lab-export';shutil.copytree(OLD/'lab-export',stage,dirs_exist_ok=True)
    for name in ['native-invalidated.json','native-invalidated.log','directed.json',
                 'green-directed.log','python312-directed-stable.log',
                 'native-reuse.json','unchanged-symbols.json']:
        shutil.copy2(OUT/name,stage/'native'/name)
    shutil.copytree(OUT/'browser',stage/'ui',dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('screencast','gallery.json','*-comparison.json','*-original.json','*.partial'))
    for name in ['services/speech/category_validation.py',
                 'audit/iteration-26-acoustic-20261026/listening.py',
                 'audit/iteration-33-diagnostics-20261027/verification_native.py',
                 'audit/iteration-33-diagnostics-20261027/browser_fixture.py',
                 'tests/test_saved_audio_verification.py','tests/test_saved_audio_acceptance.py',
                 'specification/v2/docs/saved-audio-diagnostics.md']:
        target=stage/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    call(['docker','exec',CONTAINER,'mkdir','-p',REMOTE])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':'+REMOTE])
    code='''import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-i33-verification');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
e=c.get_experiment_by_name('Tangerine I33 - saved audio diagnostic repair')
r=c.create_run(e.experiment_id,tags={'tangerine.scope':'I33 verify/repair; correct controls, unknown replies, nonblocking saved UI', 'tangerine.reference_origin':'Original authored cases and original model replies; constructed native counterexamples', 'tangerine.new_inference':'0','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='evidence')
for k,v in {'actual_new_model_calls':0,'actual_new_synthesis_calls':0,'export_inference_calls':0,'reobserved_native_cases':532,'reused_native_cases':48,'new_directed_cases':8,'original_sets':5}.items():c.log_param(r.info.run_id,k,v)
names=['reconciliation.json','native/native-invalidated.log','native/green-directed.log','original/weak-form/response.json','original/intonation-function/frozen.json','media/thought-group/mutated.wav','source/services/speech/category_validation.py','source/audit/iteration-26-acoustic-20261026/listening.py','source/specification/v2/prompts/audio-judge-v1.txt','ui/screenshots/desktop-recovered.jpg','ui/saved-listening-review.mp4','ui/weak-form-valid-context.wav']
readback=pathlib.Path('/tmp/tangerine-i33-verification-readback');readback.mkdir(exist_ok=True)
for name in names:
 p=pathlib.Path(c.download_artifacts(r.info.run_id,'evidence/'+name,'/tmp/tangerine-i33-verification-download'));assert p.read_bytes()==(root/name).read_bytes()
 target=readback/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
files=[]
def walk(path):
 for x in c.list_artifacts(r.info.run_id,path):
  if x.is_dir:walk(x.path)
  else:files.append(x.path)
walk('evidence');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=e.experiment_id,run_id=r.info.run_id,status=c.get_run(r.info.run_id).info.status,artifact_files=len(files),checked=names,actual_new_model_calls=0,actual_new_synthesis_calls=0,export_inference_calls=0)))
'''
    raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
    result=json.loads(next(l.split('=',1)[1] for l in raw.splitlines() if l.startswith('TANGERINE_RESULT=')))
    call(['docker','cp',CONTAINER+':/tmp/tangerine-i33-verification-readback/.',str(OUT/'lab-readback')])
    (OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'audit/iteration-33-diagnostics-20261027/VERIFY-MLFLOW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
