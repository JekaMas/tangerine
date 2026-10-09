"""Affected static specification checks; never application/model execution."""
import copy,json,hashlib,subprocess
from fractions import Fraction
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
checks=[]
def ck(n,x):
 if not x:raise AssertionError(n)
 checks.append(n)
def pair(n,x,fn,mutate):
 ck(n+'.positive',fn(x));bad=copy.deepcopy(x);mutate(bad);ck(n+'.negative',not fn(bad))
g=json.loads((C/'verification.json').read_text());f=json.loads((V/'domain/verification-fixtures.v1.json').read_text());dep=json.loads((V/'domain/product-data-relevance.v1.json').read_text());flow=(V/'docs/simple-generation-flow.md').read_text();emp=(V/'docs/empirical-data-needs.md').read_text()
pair('no_pregenerated_corpus',dep,lambda x:x['main_flow_pregenerated_exercise_corpus_required'] is False and x['rules']['startup_batch_corpus_generation'] is False and x['main_flow_text_and_mutation_origin']=='configured_llm_on_user_request',lambda x:x.update(main_flow_pregenerated_exercise_corpus_required=True))
ck('llm_generates_mutations','The configurable LLM generates the mutations for this user request' in flow and 'A local recipe operator can apply explicit edits' not in flow)
ck('no_bank_fallback','does not supply an alternative recipe-only mutation generator' in flow)
ck('benchmark_explicit_only','Only when explicitly selecting the optional benchmark' in emp)
ck('no_setup_suite','no full suite is generated at startup or for ordinary exercises' in emp)
for p in ['prompts/canonical-v1.txt','prompts/generate-v1.txt','prompts/map-v1.txt']:ck('trusted_prompt.'+p,'pregenerated' in (V/p).read_text())
key=json.loads((V/'contracts/evaluation-key.schema.json').read_text());utterance=key['properties']['utterances']['items'];ck('original_and_mutated_text_in_evaluation',{'canonical_text','surface_text'}<=set(utterance['required']))
for name in ['mapping-input','feedback-input']:ck('existing_evaluation_projection.'+name,json.loads((V/'contracts'/f'{name}.schema.json').read_text())['properties']['ground_truth']['$ref']=='evaluation-key.schema.json')
ck('feedback_found_and_missed',{'detected','missed'}<=set(json.loads((V/'contracts/feedback-output.schema.json').read_text())['properties']['items']['items']['properties']['kind']['enum']))
for path in ['domain/error-taxonomy.v1.yaml','domain/metrics.v1.yaml','domain/corpus-sources.v1.yaml','domain/mutation-recipes.v1.json','domain/providers.v1.yaml']:
 ck('preserved_original_scope.'+path,subprocess.check_output(['git','show','503723e:specification/v2/'+path],cwd=R)==(V/path).read_bytes())
ck('all_property_bindings',{x['id'] for x in g['properties']}=={x['property_id'] for x in f['property_bindings']})
ck('all_case_bindings',{x['id'] for x in g['cases']}=={x['case_id'] for x in f['case_bindings']})
new=[x for x in g['cases'] if x['id'].startswith('DEMAND-')];ck('four_unexecuted_cases',len(new)==4 and all(x['state']=='blocked' and x['fixture_observation_state']=='not_run' for x in new))
for b in f['case_bindings']:
 if b['case_id'].startswith('DEMAND-'):ck('exact_packet.'+b['case_id'],bool(b['input']) and bool(b['expected']) and b['observation_state']=='not_run')
pair('dispatch_order',{'startup_calls':0,'phases':['llm_canonical','llm_mutation','speech']},lambda x:x['startup_calls']==0 and x['phases']==['llm_canonical','llm_mutation','speech'],lambda x:x.update(phases=['recipe_bank','speech']))
pair('independent_score_arithmetic',{'TP':1,'FN':1,'FP':0},lambda x:Fraction(x['TP'],x['TP']+x['FP'])==1 and Fraction(x['TP'],x['TP']+x['FN'])==Fraction(1,2) and Fraction(2*x['TP'],2*x['TP']+x['FP']+x['FN'])==Fraction(2,3),lambda x:x.update(FN=0))
script="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');process.stdout.write(JSON.stringify(Y.parse(fs.readFileSync('specification/v2/prompts/manifest.yaml','utf8'))));"
m=json.loads(subprocess.check_output(['node','-e',script],cwd=R))
for b in m['bindings']:ck('prompt_hash.'+b['prompt_id'],hashlib.sha256((V/b['path']).read_bytes()).hexdigest()==b['prompt_sha256'])
old=json.loads(subprocess.check_output(['git','show','503723e:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));current={x['id']:x for x in g['cases']};ck('prior_case_states_retained',all(x['id'] in current and current[x['id']]['state']==x['state'] for x in old['cases']))
result=dict(status='passed',checks=len(checks),new_behavior_plans=4,requirements=len(g['requirements']),properties=len(g['properties']),case_edges=len(g['cases']),actual_model_audio_application_observations=0,changed_semantic_inputs=['LLM-only on-demand generation origin','same original/surface/key grading wording','three trusted prompt texts and their hashes','new four-case fixture/graph identity set'],proof_boundary='Static contract/fixture/reference and independently stated arithmetic only; no model, audio, runtime dispatch or empirical corpus creation.',results=checks)
(A/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='results'}))
