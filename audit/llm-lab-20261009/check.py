"""Read-only specification checks and independent diagnostic arithmetic fixtures."""
import copy, hashlib, json, math, subprocess
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote,urlparse
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((V/'contracts'/f'{n}.schema.json').read_text())
def ck(name,condition,detail=None):
 checks.append(dict(id=name,status='passed' if condition else 'failed',detail=detail));assert condition,name

def pair(name,fixture,predicate,break_it):
 ck(name+'.positive',predicate(fixture),'Static contract observation only')
 bad=copy.deepcopy(fixture);break_it(bad);ck(name+'.negative',not predicate(bad),'Constructed counterexample to the written contract')
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');const r='specification/v2',d={};for(const p of ['domain/llm-lab.v1.yaml','domain/semantic-invariants.yaml','domain/operation-ownership.yaml','domain/version-compatibility.yaml','domain/corpus-sources.v1.yaml','prompts/manifest.yaml'])d[p]=Y.parse(fs.readFileSync(r+'/'+p,'utf8'));let n=0;function walk(p){for(const x of fs.readdirSync(p,{withFileTypes:true})){const f=p+'/'+x.name;if(x.isDirectory())walk(f);else if(f.endsWith('.yaml')||f.endsWith('.yml')){Y.parse(fs.readFileSync(f,'utf8'));n++;}}}walk(r);d.yaml_count=n;process.stdout.write(JSON.stringify(d));"""
y=json.loads(subprocess.check_output(['node','-e',node],cwd=R,text=True));lab=y['domain/llm-lab.v1.yaml'];manifest=y['prompts/manifest.yaml'];flow=(V/'docs/llm-lab.md').read_text()
pair('optional_single_local_service',lab,lambda x:x['normal_start_required'] is False and x['additional_persistent_services']==1 and x['host_binding']=='127.0.0.1:5000' and x['required_external_accounts']==[],lambda x:x.update(normal_start_required=True))
pair('no_startup_inference_or_telemetry',lab,lambda x:x['provider_calls_at_start'] is False and x['environment']['MLFLOW_DISABLE_TELEMETRY']=='true',lambda x:x.update(provider_calls_at_start=True))
pair('nonblocking_bounded_export',lab,lambda x:x['export_timeout_ms']==1000 and x['export_automatic_retries']==0 and x['export_outage_blocks_grading'] is False,lambda x:x.update(export_outage_blocks_grading=True))
pairs={(b['stage'],b.get('phase')) for b in manifest['bindings']}
pair('every_original_stage_phase_has_context',lab,lambda x:{(p['stage'],p['phase']) for p in x['context_policies']}==pairs and len(x['context_policies'])==9,lambda x:x['context_policies'].pop())
pair('blind_context_has_no_key_or_prior_grades',lab,lambda x:all(not {'mutation_key','prior_decisions'}&set(p['component_order']) for p in x['context_policies'] if p['stage']=='blind_claim_extraction'),lambda x:next(p for p in x['context_policies'] if p['stage']=='blind_claim_extraction')['component_order'].append('mutation_key'))
pair('canonical_context_has_no_mutation_key',lab,lambda x:all('mutation_key' not in p['component_order'] for p in x['context_policies'] if p['phase']=='canonical_text'),lambda x:next(p for p in x['context_policies'] if p['phase']=='canonical_text')['component_order'].append('mutation_key'))
pair('numeric_registry_version_export',load('prompt-bundle'),lambda x:x['properties']['bindings']['items']['properties']['registry_version']['anyOf'][0]['type']=='integer' and 'selection' in x['$defs'],lambda x:x['properties']['bindings']['items']['properties']['registry_version']['anyOf'][0].update(type='string'))
pair('snapshot_preserves_components_and_wire_input',load('llm-context-snapshot'),lambda x:all(n in x['required'] for n in ['components','rendered_request_asset_id','input_sha256','binding_sha256','receipt_id','trace_id','span_id']),lambda x:x['required'].remove('rendered_request_asset_id'))
pair('local_capture_opt_in',load('configuration'),lambda x:x['properties']['llm_lab_capture_content']['default'] is False and x['properties']['llm_lab_trace_enabled']['default'] is False and 'active_prompt_bundle_id' not in x['required'],lambda x:x['properties']['llm_lab_capture_content'].update(default=True))
pair('expectation_origin_not_fake_gold',load('llm-quality-case'),lambda x:all(s in x['properties']['expectation_basis']['enum'] for s in ['authored_assertion','native_annotation','independent_llm','self_consistency']) and 'expectations' in x['$defs'],lambda x:x['properties']['expectation_basis']['enum'].remove('self_consistency'))
pair('failed_unperformed_rows_explicit',load('llm-experiment'),lambda x:set(x['properties']['rows']['items']['properties']['status']['enum'])=={'complete','failed','cancelled','not_run'},lambda x:x['properties']['rows']['items']['properties']['status']['enum'].remove('not_run'))
pair('frozen_comparable_variants',load('llm-experiment'),lambda x:all(k in x['required'] for k in ['dataset_sha256','scorer_version','metric_registry_sha256','scope','repetitions']) and 'configuration_sha256' in x['properties']['variants']['items']['required'],lambda x:x['required'].remove('dataset_sha256'))
textchecks={
 'edit_not_activation':['Editing does not change the running app','never use mutable latest/production aliases','Changing activation affects new operations only'],
 'same_native_owners_not_second_grader':['sharing the actual generation/evaluation/scoring owners','must not replace those owners with direct SDK calls'],
 'no_silent_context_truncation':['do not silently truncate the answer, key','Template variables bind named stage-input fields as data'],
 'all122_coverage_not_startup_gate':['each of the 122 leaves','Small selected datasets are usable immediately'],
 'self_consistency_not_independent_accuracy':["self_consistency",'does not establish independent accuracy'],
 'judge_explicit_not_openai_fallback':['no automatic OpenAI judge','defaulting to the existing DeepSeek fast binding'],
 'cache_repetitions_real_calls':['Live repetitions bypass semantic-result cache','Cache hits point to the original actual receipt'],
 'secrets_and_backup_deletion':['Always strip authorization/cookies/API keys','consistent backup mechanism','cleanup is shown as pending'],
 'no_quality_activation_gate':['No auto-promotion, human review, pass threshold or release gate is required']}
for name,terms in textchecks.items():pair(name,dict(text=flow),lambda x,t=terms:all(v in x['text'] for v in t),lambda x,t=terms:x.update(text=x['text'].replace(t[0],'')))
# Formula-identity and independent numerical fixtures. These are not native scorer execution.
registry=json.loads((V/'domain/llm-quality-metrics.v1.json').read_text());metrics={m['id'].removeprefix('llm_lab.'):m for m in registry['metrics']};ck('all22_distinct_diagnostic_definitions',len(metrics)==22 and all(m['scope']=='diagnostic_only_not_a_replacement_for_42_original_equations' for m in metrics.values()))
fixtures=[
('completion_rate','completed / planned',Fraction(3,5),Fraction(3,5)),
('first_response_projection_rate','projected_first_delivered_reply / logical_calls_with_delivered_reply',Fraction(2,3),Fraction(2,3)),
('repair_rate','logical_calls_with_semantic_repair / initiated_logical_calls',Fraction(1,5),Fraction(1,5)),
('canonical_preservation_rate','mutation_outputs_with_exact_saved_canonical / completed_mutation_outputs',Fraction(3,4),Fraction(3,4)),
('mutation_list_consistency_rate','mutations_with_consistent_span_category_repair_and_surface / applicable_declared_mutations',Fraction(3,5),Fraction(3,5)),
('request_fulfillment_rate','satisfied_applicable_request_predicates / applicable_request_predicates',Fraction(4,5),Fraction(4,5)),
('word_length_relative_deviation','abs(actual_words - requested_words) / requested_words',Fraction(abs(120-100),100),Fraction(1,5)),
('detection_precision','TP / (TP + FP)',Fraction(2,2+1),Fraction(2,3)),
('detection_recall','TP / (TP + FN)',Fraction(2,2+1),Fraction(2,3)),
('detection_f1','2 * TP / (2 * TP + FP + FN)',Fraction(2*2,2*2+1+1),Fraction(2,3)),
('category_accuracy','correct_reference_category_decisions / applicable_reference_category_decisions',Fraction(2,3),Fraction(2,3)),
('repair_accuracy','correct_applicable_repair_propositions / applicable_reference_repair_propositions',Fraction(2,4),Fraction(1,2)),
('explanation_accuracy','correct_applicable_explanation_propositions / applicable_reference_explanation_propositions',Fraction(3,4),Fraction(3,4)),
('score_mae_pp','sum(abs(predicted_percent - reference_percent)) / paired_reference_scores',Fraction(abs(80-60)+abs(50-50),2),Fraction(10)),
('feedback_grounding_rate','supported_factual_items_or_correctly_labelled_practice / applicable_feedback_items',Fraction(3,4),Fraction(3,4)),
('audio_target_confirmation_rate','actually_supported_target_realizations / targets_with_relevant_actual_observation',Fraction(1,2),Fraction(1,2)),
('latency_p50_ms','sorted_observed_duration_ms[ceil(0.50*n)-1]',Fraction(sorted([100,10,20])[math.ceil(.50*3)-1]),Fraction(20)),
('latency_p95_ms','sorted_observed_duration_ms[ceil(0.95*n)-1]',Fraction(sorted([100,10,20])[math.ceil(.95*3)-1]),Fraction(100)),
('reported_tokens_total','sum(reported_input_tokens + reported_output_tokens)',Fraction(10+5),Fraction(15)),
('cost_total_usd','sum(actual_cost_micro_usd) / 1000000',Fraction(250000+750000,1000000),Fraction(1)),
('repeat_detection_jaccard','mean(size(A intersection B) / size(A union B))',Fraction(len({1,2}&{2,3}),len({1,2}|{2,3})),Fraction(1,3)),
('leaf_macro_recall','sum(observed_leaf_recall) / observed_applicable_leaves',Fraction(Fraction(1)+Fraction(0),2),Fraction(1,2))]
for name,formula,result,expected in fixtures:
 ck('metric:'+name+'.positive',metrics[name]['formula']==formula and result==expected,'Independent authored arithmetic fixture, not native application execution')
 ck('metric:'+name+'.negative',metrics[name]['formula']!=formula+' + 1' and result!=expected+1,'Reject changed diagnostic formula/wrong claimed result')
pair('zero_denominator_not_perfection',registry,lambda x:x['zero_denominator']=='N/A with reason',lambda x:x.update(zero_denominator='1'))
pair('unknown_cost_tokens_not_zero',registry,lambda x:'not zero' in x['unknown'] and 'known subtotal' in metrics['cost_total_usd']['population'] and 'unknown component yields null total' in metrics['reported_tokens_total']['population'],lambda x:x.update(unknown='Unknown is zero'))
# Current metadata only, and baseline preservation; no repeated application/native-corpus test.
for name in ['error-taxonomy.v1.yaml','metrics.v1.yaml','mutation-recipes.v1.json']:
 p=V/'domain'/name;ck('preserved_original:'+name,p.read_bytes()==subprocess.check_output(['git','show','d07f030:'+p.relative_to(R).as_posix()],cwd=R))
oldsrc=subprocess.check_output(['git','show','d07f030:specification/v2/domain/corpus-sources.v1.yaml'],cwd=R,text=True);ck('all_source_scopes_byte_preserved',(V/'domain/corpus-sources.v1.yaml').read_text()==oldsrc)
ck('original_prompt_texts_unchanged',all((V/x['path']).read_bytes()==subprocess.check_output(['git','show','d07f030:specification/v2/'+x['path']],cwd=R) for x in manifest['bindings']))
objects={p.relative_to(V).as_posix():json.loads(p.read_text()) for p in V.rglob('*.json')};refs=0
def ptr(d,path):
 for k in unquote(path).lstrip('/').split('/') if path else []:d=d[int(k)] if isinstance(d,list) else d[k.replace('~1','/').replace('~0','~')]
 return d
for path,d in objects.items():
 def walk(n):
  global refs
  if isinstance(n,dict):
   if '$ref'in n:
    u=urlparse(n['$ref']);p=(V/path).parent/u.path if u.path else V/path
    if u.scheme:p=V/'contracts'/Path(u.path).name
    ptr(json.loads(p.read_text()),u.fragment);refs+=1
   for c in n.values():walk(c)
  elif isinstance(n,list):
   for c in n:walk(c)
 walk(d)
ck('all_JSON_YAML_refs_syntax',True,dict(json=len(objects),yaml=y['yaml_count'],refs=refs))
records=objects['domain/persistence-map.json']['records'];flat=[]
for rec in records:
 p=V/rec['schema'];ck('schema_hash:'+rec['kind'],sha(p)==rec['sha256']==y['domain/semantic-invariants.yaml']['schemas'][rec['kind']]['schema_sha256'])
 for f in rec['fields']:
  assert hashlib.sha256(json.dumps(ptr(json.loads(p.read_text()),f['pointer']),separators=(',',':')).encode()).hexdigest()==f['rule_sha256'],(rec['kind'],f['pointer'])
  flat.append(dict(schema=p.name,**f))
idx=objects['language/field-index.json'];ck('complete_field_index',idx['fields']==flat and idx['schema_count']==len(records)==len(list((V/'contracts').glob('*.schema.json'))) and idx['field_count']==len(flat))
for op in y['domain/operation-ownership.yaml']['operations']:
 if op.get('request_schema') and not op['request_schema'].startswith('binary:'):assert set(op['request_fields'])==set(load(op['request_schema'])['properties']),op['id']
ck('all_request_ownership',True)
for b in manifest['bindings']:assert sha(V/b['path'])==b['prompt_sha256'] and sha(V/'contracts'/b['input_schema'])==b['input_schema_sha256'] and sha(V/'contracts'/b['output_schema'])==b['output_schema_sha256'],b['prompt_id']
ck('all_original_prompt_bindings_hashes',True)
vec=y['domain/version-compatibility.yaml']['files'];ck('complete_current_version_vector',all(sha(V/x['path'])==x['sha256'] for x in vec) and {x['path'] for x in vec}=={p.relative_to(V).as_posix() for p in V.rglob('*') if p.is_file() and p!=V/'domain/version-compatibility.yaml'})
g=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());new=[c for c in g['cases'] if c['property_id'].startswith('LAB-')];ck('28_future_behavior_plans_blocked',len(new)==28 and all(c['state']=='blocked' and c['source_sha256'] is None for c in new));old=json.loads(subprocess.check_output(['git','show','d07f030:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));ck('every_original_graph_requirement_property_case_retained',all(g[k][:len(old[k])]==old[k] for k in ['requirements','properties','cases']))
paths=subprocess.check_output(['git','diff','--name-only','d07f030'],cwd=R,text=True).splitlines();ck('no_application_immutable_or_workflow_changes',not any(p.startswith(('services/','tests/','deploy/','scripts/','spec-inputs/','.agents/')) for p in paths))
result=dict(status='passed',proof_boundary='Static researched specification, independent authored diagnostic arithmetic, metadata/reference integrity and preservation only. No formal full JSON-Schema compilation, Lab/runtime/provider/application test or observed LLM quality.',checks=checks,passed=len(checks),schemas=len(records),fields=len(flat),namespace_files=len(vec)+1,json_files=len(objects),yaml_files=y['yaml_count'],local_schema_refs=refs,planned_new_behavior_edges=len(new));(A/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
