"""Export/read back retained functional artifacts. Never dispatch another model."""
from pathlib import Path
import json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-22-elevenlabs-20261026'
stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
for file in (OUT/'live').iterdir():
 if file.suffix in ('.json','.wav','.jsonl') and not file.name.startswith('private'):
  shutil.copy2(file,stage/file.name)
shutil.copytree(OUT/'live/assets',stage/'assets',dirs_exist_ok=True)
for name in ['observations.json','requests.jsonl','native-write-responses.jsonl']:
 shutil.copy2(OUT/name,stage/name)
# Exact changed inference producer source, not a stored schema archive.
for name in ['services/speech/elevenlabs_dictionary.py','services/speech/backends.py','tests/native_elevenlabs_test.go']:
 shutil.copy2(ROOT/name,stage/Path(name).name)
container='tangerine-local-llm-lab-1'
def call(args):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return r.stdout
call(['docker','exec',container,'mkdir','-p','/tmp/tangerine-i22'])
call(['docker','cp',str(stage)+'/.',container+':/tmp/tangerine-i22'])
code='''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I22 production ElevenLabs ordinary flow'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'I22 ordinary flow functional qualification','tangerine.speech_model':'eleven_flash_v2','tangerine.text_semantics':'constructed protocol fixtures','tangerine.audio_opinion':'one blinded Gemini Free pair; not gold','tangerine.paid_use':'forbidden','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,'/tmp/tangerine-i22',artifact_path='ordinary-flow')
for k,v in {'hosted_tts_calls':5,'dictionary_creations':2,'auditory_calls':1,'primary_score':100,'true_positives':1,'false_negatives':0,'false_positives':0,'export_inference_calls':0}.items():c.log_param(r.info.run_id,k,v)
expected=json.loads(pathlib.Path('/tmp/tangerine-i22/native-fixture.json').read_text())
file=c.download_artifacts(r.info.run_id,'ordinary-flow/native-fixture.json','/tmp/tangerine-i22-readback')
assert json.loads(pathlib.Path(file).read_text())==expected
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk('ordinary-flow')
assert 'ordinary-flow/exercise.wav' in files and 'ordinary-flow/result.json' in files and 'ordinary-flow/frozen-plan.json' in files
assert not any('private' in f or '.env' in f or '.key' in f for f in files)
c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'run_id':r.info.run_id,'experiment_id':eid,'artifact_count':len(files),'readback':'observed','files':files,'export_inference_calls':0,'attempt_id':expected['attempt_id']}))
'''
raw=call(['docker','exec',container,'python','-c',code]);(OUT/'lab-export.stdout').write_text(raw)
x=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')));(OUT/'lab-readback.json').write_text(json.dumps(x,indent=2));print({k:v for k,v in x.items() if k!='files'})
