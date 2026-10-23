"""Append final evidence to the existing local Lab run; never dispatch inference."""
import json
import os
from pathlib import Path
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]
A = Path(__file__).resolve().parent
O = R / 'data/linguistic-fullness-20261023'
receipt = O / 'mlflow-closure-readback.json'
if receipt.exists():
    print(receipt.read_text())
    raise SystemExit(0)

initial = json.loads((A / 'MLFLOW.json').read_text())
stage = O / 'lab-closure'
stage.mkdir(exist_ok=True)
for source in A.iterdir():
    if source.is_file():
        shutil.copyfile(source, stage / source.name)
for name in [
    'native-contract-final.jsonl', 'native-contract-final.receipt.json',
    'go-check-contract-final.log', 'dag-contract-final.json',
    'discovery-contract-final.json', 'static-stable.json', 'openspec-final.json',
]:
    shutil.copyfile(O / name, stage / name)
shutil.copyfile(R / 'services/api/internal/app/linguistic_coverage_test.go',
                stage / 'linguistic_coverage_test.go')
shutil.copyfile(R / 'openspec/changes/implement-teacher-error-trainer/tasks.md',
                stage / 'canonical-tasks.md')

env = {**os.environ,
       'DOCKER_HOST': 'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',
       'DOCKER_CONFIG': str(R / 'data/local-preview/docker-config')}
remote = '/tmp/tangerine-linguistic-closure-20261023'
container = 'tangerine-local-llm-lab-1'


def docker(*args):
    result = subprocess.run(['docker', *args], env=env, capture_output=True,
                            cwd=R, timeout=120)
    if result.returncode:
        (O / 'mlflow-closure-error.log').write_bytes(result.stdout + result.stderr)
        raise SystemExit('Local Lab closure failed; retained actual observations; no inference')
    return result.stdout


docker('exec', container, 'mkdir', '-p', remote)
docker('cp', str(stage) + '/.', container + ':' + remote)
code = """import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
root=pathlib.Path('/tmp/tangerine-linguistic-closure-20261023')
run=json.loads((root/'MLFLOW.json').read_text())['run_id']
c.log_artifacts(run,str(root),artifact_path='closure/20261023-final')
dest='/tmp/tangerine-linguistic-closure-readback'
for name in ['REPORT.md','RECONCILIATION.json','native-contract-final.jsonl','linguistic_coverage_test.go']:
 p=c.download_artifacts(run,'closure/20261023-final/'+name,dest)
 assert pathlib.Path(p).read_bytes()==(root/name).read_bytes(),name
v=json.loads((root/'RECONCILIATION.json').read_text())
assert v['native_missing']==[] and v['native_cases']==840 and v['dag_cases']==1266 and v['semantic_current_matched']==416
for name in ['dag-contract-final.json','discovery-contract-final.json','static-stable.json']:
 assert json.loads((root/name).read_text())['status']=='passed',name
def walk(path):
 out=[]
 for a in c.list_artifacts(run,path):out.extend(walk(a.path) if a.is_dir else [a.path])
 return out
files=walk('closure/20261023-final')
c.set_tag(run,'tangerine.linguistic_scope_status','1266 finite cases reconciled; acoustic/empirical limits retained')
print(json.dumps(dict(run_id=run,closure_namespace='closure/20261023-final',closure_artifact_files=len(files),closure_readback='report, reconciliation, final 244-case native event stream and exact test source',export_inference_calls=0)))
"""
raw = docker('exec', container, 'python', '-c', code)
(O / 'mlflow-closure-export.log').write_bytes(raw)
result = json.loads(next(x for x in reversed(raw.decode().splitlines()) if x.startswith('{')))
receipt.write_text(json.dumps(result, indent=2) + '\n')
(A / 'MLFLOW.json').write_text(json.dumps({**initial, **result}, indent=2) + '\n')
print(json.dumps(result))
