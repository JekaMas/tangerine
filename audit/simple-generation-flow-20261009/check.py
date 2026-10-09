"""Static specification/contract-slice checks; no application or provider execution."""
import copy, hashlib, json, re, subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse
R=Path(__file__).resolve().parents[2]; V=R/'specification/v2'; A=Path(__file__).resolve().parent
Y=json.loads(subprocess.check_output(['node',str(A/'yaml-snapshot.cjs')],cwd=R,text=True)); checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(n):return json.loads((V/'contracts'/f'{n}.schema.json').read_text())
def check(name,ok,detail=None):
 checks.append(dict(id=name,status='pass' if ok else 'fail',detail=detail));assert ok,name

def pair(name,fixture,predicate,break_it):
 check(name+'.positive',predicate(fixture),'Static specified-contract observation, not implemented behavior')
 broken=copy.deepcopy(fixture);break_it(broken);check(name+'.negative',not predicate(broken),'Constructed counterexample rejected by the same contract-slice oracle')
# Relevant request-schema slice, not a general JSON Schema engine.
def valid(schema,value):
 if '$ref' in schema:return valid(get(Path(schema['$ref'].split('#')[0]).name.removesuffix('.schema.json')),value)
 if 'anyOf' in schema and not any(valid(s,value) for s in schema['anyOf']):return False
 if 'enum' in schema and value not in schema['enum']:return False
 if 'const' in schema and value!=schema['const']:return False
 typ=schema.get('type')
 if typ=='object':
  if not isinstance(value,dict):return False
  if any(k not in value for k in schema.get('required',[])):return False
  if schema.get('additionalProperties') is False and set(value)-set(schema.get('properties',{})):return False
  if any(not valid(s,value[k]) for k,s in schema.get('properties',{}).items() if k in value):return False
 if typ=='array':
  if not isinstance(value,list):return False
  if 'items'in schema and any(not valid(schema['items'],x) for x in value):return False
 if typ=='string' and (not isinstance(value,str) or len(value)<schema.get('minLength',0)):return False
 if typ=='integer' and (not isinstance(value,int) or isinstance(value,bool) or value<schema.get('minimum',-10**20)):return False
 if typ=='boolean' and not isinstance(value,bool):return False
 if typ=='null' and value is not None:return False
 return True
req=get('exercise-request');minimal=dict(topic='Preparing dinner',speaker_count=2,text_length_words=150)
pair('minimal_three_inputs',minimal,lambda x:valid(req,x),lambda x:x.pop('topic'))
pair('positive_speaker_count',minimal,lambda x:valid(req,x),lambda x:x.update(speaker_count=0))
pair('optional_level_and_broad_families',dict(**minimal,english_level='B2',category_families=['grammar','lexis','pronunciation']),lambda x:valid(req,x),lambda x:x.update(english_level='B9'))
pair('unconstrained_level_and_control_only',dict(**minimal,english_level=None,mutation_count=0),lambda x:valid(req,x),lambda x:x.update(mutation_count=-1))
pair('blueprint_minimal_branch',get('blueprint-write'),lambda x:any(b['required']==['exercise_request'] for b in x.get('anyOf',[])) and x['properties']['exercise_request']['$ref']=='exercise-request.schema.json',lambda x:x.update(anyOf=x['anyOf'][:1]))
pair('nullable_duration_and_cefr',get('blueprint'),lambda x:any(v.get('type')=='null' for v in x['properties']['duration_ms_min']['anyOf']) and any(v.get('type')=='null' for v in x['properties']['speakers']['items']['properties']['learner_cefr']['anyOf']),lambda x:x['properties']['duration_ms_min'].update(anyOf=[{'type':'integer'}]))
generation=get('generation-input')
pair('phase_and_saved_canonical_identity',generation,lambda x:all(k in x['required'] for k in ['phase','canonical_script','canonical_script_sha256']) and len(x['allOf'])==2 and x['properties']['phase']['enum']==['canonical_text','mutation'],lambda x:x['required'].remove('canonical_script_sha256'))
pair('phase_null_nonnull_contract',generation,lambda x:x['allOf'][0]['then']['properties']['canonical_script']=={'type':'null'} and x['allOf'][1]['then']['properties']['canonical_script'].get('$ref')=='case-candidate.schema.json',lambda x:x['allOf'][1]['then']['properties'].update(canonical_script={'type':'null'}))
manifest=Y['prompts'];pair('two_generation_prompt_bindings',manifest,lambda x:{b.get('phase') for b in x['bindings'] if b['stage']=='case_generation'}=={'canonical_text','mutation'},lambda x:x['bindings'].pop(0))
flow=(V/'docs/simple-generation-flow.md').read_text()
pair('canonical_failure_and_replay_preserve_saved_artifacts',{'text':flow},lambda x:all(t in x['text'] for t in ['Save the exact canonical record and hash before','rather than rewrite its text','Reopening/replaying uses stored audio','Synthesis failure leaves the saved text/list']),lambda x:x.update(text=x['text'].replace('Reopening/replaying uses stored audio','Always synthesize playback')))
pair('novelty_not_hidden_training_distribution',{'text':flow},lambda x:'novel instances, contexts and combinations' in x['text'] and "not proof that text is absent from a proprietary LLM's training distribution" in x['text'],lambda x:x.update(text=x['text'].replace('not proof that text is absent','proof that text is absent')))
profiles=Y['providers.v1']['profiles'];local=next(p for p in profiles if p['id']=='kokoro-local-en-v1')
pair('local_speech_no_service_key_or_qualification_claim',local,lambda x:x['credentials']==[] and x['live_verified'] is False and x['roles']==['tts'],lambda x:x.update(live_verified=True))
pair('optional_case_review_setting',get('configuration'),lambda x:x['properties']['case_review_enabled']['default'] is False and 'case_review_enabled' not in x['required'] and x['properties']['speech_profile']['default']=='azure-standard-en-v1',lambda x:x['properties']['case_review_enabled'].update(default=True))
source=Y['corpus-sources.v1'];baseline=Y['baseline_sources']
pair('eleven_original_complete_source_scopes',source,lambda x:len(x['sources'])==11 and x['sources']==baseline['sources'],lambda x:x['sources'].pop())
pair('generated_origin_not_full_corpus_claim',source,lambda x:any(c['id']=='GENERATED-EXERCISE' and c['full_release_acquisition_applicable'] is False for c in x['content_sources']),lambda x:x['content_sources'][0].update(full_release_acquisition_applicable=True))
pair('ordinary_key_optional_reference_data',{'text':flow},lambda x:'saved mutation list is the answer key' in x['text'] and 'not dependencies of this flow' in x['text'] and 'Empty optional review_decisions is valid' in x['text'],lambda x:x.update(text=x['text'].replace('not dependencies of this flow','mandatory dependencies')))
pair('semantic_match_and_hidden_key',{'text':flow},lambda x:'category synonyms and valid alternative corrections' in x['text'] and 'stay hidden until submission' in x['text'] and 'Duplicate fragments do not multiply credit' in x['text'],lambda x:x.update(text=x['text'].replace('Duplicate fragments do not multiply credit','Duplicates multiply credit')))
for n in ['feedback','feedback-output']:
 d=get(n);component=d['properties']['items']['items']['properties']
 pair(n+'_recommendations_without_human_gate',component,lambda x:'recommendation' in x['kind']['enum'] and {'llm_grounded','practice_recommendation'}<=set(x['grounding_status']['enum']),lambda x:x['grounding_status']['enum'].remove('practice_recommendation'))
pair('practice_not_heard_defect_and_score_survives',{'text':flow},lambda x:'not unheard defects in the recording' in x['text'] and 'Feedback failure preserves the score and saved answer' in x['text'],lambda x:x.update(text=x['text'].replace('Feedback failure preserves the score and saved answer','Feedback failure deletes results')))
tax=Y['error-taxonomy.v1'];metrics=Y['metrics.v1'];recipes=json.loads((V/'domain/mutation-recipes.v1.json').read_text())
check('all_122_leaves_and_recipes',len(tax['items'])==122 and len(recipes['recipes'])==122 and {r['taxonomy_id'] for r in recipes['recipes']}=={x['id'] for x in tax['items']})
check('all_42_formula_definitions',len(metrics['metrics'])==27 and len(metrics['auxiliary_metrics'])==15)
for p in ['domain/error-taxonomy.v1.yaml','domain/metrics.v1.yaml','domain/mutation-recipes.v1.json']:
 before=subprocess.check_output(['git','show','b654e64:specification/v2/'+p],cwd=R);check('byte_preservation:'+p,(V/p).read_bytes()==before)
check('original_source_registry_fields_preserved',{k:v for k,v in source.items() if k!='content_sources'}==baseline)
check('original_azure_profile_and_four_voices_preserved',next(p for p in profiles if p['id']=='azure-standard-en-v1')==json.loads(subprocess.check_output(['node','-e',"const Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let d=Y.parse(require('child_process').execFileSync('git',['show','b654e64:specification/v2/domain/providers.v1.yaml'],{encoding:'utf8'}));process.stdout.write(JSON.stringify(d.profiles.find(p=>p.id==='azure-standard-en-v1')));"],cwd=R)))
# Whole current mechanical coverage: syntax, local schema references, field pointers/hashes.
json_files=list(V.rglob('*.json'));objects={str(p.relative_to(V)):json.loads(p.read_text()) for p in json_files}
def pointer(obj,fragment):
 for key in unquote(fragment).lstrip('/').split('/') if fragment else []:obj=obj[int(key)] if isinstance(obj,list) else obj[key.replace('~1','/').replace('~0','~')]
 return obj
refs=0
for path,obj in objects.items():
 def walk(node):
  global refs
  if isinstance(node,dict):
   if '$ref'in node:
    url=urlparse(node['$ref']);target=(V/path).parent/unquote(url.path) if not url.scheme else V/'contracts'/Path(url.path).name
    if not url.path:target=V/path
    pointer(json.loads(target.read_text()),url.fragment);refs+=1
   for child in node.values():walk(child)
  elif isinstance(node,list):
   for child in node:walk(child)
 walk(obj)
check('all_current_JSON_syntax_and_local_refs',True,dict(files=len(json_files),refs=refs))
check('all_current_YAML_syntax',Y['yaml_files_parsed']==len(list(V.rglob('*.yaml'))))
records=objects['domain/persistence-map.json']['records'];flat=[]
for r in records:
 p=V/r['schema'];obj=json.loads(p.read_text());check('schema_index_hash:'+r['kind'],sha(p)==r['sha256'] and Y['semantic-invariants']['schemas'][r['kind']]['schema_sha256']==sha(p))
 for f in r['fields']:
  rule=pointer(obj,f['pointer']);assert hashlib.sha256(json.dumps(rule,separators=(',',':')).encode()).hexdigest()==f['rule_sha256'],(r['kind'],f['pointer'])
  flat.append(dict(schema=p.name,**f))
index=objects['language/field-index.json'];check('exact_complete_field_index',index['fields']==flat and index['field_count']==len(flat) and index['schema_count']==len(records)==len(list((V/'contracts').glob('*.schema.json'))))
for binding in manifest['bindings']:
 check('prompt_binding:'+binding['stage']+':'+binding.get('phase','single'),sha(V/binding['path'])==binding['prompt_sha256'] and sha(V/'contracts'/binding['input_schema'])==binding['input_schema_sha256'] and sha(V/'contracts'/binding['output_schema'])==binding['output_schema_sha256'])
for operation in Y['operation-ownership']['operations']:
 if operation.get('request_schema') and not operation['request_schema'].startswith('binary:'):
  schema=get(operation['request_schema']);assert set(operation['request_fields'])==set(schema['properties']),(operation['id'],set(operation['request_fields'])^set(schema['properties']))
check('all_operation_request_field_ownership',True,len(Y['operation-ownership']['operations']))
vector=Y['version-compatibility']['files'];check('complete_current_version_vector',all(sha(V/x['path'])==x['sha256'] for x in vector) and {x['path'] for x in vector}=={p.relative_to(V).as_posix() for p in V.rglob('*') if p.is_file() and p!=V/'domain/version-compatibility.yaml'})
graph=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());new=[c for c in graph['cases'] if c['property_id'].startswith('FLOW-')]
check('24_new_positive_negative_behavior_plans_only',len(new)==24 and all(c['state']=='blocked' and c['source_sha256'] is None for c in new) and all({c['polarity'] for c in new if c['property_id']==f'FLOW-{i:02}.P1'}=={'positive','negative'} for i in range(1,7)))
modified=subprocess.check_output(['git','diff','--name-only','b654e64'],cwd=R,text=True).splitlines()
check('no_application_or_immutable_source_input_edits',not any(p.startswith(('services/','tests/','deploy/','scripts/','spec-inputs/')) for p in modified))
result=dict(status='passed',proof_boundary='Static specification/contract slices, all JSON/YAML/ref/index/hash metadata and baseline preservation only; no formal full-schema compilation, application, LLM, audio synthesis or acoustic-fidelity test.',checks=checks,passed=len(checks),schema_count=len(records),field_count=len(flat),json_files=len(json_files),yaml_files=Y['yaml_files_parsed'],schema_refs=refs,current_namespace_files=len(vector)+1,graph=dict(requirements=len(graph['requirements']),properties=len(graph['properties']),edges=len(graph['cases'])))
(A/'validation-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
