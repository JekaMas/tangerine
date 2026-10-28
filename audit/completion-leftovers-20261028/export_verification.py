"""Append retained verification to actual local Lab runs, with no inference.

Explicit allowlists exclude credentials, private environment and model caches.
Original actual-call artifacts and failed observations remain unchanged.
"""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/completion-leftovers-20261028'
CONTAINER = 'tangerine-local-llm-lab-1'
SELECTED = {
    'qwen': ('66a0eab610374c5a8fdbbdb6512acb32', [
        'gate-i25-final.json', 'qwen-browser/browser-observations.json',
        'qwen-browser/requests.json', 'media/qwen-frame.png']),
    'acoustic': ('1585a80aa1cf4ee08202ce41c450fa82', [
        'gate-i26-final.json', 'i26/browser-observations.json',
        'i26/requests.json', 'media/i26-frame.png']),
    'gemini': ('04f7146f04fc46088b435e12395d6f99', [
        'gate-provider-final.json', 'gemini-browser/browser-observations.json',
        'gemini-browser/requests.json', 'media/gemini-frame.png']),
}


def call(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=240)
    if result.returncode:
        raise RuntimeError('Local verification export failed; retained evidence is unchanged')
    return result.stdout


def main():
    receipt = DATA / 'verification-lab-readback.json'
    if receipt.exists():
        return
    stage = DATA / 'verification-lab-export'
    for label, (run_id, files) in SELECTED.items():
        for relative in files:
            target = stage / label / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DATA / relative, target)
        scope = dict(source_revision='3695f1339e540daa819163457c5dd11fdd9ceb80',
                     model_calls=0, synthesis_calls=0, export_inference_calls=0,
                     retained_run_id=run_id, original_actual_artifacts_overwritten=False,
                     scope='Committed-clean readers and actual saved-audio browser interaction; original model observations remain separate')
        (stage / label / 'scope.json').write_text(json.dumps(scope, indent=2) + '\n')
    remote = '/tmp/tangerine-completion-verification-20261028'
    call(['docker', 'exec', CONTAINER, 'mkdir', '-p', remote])
    call(['docker', 'cp', str(stage) + '/.', CONTAINER + ':' + remote])
    code = '''import json,pathlib
from mlflow import MlflowClient
c=MlflowClient(tracking_uri='http://127.0.0.1:5000');root=pathlib.Path('/tmp/tangerine-completion-verification-20261028');rows=[]
for label in ['qwen','acoustic','gemini']:
 source=root/label;scope=json.loads((source/'scope.json').read_text());run=scope['retained_run_id'];prefix='verification-3695f13'
 c.log_artifacts(run,str(source),artifact_path=prefix)
 files=sorted(p for p in source.rglob('*') if p.is_file())
 for p in files:
  relative=str(p.relative_to(source));read=c.download_artifacts(run,prefix+'/'+relative,'/tmp/tangerine-completion-verification-readback/'+label);assert pathlib.Path(read).read_bytes()==p.read_bytes()
 rows.append(dict(label=label,run_id=run,experiment_id=c.get_run(run).info.experiment_id,artifact_prefix=prefix,checked_files=len(files),readback=True,export_inference_calls=0))
print('TANGERINE_RESULT='+json.dumps(dict(status='passed',source_revision='3695f1339e540daa819163457c5dd11fdd9ceb80',rows=rows,export_inference_calls=0)))
'''
    raw = call(['docker', 'exec', CONTAINER, 'python', '-c', code])
    (DATA / 'verification-lab-export.log').write_text(raw)
    result = json.loads(next(line.split('=', 1)[1] for line in raw.splitlines()
                             if line.startswith('TANGERINE_RESULT=')))
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
