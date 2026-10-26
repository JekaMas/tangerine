"""Export actual retained functional observations to the existing local Lab.

No model calls, private environment files, account screens or external export.
FINISHED describes export; committed-clean acceptance is recorded separately.
"""
from pathlib import Path
import json,shutil
from export_lab import call

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/iteration-29-saved-case-flow-20261026'
FAILED=ROOT/'data/iteration-29-local-full-flow-20261026'

def main():
    assert not (DATA/'lab-readback.json').exists(), 'Retain existing export/readback'
    stage=DATA/'lab-export';stage.mkdir(exist_ok=True)
    for folder in ['assets','attempts','keys','preparations','snapshots','pictures','share']:
        shutil.copytree(DATA/folder,stage/folder,dirs_exist_ok=True)
    for name in ['call-reconciliation.json','dispatches.json','documents.json','answer-expectation.json',
                 'flow-selection.json','native-relationships.json','ui-observations.json','requests.jsonl',
                 'reopen-before.json','reopen-after.json','media-receipt.json','audio-video-match.json',
                 'gallery-observation.json','observer-path-reconciliation.json','quote-qualified-red.jsonl',
                 'quote-sibling-green.jsonl','web-linebreak-build.log','go-vet-stable.log','gofmt-stable.log',
                 'provider-final-green.jsonl','provider-vet-final.log','gallery-poster-before.json']:
        shutil.copy2(DATA/name,stage/name)
    for name in ['services/api/internal/app/interpretation_claims.go',
                 'services/api/internal/app/extraction_quote_projection_test.go',
                 'services/api/internal/provider/transport.go','services/api/internal/provider/local_host_test.go',
                 'services/web/app/listen/Results.js','services/web/app/listen/useListening.js',
                 'services/web/app/listen/checkingProgress.js','services/web/app/styles/base.css',
                 'specification/v2/prompts/extract-v1.txt','specification/v2/prompts/feedback-v1.txt']:
        target=stage/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    failure=stage/'retained-local-generation-failures';failure.mkdir(exist_ok=True)
    for name in ['dispatches.json','documents.json','installed-local-models.json','installed-generation-model.json',
                 'profile-selection.json','host-api-read-probes.json','provider-green.jsonl']:
        shutil.copy2(FAILED/name,failure/name)
    for folder in ['assets','preparations','snapshots']:
        shutil.copytree(FAILED/folder,failure/folder,dirs_exist_ok=True)
    container='tangerine-local-llm-lab-1';remote='/tmp/tangerine-i29-complete'
    call(['docker','exec',container,'mkdir','-p',remote])
    call(['docker','cp',str(stage)+'/.',container+':'+remote])
    code='''import json,pathlib
from mlflow import MlflowClient
p=pathlib.Path('/tmp/tangerine-i29-complete');c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
ledger=json.loads((p/'call-reconciliation.json').read_text())
assert ledger['complete_flow']
name='Tangerine I29 complete saved-case flow - explicit local checking'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'I29 actual functional flow; same generated case, explicit new local attempt','tangerine.model':'Gemini Free generation; local gpt-oss:20b checking; local Kokoro','tangerine.billing':'local and reused Free observations; purchased credits forbidden','tangerine.export_only':'true','tangerine.performance_campaign':'excluded'})
c.log_artifacts(r.info.run_id,str(p),artifact_path='flow')
for k,v in {'reused_hosted_attempts':29,'actual_new_local_checking_attempts':8,'reused_synthesis_calls':4,'new_generation_calls':0,'new_synthesis_calls':0,'primary_score':60,'optional_explanation_fraction':1,'export_inference_calls':0,'application_full_flow_complete':True}.items():c.log_param(r.info.run_id,k,v)
checked=[]
for name in ['call-reconciliation.json','dispatches.json','documents.json','media-receipt.json','attempts/'+ledger['attempt_id']+'-result.json','keys/'+ledger['preparation_id']+'.json','share/exercise.wav']:
 f=pathlib.Path(c.download_artifacts(r.info.run_id,'flow/'+name,'/tmp/tangerine-i29-complete-readback'))
 assert f.read_bytes()==(p/name).read_bytes()
 checked.append('flow/'+name)
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk('flow');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'checked_files':checked,'files':files,'export_inference_calls':0,'application_full_flow_complete':True,'acceptance_boundary':'Actual finite flow; committed-clean gate recorded separately'}))
'''
    raw=call(['docker','exec',container,'python','-c',code]);(DATA/'lab-export.log').write_text(raw)
    result=json.loads(next(x.split('=',1)[1] for x in raw.splitlines() if x.startswith('TANGERINE_RESULT=')))
    (DATA/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n')
    print({k:v for k,v in result.items() if k not in ['files','checked_files']})

if __name__=='__main__':main()
