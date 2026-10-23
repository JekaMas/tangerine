"""Local MLflow copy/readback of the finite native experiment; zero inference."""
import json
import os
from pathlib import Path
import shutil
import subprocess

R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;O=R/'data/linguistic-fullness-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
receipt=O/'mlflow-readback.json'
if receipt.exists():
    print(receipt.read_text());raise SystemExit(0)
stage=O/'lab-export';stage.mkdir(exist_ok=True)
for p in O.iterdir():
    if p.is_dir() and (p.name.startswith('model-') or p.name in ['flow','frozen-sources','first-population']):
        shutil.copytree(p,stage/p.name,dirs_exist_ok=True)
    elif p.is_file() and p.suffix in ['.json','.jsonl','.log','.stderr'] and p.name not in ['mlflow-readback.json']:
        shutil.copyfile(p,stage/p.name)
shutil.copytree(A,stage/'audit',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
sources=stage/'final-test-sources';sources.mkdir(exist_ok=True)
for name in ['linguistic_coverage_test.go','linguistic_observation_test.go','linguistic_flow_observation_test.go']:
    shutil.copyfile(R/'services/api/internal/app'/name,sources/name)
for name in ['test_linguistic_model_evidence.py','test_linguistic_flow_evidence.py','test_linguistic_injection.py']:
    shutil.copyfile(R/'tests'/name,sources/name)
shutil.copyfile(R/'specification/v2/docs/linguistic-coverage-and-variants.md',stage/'linguistic-coverage-and-variants.md')
shutil.copyfile(R/'specification/v2/domain/linguistic-contrast-set.v1.json',stage/'linguistic-contrast-set.v1.json')


def docker(*args,timeout=120):
    p=subprocess.run(['docker',*args],env=ENV,cwd=R,capture_output=True,timeout=timeout)
    if p.returncode:
        (O/'mlflow-error.log').write_bytes(p.stdout+p.stderr)
        raise SystemExit('Local Lab copy/readback failed; native observations retained; no inference')
    return p.stdout


remote='/tmp/tangerine-linguistic-fullness-20261023'
docker('exec','tangerine-local-llm-lab-1','mkdir','-p',remote)
docker('cp',str(stage)+'/.','tangerine-local-llm-lab-1:'+remote)
code="""import json,pathlib,mlflow
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-linguistic-fullness-20261023');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine linguistic fullness 20261023';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'122-leaf linguistic spec and correct variants','tangerine.billing':'existing included subscription/local only','tangerine.reference_origin':'authored; not empirical gold','tangerine.audio_proof':'one real on-demand flow; symbolic phonetic cases are not heard audio'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='experiment');c.log_param(r.info.run_id,'taxonomy_leaves',122);c.log_param(r.info.run_id,'current_semantic_cases',416);c.log_param(r.info.run_id,'observed_semantic_judgments_including_superseded',430);c.log_param(r.info.run_id,'subtype_mappings',518)
dest='/tmp/tangerine-linguistic-fullness-readback';p=c.download_artifacts(r.info.run_id,'experiment/model-reconciliation.json',dest);v=json.loads(pathlib.Path(p).read_text());assert v['current_observed']==v['current_matched']==v['total']==416 and not v['failed'] and not v['missing']
p=c.download_artifacts(r.info.run_id,'experiment/flow/actual-score-feedback.json',dest);v=json.loads(pathlib.Path(p).read_text());assert v['score']['counts']['tp']==1 and v['score']['counts']['fp']==1 and v['feedback_status']=='complete'
p=c.download_artifacts(r.info.run_id,'experiment/flow/actual-flow.wav',dest);assert pathlib.Path(p).stat().st_size==667244
p=c.download_artifacts(r.info.run_id,'experiment/flow/native-diagnostic-index.json',dest);v=json.loads(pathlib.Path(p).read_text());assert len(v['asset_ids'])==11
def walk(path):
 out=[]
 for a in c.list_artifacts(r.info.run_id,path):out.extend(walk(a.path) if a.is_dir else [a.path])
 return out
files=walk('experiment');c.set_terminated(r.info.run_id);print(json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,artifact_files=len(files),semantic_readback='416/416',flow_readback='actual score/comments + WAV + 11 native diagnostic packets',export_inference_calls=0)))
"""
raw=docker('exec','tangerine-local-llm-lab-1','python','-c',code,timeout=240)
(O/'mlflow-export.log').write_bytes(raw)
result=json.loads(next(x for x in reversed(raw.decode().splitlines()) if x.startswith('{')))
receipt.write_text(json.dumps(result,indent=2)+'\n')
(A/'MLFLOW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
