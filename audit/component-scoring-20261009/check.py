"""Affected static contract integrity and independent constructed arithmetic.

No application/reference imports, JSON Schema engine conformance, model/audio/Lab execution.
"""
import ast,copy,hashlib,json,subprocess
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote,urlparse
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(name,condition,detail='Static artifact integrity or declared shape; not behavior proof'):
 checks.append(dict(id=name,status='passed' if condition else 'failed',detail=detail));assert condition,name
def pair(name,fixture,predicate,mutate):
 ck(name+'.positive',predicate(fixture));bad=copy.deepcopy(fixture);mutate(bad);ck(name+'.negative',not predicate(bad),'Constructed rejected counterexample; no application/provider execution')
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let d={};function walk(p){for(let x of fs.readdirSync(p,{withFileTypes:true})){let f=p+'/'+x.name;if(x.isDirectory())walk(f);else if(/\\.ya?ml$/.test(f))d[f.replace('specification/v2/','')]=Y.parse(fs.readFileSync(f,'utf8'));}}walk('specification/v2');process.stdout.write(JSON.stringify(d));"""
y=json.loads(subprocess.check_output(['node','-e',node],cwd=R));j={p.relative_to(V).as_posix():json.loads(p.read_text()) for p in V.rglob('*.json')};ck('active_json_yaml_parse',len(j)>130 and len(y)>10)
refs=[]
def walk(x,p):
 if isinstance(x,dict):
  if '$ref' in x:
   u=urlparse(x['$ref'])
   if not u.scheme:
    target=p if not u.path else p.parent/unquote(u.path);assert target.is_file(),(p,x['$ref']);q=json.loads(target.read_text())
    for part in unquote(u.fragment).lstrip('/').split('/') if u.fragment else []:q=q[int(part)] if isinstance(q,list) else q[part.replace('~1','/').replace('~0','~')]
    refs.append((p,x['$ref']))
  for z in x.values():walk(z,p)
 elif isinstance(x,list):
  for z in x:walk(z,p)
for p in V.rglob('*.schema.json'):walk(json.loads(p.read_text()),p)
ck('all_local_schema_references_resolve',len(refs)>80)
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='fields'];exec(compile(ast.Module(body=nodes,type_ignores=[]),'fields_helper','exec'))
meta=j['domain/persistence-map.json'];flat=[]
for r in meta['records']:
 ck('schema_metadata.'+r['kind'],sha(V/r['schema'])==r['sha256'] and fields(j[r['schema']])==r['fields']);flat += [dict(schema=Path(r['schema']).name,**f) for f in r['fields']]
idx=j['language/field-index.json'];ck('all_field_metadata',idx['schema_count']==len(meta['records']) and idx['fields']==flat and idx['field_count']==len(flat))
for kind,r in y['domain/semantic-invariants.yaml']['schemas'].items():ck('semantic_schema_binding.'+kind,sha(V/r['schema'])==r['schema_sha256'])
vector=y['domain/version-compatibility.yaml']['files'];actual={p.relative_to(V).as_posix() for p in V.rglob('*') if p.is_file()}-{'domain/version-compatibility.yaml'};ck('complete_active_vector',set(x['path'] for x in vector)==actual and all(sha(V/x['path'])==x['sha256'] for x in vector))
for b in y['prompts/manifest.yaml']['bindings']:ck('prompt_binding.'+b['prompt_id'],sha(V/b['path'])==b['prompt_sha256'] and sha(V/'contracts'/b['input_schema'])==b['input_schema_sha256'] and sha(V/'contracts'/b['output_schema'])==b['output_schema_sha256'])
for op in y['domain/operation-ownership.yaml']['operations']:
 path='contracts/'+str(op.get('request_schema'))+'.schema.json'
 if path in j and 'properties' in j[path]:ck('operation_request_fields.'+op['id'],set(op['request_fields'])==set(j[path]['properties']))
for p in ['domain/error-taxonomy.v1.yaml','domain/metrics.v1.yaml','domain/mutation-recipes.v1.json','domain/corpus-sources.v1.yaml','domain/providers.v1.yaml','domain/llm-quality-metrics.v1.json','domain/ai-development.v1.json']:
 old=subprocess.check_output(['git','show','98cefcc:specification/v2/'+p],cwd=R);ck('protected_bytes.'+p,old==(V/p).read_bytes())
def schema(n):return j['contracts/'+n+'.schema.json']
components=schema('evaluator-output')['properties']['decisions']['items']['properties']
for name in ['correction','explanation']:
 pair('typed_extra_assertions.'+name,components[name],lambda x:'additional_assertions' in x['required'] and set(x['properties']['additional_assertions']['items']['required'])=={'start_cp','end_cp','exact_text','judgment','reason'} and set(x['properties']['additional_assertions']['items']['properties']['judgment']['enum'])=={'supported','unsupported','unknown'},lambda x:x['required'].remove('additional_assertions'))
pair('issue_scope',schema('judgment-issue'),lambda x:'affected_components' in x['required'] and x['properties']['blocks_final_score'].get('type')=='boolean' and 'const' not in x['properties']['blocks_final_score'],lambda x:x['properties']['blocks_final_score'].update(const=True))
for name in ['explanation_credit','correction_credit']:
 pair('nullable_credit.'+name,schema('scoring-input')['properties']['decisions']['items']['properties'][name],lambda x:any(a.get('type')=='null' for a in x.get('anyOf',[])),lambda x:x.update(anyOf=[a for a in x['anyOf'] if a.get('type')!='null']))
for name in ['EK','EQ','CK','CQ']:
 pair('nullable_stat.'+name,schema('score-result')['properties']['sufficient_statistics']['anyOf'][0]['properties'][name],lambda x:any(a.get('type')=='null' for a in x.get('anyOf',[])),lambda x:x.update(anyOf=[a for a in x['anyOf'] if a.get('type')!='null']))
pair('frozen_scoring_input_policy',schema('scoring-input'),lambda x:'scoring_policy_version' in x['required'],lambda x:x['required'].remove('scoring_policy_version'))
text='Use works because she is singular 🙂 and every English verb ends in s.';start=text.index('every');assertion=dict(start_cp=start,end_cp=len(text)-1,exact_text=text[start:-1],judgment='unsupported',reason='English verb morphology depends on person, tense and the verb; this universal claim is false.')
pair('actual_unicode_assertion_span',assertion,lambda x:0<=x['start_cp']<x['end_cp']<=len(text) and text[x['start_cp']:x['end_cp']]==x['exact_text'],lambda x:x.update(start_cp=x['start_cp']+1))
pair('supported_assertion_kind',assertion,lambda x:x['judgment'] in ['supported','unsupported','unknown'],lambda x:x.update(judgment='numeric_grade'))
# These are deliberately independently authored truth/credit inputs and literal expected fractions.
# The code observes arithmetic of the written policy, not model truth or application conformance.
packets=[
 dict(id='omitted',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=0,eq='0',primary='100',optional=None),
 dict(id='false_reason',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=1,eq='0',primary='100',optional='0'),
 dict(id='true_reason',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=1,eq='1',primary='100',optional='100'),
 dict(id='false_invitation_flag',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=1,eq='1',invitation=False,primary='100',optional='100'),
 dict(id='wrong_repair_true_reason',g=1,gc=1,tp=1,fp=0,cq='0',ge=1,te=1,ea=1,eq='1',primary='60',optional='100'),
 dict(id='partial_repair',g=1,gc=1,tp=1,fp=0,cq='1/2',ge=1,te=1,ea=1,eq='1',primary='80',optional='100'),
 dict(id='unknown_reason',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=1,eq=None,primary='100',optional=None),
 dict(id='pooled_present_and_absent',g=2,gc=2,tp=2,fp=0,cq='2',ge=2,te=2,ea=1,eq='1',primary='100',optional='100'),
 dict(id='unknown_correction',g=1,gc=1,tp=1,fp=0,cq=None,ge=1,te=1,ea=1,eq='1',primary=None,optional='100'),
 dict(id='unsupported_correction_addition',g=1,gc=1,tp=1,fp=0,cq='0',ge=1,te=1,ea=0,eq='0',primary='60',optional=None),
 dict(id='wrong_selected_category',g=1,gc=1,tp=1,fp=0,cq='1',hc='0',ge=1,te=1,ea=1,eq='1',primary='250/3',optional='100'),
 dict(id='missed_error_with_correct_supplied_reason',g=2,gc=2,tp=1,fp=0,cq='1',ge=2,te=1,ea=1,eq='1',primary='60',optional='100')
]
def primary(x):
 if not x['g']:return None
 f1=Fraction(2*x['tp'],2*x['tp']+x['fp']+x['g']-x['tp']);terms=[(45,f1)]
 if 'hc' in x:terms.append((15,Fraction(x['hc'])/x['g']))
 if x['gc']:
  if x['cq'] is None:return None
  terms.append((30,Fraction(x['cq'])/x['gc']))
 return 100*sum(w*f for w,f in terms)/sum(w for w,f in terms)
def optional(x):return None if not x['ea'] or x['eq'] is None else 100*Fraction(x['eq'])/x['ea']
def rational(x):return None if x is None else Fraction(x)
for x in packets:
 ck('arithmetic.'+x['id']+'.positive',primary(x)==rational(x['primary']) and optional(x)==rational(x['optional']),'Independent constructed arithmetic over stipulated semantic truth; no model/application execution')
 bad=copy.deepcopy(x);bad['primary']='0' if x['primary'] is None or x['primary']!='0' else '100';ck('arithmetic.'+x['id']+'.negative',primary(bad)!=rational(bad['primary']),'Wrong literal result cannot match independent written-policy arithmetic')
pool=packets[7];ck('optional_descriptive_denominators',Fraction(pool['ea'],pool['te'])==Fraction(1,2) and Fraction(pool['eq'])/pool['ge']==Fraction(1,2) and primary(pool)==100)
pair('optional_unknown_issue_nonblocking',dict(affected=['explanation'],blocks=False,ea=1,eq=None,status='complete'),lambda x:x['affected']==['explanation'] and not x['blocks'] and x['ea']==1 and x['eq'] is None and x['status']=='complete',lambda x:x.update(blocks=True))
reg=y['domain/configuration-registry.yaml']['internal'];pair('manual_retry_no_lifetime_ceiling',reg,lambda x:x['render_attempts_per_candidate'] is None and x['transport_retries_per_request']==1 and x['output_repairs_per_stage']==1,lambda x:x.update(render_attempts_per_candidate=3))
pair('local_first_use_default',reg,lambda x:x['speech_profile']=='kokoro-local-en-v1',lambda x:x.update(speech_profile='azure-neural-v1'))
ck('no_generation_lifetime_maximum','maximum' not in schema('generation-request')['properties']['generation_attempt'])
cap=(V/'domain/target-capabilities.yaml').read_text();ck('all_122_targets_no_manual_lifetime_ceiling',cap.count('max_render_attempts: null')==122 and 'max_render_attempts: 3' not in cap)
for name in ['operations','operation-ownership']:
 ck('source_notice_effect.'+name,'Increment permission epoch' not in (V/'domain'/f'{name}.yaml').read_text())
ck('one_mutation_contract','mutation_recipes' in (V/'docs/mistake-data-and-mutations.md').read_text() and 'Do not add recipe fields' not in (V/'docs/mistake-data-and-mutations.md').read_text())
ck('audit_repair_prompt_alignment','one' in (V/'prompts/linguistic-audit-v1.txt').read_text() and 'Do not repair JSON' not in (V/'prompts/linguistic-audit-v1.txt').read_text())
g=json.loads((C/'verification.json').read_text());old=json.loads(subprocess.check_output(['git','show','98cefcc:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));by={c['id']:c for c in g['cases']};ck('all_old_case_identities_states_receipts_retained',all(c['id'] in by and by[c['id']]['test_id']==c['test_id'] and by[c['id']]['state']==c['state'] and by[c['id']].get('source_sha256')==c.get('source_sha256') for c in old['cases']))
new=[c for c in g['cases'] if c['property_id'].startswith('ANS-')];ck('36_new_cases_explicitly_unexecuted',len(new)==36 and all(c['state']=='blocked' and c['source_sha256'] is None for c in new))
plans=json.loads((A/'BEHAVIOR-PLANS.json').read_text());ck('18_literal_scenario_plans',len(plans)==18 and all(all(p[k] for k in ['given','when','expected','negative_counterexample']) for p in plans))
(A/'ARITHMETIC-PACKETS.json').write_text(json.dumps(dict(proof_boundary='Constructed stipulated truth/credit and independent arithmetic, not observed semantic gold or runtime behavior.',packets=packets),indent=2)+'\n')
(A/'validation-results.json').write_text(json.dumps(dict(passed=len(checks),failed=0,checks=checks,active_files=len(actual)+1,schemas=len(meta['records']),fields=len(flat),local_schema_references=len(refs),yaml_files=len(y),proof_boundary='Static artifact integrity, declared-shape counterexamples and independent constructed arithmetic only. No JSON Schema engine, application, LLM, audio, Lab or source acquisition behavior.'),indent=2)+'\n')
print(json.dumps(dict(passed=len(checks),failed=0,active_files=len(actual)+1,schemas=len(meta['records']),fields=len(flat),unexecuted_new_behavior_edges=len(new))))
