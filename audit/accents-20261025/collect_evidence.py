"""Read this increment's saved artifacts; no inference or provider changes."""
import json,os,subprocess,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/accents-20261025'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
def docker(*args,input=None):
 p=subprocess.run(['docker',*args],input=input,env=ENV,cwd=R,capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr.decode()[-900:])
 return p.stdout
prep=json.loads((O/'demo-preparation-state.json').read_text())
needles=[prep['id'],'870b0da5-e7aa-4552-ac4c-ce0bf75146ca','bf423adb-2535-42c2-87ee-e5e39c9391a4']
ids=docker('exec','tangerine-local-postgres-1','psql','-U','tangerine','-d','tangerine','-tA','-c',"SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked' ORDER BY o.started_at DESC LIMIT 50").decode().splitlines()
dest=O/'native-diagnostics';dest.mkdir(exist_ok=True);selected=[]
for identity in ids:
 identity=identity.strip()
 if not identity:continue
 raw=docker('exec','-i','tangerine-local-api-1','/usr/local/bin/tangerine','lab',input=json.dumps({'action':'diagnostic-read','id':identity}).encode())
 if not any(v.encode() in raw for v in needles):continue
 p=dest/(identity+'.json');p.write_bytes(raw);p.chmod(0o600);selected.append(identity)
(O/'native-diagnostics.json').write_text(json.dumps({'asset_ids':selected,'scope':'Exact synthetic demo blueprint/preparation/case/attempt associations','readback_inference_calls':0},indent=2)+'\n')
assert selected,'Expected actual Lab packets from temporary explicit capture'
print(json.dumps({'native_diagnostics':len(selected)}))
