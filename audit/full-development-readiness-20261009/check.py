"""Scope, plan and metadata consistency, never model/audio acceptance."""
import copy,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]; V=R/'specification/v2'; C=R/'openspec/changes/implement-teacher-error-trainer'; A=Path(__file__).resolve().parent; checks=[]
def ck(name,ok):
 if not ok:raise AssertionError(name)
 checks.append(name)
def pair(name,value,predicate,corrupt):
 ck(name+'.positive',predicate(value));bad=copy.deepcopy(value);corrupt(bad);ck(name+'.negative',not predicate(bad))
obs=json.load(open(A/'observations.json'))
pair('completed_signup_only',obs['elevenlabs'],lambda d:d['registration']=='completed' and d['creative_plan']=='Free' and not d['audio_generated'],lambda d:d.update(audio_generated=True))
pair('actual_free_pool',obs['elevenlabs'],lambda d:d['creative_credits_used']==0 and d['creative_credits_total']==10000,lambda d:d.update(creative_credits_total=100000))
pair('no_top_up',obs['elevenlabs'],lambda d:d['api_auto_top_up']=='off' and not d['paid_plan_selected'],lambda d:d.update(paid_plan_selected=True))
pair('account_is_not_api_qualification',obs['elevenlabs'],lambda d:not d['api_key_created'] and not d['api_model_listing_observed'],lambda d:d.update(api_model_listing_observed=True))
for path in ['domain/error-taxonomy.v1.yaml','domain/mutation-recipes.v1.json','domain/metrics.v1.yaml','domain/corpus-sources.v1.yaml','domain/providers.v1.yaml','domain/provider-access.v1.json','domain/product-data-relevance.v1.json']:
 ck('original_scope_bytes.'+path,subprocess.check_output(['git','show','8f89757:specification/v2/'+path],cwd=R)==(V/path).read_bytes())
g=json.load(open(C/'verification.json')); f=json.load(open(V/'domain/verification-fixtures.v1.json')); inv=json.load(open(A/'scope-inventory.json')); cases={x['case_id']:x for x in f['case_bindings']}
ck('every_property_traced',set(x['id'] for x in g['properties'])==set(x['property_id'] for x in inv['property_records']))
ck('every_case_has_binding',set(x['id'] for x in g['cases'])==set(cases))
for p in g['properties']:
 edges=[c for c in g['cases'] if c['property_id']==p['id']];ck('polarities.'+p['id'],{c['polarity'] for c in edges}=={'positive','negative'})
 for c in edges:ck('literal_binding.'+c['id'],bool(cases[c['id']]['input']) and bool(cases[c['id']]['expected']))
new=[x for x in g['cases'] if x['property_id'].startswith('READY-')];ck('new_case_count',len(new)==16)
ck('new_not_run',all(x['state']=='blocked' and cases[x['id']]['observation_state']=='not_run' for x in new))
ck('all_recipes_traced',len(inv['taxonomy_records'])==122 and all(not x['actual_audio_observed'] for x in inv['taxonomy_records']))
ck('recorded_contrasts_retained',sum(x['operator']=='recorded_contrast' for x in inv['taxonomy_records'])==5)
# Current version vector parsed by existing YAML runtime; no install.
script="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');process.stdout.write(JSON.stringify(Y.parse(fs.readFileSync('specification/v2/domain/version-compatibility.yaml','utf8'))));"
v=json.loads(subprocess.check_output(['node','-e',script],cwd=R));ck('version_vector',all(hashlib.sha256((V/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in v['files']))
sem_script=script.replace('domain/version-compatibility.yaml','domain/semantic-invariants.yaml');sem=json.loads(subprocess.check_output(['node','-e',sem_script],cwd=R))
for n in ['render-plan','speech-render-request','audio-measurement']:ck('semantic_schema_hash.'+n,sem['schemas'][n]['schema_sha256']==hashlib.sha256((V/'contracts'/f'{n}.schema.json').read_bytes()).hexdigest())
for path in [V/'README.md',V/'docs/service-setup-guide.md',V/'docs/speech-service-selection.md',V/'docs/full-development-readiness.md',V/'docs/audio-methods.md']:
 import re
 for label,target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',path.read_text()):
  if not target.startswith(('https://','http://','#')):ck('link.'+path.name+'.'+label,(path.parent/target.split('#')[0]).exists())
ck('no_human_measurement_status','human_required' not in json.load(open(V/'contracts/audio-measurement.schema.json'))['properties']['status']['enum'])
ck('new_scope_not_mvp','not an MVP' in (V/'docs/full-development-readiness.md').read_text())
ck('oauth_unobserved',obs['chatgpt']['tangerine_oauth']=='not_performed_adapter_unimplemented')
result={'status':'passed','static_checks':len(checks),'scope':[len(g['requirements']),len(g['properties']),len(g['cases'])],'actual_new_behavior_tests':0,'proof_boundary':'Static scope/binding/hash/document checks; model/audio/native packets remain not_run. Browser account facts are separate live observations.','checks':checks}
(A/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
