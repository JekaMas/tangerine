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
 old=subprocess.check_output(['git','show','9f5124a:specification/v2/'+p],cwd=R);ck('protected_bytes.'+p,old==(V/p).read_bytes())
def schema(n):return j['contracts/'+n+'.schema.json']
# Finite property/case/fixture identity reconciliation, and exact constructed expectations.
g=json.loads((C/'verification.json').read_text());f=j['domain/verification-fixtures.v1.json'];fixtures={x['id']:x for x in f['fixtures']}
ck('all_property_fixture_bindings',set(x['property_id'] for x in f['property_bindings'])==set(x['id'] for x in g['properties']) and len(f['property_bindings'])==len(g['properties']))
ck('all_case_fixture_bindings',set(x['case_id'] for x in f['case_bindings'])==set(x['id'] for x in g['cases']) and len(f['case_bindings'])==len(g['cases']))
for x in f['fixtures']:
 ck('literal_fixture.'+x['id'],bool(x['action']) and bool(x['independent_oracle']) and bool(x['positive']['input']) and bool(x['positive']['expected']) and bool(x['negative']['input']) and bool(x['negative']['expected']) and x['positive']['input']!=x['negative']['input'])
for x in f['case_bindings']:
 assert x['fixture_id'] in fixtures and x['input'] and x['expected'] and x['observation_state']=='not_run',x['case_id']
ck('all_case_expectation_packets',len(f['case_bindings'])==1620)
old=json.loads(subprocess.check_output(['git','show','9f5124a:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));cases={x['id']:x for x in g['cases']};invalidated=json.loads((A/'invalidated-historical-cases.json').read_text());invalidids={x['id'] for x in invalidated}
for x in old['cases']:
 current=cases[x['id']]
 assert all(current[k]==x[k] for k in ['id','test_id','source_path','source_sha256','command_id']),x['id']
 if x['state']=='implemented':assert current['state']==('blocked' if x['id'] in invalidids else 'implemented'),x['id']
ck('original_identity_and_proof_scopes_preserved',len(invalidids)==4 and len(old['cases'])==1604)
ck('new_plans_not_observations',all(x['fixture_observation_state']=='not_run' for x in g['cases']) and all(x['state']=='blocked' for x in g['cases'] if x['id'] not in {x['id'] for x in old['cases']}))
ck('all_122_category_packets',len([x for x in fixtures if x.startswith('leaf-')])==122)
ck('all_42_metric_packets',len([x for x in fixtures if x.startswith('equation-')])==42)
ck('all_22_quality_packets',len([x for x in fixtures if x.startswith('quality-llm_lab.')])==22)
ck('all_11_source_packets',all('full-source-'+x['id'] in fixtures for x in y['domain/corpus-sources.v1.yaml']['sources']) and len(y['domain/corpus-sources.v1.yaml']['sources'])==11)
# Independently write the arithmetic, without importing application/reference scorers.
s=fixtures['equation-detection.precision']['positive']['input']['stats'];S={k:Fraction(v) for k,v in s.items()}
manual=[S['TP']/(S['TP']+S['FP']),S['TP']/S['G'],2*S['TP']/(2*S['TP']+S['FP']+S['FN']),S['FN']/S['G'],S['FP']/(S['TP']+S['FP']),S['LC']/S['TP'],S['LF']/S['LC'],S['LE']/S['LC'],S['H']/S['LC'],S['H']/S['G'],S['CA']/S['TC'],S['CK']/S['CA'],S['CQ']/S['CA'],S['CK']/S['GC'],S['CQ']/S['GC'],S['CK']/(S['CA']+S['FC']),S['EA']/S['TE'],S['EK']/S['EA'],S['EQ']/S['EA'],S['EQ']/S['GE'],S['DF']/S['D'],(S['D']-S['DF'])/S['D'],S['DA']/(S['DA']+S['DF']),S['SA']/S['SN'],S['WTP']/(S['WTP']+S['WFP']),S['WTP']/(S['WTP']+S['WFN']),2*S['WTP']/(2*S['WTP']+S['WFP']+S['WFN'])]
for m,expected in zip(y['domain/metrics.v1.yaml']['metrics'],manual):ck('independent_equation.'+m['id'],expected==Fraction(fixtures['equation-'+m['id']]['positive']['expected']['exact']))
aux=[Fraction(5,6),(Fraction(5,6)-Fraction(1,2))/(1-Fraction(1,2)),Fraction(3,10),Fraction(60*10,5),Fraction(60*10,4),Fraction(1,5),Fraction(100*2,10),Fraction(4,5),Fraction(3,5),Fraction(25,2),Fraction(3)]+[None]*4
for m,expected in zip(y['domain/metrics.v1.yaml']['auxiliary_metrics'],aux):
 got=fixtures['equation-'+m['id']]['positive']['expected']['exact'];ck('independent_equation.'+m['id'],expected==(Fraction(got) if got is not None else None))
k=fixtures['equation-annotation.cohen_kappa']['positive']['input']['inputs'];N=sum(k['confusion'].values());agreements=k['confusion']['a_a']+k['confusion']['b_b'];Pe=sum(Fraction(k['rater1_counts'][label],N)*Fraction(k['rater2_counts'][label],N) for label in ['a','b']);ck('kappa_realizable_marginals',N==6 and Fraction(agreements,N)==Fraction(k['Po']) and Pe==Fraction(k['Pe']))
qexpected=[Fraction(8,10),Fraction(7,10),Fraction(2,10),Fraction(9,10),Fraction(8,10),Fraction(9,10),Fraction(10,100),Fraction(2,3),Fraction(2,4),Fraction(4,7),Fraction(4,5),Fraction(3,4),Fraction(2,4),Fraction(20+0,2),Fraction(4,5),Fraction(3,4),Fraction(30),Fraction(50),Fraction(10+20+5+6),Fraction(100000,1000000),(Fraction(1,2)+1)/2,(1+Fraction(1,2))/2]
for m,e in zip(j['domain/llm-quality-metrics.v1.json']['metrics'],qexpected):ck('independent_quality_equation.'+m['id'],Fraction(fixtures['quality-'+m['id']]['positive']['expected']['exact'])==e)
ck('native_primary_independent_explanation',Fraction(45*1+15*1+30*Fraction(2,5),90)*100==80 and Fraction(0,1)*100==0)
ck('all_named_scenario_contracts',all(x.get('declared_scenario_contract') for x in f['case_bindings']))
for n in ['CLOSE-01 Rationale-only repair or incomplete proposal','CLOSE-02 Response loss and late writer','CLOSE-03 Hidden preference cannot create an error','CLOSE-04 Exact voice and arithmetic fixtures']:
 ck('named_scenario.'+n,any(x['fixture_id']=='scenario-'+n for x in f['case_bindings']))
ck('rationale_only_named_packet',fixtures['scenario-CLOSE-01 Rationale-only repair or incomplete proposal']['positive']['expected']['primary_statistics_changed'] is False)
ck('response_loss_zero_calls',fixtures['scenario-CLOSE-02 Response loss and late writer']['positive']['expected']['speech_calls']==0)
# Local references and finite declared shape, not JSON Schema engine/full conformance.
proposal=schema('key-repair-proposal');pair('complete_typed_key_proposal',proposal,lambda x:set(x['required'])=={'base_case_sha256','audio_sha256','affected_components','proposed_units','correspondence_relations','reason'} and x['properties']['proposed_units']['items']['$ref'].endswith('/planned_units/items'),lambda x:x['required'].remove('proposed_units'))
review=schema('llm-review-output');pair('review_return_attachment',review,lambda x:'key_repair' in x['required'] and x['properties']['key_repair']['anyOf'][0]['$ref']=='key-repair-proposal.schema.json',lambda x:x['required'].remove('key_repair'))
ck('mutation_input_for_review','mutation_manifest' in schema('llm-review-input')['required'])
packet=json.loads((A/'KEY-REPAIR-PACKET.json').read_text());u_schema=schema('case-candidate')['properties']['planned_units']['items'];needed=set(u_schema['required']);relations=packet['proposal']['correspondence_relations'];ids={u['id'] for u in packet['proposal']['proposed_units']}
ck('complete_literal_key_packet',all(set(u)==needed and set(u['corrections'][0])==set(u_schema['properties']['corrections']['items']['required']) and all(packet['surface'][s['span']['start_cp']:s['span']['end_cp']]==s['span']['exact_text'] for s in u['text_spans']) for u in packet['proposal']['proposed_units']))
ck('total_literal_correspondence',{x for r in relations for x in r['old_unit_ids']}=={'u1'} and {x for r in relations for x in r['new_unit_ids']}==ids and len([x for r in relations for x in r['new_unit_ids']])==len(ids))
pair('packet_audio_preserved',packet,lambda x:x['proposal']['audio_sha256']==x['expected']['audio_sha256'],lambda x:x['proposal'].update(audio_sha256='c'*64))
pair('packet_complete_unit_set',packet,lambda x:{u['id'] for u in x['proposal']['proposed_units']}=={'u1','new:u2'},lambda x:x['proposal']['proposed_units'].pop())
for n in ['generation-request','render-request']:
 ck('preparation_request.'+n,'preparation_id' in schema(n)['required'])
 attempt='generation_attempt' if n=='generation-request' else 'render_attempt';ck('no_manual_attempt_ceiling.'+n,'maximum' not in schema(n)['properties'][attempt])
for n in ['operation-status','prepare-view']:ck('preparation_readback.'+n,'preparation' in schema(n)['required'])
state=schema('preparation-state');pair('durable_phase_association',state,lambda x:{'settings_asset_id','settings_sha256','active_operation_id','phase_states','canonical_asset_id','canonical_sha256','candidate_id','mutated_asset_id','mutation_manifest_asset_id','render_plan_asset_id','audio_asset_id','audio_sha256','key_id'}<=set(x['required']),lambda x:x['required'].remove('settings_asset_id'))
settings=schema('preparation-settings');ck('complete_frozen_settings',{'blueprint','configuration','prompt_bundle','generation_bindings','speech_registry_asset_id','recipe_registry_asset_id','source_record_ids'}<=set(settings['required']))
# Mutate the literal resume/context packets and compare independent identities, no fake native restart.
r=fixtures['persistent-resume'];ck('frozen_resume_literal',r['positive']['expected']['bindings']==r['positive']['input']['frozen'] and r['positive']['expected']['bindings']!=r['positive']['input']['current'] and r['positive']['expected']['canonical_calls']==0)
ck('late_writer_literal',r['negative']['expected']['late_checkpoint_selected'] is False)
e=fixtures['english-context'];ck('audible_context_literal',e['positive']['input']['private_context'] is None and len(e['positive']['input']['audible_turns'])==2 and e['negative']['expected']['that_instance_generated'] is False)
for p in ['prompts/canonical-v1.txt','prompts/generate-v1.txt']:
 ck('self_contained_prompt.'+p,'private' in (V/p).read_text().lower() and 'audible' in (V/p).read_text().lower())
ops=y['domain/operations.yaml']['operations'];own=y['domain/operation-ownership.yaml']['operations'];oas=y['contracts/openapi.yaml'];ck('operation_inventory',len(ops)==len(own)==68 and {x['id'] for x in ops}=={x['id'] for x in own})
for op in ops:assert oas['paths'][op['path']][op['method'].lower()]['operationId']==op['id'],op['id']
ck('operation_openapi_inventory',len(ops)==68)
ck('preparation_list_read_only',oas['paths']['/api/v1/preparations']['get']['x-activity']=='prepare' and next(x for x in ops if x['id']=='list_preparations')['method']=='GET')
source_scopes=y['domain/corpus-sources.v1.yaml']['sources']
for src in source_scopes:ck('full_source_scope.'+src['id'],fixtures['full-source-'+src['id']]['positive']['input']['components']==src['required_components'])
# All textual illustration edits replay exactly; acoustic intent is explicitly unobserved.
for r in j['domain/mutation-recipes.v1.json']['recipes']:
 edit=r['codepoint_edit']
 if edit:
  canonical=r['canonical_example'];actual=canonical[:edit['start_cp']]+edit['replacement']+canonical[edit['end_cp']:];assert actual==r['surface_example'] and canonical[edit['start_cp']:edit['end_cp']]==edit['exact_text'],r['taxonomy_id']
ck('all_text_recipe_literal_replays',len(j['domain/mutation-recipes.v1.json']['recipes'])==122)
result=dict(status='passed',checks=len(checks),schemas=len(meta['records']),fields=len(flat),properties=len(g['properties']),case_plans=len(g['cases']),fixture_templates=len(fixtures),actual_behavior_observations=0,proof_boundary='Static declarative integrity and independent constructed arithmetic only; no JSON Schema engine conformance, application, LLM, speech, restart/restore, corpus intake or Lab behavior observed.',results=checks)
(A/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='results'}))
