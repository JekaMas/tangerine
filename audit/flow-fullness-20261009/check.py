"""Read-only whole-spec artifact checks and independent constructed oracles.

This is not production execution, JSON Schema engine conformance or LLM quality.
"""
import copy,hashlib,json,subprocess
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote,urlparse
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(name,condition,detail='Static contract/artifact observation only'):
 checks.append(dict(id=name,status='passed'if condition else'failed',detail=detail));assert condition,name
def pair(name,fixture,predicate,mutate):
 ck(name+'.positive',predicate(fixture));bad=copy.deepcopy(fixture);mutate(bad);ck(name+'.negative',not predicate(bad),'Constructed counterexample, not application behavior')
def load(name):return json.loads((V/'contracts'/(name+'.schema.json')).read_text())
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let d={},n=0;function walk(p){for(const x of fs.readdirSync(p,{withFileTypes:true})){let f=p+'/'+x.name;if(x.isDirectory())walk(f);else if(/\\.ya?ml$/.test(f)){let o=Y.parse(fs.readFileSync(f,'utf8'));d[f.replace('specification/v2/','')]=o;n++;}}}walk('specification/v2');process.stdout.write(JSON.stringify({docs:d,count:n}));"""
y=json.loads(subprocess.check_output(['node','-e',node],cwd=R,text=True));Y=y['docs'];ck('all_yaml_parse',y['count']>0)
alljson={p.relative_to(V).as_posix():json.loads(p.read_text())for p in V.rglob('*.json')};ck('all_json_parse',len(alljson)>130)
refs=[]
def walk(d,path):
 if isinstance(d,dict):
  if '$ref'in d:
   ref=d['$ref'];u=urlparse(ref);target=path if not u.path else path.parent/unquote(u.path)
   if not u.scheme:
    assert target.is_file(),(path,ref)
    node=json.loads(target.read_text())
    for part in unquote(u.fragment).lstrip('/').split('/')if u.fragment else[]:node=node[part.replace('~1','/').replace('~0','~')]
    refs.append((str(path),ref))
  for v in d.values():walk(v,path)
 elif isinstance(d,list):
  for v in d:walk(v,path)
for p in V.rglob('*.schema.json'):walk(json.loads(p.read_text()),p)
ck('every_local_schema_reference_resolves',len(refs)>80)
meta=alljson['domain/persistence-map.json'];index=alljson['language/field-index.json'];flatten=[]
for record in meta['records']:
 ck('schema_hash.'+record['kind'],sha(V/record['schema'])==record['sha256'])
 for f in record['fields']:
  node=alljson[record['schema']]
  for part in f['pointer'].lstrip('/').split('/'):node=node[int(part)]if isinstance(node,list)else node[part.replace('~1','/').replace('~0','~')]
  assert hashlib.sha256(json.dumps(node,separators=(',',':')).encode()).hexdigest()==f['rule_sha256'],(record['schema'],f['pointer'])
  flatten.append(dict(schema=Path(record['schema']).name,**f))
ck('all_field_pointers_and_rule_hashes',index['fields']==flatten and index['field_count']==len(flatten))
for kind,rule in Y['domain/semantic-invariants.yaml']['schemas'].items():ck('semantic_schema_hash.'+kind,sha(V/rule['schema'])==rule['schema_sha256'])
compat=Y['domain/version-compatibility.yaml'];vector=next(x for x in compat.values()if isinstance(x,list)and x and isinstance(x[0],dict)and'path'in x[0]);actual={p.relative_to(V).as_posix()for p in V.rglob('*')if p.is_file()}-{'domain/version-compatibility.yaml'}
ck('complete_current_contract_vector',set(x['path']for x in vector)==actual and all(sha(V/x['path'])==x['sha256']for x in vector))
for b in Y['prompts/manifest.yaml']['bindings']:ck('prompt_binding.'+b['prompt_id'],sha(V/b['path'])==b['prompt_sha256']and sha(V/'contracts'/b['input_schema'])==b['input_schema_sha256']and sha(V/'contracts'/b['output_schema'])==b['output_schema_sha256'])
for op in Y['domain/operation-ownership.yaml']['operations']:
 name=op.get('request_schema');path=V/'contracts'/(str(name)+'.schema.json')
 if path.exists():
  d=json.loads(path.read_text())
  if 'properties'in d:ck('request_ownership.'+op['id'],set(op['request_fields'])==set(d['properties']))
# Preserve all original categories, recipes, scoring formulas and source scopes byte-for-byte.
protected=['domain/error-taxonomy.v1.yaml','domain/metrics.v1.yaml','domain/mutation-recipes.v1.json','domain/corpus-sources.v1.yaml','domain/providers.v1.yaml']
for p in protected:
 old=subprocess.check_output(['git','show','03abd3d:specification/v2/'+p],cwd=R);ck('preserved.'+p,old==(V/p).read_bytes())
pair('explicit_defaults',Y['domain/configuration-registry.yaml']['simple_preparation'],lambda x:x['pace_wpm']==150 and x['gap_after_ms']==0 and x['task_components']==dict(detection=True,classification=False,correction=True,explanation=False),lambda x:x['task_components'].update(explanation=True))
pair('independent_audit_context',Y['domain/llm-lab.v1.yaml'],lambda x:all('prior_decisions'not in p['component_order']for p in x['context_policies']if p['stage']=='mapping_audit'),lambda x:next(p for p in x['context_policies']if p['stage']=='mapping_audit')['component_order'].append('prior_decisions'))
pair('mapping_context_contains_extraction',Y['domain/llm-lab.v1.yaml'],lambda x:all('extraction'in p['component_order']for p in x['context_policies']if p['stage']in['claim_mapping','mapping_audit']),lambda x:next(p for p in x['context_policies']if p['stage']=='claim_mapping')['component_order'].remove('extraction'))
pair('feedback_context_contains_native_result',Y['domain/llm-lab.v1.yaml'],lambda x:'scoring_result'in next(p for p in x['context_policies']if p['stage']=='feedback')['component_order'],lambda x:next(p for p in x['context_policies']if p['stage']=='feedback')['component_order'].remove('scoring_result'))
pair('quality_warn_not_fail',Y['domain/audio-methods.yaml'],lambda x:x['qc']['sample_peak_warning_gte']==0.9999 and x['qc']['unplanned_silence_warning_ms_gte']==2000 and'sample_peak_reject_gte'not in x['qc'],lambda x:x['qc'].update(sample_peak_reject_gte=0.9999))
pair('frozen_variant_snapshot',load('llm-experiment'),lambda x:'configuration_asset_id'in x['properties']['variants']['items']['required'],lambda x:x['properties']['variants']['items']['required'].remove('configuration_asset_id'))
pair('judge_policy_frozen',load('llm-experiment'),lambda x:all(k in x['required']for k in ['judge_policy_asset_id','judge_policy_sha256'])and'judge_policy'in x['$defs'],lambda x:x['required'].remove('judge_policy_sha256'))
pair('typed_judge_no_grade',load('llm-quality-judge-output'),lambda x:set(x['properties'])=={'schema_version','verdicts'}and set(x['properties']['verdicts']['items']['properties']['verdict']['enum'])=={'supported','unsupported','unknown'},lambda x:x['properties'].update(grade=dict(type='number')))
pair('typed_whole_pipeline_inputs',load('llm-quality-dataset'),lambda x:'answer_pipeline_input'in x['$defs']and'cases'in x['required'],lambda x:x['$defs'].pop('answer_pipeline_input'))
pair('actual_recipe_input',load('generation-input'),lambda x:all(k in x['required']for k in ['mutation_recipes','recipe_registry_sha256']),lambda x:x['required'].remove('mutation_recipes'))
pair('mutation_ledger_complete',load('mutation-manifest'),lambda x:all(k in x['required']for k in ['canonical_asset_id','canonical_sha256','mutated_asset_id','mutated_sha256','edits','acoustic_intents','planned_units','manifest_sha256']),lambda x:x['required'].remove('edits'))
metric=load('llm-experiment')['properties']['rows']['items']['properties']['metrics']['items']
pair('raw_counts_and_known_subtotals',metric,lambda x:all(k in x['required']for k in ['sufficient_statistics','known_subtotal']),lambda x:x['required'].remove('known_subtotal'))
pair('difficulty_labels_match_schema',dict(text=(V/'docs/review-and-gold.md').read_text()),lambda x:'medium lower>=0.5'in x['text']and'expert upper<0.2'in x['text'],lambda x:x.update(text=x['text'].replace('medium lower>=0.5','moderate lower>=0.5')))
pair('native_audio_origin_preserved',load('ground-truth'),lambda x:set(x['properties']['audio']['properties']['origin']['enum'])=={'synthetic','native_recording','local_recording'},lambda x:x['properties']['audio']['properties']['origin']['enum'].remove('native_recording'))
pair('generated_accent_status_matches_schema',dict(text=(V/'docs/generation-contract-details.md').read_text()),lambda x:'accent_evidence=not_verified'in x['text']and'not_verified'in load('ground-truth')['properties']['speakers']['items']['properties']['accent_evidence']['enum'],lambda x:x.update(text=x['text'].replace('accent_evidence=not_verified','accent_evidence=[]')))
# Independent literal replay oracle on Unicode canonical coordinates. No production owner used.
def replay(s,edits):
 out=[];cursor=0
 for e in sorted(edits,key=lambda e:(e['start'],e['order'])):
  assert cursor<=e['start']<=e['end']<=len(s)and s[e['start']:e['end']]==e['old']
  out.extend([s[cursor:e['start']],e['new']]);cursor=e['end']
 return ''.join(out)+s[cursor:]
base='🙂 She works here.';edits=[dict(start=6,end=11,old='works',new='work',order=0),dict(start=2,end=2,old='',new='Well, ',order=0),dict(start=2,end=2,old='',new='um, ',order=1)]
ck('unicode_insertion_deletion_replay',replay(base,edits)=='🙂 Well, um, She work here.','Independent constructed replay arithmetic')
bad=copy.deepcopy(edits);bad[0]['start']=5
try:replay(base,bad);invalid=False
except AssertionError:invalid=True
ck('mislocalized_edit_counterexample',invalid)
counts=[dict(tp=1,fp=0,fn=0),dict(tp=1,fp=8,fn=8)];pooled=Fraction(2*sum(x['tp']for x in counts),sum(2*x['tp']+x['fp']+x['fn']for x in counts));mean=sum(Fraction(2*x['tp'],2*x['tp']+x['fp']+x['fn'])for x in counts)/2
ck('pooled_F1_independent_fixture',pooled==Fraction(1,5)and mean==Fraction(5,9)and pooled!=mean,'Independent arithmetic counterexample to averaging per-row F1')
ck('unknown_cost_known_subtotal_fixture',sum([Fraction(100000,1000000),Fraction(250000,1000000)])==Fraction(7,20),'Known subtotal0.35USD; an additional unknown receipt leaves total unavailable')
cases=['c1','c2'];variants=['baseline','candidate'];reps=2;keys=[(c,v,r)for c in cases for v in variants for r in range(1,reps+1)];ck('planned_cross_product_fixture',len(keys)==8 and len(set(keys))==8);ck('cancelled_rows_full_denominator',Fraction(3,len(keys))==Fraction(3,8),'Three completions plus five failed/cancelled/not_run, not3/3')
graph=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());old=json.loads(subprocess.check_output(['git','show','03abd3d:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R,text=True))
for kind in ['requirements','properties','cases']:
 current={x['id']:x for x in graph[kind]};ck('prior_graph_unchanged.'+kind,all(current[x['id']]==x for x in old[kind]))
ck('new_24_behavior_edges_unexecuted',sum(c['id'].startswith('CMP-')and c['state']=='blocked'for c in graph['cases'])==24)
inventory=[]
for p in sorted(V.rglob('*')):
 if p.is_file():inventory.append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size,line_count=len(p.read_text().splitlines()),kind='schema'if p.name.endswith('.schema.json')else p.suffix.lstrip('.')))
(A/'file-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(A/'validation-results.json').write_text(json.dumps(dict(checks=checks,passed=len(checks),failed=0,proof_boundary='Static whole-spec metadata/contract checks and independent constructed arithmetic only; no app/provider/audio/Lab behavior.',files=len(inventory),schemas=len(meta['records']),fields=len(flatten),local_schema_references=len(refs),yaml_files=y['count']),indent=2)+'\n')
print(json.dumps(dict(passed=len(checks),files=len(inventory),schemas=len(meta['records']),fields=len(flatten),references=len(refs))))
