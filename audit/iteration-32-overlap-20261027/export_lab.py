"""Export the finite local I32 observations to the existing private Lab; no calls."""
import json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-32-overlap-20261027';CONTAINER='tangerine-local-llm-lab-1'
def call(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr[-1500:])
 return p.stdout
def main():
 stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
 for name in ['selected','recordings']:shutil.copytree(OUT/name,stage/name,dirs_exist_ok=True)
 for name in ['go-stable.jsonl','native-stable.jsonl','OBSERVATIONS.json','browser-observations.json','asr.log','player-desktop.jpg','player-mobile-390.jpg','player-mobile-320.jpg','spec-check.json']:shutil.copy2(OUT/name,stage/name)
 for path in [*ROOT.glob('services/api/internal/app/*overlap*.go'),*ROOT.glob('services/api/internal/app/speech*.go'),ROOT/'services/api/internal/lab/builtin.json',ROOT/'specification/v2/prompts/generate-v1.txt',ROOT/'tests/native_overlap_test.go',ROOT/'tests/test_overlap_evidence.py']:
  target=stage/'source'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 remote='/tmp/tangerine-iteration32-overlap';call(['docker','exec',CONTAINER,'mkdir','-p',remote]);call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
 code='''import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-iteration32-overlap');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I32 - actual local overlapping speech';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'Two authored native speech scenes; exact waveform/clock/resume and finite independent local recognition','tangerine.model_observation':'4 actual local Kokoro source recordings and 4 local Whisper recognitions; original contexts/receipts retained','tangerine.semantic_origin':'Constructed text and scoring decisions; no hosted semantic qualification','tangerine.paid_provider_calls':'0','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='evidence')
for key,value in {'actual_local_tts_calls':4,'actual_local_asr_calls':4,'hosted_llm_calls':0,'paid_provider_calls':0,'stable_acceptance_synthesis_calls':0,'export_inference_calls':0}.items():c.log_param(r.info.run_id,key,value)
files=[]
def walk(p):
 for item in c.list_artifacts(r.info.run_id,p):
  if item.is_dir:walk(item.path)
  else:files.append(item.path)
walk('evidence');checked=[]
for name in ['selected/obstructive/key.json','selected/obstructive/mixed.wav','selected/cooperative_backchannel/key.json','selected/cooperative_backchannel/mixed.wav','selected/obstructive/mixed.wav.asr.json','selected/cooperative_backchannel/mixed.wav.asr.json','OBSERVATIONS.json']:
 p=pathlib.Path(c.download_artifacts(r.info.run_id,'evidence/'+name,'/tmp/tangerine-i32-readback'));assert p.read_bytes()==(root/name).read_bytes();checked.append(name)
c.set_terminated(r.info.run_id);print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,status=c.get_run(r.info.run_id).info.status,artifact_files=len(files),checked=checked,readback=True,export_inference_calls=0,actual_local_tts_calls=4,actual_local_asr_calls=4,hosted_llm_calls=0)))
'''
 raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
 result=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')));(OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'audit/iteration-32-overlap-20261027/MLFLOW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
