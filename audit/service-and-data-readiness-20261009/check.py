"""Static specification checks only. Does not simulate provider/application acceptance."""
import ast,copy,hashlib,json,subprocess
from pathlib import Path
from fractions import Fraction
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer'
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def pair(n,x,validate,mutate):
 ck(n+'.positive',validate(x));bad=copy.deepcopy(x);mutate(bad);ck(n+'.negative',not validate(bad))
def read(p):return json.loads((V/p).read_text())
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
script="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let out={};for(let p of process.argv.slice(1)){out[p]=Y.parse(fs.readFileSync(p,'utf8'));}process.stdout.write(JSON.stringify(out));"
y=json.loads(subprocess.check_output(['node','-e',script]+[str(p.relative_to(R)) for p in V.rglob('*.yaml')],cwd=R))
pol=read('domain/provider-access.v1.json');profile=pol['llm_profiles'][0];catalog=read('domain/service-research.v1.json');g=json.loads((C/'verification.json').read_text());f=read('domain/verification-fixtures.v1.json');meta=read('domain/persistence-map.json');idx=read('language/field-index.json')
pair('policy_blocks_purchased_usage',pol['policy'],lambda p:p=={'mode':'included_only','allow_purchased_credits':False,'allow_overage':False,'allow_silent_billing_fallback':False},lambda p:p.update(allow_overage=True))
pair('subscription_wire_projection',profile,lambda p:p['stream'] is True and p['store'] is False and p['max_output_tokens'] is None and p['temperature'] is None and p['auth_method']=='chatgpt_plan_oauth',lambda p:p.update(stream=False))
ck('new_registry_default',y['specification/v2/domain/configuration-registry.yaml']['internal']['llm_profile']==pol['default_llm_profile'])
ck('retained_legacy_providers',subprocess.check_output(['git','show','63c1ec7:specification/v2/domain/providers.v1.yaml'],cwd=R)==(V/'domain/providers.v1.yaml').read_bytes())
for path in ['domain/error-taxonomy.v1.yaml','domain/metrics.v1.yaml','domain/corpus-sources.v1.yaml','domain/mutation-recipes.v1.json']:
 ck('preserved_scope.'+path,subprocess.check_output(['git','show','63c1ec7:specification/v2/'+path],cwd=R)==(V/path).read_bytes())
ck('catalogue_primary_sources',len(catalog['services'])==11 and all(x['primary_sources'] and x['adapter_status']=='specified_candidate_not_implemented_or_live_qualified' for x in catalog['services']))
for s in catalog['services']:ck('source_links.'+s['id'],all(u.startswith('https://') for u in s['primary_sources']))
ck('all_original_scopes',len(y['specification/v2/domain/corpus-sources.v1.yaml']['sources'])==11)
for name in ['llm-profile','effective-binding']:
 d=read('contracts/'+name+'.schema.json');ck('auth_conditional.'+name,d['allOf'][0]['then']['properties']['stream']['const'] is True);ck('nullable_output.'+name,any(x.get('type')=='null' for x in d['properties']['max_output_tokens']['anyOf']))
connections=read('contracts/provider-connection.schema.json');ck('connection_has_no_token_fields',not {'access_token','refresh_token','id_token','code','authorization_url','code_verifier'}&set(connections['properties']))
ck('configuration_frozen_policy','provider_access_policy' in read('contracts/configuration.schema.json')['properties'])
ck('typed_speech_extensions',read('contracts/configuration.schema.json')['properties']['speech_profiles']['items']['$ref']=='speech-profile.schema.json')
ops=y['specification/v2/domain/operations.yaml']['operations'];own=y['specification/v2/domain/operation-ownership.yaml']['operations'];api=y['specification/v2/contracts/openapi.yaml'];ck('operation_identity_sets',len(ops)==len(own)==71 and {x['id'] for x in ops}=={x['id'] for x in own})
for op in ops:ck('operation_wire.'+op['id'],api['paths'][op['path']][op['method'].lower()]['operationId']==op['id'])
callback=api['paths']['/auth/callback']['get'];ck('callback_is_query_only','requestBody' not in callback and {x['name'] for x in callback['parameters']}==set(read('contracts/provider-callback-query.schema.json')['properties']))
ck('callback_state_required',next(x for x in callback['parameters'] if x['name']=='state')['required'] is True)
# Reconcile every schema field hash and local ref (shape/reference check, not a JSON Schema engine).
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='fields'];exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
flat=[]
for record in meta['records']:
 p=V/record['schema'];ck('schema_hash.'+record['schema'],sh(p)==record['sha256']);ff=fields(json.loads(p.read_text()));ck('schema_fields.'+record['schema'],ff==record['fields']);flat.extend(dict(schema=p.name,**x) for x in ff)
ck('field_index',idx==dict(schema_count=len(meta['records']),field_count=len(flat),fields=flat))
def refs(node,base):
 if isinstance(node,dict):
  ref=node.get('$ref')
  if ref and not ref.startswith(('https:','http:')):
   file,_,pointer=ref.partition('#');p=base.parent/file if file else base;ck('ref_file.'+ref,p.exists());obj=json.loads(p.read_text())
   for token in pointer.removeprefix('/').split('/') if pointer else []:obj=obj[int(token)] if isinstance(obj,list) else obj[token.replace('~1','/').replace('~0','~')]
  for x in node.values():refs(x,base)
 elif isinstance(node,list):
  for x in node:refs(x,base)
for p in (V/'contracts').glob('*.schema.json'):refs(json.loads(p.read_text()),p)
props={x['id'] for x in g['properties']};cases={x['id'] for x in g['cases']};ck('all_property_fixture_bindings',{x['property_id'] for x in f['property_bindings']}==props);ck('all_case_fixture_bindings',{x['case_id'] for x in f['case_bindings']}==cases)
ck('24new_behavior_plans_not_run',len([x for x in g['cases'] if x['id'].startswith('CAP-')])==24 and all(x['state']=='blocked' and x['fixture_observation_state']=='not_run' for x in g['cases'] if x['id'].startswith('CAP-')))
for b in f['case_bindings']:
 if b['case_id'].startswith('CAP-'):ck('concrete_packet.'+b['case_id'],bool(b['input']) and bool(b['expected']) and b['observation_state']=='not_run')
pair('independent_association_fractions',{'N':100,'nA':20,'nB':10,'nAB':5},lambda x:Fraction(x['nAB'],x['N'])==Fraction(1,20) and Fraction(x['nAB'],x['nA'])==Fraction(1,4) and Fraction(x['nAB']*x['N'],x['nA']*x['nB'])==Fraction(5,2),lambda x:x.update(nAB=4))
text='three then three';pair('pronunciation_scope',{'start':11,'end':16},lambda x:text[x['start']:x['end']]=='three' and x['start']!=0,lambda x:x.update(start=0,end=5))
for n,phrases in {'provider-access.md':['dynamic_agent_client','chatgpt.tokens.use.direct','response.completed','subscription_sharing_usage_limit_exceeded','disable using credits','no application login','max_output_tokens'],'speech-service-selection.md':['pronunciation_dictionary_locators','VoiceDesign','F0','no top-up','speech-profile.schema.json'],'empirical-data-needs.md':['732','122','unknown/N/A','unrated','companion is not a substitute','no external empirical dataset']}.items():
 text=(V/'docs'/n).read_text().lower()
 for phrase in phrases:ck('declared_contract.'+phrase,phrase.lower() in text)
result=dict(status='passed',checks=len(checks),schemas=len(meta['records']),fields=len(flat),internal_operations=len(ops),properties=len(props),case_edges=len(cases),new_behavior_plans=24,actual_provider_or_audio_observations=0,proof_boundary='Static specification/reference/metadata consistency and independently stated constructed arithmetic/scope only; not JSON Schema engine, application, account eligibility/billing, LLM quality, speech realization or Lab execution.',results=checks)
(A/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='results'}))
