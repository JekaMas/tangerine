"""Specification metadata/blocked-plan reconciliation; no application execution."""
import ast,copy,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['sha','save','fields']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_helpers','exec'))
p=V/'domain/persistence-map.json';meta=json.loads(p.read_text());changed=[]
for record in meta['records']:
 path=V/record['schema'];digest=sha(path)
 if record['sha256']!=digest:record.update(sha256=digest,fields=fields(json.loads(path.read_text())));changed.append(record['schema'])
save(p,meta);flat=[dict(schema=Path(r['schema']).name,**f) for r in meta['records'] for f in r['fields']];save(V/'language/field-index.json',dict(schema_count=len(meta['records']),field_count=len(flat),fields=flat))
p=V/'docs/data-dictionary.md';s=p.read_text()
for r in meta['records']:
 row=f"| {r['kind']} | {r['schema_version'] or 'schema hash'} | {r['storage']} | {len(r['fields'])} |"
 s=re.sub(r'^\| '+re.escape(r['kind'])+r' \|.*$',lambda _:row,s,flags=re.M)
p.write_text(s)
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
parsed=parse_delta_specs(C);g=json.loads((C/'verification.json').read_text());inv=json.loads((C/'property-inventory.json').read_text());pending=next(x for x in g['commands'] if x['id']=='pending');changedreq=[];selectedprops=[];selectedtests=[]
def body(d,title):return (R/d['path']).read_text().split('### Requirement: '+title,1)[1].split('#### Scenario:',1)[0].strip()
for req in g['requirements']:
 d=parsed[(req['capability'],req['title'])]
 if req['fingerprint']==d['fingerprint']:continue
 changedreq.append(req['id']);req['fingerprint']=d['fingerprint'];statement=body(d,req['title'])
 for prop in g['properties']:
  if prop['requirement_id']!=req['id']:continue
  prop['statement']=statement;selectedprops.append(prop['id'])
  for c in g['cases']:
   if c['property_id']!=prop['id']:continue
   assert c['state'] in ['blocked','planned'],('Do not relabel observed behavior',c['id'])
   c['scenario_fingerprint']=d['scenario_fingerprints'][c['scenario']];c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+['specification/v2/docs/answer-component-scoring.md',d['path']]))
   c['green_expectation']=c['green_expectation']+' Apply current answer-components-v2 component scope: optional explanation cannot penalize or null supported primary credit.';selectedtests.append(c['test_id'])
 for i in inv:
  if i['id']==req['id']:i['statement']=statement
counterexamples=[
 'Return correction credit 0 solely because the separately extracted universal-rule explanation is false.',
 'Skip the supplied explanation because its legacy invitation flag is false, or grade omitted explanation as a primary zero.',
 'Invent a forbidden proposition ID for the extra present-tense detail, or cite a span not equal to the actual answer slice.',
 'Assign the false universal-rule reason to correction, or let a true reason rescue an incorrect past-tense repair.',
 'Return blocks_final_score=true for explanation-only uncertainty, or remove the unknown reason from EA.',
 'Select only works from two incompatible endorsed repairs and publish primary 100 while meaning remains unresolved.',
 'Pool EA=2 for one supplied/one absent reason and use graded recall 1/2 to reduce primary grade.',
 'Use explanation weight10 or LLM-provided partial credit to change the independently expected primary80.',
 'Rewrite primary statistics or heard audio for an explanation-only revision with no changed primary evidence.',
 'Replace saved explanation0 or primary100 with failed/zero score after commentary timeout.',
 'Automatically regrade the historical frozen legacy result after new policy activation.',
 'Exclude unknown supplied explanation from a Lab packet population and call static schema validation an actual model success.',
 'Use the old custom edit/provenance DTO without typed manifest asset/hash association.',
 'Require a source permission epoch or block an independent authored exercise for the unrelated source notice.',
 'Reject the fourth explicit manual render solely due to a candidate-lifetime three-attempt ceiling.',
 'Request a second linguistic-output repair or invent missing measured content.',
 'Require an Azure speech key even though local assets were explicitly set up and local rendering was selected.',
 'Silently switch the selected local/service profile, or publish successful audio with absent weights/key.'
]
plans=[];newprops=[];newtests=[]
for (cap,title),d in parsed.items():
 if cap!='answer-component-scoring':continue
 rid=title.split()[0];pid=rid+'.P1';assert not any(x['id']==rid for x in g['requirements'])
 statement=body(d,title);g['requirements'].append(dict(id=rid,capability=cap,title=title,fingerprint=d['fingerprint']))
 prop=dict(id=pid,requirement_id=rid,statement=statement,scenarios=d['scenarios'],owner='services/api',oracle='Literal given/when/then fixture and independent exact rational/population/state assertions; actual model semantics and storage/speech require later native-owner observations. No current application/model proof.',source_globs=['services/api/**','services/speech/**','services/web/**','specification/v2/docs/answer-component-scoring.md','specification/v2/contracts/evaluator-output.schema.json'])
 g['properties'].append(prop);inv.append(dict(id=rid,capability=cap,title=title,statement=statement,scenarios=d['scenarios'],owner=prop['owner'],source='Actual user correction/optional-explanation decision; current component-scoring contract and routine pre-implementation findings.'));newprops.append(pid)
 raw=(R/d['path']).read_text()
 for idx,scenario in enumerate(d['scenarios'],1):
  fragment=raw.split('#### Scenario: '+scenario,1)[1].split('#### Scenario:',1)[0].split('### Requirement:',1)[0]
  given=re.search(r'\*\*GIVEN\*\* (.*)',fragment)[1];when=re.search(r'\*\*WHEN\*\* (.*)',fragment)[1];then=re.search(r'\*\*THEN\*\* (.*)',fragment)[1];mutant=counterexamples[len(plans)]
  plan=dict(property_id=pid,scenario=scenario,given=given,when=when,expected=then,negative_counterexample=mutant,proof='Concrete unexecuted application/provider plan; independent constructed arithmetic in check.py has narrower scope.');plans.append(plan)
  for polarity in ['positive','negative']:
   cid=f'{pid}.S{idx}.{polarity.upper()}';tid='planned::answer-components::'+cid;c=copy.deepcopy(g['cases'][-1]);c.update(id=cid,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=d['scenario_fingerprints'][scenario],setup=given+'. Action: '+when+'. '+('Use actual supported native-owner observations.' if polarity=='positive' else 'Counterexample: '+mutant),observable=then,red_expectation='Violate the independent literal expectation: '+then,green_expectation='Observe '+then,test_id=tid,command_id='pending',state='blocked',source_path='tests/acceptance/test_answer_components.py',source_sha256=None,invalidation_dependencies=['specification/v2/docs/answer-component-scoring.md','specification/v2/contracts/evaluator-output.schema.json','specification/v2/contracts/scoring-input.schema.json','specification/v2/contracts/score-result.schema.json','specification/v2/contracts/judgment-issue.schema.json','specification/v2/prompts/map-v1.txt','specification/v2/prompts/feedback-v1.txt','specification/v2/domain/configuration-registry.yaml','specification/v2/domain/operations.yaml','specification/v2/domain/operation-ownership.yaml',d['path']],substitution=dict(classification='UNDECIDED',note='Static contract/oracle checks are not actual model, application, speech or Lab evidence.'),blocker='Specification-only authority; application implementation and model/audio/Lab observations remain unperformed.')
   g['cases'].append(c);pending['expected_markers'].append(tid);newtests.append(tid)
save(C/'verification.json',g);save(C/'property-inventory.json',inv);save(A/'BEHAVIOR-PLANS.json',plans)
d=json.loads((C/'discovery.json').read_text());d['scope']['property_ids']+=newprops;d['scope']['test_ids']+=newtests
pids=selectedprops+newprops;tids=sorted(set(selectedtests+newtests))
d['reviews'].append(dict(id='answer-components-20261009',question='Do correction and optional supplied explanation keep separate credit, uncertainty, populations and feedback through mapping/scoring/reconsideration/Lab, with the routine stale mutation/recovery/setup rules removed?',property_ids=pids,test_ids=tids,searches=[dict(kind='exact',status='completed',query='Read named schemas/prompts/scoring/flow/lifecycle/Lab/operation/default contracts and previous EXP findings; trace additional semantic assertions to exact credit, issue state, persisted sufficient statistics and feedback.',outcome='Apply actual user component policy and EXP-001/005/006/007/008/009 repairs; retain unresolved typed key repair, preparation resume, decisive context projection and older generic fixture design.',results=[dict(path=x,classification='change_candidate',reason='Known declarative producer/consumer/policy or exact affected OpenSpec definition.') for x in ['specification/v2/docs/answer-component-scoring.md','specification/v2/contracts/evaluator-output.schema.json','specification/v2/contracts/scoring-input.schema.json','specification/v2/contracts/judgment-issue.schema.json','specification/v2/docs/math-and-judgments.md','openspec/changes/implement-teacher-error-trainer/specs/answer-component-scoring/spec.md']]),dict(kind='semantic',status='not_applicable',query='Discover unfamiliar implementation ownership.',outcome='Known specification paths; no implementation owner or semantic evidence claim.',reason='User explicitly restricts this task to specification updates and checks.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Inspect code symbols/references.',outcome='No code-symbol or runtime claim.',reason='Known declarative contracts, no implementation authorized.',results=[])],disposition='current_change',rationale='User authorizes applying independent correction/optional-explanation assessment and suitable related repairs to the active spec. No extra approval, human review, service or ordinary model stage.'))
save(C/'discovery.json',d)
# Update schema and prompt bindings, then full active file vector once.
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml'),crypto=require('crypto');const V='specification/v2/';let sha=p=>crypto.createHash('sha256').update(fs.readFileSync(V+p)).digest('hex');let load=p=>Y.parse(fs.readFileSync(V+p,'utf8'));let save=(p,d)=>fs.writeFileSync(V+p,Y.stringify(d));let s=load('domain/semantic-invariants.yaml');for(let x of Object.values(s.schemas))x.schema_sha256=sha(x.schema);save('domain/semantic-invariants.yaml',s);let m=load('prompts/manifest.yaml');for(let b of m.bindings){b.prompt_sha256=sha(b.path);b.input_schema_sha256=sha('contracts/'+b.input_schema);b.output_schema_sha256=sha('contracts/'+b.output_schema);}save('prompts/manifest.yaml',m);let c=load('domain/version-compatibility.yaml'),files=[];function walk(p){for(let e of fs.readdirSync(V+p,{withFileTypes:true})){let q=p+e.name;if(e.isDirectory())walk(q+'/');else if(q!='domain/version-compatibility.yaml')files.push({path:q,sha256:sha(q)});}}walk('');c.files=files.sort((a,b)=>a.path.localeCompare(b.path));save('domain/version-compatibility.yaml',c);"""
subprocess.run(['node','-e',node],cwd=R,check=True)
save(A/'reconciliation.json',dict(changed_schemas=changed,schemas=len(meta['records']),fields=len(flat),changed_existing_requirements=changedreq,new_requirements=len(newprops),new_properties=len(newprops),new_blocked_edges=len(newtests),requirements=len(g['requirements']),properties=len(g['properties']),edges=len(g['cases']),actual_behavior_receipts_relabelled=0))
print(json.dumps(json.loads((A/'reconciliation.json').read_text())))
