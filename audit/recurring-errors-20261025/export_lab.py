"""Export/read back the exact synthetic experiment in existing local MLflow."""
import json, os, shutil, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[2]
O = R / 'data/recurring-errors-20261025'
if (O / 'mlflow.json').exists():
    print((O / 'mlflow.json').read_text())
    raise SystemExit(0)
stage = O / 'lab-export'
stage.mkdir(exist_ok=True)
for name in ['speech-grouped', 'speech-kokoro', 'native-diagnostics']:
    shutil.copytree(O / name, stage / name, dirs_exist_ok=True)
for name in ['native-diagnostics.json', 'browser.json', 'demo-blueprint.json', 'demo-preparation-state.json', 'demo-candidate.json', 'demo-key.json', 'demo-dialogue.wav', 'positive-attempt.json', 'positive-results.json', 'negative-attempt.json', 'negative-results.json', 'preservation.json']:
    shutil.copyfile(O / name, stage / name)
for path in ['services/api/internal/app/recurring_errors.go', 'services/api/internal/app/scoring_projection.go', 'services/api/internal/app/speech_plan.go', 'services/speech/acoustic_alignment.py', 'services/speech/melo_english.py', 'services/web/app/prepare/RecurringErrors.js', 'specification/v2/docs/recurring-errors.md', 'specification/v2/contracts/recurring-error.schema.json', 'specification/v2/contracts/evaluation-key.schema.json', 'specification/v2/contracts/feedback-score.schema.json', 'specification/v2/prompts/canonical-v1.txt', 'specification/v2/prompts/generate-v1.txt', 'specification/v2/prompts/map-v1.txt', 'specification/v2/prompts/audit-map-v1.txt', 'specification/v2/prompts/feedback-v1.txt']:
    p = stage / 'sources' / path
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(R / path, p)
env = {**os.environ, 'DOCKER_HOST': 'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock', 'DOCKER_CONFIG': str(R / 'data/local-preview/docker-config')}
def call(args):
    p = subprocess.run(['docker', *args], env=env, cwd=R, capture_output=True, text=True, timeout=240)
    if p.returncode:
        raise RuntimeError(p.stderr[-1500:])
    return p.stdout
remote = '/tmp/tangerine-recurring-20261025'
call(['exec', 'tangerine-local-llm-lab-1', 'mkdir', '-p', remote])
call(['cp', str(stage) + '/.', 'tangerine-local-llm-lab-1:' + remote])
code = '''import json,pathlib,mlflow,wave
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-recurring-20261025');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine recurring speaker patterns 20261025';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'speaker recurrence; seven literal contexts; correct exception; repeated local phone scopes','tangerine.billing':'included ChatGPT and local speech only','tangerine.oracle':'literal independent contexts, quotas, score arithmetic and false universal explanation','tangerine.limit':'finite authored synthetic observations; no real-person diagnosis or universal empirical error rate'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='experiment')
def read(name):return pathlib.Path(c.download_artifacts(r.info.run_id,'experiment/'+name,'/tmp/recurring-readback'))
key=json.loads(read('demo-key.json').read_text());rows=key['units'][0]['recurrence']['opportunities'];assert len(rows)==7 and sum(x['mutated'] for x in rows)==6
for label,expected in [('positive',(1,0,0)),('negative',(0,1,1))]:
 v=json.loads(read(label+'-results.json').read_text());assert v['status']=='complete' and v['feedback_status']=='complete';assert tuple(v['score']['counts'][k] for k in ['tp','fn','fp'])==expected;assert v['feedback']['items']
v=json.loads(read('positive-results.json').read_text());assert v['score']['optional_explanation']['value']==0 and v['score']['composite']['exact_value_0_100']=={'numerator':'100','denominator':'1'}
for name in ['speech-grouped','speech-kokoro']:
 v=json.loads(read(name+'/response.json').read_text())['receipt']['native'];assert set(v['paired_mutations'])=={'habit'} and len(v['acoustic_scopes'])==3
 obs=json.loads(read(name+'/observation.json').read_text());a,b=obs['correct_before'],obs['correct_after']
 def pcm(name):
  with wave.open(str(read(name))) as w:assert w.getframerate()==24000;return w.readframes(w.getnframes())
 assert pcm(name+'/reference.wav')[a['start_sample']*2:a['end_sample']*2]==pcm(name+'/mutated.wav')[b['start_sample']*2:b['end_sample']*2]
ids=json.loads(read('native-diagnostics.json').read_text())['asset_ids']
for identity in ids:
 v=json.loads(read('native-diagnostics/'+identity+'.json').read_text());assert v['capture'] and v['artifacts']
c.log_param(r.info.run_id,'actual_eligible_contexts',7);c.log_param(r.info.run_id,'actual_mutations',6);c.log_param(r.info.run_id,'target_percent',85);c.log_param(r.info.run_id,'actual_pronunciation_engines',2);c.log_param(r.info.run_id,'actual_answer_probes',2);c.log_param(r.info.run_id,'native_packets',len(ids));c.set_terminated(r.info.run_id)
print(json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'native_packet_readback':len(ids),'actual_key':'6/7','result_readback':['positive:100;optional reason:0','correct exception:false positive;primary:0'],'local_speech_readback':['Melo','Kokoro'],'export_inference_calls':0}))
'''
raw = call(['exec', 'tangerine-local-llm-lab-1', 'python', '-c', code])
(O / 'mlflow-export.log').write_text(raw)
result = json.loads(next(line for line in reversed(raw.splitlines()) if line.startswith('{')))
(O / 'mlflow.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
