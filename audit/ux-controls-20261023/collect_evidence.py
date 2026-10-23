"""Read only this increment's native captures, then export/read back locally.

No inference, provider/financial settings change or unrelated artifact export.
"""
import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/ux-controls-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
def docker(*args,input=None):
 p=subprocess.run(['docker',*args],input=input,env=ENV,cwd=R,capture_output=True,timeout=90)
 if p.returncode:raise RuntimeError(p.stderr.decode()[-900:])
 return p.stdout
needles=[]
for label in ['minor','zero']:
 v=json.loads((O/'flow'/label/'binding.json').read_text());needles.extend(v[k] for k in ['blueprint_id','preparation_id','case_id'])
ids=docker('exec','tangerine-local-postgres-1','psql','-U','tangerine','-d','tangerine','-tA','-c',"SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked' ORDER BY o.started_at DESC LIMIT 40").decode().splitlines()
dest=O/'native-diagnostics';dest.mkdir(exist_ok=True);selected=[]
for identity in ids:
 identity=identity.strip()
 if not identity:continue
 raw=docker('exec','-i','tangerine-local-api-1','/usr/local/bin/tangerine','lab',input=json.dumps({'action':'diagnostic-read','id':identity}).encode())
 if not any(v.encode() in raw for v in needles):continue
 p=dest/(identity+'.json');p.write_bytes(raw);p.chmod(0o600);selected.append(identity)
(O/'native-diagnostics.json').write_text(json.dumps({'asset_ids':selected,'scope':'Exact two authored blueprint/preparation/case associations','readback_inference_calls':0},indent=2)+'\n')
print(json.dumps({'native_diagnostics':len(selected),'first_packet_keys':list(json.loads((dest/(selected[0]+'.json')).read_text())) if selected else []}))
