"""Read sanitized native diagnostic assets for this one authored development flow.
No inference, secret export, configuration mutation or application deployment.
"""
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[2]
O=R/'data/linguistic-fullness-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}


def docker(*args,input=None):
    p=subprocess.run(['docker',*args],input=input,cwd=R,env=ENV,capture_output=True,timeout=60)
    if p.returncode:
        (O/'diagnostic-read-error.log').write_bytes(p.stderr)
        raise SystemExit('Native diagnostic read failed; no inference retry')
    return p.stdout


flow=O/'flow'
blueprint=json.loads((flow/'blueprint.json').read_text())
binding=json.loads((flow/'flow-binding.json').read_text())
attempt=json.loads((flow/'attempt-start.json').read_text())
needles=[blueprint['id'],binding['preparation_id'],binding['case_id'],attempt['attempt_id'],'shall is never correct in a British offer']
ids=docker('exec','tangerine-local-postgres-1','psql','-U','tangerine','-d','tangerine','-tA','-c',"SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked' ORDER BY o.started_at DESC LIMIT 64").decode().splitlines()
dest=flow/'native-diagnostics';dest.mkdir(exist_ok=True)
selected=[]
for identity in ids:
    identity=identity.strip()
    if not identity:continue
    raw=docker('exec','-i','tangerine-local-api-1','/usr/local/bin/tangerine','lab',input=json.dumps(dict(action='diagnostic-read',id=identity)).encode())
    # Do not retain unrelated records, including a user's parallel operation.
    if not any(needle.encode() in raw for needle in needles):continue
    p=dest/(identity+'.json');p.write_bytes(raw);p.chmod(0o600)
    selected.append(identity)
(flow/'native-diagnostic-index.json').write_text(json.dumps(dict(asset_ids=selected,selection='Exact authored blueprint/preparation/published case/attempt IDs or distinctive authored negative assertion',inference_calls=0),indent=2)+'\n')
print(json.dumps(dict(selected_native_diagnostics=len(selected),readback_inference_calls=0)))
