"""Export/read back zero-inference native/UI evidence to the existing local Lab."""
from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'data/final-functional-ux-20261025'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(ROOT/'data/local-preview/docker-config')}
def docker(*args):
 p=subprocess.run(['docker',*args],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=240)
 if p.returncode:
  (OUT/'mlflow-failure.log').write_text(p.stdout+p.stderr)
  raise RuntimeError('Local Lab export failed; selected native artifacts remain under '+str(OUT))
 return p.stdout
receipt=OUT/'mlflow-readback.json'
if receipt.exists():print(receipt.read_text());raise SystemExit(0)
stage=OUT/'lab-export'
if stage.exists():shutil.rmtree(stage)
stage.mkdir()
for p in OUT.iterdir():
 if p==stage or p.name.startswith('mlflow'):continue
 if p.is_dir():shutil.copytree(p,stage/p.name,dirs_exist_ok=True)
 else:shutil.copyfile(p,stage/p.name)
shutil.copytree(HERE,stage/'audit',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
source=stage/'sources'
paths=[x for x in subprocess.check_output(['git','diff','--name-only','HEAD','--','services/web','services/api/internal/app','services/api/internal/contracts/schemas'],cwd=ROOT,text=True).splitlines()]
paths+=['services/api/internal/app/functional_category_test.go','services/api/internal/app/history_summary.go','services/web/app/cleanup/RecordPicker.js','services/web/app/listen/passageReplay.js','services/web/app/prepare/SavedFailure.js','services/web/app/prepare/failureMessage.js','services/web/app/reports/StarterForms.js','services/web/app/reports/starters.js','services/web/app/requestError.js','services/web/app/savedRecord.js','tests/test_final_functional_browser.py','tests/test_final_functional_helpers.py','tests/test_request_error.py']
for name in paths:
 p=ROOT/name;q=source/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
remote='/tmp/tangerine-final-functional-ux-20261025'
docker('exec','tangerine-local-llm-lab-1','mkdir','-p',remote);docker('cp',str(stage)+'/.','tangerine-local-llm-lab-1:'+remote)
code='''import json,pathlib,mlflow,wave
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-final-functional-ux-20261025');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine final functional and UI 20261025';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.get_run('924b6d28f7c241f1bd2fd3d323042acc')
c.set_tag(r.info.run_id,'tangerine.first_export_note','Original CUA screenshots are JPEG; corrected an initial PNG-specific artifact assertion without altering images.')
c.log_batch(r.info.run_id,tags=[mlflow.entities.RunTag(k,v) for k,v in {'tangerine.scope':'252 FX software and actual CUA/native observation cases','tangerine.inference_calls':'0','tangerine.zero_call_reason':'Native fixture and presentation changes; unchanged model context/outputs retain LF/CV provenance','tangerine.billing':'No inference/synthesis, purchase, overage or provider change','tangerine.review':'Self-review with literal independent expectations; mixed audio evidence remains mixed'}.items()])
c.log_artifacts(r.info.run_id,str(root),artifact_path='verification')
dest='/tmp/tangerine-final-functional-ux-readback';p=c.download_artifacts(r.info.run_id,'verification/audit/RECONCILIATION.json',dest);v=json.loads(pathlib.Path(p).read_text());assert v['cases']==252 and len(v['cases_observed'])==252 and not v['missing'] and all(x['status']=='passed' for x in v['cases_observed'])
p=c.download_artifacts(r.info.run_id,'verification/browser-observations.json',dest);b=json.loads(pathlib.Path(p).read_text());assert len(b['routes'])==len(b['narrow'])==11 and b['checks']['replayLiteralEnd']['paused'] and b['checks']['cleanupPreview']['applyDisabled']
p=c.download_artifacts(r.info.run_id,'verification/saved-demo-audio.wav',dest)
with wave.open(p,'rb') as w: assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000) and w.getnframes()>48000
p=c.download_artifacts(r.info.run_id,'verification/screens/results-desktop-final.jpg',dest);assert pathlib.Path(p).read_bytes().startswith(bytes([255,216,255]))
p=c.download_artifacts(r.info.run_id,'verification/audit/COVERAGE.json',dest);a=json.loads(pathlib.Path(p).read_text());assert len(a['categories'])==88 and sum(x['audio_evidence']['audio']['audio_confirmation']=='confirmed' for x in a['categories'])==39
c.log_param(r.info.run_id,'selected_cases',252);c.log_param(r.info.run_id,'new_inference_calls',0);c.log_metric(r.info.run_id,'selected_software_passes',252);c.set_terminated(r.info.run_id)
print(json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,selected_cases=252,new_inference_calls=0,readback=['252 exact observed identities','11 desktop and 11 mobile routes','Actual finite media stop and preview-only cleanup','Stored actual WAV','Actual result screenshot','All 88 category evidence rows with mixed audio states'])))
'''
raw=docker('exec','tangerine-local-llm-lab-1','python','-c',code);(OUT/'mlflow-export.log').write_text(raw)
result=json.loads(next(x for x in reversed(raw.splitlines()) if x.startswith('{')));receipt.write_text(json.dumps(result,indent=2)+'\n');(HERE/'MLFLOW.json').write_text(receipt.read_text());print(json.dumps(result))
