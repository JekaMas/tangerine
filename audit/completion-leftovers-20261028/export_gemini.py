"""Actual finite Gemini requests/replies/audio and legacy failure, local Lab only."""
import json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/completion-leftovers-20261028';PAIR=OUT/'gemini-current-api';CONTAINER='tangerine-local-llm-lab-1'
def call(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=240)
 if r.returncode:raise RuntimeError('Local Lab export failed; source evidence remains retained')
 return r.stdout
def main():
 if (OUT/'gemini-lab-readback.json').exists():return
 stage=OUT/'gemini-lab-export';stage.mkdir(exist_ok=True)
 selected=[PAIR/name for name in ['plan.json','result.json','dispatches.json','gemini-clean-request.json','gemini-clean-receipt.json','gemini-clean.raw','gemini-clean.wav','gemini-mistakes-request.json','gemini-mistakes-receipt.json','gemini-mistakes.raw','gemini-mistakes.wav','container-projection-failure/SCOPE.json']]
 selected += [OUT/('gemini-resume/'+name) for name in ['allowance.json','gemini-mistakes-3-request.json','gemini-mistakes-3-receipt.json','gemini-mistakes-3.raw']]
 selected += [OUT/('gemini-browser/'+name) for name in ['browser-observations.json','requests.json']]
 for source in selected:
  destination=stage/source.relative_to(OUT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
 for relative in ['audit/completion-leftovers-20261028/gemini_current_pair.py','audit/completion-leftovers-20261028/resume_gemini.py','services/speech/audio.py','tests/test_provider_followup.py','data/speech-comparison-20261022/compare.py']:
  destination=stage/'source'/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,destination)
 (stage/'scope.json').write_text(json.dumps(dict(successful_model_calls=2,failed_contract_requests=1,export_inference_calls=0,billing='existing unbilled Free project',mode='New explicit mode-omitted configuration, no legacy request rewrite',quality='Directions requested26contrasts; actual perception is unconfirmed; this is not a production adapter qualification',source_preparation='9dbf8c95-51a3-4c0f-9395-b3a77a824d22'),indent=2)+'\n')
 remote='/tmp/tangerine-gemini-current-20261028';call(['docker','exec',CONTAINER,'mkdir','-p',remote]);call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
 code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000');name='Tangerine Gemini Free current TTS API 20261028';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.origin':'Actual two Gemini Free requests; legacy contract failure retained','tangerine.paid_use':'forbidden','tangerine.scope':'New explicit comparison; no original plan replacement or production speech adapter','tangerine.quality':'Requested26contrasts; perceived realization unconfirmed'})
root=pathlib.Path('/tmp/tangerine-gemini-current-20261028');c.log_artifacts(r.info.run_id,str(root),artifact_path='actual')
for key,value in {'successful_model_calls':2,'failed_contract_requests':1,'export_inference_calls':0}.items():c.log_param(r.info.run_id,key,value)
for name in ['scope.json','gemini-current-api/gemini-clean-request.json','gemini-current-api/gemini-mistakes-request.json','gemini-browser/browser-observations.json','gemini-resume/gemini-mistakes-3.raw']:
 file=c.download_artifacts(r.info.run_id,'actual/'+name,'/tmp/tangerine-gemini-current-readback');assert pathlib.Path(file).read_bytes()==(root/name).read_bytes()
c.set_terminated(r.info.run_id);print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'readback':True,'matched_successful_model_calls':2,'failed_contract_requests':1,'export_inference_calls':0,'artifact_prefix':'actual'}))
'''
 raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'gemini-lab-export.log').write_text(raw);result=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')));(OUT/'gemini-lab-readback.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
