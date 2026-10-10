"""Executable specification integrity and negative oracle-sensitivity checks; no runtime acceptance."""
from pathlib import Path
import json,copy,collections,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());g=load(C/'verification.json');f=load(V/'domain/verification-fixtures.v1.json');s=load(V/'domain/property-test-sets.v1.json');checks=[]
def ck(name,condition):
 checks.append({'name':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
def validate(graph,fixtures,sets):
 props={p['id']:p for p in graph['properties']};cases={c['id']:c for c in graph['cases']};bindings={b['case_id']:b for b in fixtures['case_bindings']};packets={x['id']:x for x in fixtures['fixtures']};rows={x['property_id']:x for x in sets['properties']};pb={x['property_id']:x for x in fixtures['property_bindings']}
 assert len(props)==len(graph['properties'])==len(rows)==len(sets['properties'])==len(pb)
 assert set(rows)==set(props)==set(pb);assert set(cases)==set(bindings);assert len(cases)==len(graph['cases'])==len(fixtures['case_bindings'])
 pending=next(x for x in graph['commands'] if x['id']=='pending');markers=pending['expected_markers'];assert len(markers)==len(set(markers))
 for pid,p in props.items():
  row=rows[pid];assert row['requirement_id']==p['requirement_id'];assert row['owner']==p['owner'];assert row['scenario_names']==p['scenarios'];assert row['runtime_set_observation']=='not_run'
  for pol in ['positive','negative']:
   ids=row[pol+'_cases'];actual={c['id'] for c in cases.values() if c['property_id']==pid and c['polarity']==pol};assert set(ids)==actual;assert len(ids)==len(set(ids))
   unique=set()
   for cid in ids:
    c=cases[cid];b=bindings[cid];x=packets[b['fixture_id']];assert b['property_id']==pid;assert b['polarity']==c['polarity']==pol;assert b['test_id']==c['test_id'];assert b['scenario']==c['scenario'];assert b['observation_state']=='not_run'
    assert isinstance(b['input'],dict) and isinstance(b['expected'],dict);assert b['expected'];assert b['independent_oracle'];assert b['initial_state']==x['initial_state']
    if '.SET2.' in cid or b['fixture_id'].startswith('scenario-'):
     assert b['input']==x[pol]['input'];assert b['expected']==x[pol]['expected']
    unique.add(json.dumps([b['input'],b['expected']],sort_keys=True))
    if '.SET2.' in cid:
     assert c['state']=='blocked';assert c['source_sha256'] is None;assert c['command_id']=='pending';assert c['test_id'] in markers
   assert len(unique)>=2;assert row[pol+'_distinct_packets']==len(unique)
  for scenario in p['scenarios']:
   assert {c['polarity'] for c in cases.values() if c['property_id']==pid and c['scenario']==scenario}=={'positive','negative'}
 for x in fixtures['fixtures']:
  if x['id'].startswith('leaf-acceptable_variant.'):
   assert x['positive']['expected']['design_event_count']==0;assert x['positive']['expected']['design_TP']==0;assert x['positive']['expected']['design_CQ']=='0/1'
   assert x['positive']['expected']['design_DA']==1;assert x['positive']['input']['answer']['stance']=='assert_acceptable'
 return True
ck('complete.current.set.graph.fixture.relationship',validate(g,f,s))
# Independent collection-order invariance; table order is not an identity.
rev=copy.deepcopy(s);rev['properties'].reverse();ck('positive.collection.order.invariance',validate(g,f,rev))
def reject(name,mutate):
 gg,ff,ss=copy.deepcopy(g),copy.deepcopy(f),copy.deepcopy(s);mutate(gg,ff,ss)
 try:validate(gg,ff,ss)
 except (AssertionError,KeyError):ck(name,True)
 else:ck(name,False)
reject('negative.missing.DAG.edge',lambda g,f,s:g['cases'].pop())
reject('negative.wrong.binding.polarity',lambda g,f,s:f['case_bindings'][-1].update(polarity='positive'))
reject('negative.fabricated.set.execution',lambda g,f,s:s['properties'][0].update(runtime_set_observation='passed'))
reject('negative.false.decoy.error.credit',lambda g,f,s:next(x for x in f['fixtures'] if x['id']=='leaf-acceptable_variant.grammar_variant')['positive']['expected'].update(design_TP=1))
reject('negative.unbound.property',lambda g,f,s:s['properties'].pop())
def duplicate(g,f,s):
 pid='COV-001.P1';ids=next(x for x in s['properties'] if x['property_id']==pid)['positive_cases'];b={x['case_id']:x for x in f['case_bindings']};x={x['id']:x for x in f['fixtures']};base=b[ids[0]]
 for cid in ids[1:]:
  b[cid]['input']=copy.deepcopy(base['input']);b[cid]['expected']=copy.deepcopy(base['expected']);x[b[cid]['fixture_id']]['positive']={'input':copy.deepcopy(base['input']),'expected':copy.deepcopy(base['expected'])}
reject('negative.scenario.rename.does.not.add.packet',duplicate)
# Requirement/scenario fingerprints must follow actual current prose.
D=parse_delta_specs(C);req={x['id']:x for x in g['requirements']}
for p in g['properties']:
 d=D[req[p['requirement_id']]['capability'],req[p['requirement_id']]['title']];ck(p['id']+'.requirement.fingerprint',d['fingerprint']==req[p['requirement_id']]['fingerprint'])
 for c in [x for x in g['cases'] if x['property_id']==p['id']]:ck(c['id']+'.scenario.fingerprint',c['scenario_fingerprint']==d['scenario_fingerprints'][c['scenario']])
# Keep original scope bytes and historical executable owners stable against the starting revision.
for rel in ['domain/error-taxonomy.v1.yaml','domain/mutation-recipes.v1.json','domain/metrics.v1.yaml','domain/providers.v1.yaml','domain/corpus-sources.v1.yaml']:
 ck('preserved.'+rel,(V/rel).read_bytes()==subprocess.check_output(['git','show','b0cbe97:specification/v2/'+rel],cwd=R))
old=json.loads(subprocess.check_output(['git','show','b0cbe97:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));new={x['id']:x for x in g['cases']}
for c in old['cases']:
 if c['state']=='implemented':
  invalidations={x['case_id']:x for x in load(R/'audit/iteration-1-local-foundation-20261010/INVALIDATED.json')}
  ck('retained.or.explicitly.invalidated.historical.scope.'+c['id'],new[c['id']]==c or (c['id'] in invalidations and invalidations[c['id']]['previous']==c and new[c['id']]['state']=='blocked'))
# Every leaf's textual recipe still replays the exact independently saved surface string.
recipes=load(V/'domain/mutation-recipes.v1.json')['recipes']
for r in recipes:
 edit=r['codepoint_edit']
 if edit:
  text=r['canonical_example'];start=edit['start_cp'];end=edit['end_cp'];ck(r['taxonomy_id']+'.exact.slice',text[start:end]==edit['exact_text']);ck(r['taxonomy_id']+'.exact.replay',text[:start]+edit['replacement']+text[end:]==r['surface_example'])
ck('all122.recipe.identities',len(recipes)==122);ck('all448.original.and22.iteration3.and32.iteration4.property.sets',len(s['properties'])==502 and sum(x['property_id'].startswith('I3-') for x in s['properties'])==22 and sum(x['property_id'].startswith('I4-') for x in s['properties'])==32)
for pol in ['POSITIVE','NEGATIVE']:
 b=next(x for x in f['case_bindings'] if x['case_id']=='V6-SES-01.P1.S2.'+pol);ck('named.empty.answer.'+pol,b['input']['answer']=='' and b['expected']['TP']==0 and b['expected']['primary']=='0/1')
ck('no.unregistered.old.secondary.leaf','grammar.verbs.verb_form' not in json.dumps(f))

out={'status':'passed','assertions':len(checks),'requirements':len(g['requirements']),'properties':len(g['properties']),'case_edges':len(g['cases']),'new_case_edges':sum('.SET2.' in x['id'] for x in g['cases']),'minimum_distinct_packets_per_polarity':min(min(x['positive_distinct_packets'],x['negative_distinct_packets']) for x in s['properties']),'fixtures':len(f['fixtures']),'case_states':dict(collections.Counter(x['state'] for x in g['cases'])),'behavior_runs':0,'proof_boundary':'Finite specification DAG/fixture/set identity, literal recipe replay, oracle-sensitivity perturbations and original/historical preservation. No application, inference, speech, corpus or independent linguistic validity observation.','checks':checks}
(Path(sys.argv[1]) if sys.argv[1:] else A/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
