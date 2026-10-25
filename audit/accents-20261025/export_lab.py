"""Export exact synthetic accent observations to existing local MLflow; no AI."""
import json,os,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/accents-20261025'
if (O/'mlflow.json').exists():print((O/'mlflow.json').read_text());raise SystemExit(0)
stage=O/'lab-export';stage.mkdir(exist_ok=True)
for name in ['speech','native-diagnostics']:shutil.copytree(O/name,stage/name,dirs_exist_ok=True)
for name in ['native-diagnostics.json','demo-preparation.json','demo-preparation-state.json','demo-key.json','demo-attempt.json','demo-results.json','demo-dialogue.wav','video-edit.json']:
 shutil.copyfile(O/name,stage/name)
for source in ['services/speech/melo_english.py','services/speech/accent_phones.py','services/speech/english_accents.py','services/api/internal/app/local_voices.go','services/api/internal/app/speech_plan.go','services/web/app/prepare/SpeakerVoices.js','audit/accents-20261025/observe_speech.py']:
 p=stage/'sources'/source;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/source,p)
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
def call(args):
 p=subprocess.run(['docker',*args],cwd=R,env=ENV,capture_output=True,text=True,timeout=180)
 if p.returncode:raise RuntimeError(p.stderr[-1200:])
 return p.stdout
remote='/tmp/tangerine-accents-20261025'
call(['exec','tangerine-local-llm-lab-1','mkdir','-p',remote]);call(['cp',str(stage)+'/.','tangerine-local-llm-lab-1:'+remote])
code='''import json,pathlib,mlflow,wave
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-accents-20261025');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine local English accents 20261025';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'six fixed voice previews; AU/IN phone pairs; real mixed-accent browser flow','tangerine.billing':'existing included ChatGPT plan and local speech only','tangerine.reference_origin':'independent literal phone/voice/count/result expectations','tangerine.limit':'finite voice/production evidence; not universal accent or perceptual correctness'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='experiment')
def read(name):return pathlib.Path(c.download_artifacts(r.info.run_id,'experiment/'+name,'/tmp/accent-readback'))
for voice,sp in [('melo_en_au',3),('melo_en_in',2)]:
 v=json.loads(read('speech/'+voice+'/preview.json').read_text());assert v['receipt']['native']['speaker_id']==sp
 with wave.open(str(read('speech/'+voice+'/preview.wav'))) as w:assert w.getframerate()==24000 and w.getnframes()>24000
 x=json.loads(read('speech/'+voice+'/acoustic-response.json').read_text())['receipt']['native'];assert x['acoustic_scopes'][0]['phonemes']==['th','ih','ng','k'];assert x['paired_mutations']['target']['native']['acoustic_scopes'][0]['phonemes']==['s','ih','ng','k'];assert read('speech/'+voice+'/mutated.wav').stat().st_size>24000
v=json.loads(read('demo-results.json').read_text());assert v['status']=='complete' and v['feedback_status']=='complete' and v['score']['counts']['tp']==1 and v['score']['counts']['fn']==1
ids=json.loads(read('native-diagnostics.json').read_text())['asset_ids'];assert len(ids)==6
for identity in ids:
 v=json.loads(read('native-diagnostics/'+identity+'.json').read_text());assert v['capture'] and v['artifacts']
c.log_param(r.info.run_id,'actual_voice_previews',6);c.log_param(r.info.run_id,'actual_phone_pairs',2);c.log_param(r.info.run_id,'actual_ui_flows',1);c.log_param(r.info.run_id,'native_packets',len(ids));c.set_terminated(r.info.run_id)
print(json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'native_packet_readback':len(ids),'voice_readback':['melo_en_au','melo_en_in'],'result_readback':'complete','export_inference_calls':0}))
'''
raw=call(['exec','tangerine-local-llm-lab-1','python','-c',code]);(O/'mlflow-export.log').write_text(raw)
result=json.loads(next(line for line in reversed(raw.splitlines()) if line.startswith('{')));(O/'mlflow.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
