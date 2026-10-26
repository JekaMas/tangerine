"""Copy existing functional observations to the local Lab. No model execution.

FINISHED describes this artifact export, never complete product acceptance.
Only the explicit synthetic/native evidence allowlist is exported. Private
environment files and account-screen observations are deliberately excluded.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/iteration-29-full-flow-20261026'


def call(args):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=120)
    if p.returncode:
        raise RuntimeError('Local Lab export failed; inspect local output')
    return p.stdout


def main():
    verify = '--verify' in sys.argv
    destination = ROOT / 'data/iteration-29-verify-20261026' if verify else OUT
    stage = destination / 'lab-export'
    if (destination / 'lab-readback.json').exists():
        raise SystemExit('Export already recorded; retain its readback')
    stage.mkdir(exist_ok=True)
    for folder in ['assets', 'attempts', 'keys', 'preparations', 'result-history', 'snapshots', 'pictures', 'share']:
        shutil.copytree(OUT / folder, stage / folder, dirs_exist_ok=True)
    for name in ['call-reconciliation.json', 'dispatches.json', 'documents.json',
                 'answer-expectation.json', 'answer-expectation-original.json',
                 'browser-observations.json', 'requests.jsonl', 'typography-controls.json',
                 'media-receipt.json', 'audio-video-match.json', 'native-relationships.json',
                 'reopen-before.json', 'reopen-after.json', 'attachment-green.jsonl',
                 'extraction-red.jsonl', 'extraction-green.jsonl', 'extraction-detail-green.jsonl']:
        shutil.copy2(OUT / name, stage / name)
    for name in ['services/api/internal/app/interpretation_claims.go',
                 'services/api/internal/app/interpretation_shape.go',
                 'services/api/internal/app/interpretation_relations.go',
                 'services/api/internal/app/extraction_repair_guidance_test.go',
                 'services/web/app/listen/checkingProgress.js',
                 'services/web/app/listen/useListening.js',
                 'specification/v2/prompts/extract-v1.txt',
                 'audit/iteration-29-full-flow-20261026/REVIEW.json']:
        dest = stage / 'source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
    container = 'tangerine-local-llm-lab-1'
    remote = '/tmp/tangerine-i29-verify' if verify else '/tmp/tangerine-i29'
    if verify:
        shutil.copytree(destination / 'pictures', stage / 'verification/pictures', dirs_exist_ok=True)
        for name in ['feedback-before.json', 'ui-observations.json', 'dispatch-delta.json', 'feedback-notice-green.log']:
            shutil.copy2(destination / name, stage / 'verification' / name)
    call(['docker', 'exec', container, 'mkdir', '-p', remote])
    call(['docker', 'cp', str(stage) + '/.', container + ':' + remote])
    code = '''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000')
name='Tangerine I29 actual functional flow - recommendations unavailable'
e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'I29 functional UI/native flow', 'tangerine.acceptance':'incomplete: required recommendations unavailable', 'tangerine.model':'gemini-3.1-flash-lite', 'tangerine.billing':'Free tier; no billing account observed', 'tangerine.paid_use':'forbidden', 'tangerine.performance_campaign':'excluded', 'tangerine.export_only':'true'})
c.log_artifacts(r.info.run_id,'/tmp/tangerine-i29',artifact_path='flow')
ledger=json.loads(pathlib.Path('/tmp/tangerine-i29/call-reconciliation.json').read_text())
for k,v in {'hosted_dispatch_attempts':ledger['provider_dispatches'], 'native_text_receipts':ledger['native_receipts'], 'local_synthesis_calls':ledger['local_synthesis_requests'], 'primary_score':60, 'optional_explanation_fraction':1, 'export_inference_calls':0, 'application_full_flow_complete':False}.items():c.log_param(r.info.run_id,k,v)
checked=[]
for name in ['call-reconciliation.json','media-receipt.json','keys/bc740ead-ff03-455f-805b-0fb4c7babcf1.json','attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5-result.json','share/exercise.wav']:
 p=c.download_artifacts(r.info.run_id,'flow/'+name,'/tmp/tangerine-i29-readback')
 assert pathlib.Path(p).read_bytes()==(pathlib.Path('/tmp/tangerine-i29')/name).read_bytes()
 checked.append('flow/'+name)
files=[]
def walk(path):
 for f in c.list_artifacts(r.info.run_id,path):
  if f.is_dir:walk(f.path)
  else:files.append(f.path)
walk('flow');c.set_terminated(r.info.run_id)
print('TANGERINE_RESULT='+json.dumps({'experiment_id':eid,'run_id':r.info.run_id,'status':c.get_run(r.info.run_id).info.status,'readback':True,'checked_files':checked,'files':files,'export_inference_calls':0,'application_acceptance':'incomplete: recommendations unavailable'}))
'''
    if verify:
        code = code.replace('/tmp/tangerine-i29', remote).replace('Tangerine I29 actual functional flow', 'Tangerine I29 verify and notice repair')
    raw = call(['docker', 'exec', container, 'python', '-c', code])
    (destination / 'lab-export.log').write_text(raw)
    result = json.loads(next(x.split('=', 1)[1] for x in raw.splitlines() if x.startswith('TANGERINE_RESULT=')))
    (destination / 'lab-readback.json').write_text(json.dumps(result, indent=2) + '\n')
    print({k: v for k, v in result.items() if k not in ['files', 'checked_files']})


if __name__ == '__main__':
    main()
