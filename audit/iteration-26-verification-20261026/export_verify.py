"""Append finite saved verification to existing local Lab17; no inference."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-26-verification-20261026'
RUN='1585a80aa1cf4ee08202ce41c450fa82'
CONTAINER='tangerine-local-llm-lab-1'


def call(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    if result.returncode:
        (OUT/'lab-failure.log').write_text(result.stdout+result.stderr)
        raise SystemExit('The local Lab update did not finish. Native verification remains saved.')
    return result.stdout


def main():
    stage=OUT/'lab-export';stage.mkdir(exist_ok=True)
    for name in ['clean.json','source-revision.json','browser-observations.json',
                 'http-observations.json','recovery-red.log','recovery-green.log',
                 'recovery-siblings.log','language.json','initial-unavailable.png',
                 'error-and-retry.png','error-mobile-390.png','error-mobile-320.png',
                 'restored-desktop.png']:
        shutil.copy2(OUT/name,stage/name)
    sources=['audit/iteration-26-acoustic-20261026/listening.py',
             'audit/iteration-26-acoustic-20261026/register.py',
             'audit/iteration-26-acoustic-20261026/REUSE.json',
             'audit/iteration-26-verification-20261026/browser_fixture.py',
             'audit/iteration-26-verification-20261026/VERIFY.md',
             'tests/test_completion_i26.py','tests/test_selected_acoustic.py',
             'tests/test_selected_listening_recovery.py']
    for name in sources:
        target=stage/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    remote='/tmp/tangerine-i26-verification'
    call(['docker','exec',CONTAINER,'mkdir','-p',remote])
    call(['docker','cp',str(stage)+'/.',CONTAINER+':'+remote])
    code='''import json,pathlib
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-i26-verification');c=MlflowClient(tracking_uri='http://127.0.0.1:5000');run='1585a80aa1cf4ee08202ce41c450fa82'
source=json.loads((root/'source-revision.json').read_text());prefix='verify-'+source['commit'][:7]
c.log_artifacts(run,str(root),artifact_path=prefix)
checked=[]
for name in ['clean.json','source-revision.json','browser-observations.json','http-observations.json']:
 p=pathlib.Path(c.download_artifacts(run,prefix+'/'+name,'/tmp/tangerine-i26-verify-readback'));assert json.loads(p.read_text())==json.loads((root/name).read_text());checked.append(name)
previous=c.list_artifacts(run,'source-0987483/selected');assert len(previous)==4
c.set_tag(run,'tangerine.i26.verification',source['status']);c.set_tag(run,'tangerine.i26.verify_source',source['commit'])
files=[]
def walk(path):
 for item in c.list_artifacts(run,path):
  if item.is_dir:walk(item.path)
  else:files.append(item.path)
walk(prefix)
print('TANGERINE_RESULT='+json.dumps(dict(experiment_id=c.get_run(run).info.experiment_id,run_id=run,artifact_prefix=prefix,source_commit=source['commit'],readback=True,checked=checked,files=files,retained_model_prefix='source-0987483',retained_actual_model_calls=4,new_model_calls=0,new_synthesis_calls=0,export_inference_calls=0,qualification=source['status'])))
'''
    raw=call(['docker','exec',CONTAINER,'python','-c',code]);(OUT/'lab-export.log').write_text(raw)
    result=json.loads(next(line.split('=',1)[1] for line in raw.splitlines() if line.startswith('TANGERINE_RESULT=')))
    (OUT/'lab-readback.json').write_text(json.dumps(result,indent=2)+'\n')
    summary={key:value for key,value in result.items() if key not in {'files','checked'}}
    summary['checked_artifacts']=len(result['checked']);summary['artifact_files']=len(result['files'])
    (HERE/'MLFLOW.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
