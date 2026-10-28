"""Export actual finite local Qwen requests/context/audio to the existing Lab.

Explicit artifact allowlist excludes credentials, environment, caches and weights.
Export/readback never invokes an inference owner.
"""
import json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/completion-leftovers-20261028';PAIR=OUT/'qwen-mps-float32-cpu-codec';CONTAINER='tangerine-local-llm-lab-1'
def call(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=240)
 if r.returncode:raise RuntimeError('Lab operation failed; native export retained')
 return r.stdout

def main():
 if (OUT/'qwen-lab-readback.json').exists():return
 result=json.loads((PAIR/'result.json').read_text());plan=json.loads((PAIR/'plan.json').read_text());dispatches=json.loads((PAIR/'dispatches.json').read_text())
 actual=[d for d in dispatches if d['action']=='piece'];assert result['status']=='complete' and len(actual)==len(plan['pieces'])==26 and all(d['outcome']=='complete' and d['http_status']==200 for d in actual)
 stage=OUT/'qwen-lab-export';stage.mkdir(exist_ok=True)
 selected=[PAIR/name for name in ['plan.json','state.json','result.json','dispatches.json','qwen-clean.wav','qwen-mistakes.wav']]
 selected+=sorted(PAIR.glob('piece-*-response.json'))+sorted(PAIR.glob('piece-*.wav'))
 selected +=[OUT/name for name in ['qwen-mps-installed.txt','qwen-mps-constraints.txt','qwen-diagnostic.log','qwen-float32-diagnostic.log','qwen-codec-red.log','qwen-codec-green.log','qwen-codec-cache-green.log']]
 for relative in ['qwen-mps/dispatches.json','qwen-mps/state.json','qwen-mps-float32/dispatches.json','qwen-mps-float32/state.json','qwen-browser/browser-observations.json','qwen-browser/requests.json']:
  selected.append(OUT/relative)
 for source in selected:
  target=stage/source.relative_to(OUT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 for relative in ['services/speech/backends.py','services/speech/qwen_runtime.py','services/speech/server.py','services/speech/inference_capture.py','audit/iteration-25-qwen-20261026/compare.py','audit/iteration-24-azure-20261026/material.json']:
  target=stage/'source'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
 scope=dict(source_preparation=result['source_preparation'],runtime=plan['runtime'],successful_native_generations=26,failed_native_generations=2,direct_diagnostic_attempts=2,total_actual_model_attempts_this_followup=30,export_inference_calls=0,paid_use=False,claim='Complete four-turn clean/mutated pair; phonetic respelling approximation, no exact IPA or confirmed perception claim. Original CPU and both separately frozen MPS failures retained.',artifacts=[str(p.relative_to(OUT)) for p in selected])
 (stage/'run-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
 remote='/tmp/tangerine-qwen-completion-20261028';call(['docker','exec',CONTAINER,'mkdir','-p',remote]);call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
 code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000');name='Tangerine I25 complete local Qwen pair 20261028';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.origin':'Actual native local MPS generation; explicit CPU codec; actual saved Chrome playback','tangerine.paid_use':'forbidden','tangerine.quality_scope':'Four phonetic respellings requested, not exact IPA or universal acoustic confirmation','tangerine.performance_campaign':'excluded'})
root=pathlib.Path('/tmp/tangerine-qwen-completion-20261028');c.log_artifacts(r.info.run_id,str(root),artifact_path='actual')
scope=json.loads((root/'run-scope.json').read_text())
for key in ['successful_native_generations','failed_native_generations','direct_diagnostic_attempts','total_actual_model_attempts_this_followup','export_inference_calls']:c.log_param(r.info.run_id,key,scope[key])
for name in ['run-scope.json','qwen-mps-float32-cpu-codec/plan.json','qwen-mps-float32-cpu-codec/piece-25-response.json','qwen-browser/browser-observations.json']:
 p=c.download_artifacts(r.info.run_id,'actual/'+name,'/tmp/tangerine-qwen-completion-readback');assert pathlib.Path(p).read_bytes()==(root/name).read_bytes()
responses=c.list_artifacts(r.info.run_id,'actual/qwen-mps-float32-cpu-codec');assert len([p for p in responses if p.path.endswith('-response.json')])==26
c.set_terminated(r.info.run_id);print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'readback':True,'export_inference_calls':0,'matched_successful_model_calls':26,'failed_native_generations':2,'direct_diagnostic_attempts':2,'artifact_prefix':'actual','qualification':'complete finite pair; approximate requested pronunciation only'}))
'''
 raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'qwen-lab-export.log').write_text(raw)
 receipt=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')));(OUT/'qwen-lab-readback.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
