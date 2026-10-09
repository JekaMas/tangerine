"""Focused artifact scope/counterexample checks; not native runtime evidence."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;BASE='d074529';C=R/'openspec/changes/implement-teacher-error-trainer'
checks=[]
def ck(name,ok):
 checks.append(dict(name=name,passed=bool(ok)));assert ok,name
def pair(name,data,predicate,mutate):
 ck(name+'.positive',predicate(data));bad=copy.deepcopy(data);mutate(bad);ck(name+'.negative',not predicate(bad))
def prior(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=R)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
policy=json.loads((V/'domain/product-data-relevance.v1.json').read_text());doc=(V/'docs/product-data-relevance.md').read_text();items=policy['items']
pair('all_prior_groups_mapped',policy,lambda p:{x['prior_group']for x in p['items']if x['prior_group']}==set(range(1,8)),lambda p:p.update(items=[x for x in p['items']if x['prior_group']!=4]))
pair('no_external_core_requirement',policy,lambda p:p['main_flow_external_corpora_required']is False and all(x['ordinary_flow_requires_external_corpus_or_population']is False for x in p['items']),lambda p:p['items'][0].update(ordinary_flow_requires_external_corpus_or_population=True))
pair('finite_ids_and_semantic_mapping',policy,lambda p:len(p['items'])==28 and len({x['id']for x in p['items']})==28 and all(all(x[k]for k in ['product_use','needed_when','disposition','contracts','removed_requirement','preserved'])for x in p['items']),lambda p:p['items'][10].update(needed_when=''))
for x in items:
 ck('actual_owner_paths.'+x['id'],all((V/p).is_file()for p in x['contracts'])and x['id']in doc)
pair('scope_rules_preserved',policy,lambda p:all(p['rules'].values()),lambda p:p['rules'].update(all_supplied_native_fields_and_members_preserved=False))
pair('no_benchmark_reduction',policy,lambda p:p['preserve_taxonomy_leaves']==122 and p['preserve_grade_formulas']==42 and p['preserve_full_benchmark_distinct_stimuli']==732,lambda p:p.update(preserve_full_benchmark_distinct_stimuli=6))
removed={x['id']for x in items if x['disposition']=='remove_as_product_requirement'}
ck('exact_administrative_api_duplicate_certification_removals',removed=={'REL-05','REL-11','REL-13','REL-14','REL-18','REL-27'})
by={x['id']:x for x in items}
ck('core_runtime_and_development_checks_retained',by['REL-23']['disposition']=='keep_core_verification'and by['REL-26']['disposition']=='keep_development_verification'and 'mandatory'in by['REL-26']['preserved'])
ck('native_instruments_no_app_grade_adoption',by['REL-08']['disposition']=='keep_raw_optional_analysis'and 'conversion'in by['REL-08']['removed_requirement']and 'raw_only'in by['REL-08']['preserved'])
# Independent small claim oracle, constructed source/component observations.
# It tests audit scope reasoning, not a product importer or scoring implementation.
def full_claim(source):
 return source['declared_source']==source['actual_source'] and source['expected_members']==source['observed_members'] and bool(source['observed_members'])
fixture=dict(declared_source='FCE-2.1',actual_source='FCE-2.1',expected_members={'train','dev','test','readme'},observed_members={'train','dev','test','readme'})
pair('full_claim_member_scope',fixture,full_claim,lambda x:x['observed_members'].remove('test'))
pair('full_claim_no_other_source_substitution',fixture,full_claim,lambda x:x.update(actual_source='WILOCNESS-2.1'))
def action_has_inputs(selected,available):return set(selected)<=set(available)
ck('independent_generation_with_no_corpus',action_has_inputs(['recipes','canonical','key','audio','answer'],['recipes','canonical','key','audio','answer']))
ck('selected_source_unavailable_is_not_full',not action_has_inputs(['recipes','EFCAMDAT-R2'],['recipes']))
# Parse only changed YAML/vector and compare unchanged members to retained baseline.
node="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');process.stdout.write(JSON.stringify(Y.parse(fs.readFileSync(0,'utf8'))));"
def yaml_bytes(b):return json.loads(subprocess.check_output(['node','-e',node],input=b,cwd=R))
src=yaml_bytes((V/'domain/corpus-sources.v1.yaml').read_bytes());oldsrc=yaml_bytes(prior('specification/v2/domain/corpus-sources.v1.yaml'))
ck('all_original_source_records_and_components_unchanged',src['sources']==oldsrc['sources'] and len(src['sources'])==11 and policy['preserve_original_sources']==[x['id']for x in src['sources']])
val=yaml_bytes((V/'domain/validation-policy.yaml').read_bytes());oldval=yaml_bytes(prior('specification/v2/domain/validation-policy.yaml'))
oldval['gates'][3]['measure']='strict correction verdict agreement with provenance-labelled reference verdicts';oldval['gates'][3]['source']='The held-out corpus with LLM or imported native reference verdicts; label origin and circular-reference limits remain explicit.';oldval['product_dependency_scope']='domain/product-data-relevance.v1.json'
ck('only_reference_origin_wording_and_scope_change',val==oldval)
ck('full_gold_policy_and_numeric_thresholds_retained',val['gold']==yaml_bytes(prior('specification/v2/domain/validation-policy.yaml'))['gold'])
cv=yaml_bytes((V/'domain/version-compatibility.yaml').read_bytes());files={p.relative_to(V).as_posix()for p in V.rglob('*')if p.is_file()}-{'domain/version-compatibility.yaml'}
pair('complete_current_vector',cv,lambda c:{x['path']for x in c['files']}==files and all(sha(V/x['path'])==x['sha256']for x in c['files']),lambda c:c['files'].pop())
for path in ['domain/error-taxonomy.v1.yaml','domain/mutation-recipes.v1.json','domain/metrics.v1.yaml','domain/llm-quality-metrics.v1.json','domain/providers.v1.yaml','domain/ai-development.v1.json','domain/persistence-map.json','domain/semantic-invariants.yaml','language/field-index.json','prompts/manifest.yaml']:
 ck('protected_contract_bytes.'+path,prior('specification/v2/'+path)==(V/path).read_bytes())
oldgraph=json.loads(prior('openspec/changes/implement-teacher-error-trainer/verification.json'));g=json.loads((C/'verification.json').read_text())
for k in ['requirements','properties','cases','executions']:
 if k not in oldgraph:continue
 now={x['id']:x for x in g[k]};ck('earlier_graph_receipts_preserved.'+k,all(now[x['id']]==x for x in oldgraph[k]))
new=[x for x in g['cases']if x['id'].startswith('DREL-')];ck('12_new_edges_blocked',len(new)==12 and all(x['state']=='blocked'for x in new))
ck('changed_docs_no_acquisition_claim',all('acquired'not in x['disposition']for x in items))
ck('no_app_deploy_input_changes',subprocess.run(['git','diff','--quiet',BASE,'--','services','scripts/tangerine','deploy','data'],cwd=R).returncode==0)
(A/'validation-results.json').write_text(json.dumps(dict(passed=len(checks),failed=0,baseline=BASE,checks=checks,mapped_items=28,remaining_groups=7,vector_files=len(files),retained_schema_count=134,retained_field_count=3001,proof_boundary='Focused static scope/mapping and independent constructed source/member/claim counterexamples only; no native importer, generation/audio/provider/Lab runtime acceptance.',invalidation='New dependency contract/spec/graph; changed source/validation policy wording and document vector. Original schemas/field indexes/grade formulas/prompts/providers and old graph records retained; no rerun of unchanged runtime/native data tests.'),indent=2)+'\n')
print(json.dumps({'passed':len(checks),'mapped_items':28,'vector_files':len(files)}))
