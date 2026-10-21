"""Actual local MLflow export/readback of already captured native packets.
Never dispatches a model or reads another workspace's native evidence.
"""
from pathlib import Path
import json,os,subprocess,time,uuid
R=Path(__file__).resolve().parents[1]
def export_packets(packets,evidence):
 evidence=Path(evidence);evidence.mkdir(parents=True,exist_ok=True);name='tangerine-i16-lab-'+uuid.uuid4().hex[:10]
 def call(args,input=None,check=True):
  p=subprocess.run(args,cwd=R,env=os.environ,input=input,capture_output=True,timeout=160)
  with (evidence/'commands.log').open('ab') as log:log.write(p.stdout+p.stderr)
  if check and p.returncode:raise AssertionError('Native Lab action failed: '+str(evidence))
  return p
 try:
  call(['docker','build','-t',name+'-api:local','-f','services/api/Dockerfile','.'])
  call(['docker','create','--name',name+'-native',name+'-api:local'])
  call(['docker','cp',name+'-native:/usr/local/bin/tangerine',str(evidence/'native')]);(evidence/'native').chmod(0o700)
  mounts=['-v',str((evidence/'native').resolve())+':/tangerine/native:ro']+['-v',str(evidence.resolve())+':/lab','-v',str(R/'deploy/local/lab.py')+':/tangerine/lab.py:ro','-v',str(R/'specification/v2')+':/tangerine/spec:ro','-v',str(R/'services/api/internal/lab/builtin.json')+':/tangerine/builtin.json:ro','-v',str(R/'services/api/internal/provider')+':/tangerine/source/provider:ro','-v',str(R/'services/api/internal/contracts')+':/tangerine/source/contracts:ro','-v',str(R/'services/api/internal/app')+':/tangerine/source/app:ro','-v',str(R/'services/speech')+':/tangerine/speech-source:ro']
  call(['docker','run','-d','--name',name,'--network','none','-e','MLFLOW_DISABLE_TELEMETRY=true','-e','DO_NOT_TRACK=true','-e','MLFLOW_TRACKING_URI=http://127.0.0.1:5000',*mounts,'--entrypoint','mlflow',os.environ.get('TANGERINE_LAB_IMAGE','tangerine-mlflow-upstream:3.17.0'),'server','--host','127.0.0.1','--port','5000','--backend-store-uri','sqlite:////lab/mlflow.db','--artifacts-destination','/lab/artifacts','--allowed-hosts','127.0.0.1,127.0.0.1:5000'])
  for _ in range(90):
   if call(['docker','exec',name,'python','-c',"import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/health',timeout=2)"],check=False).returncode==0:break
   time.sleep(.5)
  else:raise AssertionError('Actual local MLflow did not start')
  command=['docker','exec','-i',name,'python','/tangerine/lab.py'];call(command+['seed']);observations=[]
  for path in packets:
   packet=json.loads(Path(path).read_bytes())
   if not packet['capture'] or not packet['trace_enabled']:continue
   assert packet['artifacts']
   exported=json.loads(call(command+['sync'],input=json.dumps(packet).encode()).stdout)
   verified=json.loads(call(command+['verify'],input=json.dumps(exported).encode()).stdout)
   assert exported['provider_calls']==0 and verified['status']=='observed' and verified['provider_calls']==0 and not verified['discrepancies']
   row=dict(operation=packet['operation'],packet=str(path),exported=exported,verified=verified);observations.append(row);(evidence/('operation-'+packet['operation']+'.json')).write_text(json.dumps(row,indent=2))
  assert observations
  missing_script="import mlflow,json,tempfile;from mlflow import MlflowClient;c=MlflowClient();rejected=False\ntry:\n with tempfile.TemporaryDirectory() as d:c.download_artifacts('"+observations[0]['exported']['run']+"','required-but-absent-i16.json',d)\nexcept Exception:rejected=True\nassert rejected;print(json.dumps({'missing_rejected':rejected}))"
  missing=json.loads(call(['docker','exec',name,'python','-c',missing_script]).stdout)
  result=dict(status='observed',mlflow='3.17.0',model_calls=0,operations=len(observations),missing_rejected=missing['missing_rejected'],items=observations)
  (evidence/'readback.json').write_text(json.dumps(result,indent=2));return result
 finally:
  call(['docker','rm','-f','-v',name],check=False);call(['docker','rm','-f',name+'-native'],check=False);call(['docker','image','rm',name+'-api:local'],check=False)
if __name__=='__main__':
 import sys
 root=Path(sys.argv[1]);print(json.dumps(export_packets(sorted(root.glob('diagnostic-*.json')),Path(sys.argv[2]))))
