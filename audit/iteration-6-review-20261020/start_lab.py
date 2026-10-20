"""Start an owned local MLflow observer with the exact native binary; no inference."""
from pathlib import Path
import json,os,subprocess,time,uuid
R=Path(__file__).resolve().parents[2];name='tangerine-i6-observer-'+uuid.uuid4().hex[:8];root=R/'data/iteration6-review-20261020'/name;root.mkdir(parents=True,exist_ok=True)
def call(args,check=True):
 p=subprocess.run(args,cwd=R,env=os.environ,capture_output=True,text=True,timeout=180)
 if check and p.returncode:raise RuntimeError('Observer command failed: '+p.stderr[-2000:])
 return p
image=name+'-api:local';call(['docker','build','-t',image,'-f','services/api/Dockerfile','.']);temporary=call(['docker','create',image]).stdout.strip()
try:call(['docker','cp',temporary+':/usr/local/bin/tangerine',str(root/'native')])
finally:call(['docker','rm',temporary],False)
network=name;call(['docker','network','create',network]);(root/'lab').mkdir(exist_ok=True)
args=['docker','run','-d','--name',name,'--network',network,'--network-alias','llm-lab','-e','MLFLOW_DISABLE_TELEMETRY=true','-e','DO_NOT_TRACK=true','-e','MLFLOW_TRACKING_URI=http://llm-lab:5000']
for source,target in [(root/'lab','/lab'),(root/'native','/tangerine/native'),(R/'deploy/local/lab.py','/tangerine/lab.py'),(R/'specification/v2','/tangerine/spec'),(R/'services/api/internal/lab/builtin.json','/tangerine/builtin.json'),(R/'services/api/internal/contracts','/tangerine/source/contracts'),(R/'services/api/internal/provider','/tangerine/source/provider'),(R/'services/api/internal/app','/tangerine/source/app')]:args+=['-v',str(source)+':'+target+('' if target=='/lab' else ':ro')]
args+=['tangerine-mlflow-upstream:3.17.0','mlflow','server','--host','0.0.0.0','--port','5000','--backend-store-uri','sqlite:////lab/mlflow.db','--artifacts-destination','/lab/artifacts','--allowed-hosts','localhost,127.0.0.1,llm-lab,llm-lab:5000']
try:
 call(args)
 for n in range(90):
  if call(['docker','exec',name,'python','-c',"import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/health',timeout=2)"],False).returncode==0:break
  time.sleep(1)
 else:raise RuntimeError('Owned observer did not become ready')
 receipt={'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'container':name,'network':network,'image':image,'data':str(root.relative_to(R)),'provider_calls':0};(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
except BaseException:
 call(['docker','rm','-f',name],False);call(['docker','network','rm',network],False);raise
