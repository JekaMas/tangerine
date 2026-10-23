"""Export the two actual development flows and their native captures to local Lab."""
import json,os,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/ux-controls-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
if (O/'mlflow.json').exists():print((O/'mlflow.json').read_text());raise SystemExit(0)
stage=O/'lab-export';stage.mkdir(exist_ok=True)
for name in ['flow','native-diagnostics']:shutil.copytree(O/name,stage/name,dirs_exist_ok=True)
for name in ['native-diagnostics.json','model-minor.log','model-minor-repaired.log','model-zero.log','native-checkpoint.jsonl']:shutil.copyfile(O/name,stage/name)
sources=stage/'sources';sources.mkdir(exist_ok=True)
for source in ['services/api/internal/app/ux_observation_test.go','services/api/internal/app/ux_controls_test.go','services/api/internal/app/mutation_selection.go','services/api/internal/app/mutation_content.go','specification/v2/prompts/generate-v1.txt','specification/v2/contracts/exercise-request.schema.json']:
 p=sources/source;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/source,p)
def call(args):
 p=subprocess.run(['docker',*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=180)
 if p.returncode:raise RuntimeError(p.stderr[-1200:])
 return p.stdout
remote='/tmp/tangerine-ux-controls-20261023'
call(['exec','tangerine-local-llm-lab-1','mkdir','-p',remote]);call(['cp',str(stage)+'/.','tangerine-local-llm-lab-1:'+remote])
code='''import json,pathlib,mlflow
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-ux-controls-20261023');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine UX controls 20261023';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'exact category and severity; positive and zero-error native flows','tangerine.billing':'existing included ChatGPT plan and local Kokoro only','tangerine.reference_origin':'authored independent count/category/severity expectations','tangerine.limit':'not a universal linguistic or pronunciation benchmark'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='experiment')
for label,count in [('minor',1),('zero',0)]:
 p=c.download_artifacts(r.info.run_id,'experiment/flow/'+label+'/ground-truth.json','/tmp/ux-readback');v=json.loads(pathlib.Path(p).read_text());assert len(v['units'])==count
 if count:assert v['units'][0]['severity']=='minor' and v['units'][0]['primary_taxonomy_id']=='lexis.collocation'
 p=c.download_artifacts(r.info.run_id,'experiment/flow/'+label+'/actual.wav','/tmp/ux-readback');assert pathlib.Path(p).stat().st_size>48044
p=c.download_artifacts(r.info.run_id,'experiment/native-diagnostics.json','/tmp/ux-readback');v=json.loads(pathlib.Path(p).read_text());assert len(v['asset_ids'])==12
for identity in v['asset_ids']:
 p=c.download_artifacts(r.info.run_id,'experiment/native-diagnostics/'+identity+'.json','/tmp/ux-readback');packet=json.loads(pathlib.Path(p).read_text());assert packet['capture'] is True and packet['artifacts']
c.log_param(r.info.run_id,'actual_flows',2);c.log_param(r.info.run_id,'native_capture_packets',12);c.set_terminated(r.info.run_id)
print(json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'flow_readback':['minor','zero'],'native_packet_readback':12,'export_inference_calls':0}))
'''
raw=call(['exec','tangerine-local-llm-lab-1','python','-c',code]);(O/'mlflow-export.log').write_text(raw)
result=json.loads(next(line for line in reversed(raw.splitlines()) if line.startswith('{')));(O/'mlflow.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
