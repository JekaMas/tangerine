"""Active spec/graph metadata reconciliation only; no application operation."""
import ast,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['sha','save','fields']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'helpers','exec'))
# Correct stale plan clauses without changing original taxonomy/formula/source bytes.
p=C/'specs/specification-fullness/spec.md';s=p.read_text();s=s.replace('All remaining subfindings and source contracts block a gap-free readiness claim.','Historical source audits retain their original evidence limits. Current product-relevant dependencies follow docs/simple-local-product.md and specification/v2/docs/product-data-relevance.md; unavailable optional sources do not block independently generated exercises.')
s=s.replace('A model approval or one person represented as two reviewers cannot publish a case.','An ordinary generated case is usable once its real audio and key are stored. No model approval or human peer-review ceremony is a prerequisite, and machine provenance cannot be relabelled as a person.')
s=s.replace('One local resource policy MUST bound expensive concurrency, request capacity, cost reservations, and safe archive expansion without disabling stored playback.','One local resource policy MUST apply declared expensive-concurrency/request/import limits and any explicitly enabled cost guard without disabling stored playback. Unknown prices MUST remain unknown; a disabled optional cost guard MUST NOT block ordinary generation merely because price is unavailable.')
p.write_text(s)
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
parsed=parse_delta_specs(C);g=json.loads((C/'verification.json').read_text());inv=json.loads((C/'property-inventory.json').read_text());pending=next(x for x in g['commands'] if x['id']=='pending');changed=[];newprops=[];newtests=[];invalidated=[]
def body(d,title):return (R/d['path']).read_text().split('### Requirement: '+title,1)[1].split('#### Scenario:',1)[0].strip()
for req in g['requirements']:
 d=parsed[(req['capability'],req['title'])]
 if req['fingerprint']!=d['fingerprint']:
  changed.append(req['id']);req['fingerprint']=d['fingerprint'];statement=body(d,req['title'])
  for p in g['properties']:
   if p['requirement_id']==req['id']:p['statement']=statement
  for x in inv:
   if x['id']==req['id']:x['statement']=statement
 for c in g['cases']:
  p=next(x for x in g['properties'] if x['id']==c['property_id'])
  if p['requirement_id']==req['id']:c['scenario_fingerprint']=d['scenario_fingerprints'][c['scenario']]
for p in g['properties']:
 if p['id']=='RUN-03.P2':
  p['statement']='First-start local library returns the actual empty PostgreSQL result without login/session state and without fabricated demo records.'
 elif p['id']=='RUN-06.P3':
  p['statement']='Restart preserves the actual local workspace catalog, preparation checkpoint, saved answer/key/audio/policy identities; isolated restore refuses an existing target without altering it.'
 else:continue
 for c in g['cases']:
  if c['property_id']!=p['id']:continue
  if c['state']=='implemented':
   invalidated.append(copy.deepcopy(c));c['state']='blocked';c['blocker']='Original receipt covers former account/session contract. Current no-login/workspace-persistence property requires later actual native-owner observations; old receipt is retained as historical evidence only.'
  c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+['specification/v2/docs/preparation-persistence.md','specification/v2/docs/simple-local-product.md']))
for (cap,title),d in parsed.items():
 if cap!='final-spec-closure':continue
 rid=title.split()[0]
 if any(x['id']==rid for x in g['requirements']):continue
 pid=rid+'.P1';statement=body(d,title)
 g['requirements'].append(dict(id=rid,capability=cap,title=title,fingerprint=d['fingerprint']))
 p=dict(id=pid,requirement_id=rid,statement=statement,scenarios=d['scenarios'],owner='services/api',oracle='Literal constructed input/output/key/state/arithmetic packet and independent reference identity set; later actual model/audio/storage observations are not replaced by static checks.',source_globs=['services/api/**','services/speech/**','services/web/**','specification/v2/docs/preparation-persistence.md','specification/v2/docs/key-repair-projection.md','specification/v2/docs/self-contained-generation.md','specification/v2/domain/verification-fixtures.v1.json']);g['properties'].append(p);newprops.append(pid)
 inv.append(dict(id=rid,capability=cap,title=title,statement=statement,scenarios=d['scenarios'],owner=p['owner'],source='Actual user instruction to resolve four remaining specification gaps, with ordinary LLM judging and no human review.'))
 for idx,scenario in enumerate(d['scenarios'],1):
  for polarity in ['positive','negative']:
   cid=f'{pid}.S{idx}.{polarity.upper()}';tid='planned::final-spec-closure::'+cid;c=copy.deepcopy(g['cases'][-1]);c.update(id=cid,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=d['scenario_fingerprints'][scenario],setup='Exact fixture catalogue binding will be authored in this batch.',observable='Concrete expected revision/resume/context/data result.',red_expectation='Violate independently stated packet.',green_expectation='Observe the exact named outcome through actual native owners.',test_id=tid,command_id='pending',state='blocked',source_path='tests/acceptance/test_final_spec_closure.py',source_sha256=None,invalidation_dependencies=p['source_globs']+[d['path']],substitution=dict(classification='UNDECIDED',note='No current model/audio/application evidence; constructed contract packet only.'),blocker='Specification-only task; later actual application/provider behavior is unperformed.');g['cases'].append(c);pending['expected_markers'].append(tid);newtests.append(tid)
save(C/'verification.json',g);save(C/'property-inventory.json',inv);prior=json.loads((A/'invalidated-historical-cases.json').read_text()) if (A/'invalidated-historical-cases.json').exists() else [];invalidated=list({x['id']:x for x in prior+invalidated}.values());save(A/'invalidated-historical-cases.json',invalidated)
d=json.loads((C/'discovery.json').read_text());d['scope']['property_ids']+=newprops;d['scope']['test_ids']+=newtests
d['reviews'].append(dict(id='final-spec-closure-20261009',question='Resolve typed key repair, durable preparation resume, self-contained generated context and exact fixtures for every declared property/case without adding accounts, peers, a queue or new ordinary judging stages.',property_ids=[x['id'] for x in g['properties']],test_ids=sorted(set(x['test_id'] for x in g['cases'])),searches=[dict(kind='exact',status='completed',query='Read named schema/prompt/operation/storage/scoring and prior gap contracts; inspect every current graph property/case identity and bind literal positive/negative input/expected/oracle packets.',outcome='Typed complete proposal and persisted preparation association specified; private-context examples prohibited; fixture plans cover the finite graph. Former login/account proof scope invalidated explicitly.',results=[dict(path=x,classification='change_candidate',reason='Declarative producer/consumer or exact expectation under current user decision.') for x in ['specification/v2/contracts/llm-review-input.schema.json','specification/v2/contracts/key-repair-proposal.schema.json','specification/v2/contracts/preparation-state.schema.json','specification/v2/domain/verification-fixtures.v1.json','openspec/changes/implement-teacher-error-trainer/specs/final-spec-closure/spec.md']]),dict(kind='semantic',status='not_applicable',query='Discover unfamiliar implementation ownership.',outcome='No unfamiliar code ownership or semantic evidence claimed.',reason='Spec-only task with known declarative paths.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Inspect implementation symbols.',outcome='No code or runtime inspection claimed.',reason='Specification-only task.',results=[])],disposition='current_change',rationale='Actual user instruction to resolve these four specification gaps; no implementation, inference, speech or publication authorized.'))
d['reviews']=list({x['id']:x for x in d['reviews']}.values());d['scope']['property_ids']=list(dict.fromkeys(d['scope']['property_ids']));d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']));save(C/'discovery.json',d)
# New schemas use the existing local document/assets storage; enumerate all contract fields.
meta=json.loads((V/'domain/persistence-map.json').read_text());known={x['schema'] for x in meta['records']}
for name,persistent,storage in [('key-repair-proposal',False,'LLM canonical payload stored with review/judgment and private raw receipt assets'),('preparation-settings',True,'immutable private settings asset linked from preparation document'),('preparation-state',True,'document.payload with entity_head revision and linked private assets')]:
 schema='contracts/'+name+'.schema.json'
 if schema not in known:meta['records'].append(dict(kind=name,schema=schema,schema_version='2.0.0',persistent_domain_record=persistent,storage=storage,sha256=sha(V/schema),fields=fields(json.loads((V/schema).read_text()))))
changed_schema=[]
for r in meta['records']:
 digest=sha(V/r['schema'])
 if digest!=r['sha256']:changed_schema.append(r['schema'])
 r['sha256']=digest;r['fields']=fields(json.loads((V/r['schema']).read_text()))
save(V/'domain/persistence-map.json',meta);flat=[dict(schema=Path(x['schema']).name,**f) for x in meta['records'] for f in x['fields']];save(V/'language/field-index.json',dict(schema_count=len(meta['records']),field_count=len(flat),fields=flat))
p=V/'docs/data-dictionary.md';s=p.read_text()
for r in meta['records']:
 row=f"| {r['kind']} | {r['schema_version'] or 'schema hash'} | {r['storage']} | {len(r['fields'])} |"
 pattern=r'^\| '+re.escape(r['kind'])+r' \|.*$'
 if re.search(pattern,s,re.M):s=re.sub(pattern,lambda _:row,s,flags=re.M)
 else:s+='\n'+row
p.write_text(s)
save(A/'graph-reconciliation.json',dict(changed_requirements=changed,new_properties=newprops,new_edges=len(newtests),invalidated_historical_cases=[x['id'] for x in invalidated],schemas=len(meta['records']),fields=len(flat)))
print((A/'graph-reconciliation.json').read_text())
