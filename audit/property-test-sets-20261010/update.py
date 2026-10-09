"""Finite coverage reconciliation. Run once against b0cbe97; authored plans, never observations."""
import json,copy,collections,hashlib,sys
from pathlib import Path
from fractions import Fraction
from variants import P,N
R=Path(__file__).resolve().parents[2]; V=R/'specification/v2'; C=R/'openspec/changes/implement-teacher-error-trainer'; A=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
g=load(C/'verification.json');f=load(V/'domain/verification-fixtures.v1.json');pb={x['property_id']:x for x in f['property_bindings']};fx={x['id']:x for x in f['fixtures']};cb={x['case_id']:x for x in f['case_bindings']}
assert not any('.SET2.' in c['id'] for c in g['cases'])
changed=[]
# Correct an actual fixture contradiction: eight permitted variants are controls, never true errors.
for fid,x in fx.items():
 if not fid.startswith('leaf-acceptable_variant.'):continue
 x['positive']['input']['answer']={'stance':'assert_acceptable','localized_target':x['positive']['input']['surface'],'repair':None}
 x['positive']['expected'].update(design_event_count=0,design_TP=0,design_CQ='0/1',design_DF=1,design_DA=1,design_FC=0)
 x['negative']['input']['private_decisive_context_only']=False
 x['negative']['expected']['hidden_context_instance_generated']=False
 changed.append(fid)
for b in f['case_bindings']:
 if b['fixture_id'] in changed:
  x=fx[b['fixture_id']][b['polarity']]; b['input']=copy.deepcopy(x['input']);b['expected']=copy.deepcopy(x['expected'])
# Isolate clean-control false positives from hidden-context generation rejection for all122categories.
for fid,x in fx.items():
 if fid.startswith('leaf-'):
  x['negative']['input']['private_decisive_context_only']=False
  for b in f['case_bindings']:
   if b['fixture_id']==fid and b['polarity']=='negative':b['input']=copy.deepcopy(x['negative']['input'])
# Positive patch helper: None means delete a stale assertion, not assert null.
def patch(base,updates):
 x=copy.deepcopy(base)
 for k,v in updates.items():
  if v is None:x.pop(k,None)
  else:x[k]=copy.deepcopy(v)
 return x
new=[];missing=[]
for p in g['properties']:
 pid=p['id'];fid=pb[pid]['fixture_id']; x=fx[fid]
 for pol in ['positive','negative']:
  prior=[c for c in g['cases'] if c['property_id']==pid and c['polarity']==pol]
  distinct={json.dumps([cb[c['id']]['input'],cb[c['id']]['expected']],sort_keys=True) for c in prior}
  if len(distinct)>=2:continue
  base=x[pol];inp=None;expected=None;kind='authored_functional_variant';oracle=x['independent_oracle']
  if fid.startswith('leaf-'):
   source=x['positive'];inp=copy.deepcopy(source['input']);expected=copy.deepcopy(source['expected'])
   if pol=='positive':
    if inp['domain']=='acceptable_variant':
     inp['answer']={'stance':'assert_acceptable','localized_target':inp['surface'],'description':'This is a permitted alternative in the stated context.','repair':None}
    else:inp['answer']={'localized_target':inp['surface'],'description':'The intended wording is '+inp['canonical'],'repair':inp['canonical'],'explanation':None}
    expected['explanation_penalty']=0
   else:
    if inp['domain']=='acceptable_variant':
     inp['answer']={'stance':'assert_error','localized_target':inp['surface'],'repair':inp['canonical']};expected.update(design_TP=0,design_FP=1,design_DF=0,design_DA=0,design_FC=1)
    else:
     inp['answer']={'stance':'assert_acceptable','localized_target':inp['surface'],'repair':None};expected.update(design_TP=0,design_FN=1,design_CQ='0/1')
   oracle+=' Independently stipulated acceptable/error stance; an unchanged contextual error must be missed when accepted, while a permitted variant has zero true-error denominator.'
  elif fid.startswith('equation-'):
   inp=copy.deepcopy(x['positive']['input']);expected=copy.deepcopy(x['positive']['expected']);kind='independent_arithmetic_variant'
   if pol=='positive':
    if 'stats' in inp:
     inp['stats']={k:str(Fraction(v)*2) if isinstance(v,str) else v*2 for k,v in inp['stats'].items()}
    elif inp['metric']=='telemetry.elapsed_seconds':
     inp['inputs']={'started_at':'2026-10-10T12:00:00Z','submitted_at':'2026-10-10T12:00:25Z'};expected['exact']='25/1'
    elif inp['metric']=='telemetry.replay_count':
     inp['inputs']={'validated_distinct_event_ids':['e1','e2'],'duplicate':'e2','rejected':'e3'};expected['exact']='2/1'
    elif inp['metric'].startswith('teacher.'):
     inp['inputs'].update(listener_answer='The agreement needs correction.',generated_exercise_audio=True)
    elif inp['metric']=='annotation.cohen_kappa':
     for k in ['rater1_counts','rater2_counts','confusion']:inp['inputs'][k]={n:v*2 for n,v in inp['inputs'][k].items()}
    else:inp['inputs']={k:v*2 if isinstance(v,(int,float)) else v for k,v in inp['inputs'].items()}
   else:
    # A wrong candidate result is a stipulated failure of the formula oracle, not a schema gate.
    inp['proposed_result']=str(Fraction(expected['exact'])+1) if expected['exact'] is not None else '99/1'
    expected['proposed_result_accepted']=False; expected['original_inputs_retained']=True
   oracle+=' Doubling numerator and exposure preserves a ratio; expected literals come from the original independent fraction, never candidate output. A deliberately different proposed result must be identified as a failure of this exact formula.'
  elif fid.startswith('full-source-'):
   assert pol=='negative'
   components=x['positive']['input']['components'];inp={'source':x['positive']['input']['source'],'components':components[1:],'dictionary_missing':False,'claim_full':True};expected={'missing_components':[components[0]],'full_claim':False,'raw_preserved':True,'independent_generation_available':True}
   oracle+=' Independently enumerate the first mandatory component absent from an otherwise complete component list; do not confound it with dictionary missingness.'
  elif pol=='positive' and fid in P:
   pi,pe=P[fid];inp=patch(x['positive']['input'],pi);expected=patch(x['positive']['expected'],pe)
   # Null CEFR is an actual value; it is not patch deletion.
   if fid=='authoring':inp['english_level']=None;expected['level']=None
   oracle+=' Compare these additional fixed input/output literals against the real owner, without copying candidate output into expectations.'
  elif pol=='negative' and fid in N:
   inp,expected=copy.deepcopy(N[fid]);oracle+=' Isolate the separately stated failure/change; only its stated expected fields are compared.'
  else:missing.append((pid,fid,pol));continue
  sig=json.dumps([inp,expected],sort_keys=True);assert sig not in distinct,(pid,pol,'duplicate')
  cid=pid+'.SET2.'+pol.upper();tid='planned::property-sets::'+cid;newfid='set2-'+pid+'-'+pol
  # Each single variant has an explicit packet; it does not duplicate the opposite polarity.
  packet={'id':newfid,'action':x['action'],'initial_state':copy.deepcopy(x['initial_state']),pol:{'input':inp,'expected':expected},'independent_oracle':oracle,'origin':'constructed_specification_fixture_not_empirical_or_provider_observation'}
  f['fixtures'].append(packet)
  c=copy.deepcopy(prior[0]);c.update(id=cid,test_id=tid,command_id='pending',state='blocked',source_path='tests/acceptance/test_property_sets.py',source_sha256=None,setup='Use literal '+newfid+' packet in verification-fixtures.v1.json; execute the real named owner.',observable='Compare all independently fixed expected fields plus real artifacts/receipts; '+kind,designed_fixture_id=newfid,fixture_observation_state='not_run',blocker='Constructed specification test plan; runtime/provider/audio/native Lab execution remains unperformed.')
  c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+['specification/v2/domain/verification-fixtures.v1.json','specification/v2/domain/property-test-sets.v1.json','specification/v2/docs/verification-fixtures.md']))
  g['cases'].append(c)
  b={'case_id':cid,'test_id':tid,'property_id':pid,'scenario':c['scenario'],'polarity':pol,'fixture_id':newfid,'mode':kind,'action':x['action'],'initial_state':copy.deepcopy(x['initial_state']),'input':inp,'expected':expected,'independent_oracle':oracle,'observation_state':'not_run','existing_case_state':'blocked','historical_receipt_not_reused_as_new_fixture_observation':True,'declared_scenario_contract':copy.deepcopy(cb[prior[0]['id']].get('declared_scenario_contract',[]))}
  f['case_bindings'].append(b);cb[cid]=b;new.append(tid)
if missing:raise AssertionError(missing)
# Exact complete coverage-collection inputs, not obsolete counts.
for packet in f['fixtures']:
 if packet['id'] in ['all-fixtures','scenario-CLOSE-04 No generic or fabricated passing plans']:
  for pol in ['positive','negative']:
   for k,vals in [('expected_properties',[x['id'] for x in g['properties']]),('expected_cases',[x['id'] for x in g['cases']])]:
    if k in packet[pol]['input']:packet[pol]['input'][k]=vals
for b in f['case_bindings']:
 if b['fixture_id'] in ['all-fixtures','scenario-CLOSE-04 No generic or fabricated passing plans']:b['input']=copy.deepcopy(fx[b['fixture_id']][b['polarity']]['input']);b['expected']=copy.deepcopy(fx[b['fixture_id']][b['polarity']]['expected'])
pending=next(x for x in g['commands'] if x['id']=='pending');pending['expected_markers']+=new
sets=[]
for p in g['properties']:
 row={'property_id':p['id'],'requirement_id':p['requirement_id'],'owner':p['owner'],'scenario_names':p['scenarios'],'positive_cases':[],'negative_cases':[],'proof_boundary':'Functional constructed plans; historical bounded receipts do not observe this set.','runtime_set_observation':'not_run'}
 for pol in ['positive','negative']:
  cases=[c for c in g['cases'] if c['property_id']==p['id'] and c['polarity']==pol];row[pol+'_cases']=[c['id'] for c in cases];row[pol+'_distinct_packets']=len({json.dumps([cb[c['id']]['input'],cb[c['id']]['expected']],sort_keys=True) for c in cases});assert row[pol+'_distinct_packets']>=2
 sets.append(row)
save(V/'domain/property-test-sets.v1.json',{'version':'1.0.0','authority':'docs/verification-fixtures.md','minimum_distinct_packets_per_polarity':2,'properties':sets})
save(C/'verification.json',g);save(V/'domain/verification-fixtures.v1.json',f)
d=load(C/'discovery.json');d['scope']['test_ids']+=new;d['reviews'].append({'id':'property-test-sets-20261010','question':'Every property has distinct positive and negative functional sets, independent expectations and DAG wiring.','property_ids':[p['id'] for p in g['properties']],'test_ids':new,'searches':[{'kind':'exact','status':'completed','query':'Compare every case packet by property/polarity, decoy semantics, independent arithmetic and DAG/command/discovery identities.','outcome':'Removed duplicated-packet coverage assumptions and false true-error credit for eight acceptable variants.','results':[{'path':'specification/v2/domain/verification-fixtures.v1.json','classification':'change_candidate','reason':'Exact functional packets and independent expectations.'}]},{'kind':'semantic','status':'not_applicable','query':'Unknown code owner discovery','reason':'Known specification/graph files; no implementation search.','outcome':'Requested exact-HEAD Context index is a separate handoff operation.','results':[]},{'kind':'jetbrains-index','status':'not_applicable','query':'Implementation symbol tracing','reason':'Specification-only work; user-requested project/index setup follows commit.','outcome':'IDE opening/indexing is recorded separately from behavior evidence.','results':[]}],'disposition':'current_change','rationale':'Preserve all product scope; constructed plans do not fabricate observed operation.'});save(C/'discovery.json',d)
save(A/'reconciliation.json',{'changed_semantic_inputs':['specification/v2/domain/verification-fixtures.v1.json','specification/v2/domain/property-test-sets.v1.json','specification/v2/docs/verification-fixtures.md','openspec/changes/implement-teacher-error-trainer/verification.json','openspec/changes/implement-teacher-error-trainer/discovery.json'],'corrected_decoy_packets':changed,'new_case_edges':len(new),'properties':len(sets),'runtime_behavior_runs':0,'invalidated_behavior_receipts':[],'retained_green_scope':'Original64bounded implemented case source/test/command dependencies unchanged; new and modified constructed packets not observed by old receipts.'})
print(json.dumps({'properties':len(sets),'new_cases':len(new),'case_edges':len(g['cases']),'fixtures':len(f['fixtures']),'decoy_repairs':len(changed)}))
