"""Restore temporary Lab flags and read back unchanged original user records."""
import json, urllib.request, uuid
from pathlib import Path
R = Path(__file__).resolve().parents[2]
O = R / 'data/recurring-errors-20261025'
base = json.loads((O / 'configuration-before.json').read_text())
url = 'http://localhost:3000/api/v1/configuration'
with urllib.request.urlopen(url, timeout=15) as r:
    restored, etag = json.load(r), r.headers['ETag']
if base['configuration'] != restored['configuration']:
    body = dict(base['configuration'])
    for field in ['workspace_id', 'configuration_sha256', 'provider_access_policy']:
        body.pop(field, None)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='PUT', headers={'Content-Type': 'application/json', 'Origin': 'http://localhost:3000', 'If-Match': etag, 'Idempotency-Key': str(uuid.uuid4())})
    with urllib.request.urlopen(req, timeout=15) as r:
        restored = json.load(r)
original = json.loads((O / 'attempt-before.json').read_text())
now = json.load(urllib.request.urlopen('http://localhost:3000/api/v1/attempts/' + original['attempt_id'], timeout=15))
assert now == original
assert base['configuration'] == restored['configuration']
assert [(x['name'], x['present']) for x in base['credentials']] == [(x['name'], x['present']) for x in restored['credentials']]
providers, billings, engines, profiles, stages = set(), set(), set(), set(), []
for path in (O / 'native-diagnostics').glob('*.json'):
    packet = json.loads(path.read_text())
    for artifact in packet['artifacts']:
        try:
            value = json.loads(artifact.get('body', ''))
        except (ValueError, TypeError):
            continue
        if not isinstance(value, dict):
            continue
        for doc in value.get('documents', []):
            if doc.get('kind') == 'effective-binding':
                b = doc['payload']
                providers.add(b['provider'])
                billings.add(b['billing_mode'])
                stages.append(b['stage'])
        if packet['origin'] != 'native_speech_transport':
            continue
        for asset in value.get('wire_assets', []):
            wire = json.loads(asset['body'])
            if 'profile' in wire:
                assert wire['profile']['billing_mode'] == 'local'
                profiles.add(wire['profile']['provider'])
            if 'receipt' in wire:
                engines.add(wire['receipt']['provider'])
assert providers == {'openai_chatgpt'} and billings == {'included_subscription'}
assert engines == {'local_melo'} and profiles == {'local_english_accents'}
result = dict(original_attempt_unchanged=True, configuration_restored=True, credential_presence_unchanged=True, provider_bindings=sorted(providers), billing_modes=sorted(billings), speech_providers=sorted(engines), speech_profiles=sorted(profiles), actual_text_stages=sorted(stages), billing_evidence='Retained native bindings; browser purchased-credit use and automatic reload off; no API-key fallback.', original_attempt_id=original['attempt_id'])
(O / 'preservation.json').write_text(json.dumps(result, indent=2) + '\n')
(O / 'configuration-restored.json').write_text(json.dumps(restored, indent=2) + '\n')
print(json.dumps(result))
