"""Static observation-ledger consistency; never a provider or app test."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = Path(__file__).resolve().parent
V = R / 'specification/v2'
checks = []

def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

def pair(name, value, predicate, invalidate):
    check(name + '.positive', predicate(value))
    bad = copy.deepcopy(value)
    invalidate(bad)
    check(name + '.negative', not predicate(bad))

obs = json.loads((A / 'observations.json').read_text())
chat = obs['accounts']['chatgpt']
pair('pro_does_not_prove_tangerine_access', chat,
     lambda x: x['existing_plan_verified'] == 'pro' and not x['inference_ready_verified'],
     lambda x: x.update(inference_ready_verified=True))
pair('reload_off_does_not_prove_credit_exclusion', chat,
     lambda x: x['automatic_credit_reload'] == 'off' and x['tangerine_purchased_credit_exclusion'] == 'unobserved',
     lambda x: x.update(tangerine_purchased_credit_exclusion='verified'))
pair('prepared_signup_is_not_registered', obs['accounts']['elevenlabs'],
     lambda x: x['registration'] == 'pending_confirmation' and x['actual_plan'] == 'unobserved' and not x['api_key_created'],
     lambda x: x.update(registration='registered'))
pair('local_models_need_no_registration', obs['accounts']['local_speech'],
     lambda x: not x['registration_required'] and not x['synthesis_observed'],
     lambda x: x.update(registration_required=True))
for key in ['provider_token_exchange_observations', 'provider_inference_observations', 'audio_generation_observations', 'new_purchases']:
    check('no_unperformed_claim.' + key, obs[key] == 0)
check('no_public_credentials', obs['public_account_identifiers_or_credentials_saved'] is False)
for path in ['domain/error-taxonomy.v1.yaml', 'domain/mutation-recipes.v1.json', 'domain/metrics.v1.yaml', 'domain/corpus-sources.v1.yaml', 'domain/providers.v1.yaml', 'domain/provider-access.v1.json', 'domain/product-data-relevance.v1.json', 'domain/verification-fixtures.v1.json']:
    check('scope_preserved.' + path,
          subprocess.check_output(['git', 'show', '6fd4899:specification/v2/' + path], cwd=R) == (V / path).read_bytes())
for name in ['verification.json', 'property-inventory.json', 'discovery.json']:
    p = 'openspec/changes/implement-teacher-error-trainer/' + name
    check('graph_preserved.' + name,
          subprocess.check_output(['git', 'show', '6fd4899:' + p], cwd=R) == (R / p).read_bytes())
speech = (V / 'docs/speech-service-selection.md').read_text()
check('generation_time_free_media_rights', 'non-commercial use terms' in speech and 'does not retroactively' in speech and 'Apache-2.0 covers Tangerine software' in speech)
check('credit_control_distinction', 'Automatic reload off does not establish exclusion of existing purchased credits' in (V / 'docs/provider-access.md').read_text())
script = "const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');process.stdout.write(JSON.stringify(Y.parse(fs.readFileSync('specification/v2/domain/version-compatibility.yaml','utf8'))));"
vector = json.loads(subprocess.check_output(['node', '-e', script], cwd=R))
check('current_version_hashes', all(hashlib.sha256((V / x['path']).read_bytes()).hexdigest() == x['sha256'] for x in vector['files']))
g = json.loads((R / 'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
result = dict(status='passed', checks=len(checks), proof_boundary='Static ledger/document/hash/scope checks; account facts came from live browser readback, not this checker. No runtime qualification.', requirements=len(g['requirements']), properties=len(g['properties']), case_edges=len(g['cases']), results=checks)
(A / 'validation-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'results'}))
