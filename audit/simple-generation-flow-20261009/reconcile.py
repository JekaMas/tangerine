"""Specification metadata reconciliation only; never imports application/reference code."""
import copy, hashlib, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT/'specification/v2'
CHANGE = ROOT/'openspec/changes/implement-teacher-error-trainer'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def fields(node,pointer=''):
 out=[]
 if isinstance(node,dict):
  for name,rule in node.get('properties',{}).items():
   ptr=pointer+'/properties/'+name.replace('~','~0').replace('/','~1')
   out.append(dict(name=name,pointer=ptr,required_in_parent=name in node.get('required',[]),description=rule.get('description'),schema_reference=rule.get('$ref'),rule_sha256=hashlib.sha256(json.dumps(rule,separators=(',',':')).encode()).hexdigest()))
  for key,value in node.items(): out+=fields(value,pointer+'/'+key.replace('~','~0').replace('/','~1'))
 elif isinstance(node,list):
  for i,value in enumerate(node): out+=fields(value,pointer+'/'+str(i))
 return out
p=V2/'domain/persistence-map.json';data=json.loads(p.read_text());by={r['schema']:r for r in data['records']}
changed=[]
for schema in sorted((V2/'contracts').glob('*.schema.json')):
 rel=schema.relative_to(V2).as_posix(); digest=sha(schema)
 if rel in by and by[rel]['sha256']==digest: continue
 obj=json.loads(schema.read_text());kind=schema.name.removesuffix('.schema.json')
 rec=by.get(rel,dict(kind=kind,schema=rel,schema_version=None,persistent_domain_record=False,storage='derived DTO or actual operation input/output receipt'))
 rec.update(sha256=digest,fields=fields(obj));by[rel]=rec;changed.append(rel)
data['records']=list(by.values());save(p,data)
flat=[dict(schema=Path(r['schema']).name,**f) for r in data['records'] for f in r['fields']]
save(V2/'language/field-index.json',dict(schema_count=len(data['records']),field_count=len(flat),fields=flat))
p=V2/'docs/data-dictionary.md';s=p.read_text()
for r in data['records']:
 row=f"| {r['kind']} | {r['schema_version'] or 'schema hash'} | {r['storage']} | {len(r['fields'])} |"
 pattern=r'^\| '+re.escape(r['kind'])+r' \|.*$'
 if re.search(pattern,s,re.M):s=re.sub(pattern,lambda _:row,s,flags=re.M)
 else:s+='\n'+row+'\n'
p.write_text(s)
if '--indexes-only' in sys.argv:
 print(json.dumps(dict(changed_schemas=changed,schemas=len(data['records']),fields=len(flat))))
 raise SystemExit(0)
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs
parsed=parse_delta_specs(CHANGE);p=CHANGE/'verification.json';v=json.loads(p.read_text());affected=[]
for r in v['requirements']:
 definition=parsed[(r['capability'],r['title'])]
 if r['fingerprint']==definition['fingerprint']:continue
 affected.append(r['id']);r['fingerprint']=definition['fingerprint']
 for prop in v['properties']:
  if prop['requirement_id']!=r['id']:continue
  prop['statement']=r['title']+' under the current simple-generation flow; separate review/empirical sources are optional.'
  for c in v['cases']:
   if c['property_id']!=prop['id']:continue
   if c['state']!='blocked':raise RuntimeError('Changed active behavior receipt needs explicit review: '+c['id'])
   c['scenario_fingerprint']=definition['scenario_fingerprints'][c['scenario']]
   c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+['specification/v2/docs/simple-generation-flow.md',definition['path']]))
   c['setup']='Invoke this specific supported action or inject its stated failure under the latest simple-generation contract; optional review is invoked only when explicitly selected.'
   c['green_expectation']='Observe '+c['scenario']+' under the latest requirement body, without a mandatory extra review/corpus prerequisite.'
pending=next(x for x in v['commands'] if x['id']=='pending');inventory=json.loads((CHANGE/'property-inventory.json').read_text())
for (cap,title),d in parsed.items():
 if cap!='simple-generation-flow':continue
 rid=title.split()[0]
 if any(r['id']==rid for r in v['requirements']):continue
 pid=rid+'.P1';owner='services/speech' if rid=='FLOW-03' else ('services/web' if rid=='FLOW-01' else 'services/api')
 v['requirements'].append(dict(id=rid,capability=cap,title=title,fingerprint=d['fingerprint']))
 v['properties'].append(dict(id=pid,requirement_id=rid,statement=title+' using saved request/text/mutations/audio/answer and actual observations; reference corpora and additional case review are optional.',scenarios=d['scenarios'],owner=owner,oracle='Frozen canonical/mutated script and mutation list, actual stored audio, independently asserted semantic matches and unchanged equations. Static spec checks do not prove provider/application behavior.',source_globs=[owner+'/**','specification/v2/docs/simple-generation-flow.md','specification/v2/contracts/exercise-request.schema.json']))
 inventory.append(dict(id=rid,capability=cap,title=title,statement=v['properties'][-1]['statement'],scenarios=d['scenarios'],owner=owner,source='Actual user primary-flow instruction; specification/v2/docs/simple-generation-flow.md.'))
 for i,scenario in enumerate(d['scenarios'],1):
  for polarity in ['positive','negative']:
   cid=f'{pid}.S{i}.{polarity.upper()}';c=copy.deepcopy(v['cases'][-1]);c.update(id=cid,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=d['scenario_fingerprints'][scenario],setup='Use the stated simple-flow fixture and a '+polarity+' observation, retaining actual phase/audio/key/answer identity.',observable=scenario,red_expectation='The production owner violates the explicit simple-flow action or mishandles its stated failure.',green_expectation='Observe '+scenario+' with exact saved artifacts and unchanged grading formulas.',test_id='planned::simple-flow::'+cid,command_id='pending',state='blocked',source_path='tests/acceptance/test_simple_generation_flow.py',source_sha256=None,invalidation_dependencies=['specification/v2/docs/simple-generation-flow.md','specification/v2/contracts/exercise-request.schema.json','specification/v2/contracts/generation-input.schema.json','specification/v2/prompts/canonical-v1.txt','specification/v2/prompts/generate-v1.txt',d['path']],substitution=dict(classification='UNDECIDED',note='Future application/provider plan; specification static checks cannot substitute.'),blocker='Specification-only authority; no implementation, inference or audio synthesis in this increment.')
   v['cases'].append(c);pending['expected_markers'].append(c['test_id'])
save(p,v);save(CHANGE/'property-inventory.json',inventory)
save(ROOT/'audit/simple-generation-flow-20261009/reconciliation.json',dict(changed_schemas=changed,schemas=len(data['records']),fields=len(flat),changed_existing_requirements=affected,new_requirements=6,new_properties=6,new_blocked_edges=24,requirements=len(v['requirements']),properties=len(v['properties']),case_edges=len(v['cases']),actual_behavior_receipts_relabelled=0))
print(json.dumps(json.loads((ROOT/'audit/simple-generation-flow-20261009/reconciliation.json').read_text())))
