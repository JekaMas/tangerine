"""Read the named synthetic exercise through native storage; never infer."""
import json, os, subprocess, urllib.request
from pathlib import Path

R = Path(__file__).resolve().parents[2]
O = R / 'data/recurring-errors-20261025'
ENV = {**os.environ, 'DOCKER_HOST': 'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',
       'DOCKER_CONFIG': str(R / 'data/local-preview/docker-config')}
PREPARATION = 'a6e1b2ba-5b73-4790-b9ed-4f471a8c1f21'
BLUEPRINT = '5f8c8bc5-2d4e-4877-a720-755cf43ba9fe'

def docker(*args, input=None):
    p = subprocess.run(['docker', *args], input=input, env=ENV, cwd=R, capture_output=True, timeout=120)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[-900:])
    return p.stdout

def sql(query):
    return docker('exec', 'tangerine-local-postgres-1', 'psql', '-U', 'tangerine', '-d', 'tangerine', '-tA', '-c', query)

def save(name, value):
    path = O / name
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    path.chmod(0o600)

def get(path):
    return json.load(urllib.request.urlopen('http://localhost:3000/api/v1/' + path, timeout=15))

if __name__ == '__main__':
    prep = json.loads(sql("SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='preparation-state' AND h.id='" + PREPARATION + "'"))
    save('demo-preparation-state.json', prep)
    assert prep['phase_states'] == dict(canonical_text='complete', mutation='complete', render='complete')
    settings = json.loads(docker('exec', '-i', 'tangerine-local-api-1', '/usr/local/bin/tangerine', 'lab', input=json.dumps({'action': 'diagnostic-read', 'id': prep['settings_asset_id']}).encode()))
    save('demo-blueprint.json', settings['blueprint'])
    save('demo-key.json', json.loads(sql("SELECT payload FROM document WHERE kind='ground-truth' AND id='" + prep['key_id'] + "'")))
    (O / 'demo-dialogue.wav').write_bytes(urllib.request.urlopen('http://localhost:3000/api/v1/preparations/' + PREPARATION + '/audio', timeout=15).read())
    attempts = json.loads((O / 'demo-attempt-ids.json').read_text())
    for label, identity in attempts.items():
        save(label + '-attempt.json', get('attempts/' + identity))
        save(label + '-results.json', get('attempts/' + identity + '/results'))
    needles = [PREPARATION, BLUEPRINT, '62eb518a-1291-5b6a-bbd3-39f60803d481', *attempts.values(), 'all plural nouns must end', 'final line']
    dest = O / 'native-diagnostics'
    dest.mkdir(exist_ok=True)
    ids = sql("SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked' ORDER BY o.started_at DESC LIMIT 100").decode().splitlines()
    selected = []
    for identity in ids:
        raw = docker('exec', '-i', 'tangerine-local-api-1', '/usr/local/bin/tangerine', 'lab', input=json.dumps({'action': 'diagnostic-read', 'id': identity}).encode())
        if not any(v.encode() in raw for v in needles):
            continue
        p = dest / (identity + '.json')
        p.write_bytes(raw)
        p.chmod(0o600)
        selected.append(identity)
    save('native-diagnostics.json', {'asset_ids': selected, 'scope': 'Named synthetic recurring exercise and two exact attempts', 'readback_inference_calls': 0})
    print(json.dumps({'native_diagnostics': len(selected), 'attempts': list(attempts)}))
