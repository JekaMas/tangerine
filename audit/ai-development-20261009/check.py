"""Static contract/property checks and independent constructed coverage oracles.

No runtime/inference/export or production test is executed by this audit.
"""
import copy,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import unquote,urlparse
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(i,c,proof='Static artifact/contract check'):
 checks.append(dict(id=i,status='passed'if c else'failed',proof=proof));assert c,i
def pair(i,f,p,b):
 ck(i+'.positive',p(f));bad=copy.deepcopy(f);b(bad);ck(i+'.negative',not p(bad),'Constructed specification counterexample')
def load(n):return json.loads((V/'contracts'/(n+'.schema.json')).read_text())
policy=json.loads((V/'domain/ai-development.v1.json').read_text());props=json.loads((A/'properties.json').read_text());doc=(V/'docs/ai-development.md').read_text();run=load('ai-development-run');inventory=load('ai-surface-inventory')
pair('mandatory_development_optional_runtime',policy,lambda x:x['mandatory_for']=='Tangerine AI development completion with actual execution claims'and x['ordinary_runtime_lab_required']is False,lambda x:x.update(ordinary_runtime_lab_required=True))
pair('no_extra_human_threshold_corpus_gates',policy,lambda x:not any(x[k]for k in ['requires_human_review','requires_quality_threshold','requires_full_corpus','requires_periodic_calls']),lambda x:x.update(requires_human_review=True))
pair('explicit_capture_not_workspace_change',policy,lambda x:x['development_trace_enabled']and x['development_sanitized_capture_enabled']and not x['ordinary_capture_settings_modified'],lambda x:x.update(ordinary_capture_settings_modified=True))
pair('all14_inference_surfaces',policy,lambda x:len(x['planned_surfaces'])==14 and len({s['id']for s in x['planned_surfaces']})==14 and {s['kind']for s in x['planned_surfaces']}=={'llm','judge','tts','asr','assessment'},lambda x:x['planned_surfaces'].pop())
pair('all_trusted_fragment_origins',policy,lambda x:set(x['trusted_fragment_classes'])=={'stage_prompt','context_instruction','schema_description','wire_schema_projection','repair_wrapper','fallback_wrapper','judge_rubric','speech_reference_policy','adapter_role_frame'},lambda x:x['trusted_fragment_classes'].remove('adapter_role_frame'))
pair('no_fake_current_inference',policy,lambda x:all(s['implementation_state']=='planned'for s in x['planned_surfaces']),lambda x:x['planned_surfaces'][0].update(implementation_state='implemented'))
pair('typed_real_observations',run,lambda x:all(k in x['required']for k in ['inventory_asset','dependencies','selected_case_ids','required_surface_ids','observations','dispatch_observer_asset','coverage','discrepancies','mlflow_run_ids','mlflow_artifact_refs']),lambda x:x['required'].remove('dispatch_observer_asset'))
pair('exact_snapshot_parts',run,lambda x:all(k in x['$defs']['execution_snapshot']['required']for k in ['binding_asset','input_parts','wire_request','wire_format','omissions','reconstruction_status','inspection_limits']),lambda x:x['$defs']['execution_snapshot']['required'].remove('wire_request'))
pair('all_attempt_kinds',policy,lambda x:set(x['attempt_kinds'])=={'initial','transport_retry','wire_fallback','semantic_repair','local_inference','cache_reference'},lambda x:x['attempt_kinds'].remove('semantic_repair'))
pair('observed_not_empty_scope_or_export',run,lambda x:x['allOf'][0]['then']['properties']['selected_case_ids']['minItems']==1 and x['allOf'][0]['then']['properties']['mlflow_artifact_refs']['minItems']==1 and x['allOf'][0]['then']['properties']['discrepancies']['maxItems']==0,lambda x:x['allOf'][0]['then']['properties']['discrepancies'].update(maxItems=1))
pair('inventory_unknown_paths_visible',inventory,lambda x:all(k in x['required']for k in ['source_revision','entries','dependencies','non_ai_calls','unresolved_paths','inventory_sha256']),lambda x:x['required'].remove('unresolved_paths'))
pair('actual_fragment_versions',inventory,lambda x:'trusted_fragments'in x['properties']['entries']['items']['required']and'sha256'in x['properties']['entries']['items']['properties']['trusted_fragments']['items']['required'],lambda x:x['properties']['entries']['items']['required'].remove('trusted_fragments'))
# Independent finite evidence-join oracle, using separately supplied dispatch IDs.
# It does not call the planned product verifier or prove actual instrumentation.
def complete(f):
 ds=f['dispatches'];ns=f['native'];es=f['exports']
 return bool(ds)and len(ds)==len(set(ds))and len(ns)==len(set(ns))and len(es)==len(set(es))and set(ds)==set(ns)==set(es)
base=dict(dispatches=['initial','repair','local'],native=['initial','repair','local'],exports=['initial','repair','local'])
pair('coverage_join',base,complete,lambda x:x['native'].pop())
pair('orphan_dispatch',base,complete,lambda x:x['dispatches'].append('hidden_helper'))
pair('duplicate_export_not_coverage',base,complete,lambda x:x.update(exports=['initial','initial','local']))
pair('missing_export_not_synchronized',base,complete,lambda x:x['exports'].pop())
ck('zero_calls_not_integration',not complete(dict(dispatches=[],native=[],exports=[])),'Independent constructed empty-population counterexample')
cache=dict(dispatches=['original'],native=['original'],exports=['original']);pair('cache_reference_no_new_dispatch',cache,complete,lambda x:x['native'].append('cache_view_as_inference'))
sync_before=['original','repair'];sync_after=['original','repair'];ck('sync_preserves_dispatch_population',sync_before==sync_after,'Constructed export-only expectation, not runtime observation')
for p in props:
 ck('distinct_cases_oracle.'+p['id'],bool(p['oracle'])and p['positive_setup']!=p['negative_setup']and p['positive_expectation']!=p['negative_expectation'])
ck('all12_properties',len(props)==12 and len({p['id']for p in props})==12)
checks_by_property={p['id']:[]for p in props}
# Semantic commitments are read in their owning document, not treated as runtime proof.
terms={'DEV-01':['Development completion cannot claim','Ordinary downloaded application use'], 'DEV-02':['fourteen current planned inference surfaces','dynamic plugin/adapters'], 'DEV-03':['schema descriptions','repair/fallback wrappers'], 'DEV-04':['after all projection/default/repair construction','multipart framing'], 'DEV-05':['refused/incomplete/transport-error/late/cancelled/local execution','cache view'], 'DEV-06':['blind extraction sees no key','Azure assessment receives actual surface ReferenceText'], 'DEV-07':['changes the appropriate binding/cache identity','Freeze exported numeric/local content versions'], 'DEV-08':['failed/unperformed rows','candidate does not receive hidden expected labels'], 'DEV-09':['known correct, known incorrect','candidate\'s mutation list is not independent reference truth'], 'DEV-10':['redacted-byte hashes separately','inspection limit'], 'DEV-11':['Explicit sync only exports retained artifacts','development record is incomplete'], 'DEV-12':['three-way join','Zero denominator is N/A']}
for pid,phrases in terms.items():pair('contract.'+pid,dict(text=doc),lambda x,t=phrases:all(k.lower()in x['text'].lower()for k in t),lambda x,t=phrases:x.update(text=x['text'].replace(t[0],'')))
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let d={},n=0;function walk(p){for(const x of fs.readdirSync(p,{withFileTypes:true})){let f=p+'/'+x.name;if(x.isDirectory())walk(f);else if(/\\.ya?ml$/.test(f)){d[f.replace('specification/v2/','')]=Y.parse(fs.readFileSync(f,'utf8'));n++;}}}walk('specification/v2');process.stdout.write(JSON.stringify({docs:d,count:n}));"""
y=json.loads(subprocess.check_output(['node','-e',node],cwd=R,text=True));Y=y['docs'];jsons={p.relative_to(V).as_posix():json.loads(p.read_text())for p in V.rglob('*.json')};ck('current_json_yaml_parse',len(jsons)>130 and y['count']==22)
refs=[]
def walk(d,path):
 if isinstance(d,dict):
  if '$ref'in d:
   u=urlparse(d['$ref']);target=path if not u.path else path.parent/unquote(u.path)
   if not u.scheme:
    assert target.is_file();n=json.loads(target.read_text())
    for k in unquote(u.fragment).lstrip('/').split('/')if u.fragment else[]:n=n[k.replace('~1','/').replace('~0','~')]
    refs.append(d['$ref'])
  for v in d.values():walk(v,path)
 elif isinstance(d,list):
  for v in d:walk(v,path)
for p in V.rglob('*.schema.json'):walk(json.loads(p.read_text()),p)
ck('all_current_schema_refs_resolve',len(refs)==88)
meta=jsons['domain/persistence-map.json'];index=jsons['language/field-index.json'];flat=[]
for r in meta['records']:
 assert sha(V/r['schema'])==r['sha256']
 for f in r['fields']:
  n=jsons[r['schema']]
  for k in f['pointer'].lstrip('/').split('/'):n=n[int(k)]if isinstance(n,list)else n[k.replace('~1','/').replace('~0','~')]
  assert hashlib.sha256(json.dumps(n,separators=(',',':')).encode()).hexdigest()==f['rule_sha256']
  flat.append(dict(schema=Path(r['schema']).name,**f))
ck('complete_schema_field_hash_index',index['fields']==flat and index['schema_count']==len(meta['records'])and index['field_count']==len(flat))
ck('all_semantic_schema_hashes',all(sha(V/r['schema'])==r['schema_sha256']for r in Y['domain/semantic-invariants.yaml']['schemas'].values()))
cv=Y['domain/version-compatibility.yaml'];vector=next(v for v in cv.values()if isinstance(v,list)and v and isinstance(v[0],dict)and'path'in v[0]);files={p.relative_to(V).as_posix()for p in V.rglob('*')if p.is_file()}-{'domain/version-compatibility.yaml'};ck('current_vector_complete',{x['path']for x in vector}==files and all(sha(V/x['path'])==x['sha256']for x in vector))
manifest=Y['prompts/manifest.yaml'];ck('original9_stage_phase_surface_coverage',{(b['stage'],b.get('phase'))for b in manifest['bindings']}=={(s['stage'],s['phase'])for s in policy['planned_surfaces']if s['kind']=='llm'})
oldgraph=json.loads(subprocess.check_output(['git','show','d18920f:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R,text=True));graph=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
for k in ['requirements','properties','cases']:
 now={x['id']:x for x in graph[k]};ck('prior_graph_retained.'+k,all(now[x['id']]==x for x in oldgraph[k]))
ck('48_new_behavior_edges_blocked',sum(x['id'].startswith('DEV-')and x['state']=='blocked'for x in graph['cases'])==48)
for p in ['domain/error-taxonomy.v1.yaml','domain/mutation-recipes.v1.json','domain/metrics.v1.yaml','domain/llm-quality-metrics.v1.json','domain/corpus-sources.v1.yaml','domain/providers.v1.yaml','prompts/manifest.yaml']:
 ck('preserved.'+p,subprocess.check_output(['git','show','d18920f:specification/v2/'+p],cwd=R)==(V/p).read_bytes())
for p in ['AGENTS.md','CLAUDE.md']:
 current=(R/p).read_text();before=subprocess.check_output(['git','show','d18920f:'+p],cwd=R,text=True)
 block=lambda s:s.split('<!-- agent-workflow:start -->')[1].split('<!-- agent-workflow:end -->')[0]
 ck('managed_instruction_block_preserved.'+p,block(current)==block(before)and'AI_DEVELOPMENT.md'in current)
review=(R/'docs/development/REVIEW_AND_VALIDATION.md').read_text();ck('stale_review_gates_removed','Release requires all 122 source IDs'not in review and'tenant/user authorization'not in review and'No human peer review'in review)
(A/'validation-results.json').write_text(json.dumps(dict(passed=len(checks),failed=0,checks=checks,files=len(files)+1,schemas=len(meta['records']),fields=len(flat),schema_references=len(refs),proof_boundary='Static contracts/indexes and independent constructed coverage arithmetic only; no production verifier/inference/MLflow runtime was observed.'),indent=2)+'\n')
(A/'file-inventory.json').write_text(json.dumps([dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(V.rglob('*'))if p.is_file()],indent=2)+'\n')
print(json.dumps(dict(passed=len(checks),files=len(files)+1,schemas=len(meta['records']),fields=len(flat),schema_references=len(refs))))
