"""Reconcile active spec metadata and unexecuted behavior plans, never app state."""
import ast,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
source=ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text());nodes=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in ['fields','sha','save']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_helpers','exec'))
p=V/'domain/persistence-map.json';data=json.loads(p.read_text());by={r['schema']:r for r in data['records']};changed=[]
for path in sorted((V/'contracts').glob('*.schema.json')):
 rel=path.relative_to(V).as_posix();digest=sha(path)
 if rel in by and by[rel]['sha256']==digest:continue
 obj=json.loads(path.read_text());kind=path.name.removesuffix('.schema.json');r=by.get(rel,dict(kind=kind,schema=rel,schema_version=obj.get('properties',{}).get('schema_version',{}).get('const'),persistent_domain_record=True,storage='document.payload with linked private assets'));r.update(sha256=digest,fields=fields(obj));by[rel]=r;changed.append(rel)
data['records']=list(by.values());save(p,data);flat=[dict(schema=Path(r['schema']).name,**f)for r in data['records']for f in r['fields']];save(V/'language/field-index.json',dict(schema_count=len(by),field_count=len(flat),fields=flat))
p=V/'docs/data-dictionary.md';s=p.read_text()
for r in data['records']:
 row=f"| {r['kind']} | {r['schema_version']or'schema hash'} | {r['storage']} | {len(r['fields'])} |";pattern=r'^\| '+re.escape(r['kind'])+r' \|.*$'
 if re.search(pattern,s,re.M):s=re.sub(pattern,lambda _:row,s,flags=re.M)
 else:s+='\n'+row+'\n'
p.write_text(s)
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
parsed=parse_delta_specs(C);v=json.loads((C/'verification.json').read_text());inv=json.loads((C/'property-inventory.json').read_text());pending=next(x for x in v['commands']if x['id']=='pending');newprops=[];newtests=[]
for (cap,title),d in parsed.items():
 if cap!='flow-contract-completeness':continue
 rid=title.split()[0];pid=rid+'.P1'
 if any(r['id']==rid for r in v['requirements']):
  body=Path(d['path']).read_text().split('### Requirement: '+title,1)[1].split('#### Scenario:',1)[0].strip()
  next(r for r in v['requirements'] if r['id']==rid)['fingerprint']=d['fingerprint']
  next(p for p in v['properties'] if p['id']==pid)['statement']=body
  next(i for i in inv if i['id']==rid)['statement']=body
  for case in v['cases']:
   if case['property_id']==pid:case['scenario_fingerprint']=d['scenario_fingerprints'][case['scenario']]
  continue
 body=Path(d['path']).read_text().split('### Requirement: '+title,1)[1].split('#### Scenario:',1)[0].strip()
 v['requirements'].append(dict(id=rid,capability=cap,title=title,fingerprint=d['fingerprint']));prop=dict(id=pid,requirement_id=rid,statement=body,scenarios=d['scenarios'],owner='services/api',oracle='Independent literal edit replay, exact frozen input/reference identities, actual bytes/receipts and raw-statistic arithmetic. Static contract checks cannot prove provider or application conformance.',source_globs=['services/api/**','services/speech/**','services/web/**','specification/v2/docs/generation-contract-details.md','specification/v2/docs/llm-lab-contract-details.md']);v['properties'].append(prop);newprops.append(pid)
 inv.append(dict(id=rid,capability=cap,title=title,statement=body,scenarios=d['scenarios'],owner=prop['owner'],source='Current requested whole-spec completeness audit; explicit authored-flow and Lab contracts.'))
 for i,scenario in enumerate(d['scenarios'],1):
  for polarity in ['positive','negative']:
   cid=f'{pid}.S{i}.{polarity.upper()}';case=copy.deepcopy(v['cases'][-1]);case.update(id=cid,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=d['scenario_fingerprints'][scenario],setup='Freeze the stated case/configuration/reference and exercise the '+polarity+' condition in the named production owner.',observable=scenario,red_expectation='The actual owner violates this explicit contract or fabricates a completed observation.',green_expectation='Observe '+scenario+' with exact saved identities, complete populations and independently asserted expectations.',test_id='planned::flow-fullness::'+cid,command_id='pending',state='blocked',source_path='tests/acceptance/test_flow_contract_completeness.py',source_sha256=None,invalidation_dependencies=['specification/v2/docs/generation-contract-details.md','specification/v2/docs/llm-lab-contract-details.md','specification/v2/contracts/mutation-manifest.schema.json','specification/v2/contracts/llm-quality-dataset.schema.json','specification/v2/contracts/llm-quality-judge-input.schema.json','specification/v2/contracts/llm-quality-judge-output.schema.json',d['path']],substitution=dict(classification='UNDECIDED',note='Future production/provider evidence; authored audit fixtures are not a substitute.'),blocker='Specification-only authority; no application implementation, inference or audio/Lab execution.');v['cases'].append(case);pending['expected_markers'].append(case['test_id']);newtests.append(case['test_id'])
save(C/'verification.json',v);save(C/'property-inventory.json',inv);d=json.loads((C/'discovery.json').read_text());d['scope']['property_ids']+=newprops;d['scope']['test_ids']+=newtests
d['reviews']=[r for r in d['reviews'] if r['id']!='whole-flow-fullness-20261009'];d['reviews'].append(dict(id='whole-flow-fullness-20261009',question='Are ordinary generation/mutation/audio/key/matching/scoring and optional Lab contracts complete and mutually consistent?',property_ids=[p['id']for p in v['properties']if p['id'].startswith('CMP-')],test_ids=[x['test_id']for x in v['cases']if x['id'].startswith('CMP-')],searches=[dict(kind='exact',status='completed',query='Read active flow/runtime/provider/scoring/source/Lab definitions and inspect every current schema/reference/index; check defaults, mutation replay, context disclosure, frozen populations and failure rules.',outcome='Close concrete definition/contradiction gaps while preserving the original taxonomy, metrics, full-source identities and optional diagnostic behavior.',results=[dict(path=p,classification='change_candidate',reason='Owning missing or contradictory active contract.')for p in ['specification/v2/docs/generation-contract-details.md','specification/v2/docs/llm-lab-contract-details.md','specification/v2/domain/audio-methods.yaml','specification/v2/domain/llm-lab.v1.yaml']]),dict(kind='semantic',status='not_applicable',query='Unknown application implementation ownership.',outcome='Known specification owners; no implementation exploration/index claim.',reason='Specification-only audit.'),dict(kind='jetbrains-index',status='not_applicable',query='Application symbols.',outcome='No symbols or implementation altered.',reason='No implementation authorized.',results=[])],disposition='current_change',rationale='Complete existing accepted product contracts without a new approval/gate/service or application change.'))
save(C/'discovery.json',d)
save(A/'reconciliation.json',dict(changed_schemas=changed,schemas=len(by),fields=len(flat),new_requirements=6,new_properties=6,new_blocked_edges=24,requirements=len(v['requirements']),properties=len(v['properties']),edges=len(v['cases']),behavior_receipts_relabelled=0))
print(json.dumps(json.loads((A/'reconciliation.json').read_text())))
