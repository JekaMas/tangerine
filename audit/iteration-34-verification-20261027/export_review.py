"""Append a zero-inference local Lab review; never rewrite original runs."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-34-verification-20261027'
CONTAINER='tangerine-local-llm-lab-1'


def call(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=120,check=True)
    return r.stdout


def main():
    stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
    selected=['audit/iteration-34-local-generation-20261027/compare.py',
        'tests/test_local_generation_review.py',
        'data/iteration-34-verification-20261027/reassessment.json',
        'data/iteration-34-verification-20261027/decision.json',
        'data/iteration-34-verification-20261027/oracle-red.log',
        'data/iteration-34-verification-20261027/oracle-green.log',
        'data/iteration-34-verification-20261027/review-initial.log',
        'data/iteration-34-verification-20261027/browser/observations.json',
        'data/iteration-34-verification-20261027/browser/requests.jsonl',
        'data/iteration-34-verification-20261027/browser/video-probe.json',
        'data/iteration-34-verification-20261027/browser/preparation-recovery.mp4']
    for name in selected:
        target=stage/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    call(['docker','exec',CONTAINER,'mkdir','-p','/tmp/tangerine-i34-verification'])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':/tmp/tangerine-i34-verification'])
    code="""import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-i34-verification');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
r=c.create_run('23',tags={'tangerine.execution':'verification_no_inference','tangerine.scope':'Correct-control oracle repair and controlled browser UX; unchanged actual model/native observations reused'})
for k,v in {'actual_new_inference_calls':0,'actual_new_synthesis_calls':0,'api_charge_usd':0,'retained_original_actual_calls':30,'retained_native_replays':4}.items():c.log_param(r.info.run_id,k,v)
for k,v in {'reassessed_preparations':16,'review_cases':8,'selected_TP':2,'selected_FP':0,'selected_FN':0,'selected_TN':6,'selected_precision':1,'selected_recall':1,'selected_matching_event_accuracy':1}.items():c.log_metric(r.info.run_id,k,v)
c.log_artifacts(r.info.run_id,str(root),artifact_path='review')
out=pathlib.Path('/tmp/tangerine-i34-verification-readback');out.mkdir(exist_ok=True)
checks=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 relative=str(p.relative_to(root));download=pathlib.Path(c.download_artifacts(r.info.run_id,'review/'+relative,str(out)))
 assert download.read_bytes()==p.read_bytes();checks.append(relative)
c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':'23','run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'artifacts':checks,'new_inference_calls':0,'new_synthesis_calls':0}))
"""
    raw=call(['docker','exec',CONTAINER,'python','-c',code])
    (OUT/'lab-export.log').write_text(raw)
    result=json.loads(next(l.split('=',1)[1] for l in raw.splitlines() if l.startswith('TANGERINE_RESULT=')))
    call(['docker','cp',CONTAINER+':/tmp/tangerine-i34-verification-readback/.',str(OUT/'lab-readback')])
    for p in [OUT/'lab.json',HERE/'LAB.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
