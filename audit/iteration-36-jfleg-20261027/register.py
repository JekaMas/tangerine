"""Own I36 spec/property/literal-case routing; other iteration bindings unchanged."""
import ast,hashlib,json,sys,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;BASE=ROOT/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=True)+'\n')
def reconcile_shared_source(graph):
 path='tests/native_source_test.go'
 old=subprocess.check_output(['git','show','b1eb6b5:'+path],cwd=ROOT).decode()
 current=(ROOT/path).read_text()
 pattern=r'(?ms)^func TestNativeSourceSourcesPositive\(.*?(?=^func |\Z)'
 before=re.search(pattern,old);after=re.search(pattern,current)
 assert before and after and old[:before.start()]+old[before.end():]==current[:after.start()]+current[after.end():], 'Unaccounted shared source assertion/helper change'
 oldsha=hashlib.sha256(old.encode()).hexdigest();newsha=hashlib.sha256(current.encode()).hexdigest();bindings=[]
 for case in graph['cases']:
  if case.get('source_path')!=path:continue
  assert case['source_sha256'] in [oldsha,newsha], 'Unrelated prior stale source pin'
  changed=case['test_id'].endswith('::TestNativeSourceSourcesPositive')
  case['source_sha256']=newsha
  if changed:
   case['setup']='Actual supplementary-source list through TestNativeSourceSourcesPositive; all eleven original identities remain, with JFLEG added. Current literal and original superseded exclusive count are retained in audit/iteration-36-jfleg-20261027/SOURCE-BINDINGS.json.'
   case['observable']=json.dumps(dict(independent_literal_assertions=after.group(),oracle='All original eleven IDs plus the supplemental JFLEG card, current source-status schemas and independent raw/normalized completeness; no original source is removed.'),sort_keys=True)
   case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+['audit/iteration-36-jfleg-20261027/SOURCE-BINDINGS.json','data/iteration-36-jfleg-20261027/status.jsonl']))
  bindings.append(dict(case_id=case['id'],test_id=case['test_id'],disposition='Changed assertion reobserved in status.jsonl; exact test is also required by I36.P1.' if changed else 'Shared file hash only; assertion and helper bytes are unchanged. Existing case receipts keep their original boundaries.'))
 save(HERE/'SOURCE-BINDINGS.json',dict(path=path,entry_sha256=oldsha,current_sha256=newsha,only_changed_function='TestNativeSourceSourcesPositive',unchanged_remainder_verified=True,old_literal=before.group(),current_literal=after.group(),bindings=bindings,scope='Registration repair, not a claim that every historical iteration was rerun. The actual changed native case passed; no stale pin is silently accepted.'))

def main():
 spec=parse_delta_specs(BASE)[('iteration-thirty-six-jfleg','I36 Complete native JFLEG supplement and consumers')];g=json.loads((BASE/'verification.json').read_text())
 reconcile_shared_source(g)
 for key in ['requirements','properties','cases','commands']:g[key]=[r for r in g[key] if not r.get('id','').startswith(('I36','iteration36-'))]
 g['requirements'].append(dict(id='I36',capability='iteration-thirty-six-jfleg',title='I36 Complete native JFLEG supplement and consumers',fingerprint=spec['fingerprint']))
 source='tests/test_jfleg_acceptance.py';methods={}
 if (ROOT/source).exists():
  text=(ROOT/source).read_text()
  for cls in ast.parse(text).body:
   if isinstance(cls,ast.ClassDef):
    for m in cls.body:
     if isinstance(m,ast.FunctionDef) and m.name.startswith('test_'):methods[m.name]=ast.get_source_segment(text,m)
 groups=['acquisition','pairing','mapping','resume','consumers','evaluation','ui'];owners=['services/api/internal/source/types.go','services/api/internal/app/source_jfleg.go','services/api/internal/source/jfleg.go','services/api/internal/app/source_import.go','services/api/internal/app/source_corrections.go','services/api/internal/app/source_correction_lab.go','services/web/app/sources/correctionSession.js']
 deps=['services/api/internal/source/*.go','services/api/internal/app/source*.go','services/api/internal/app/http.go','services/api/internal/app/lab.go','services/api/internal/lab/command.go','services/api/internal/contracts/schemas/*correction*.json','services/web/app/sources/*.js','services/web/app/api/**/route.js','specification/v2/contracts/source-correction*.schema.json','tests/jfleg_browser.cjs','tests/jfleg_visual.cjs','audit/iteration-36-jfleg-20261027/native.py','audit/iteration-36-jfleg-20261027/browser.py','audit/iteration-36-jfleg-20261027/inspect_media.py','tests/native_jfleg_test.go','tests/native_jfleg_consumers_test.go',source,'audit/iteration-36-jfleg-20261027/PLAN.json','audit/iteration-36-jfleg-20261027/NATIVE-EVIDENCE.json','audit/iteration-36-jfleg-20261027/SOURCE-BINDINGS.json','specification/v2/docs/sources/jfleg.md','audit/corpus-acquisition-20261009/jfleg-owner-snapshot-receipt.json','audit/corpus-acquisition-20261009/jfleg-m2-corrected-inventory.json']
 plan=json.loads((HERE/'PLAN.json').read_text())
 for i,scenario in enumerate(spec['scenario_fingerprints']):
  pid=f'I36.P{i+1}';g['properties'].append(dict(id=pid,requirement_id='I36',statement=scenario,scenarios=[scenario],owner=owners[i],oracle='Independent pre-implementation owner strings/counts and literal native Go/Chrome/Lab expectations, not candidate-generated linguistic gold.',source_globs=deps,iteration=36))
  for polarity in ['positive','negative']:
   name='test_'+groups[i]+'_'+polarity;implemented=name in methods
   literal=methods.get(name,json.dumps(dict(native_population=plan['expected'],property=scenario,positive='Actual exact native source/consumer data and state.',negative='Missing/duplicate/foreign/unknown values never invent data, semantic grades or effects.'),sort_keys=True))
   g['cases'].append(dict(id=pid+'.'+name,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup='Pinned complete acquired29-file JFLEG owner archive; independent754/747originals and four references; owned real PostgreSQL/MinIO and actual native source/UI/Lab owners. Controlled incomplete/unmatched cases retain explicit origin.',observable=literal,red_expectation='A native reference/identity/byte association is lost or invented, source/derived meaning is conflated, saved-state/consumer behavior differs, or an unobserved claim is presented as native gold.',green_expectation='All concrete literal native population, reference, transform, persistence, dataset, membership and UI assertions for the selected case hold.',test_id='unittest::tests.test_jfleg_acceptance.JFLEGAcceptance.'+name if implemented else 'planned::I36::'+name,command_id='iteration36-evidence' if implemented else 'pending',state='implemented' if implemented else 'planned',source_path=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest() if implemented else None,invalidation_dependencies=deps+['data/iteration-36-jfleg-20261027/full.jsonl','data/iteration-36-jfleg-20261027/consumers.jsonl','data/iteration-36-jfleg-20261027/evaluation.jsonl','data/iteration-36-jfleg-20261027/completeness.jsonl','data/iteration-36-jfleg-20261027/partial.jsonl','data/iteration-36-jfleg-20261027/observations.json','data/iteration-36-jfleg-20261027/browser/observations.json'],substitution=dict(classification='APPROVED_TEST_DOUBLE' if groups[i] in ['consumers','ui'] else 'NO_TEST_DOUBLE',owner_replaced='Only labelled transient/unavailable GET transport replies in browser recovery cases. Successful native parsing, projection, storage, source examples, datasets, local evaluation and DOM are real; constructed negative inputs are labelled.',allowed_proof='Selected full actual JFLEG structural/native import and source-derived example/evaluation use.',forbidden_claims=['All122leaf semantic gold','New model/provider quality or speech','Semantic failure for out-of-reference corrections','Completed other supplemental sources','Actual database outage from a controlled HTTP failure','All-functionality product qualification from this JFLEG increment']),distinct_reason=scenario+': '+name))
 # Verify adds literal counterexamples to the existing properties, not another
 # iteration or another task list. Native import receipts remain unchanged.
 import copy
 extra={5:['partial_ui_positive','empty_ui_negative','export_recovery_positive','export_recovery_negative'],7:['read_order_positive','read_order_negative','history_positive','history_negative']}
 verify_deps=['services/web/app/sources/correctionSession.js','tests/correction_session.test.mjs','tests/source_read_precedence.test.mjs','tests/source_session.test.mjs','tests/native_jfleg_verify_test.go','tests/jfleg_verify_browser.cjs','tests/jfleg_empty_visual.cjs','audit/iteration-36-verification-20261027/browser.py','audit/iteration-36-verification-20261027/native.py','audit/iteration-36-verification-20261027/inspect_media.py']
 for number,names in extra.items():
  for suffix in names:
   name='test_'+suffix;polarity=suffix.rsplit('_',1)[1]
   case=copy.deepcopy(next(c for c in g['cases'] if c['property_id']==f'I36.P{number}' and c['polarity']==polarity))
   case.update(id=f'I36.P{number}.'+name,observable=methods[name],test_id='unittest::tests.test_jfleg_acceptance.JFLEGAcceptance.'+name,distinct_reason=case['scenario']+': '+name,setup='Literal verify counterexample and actual repaired source/Chrome consumer. The full acquired import is reused. Small partial/empty native inputs and HTTP delays/failures are explicitly constructed; no successful source response or DOM is substituted.')
   g['cases'].append(case)
 for prop in g['properties']:
  if prop['id'].startswith('I36.'):prop['source_globs']=list(dict.fromkeys(prop['source_globs']+verify_deps))
 retained_inputs=['unit.jsonl','repair-unit.jsonl','stable-go.jsonl','status.jsonl','metadata.jsonl','consumer-observations.json','native-expected.json','dataset-dev.json','dataset-test.json','cursor-observations.json','consumer-negative.json','partial-observations.json','completeness-negative.json','evaluation-positive.json','evaluation-negative.json','regression.jsonl']
 verify_inputs=['sessions-green.tap','history-red.tap','native.jsonl','native-commit.jsonl','verify-ui-fixtures.json','verify-fixtures-commit.json','browser-red/observations.json','browser-green/observations.json','browser-green/requests.json','browser-regression-fixed/observations.json','browser-regression-fixed/requests.json','browser-visual/observations.json','browser-states/observations.json','media-observations.json']
 for case in g['cases']:
  if case['id'].startswith('I36.'):
   case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+verify_deps+['data/iteration-36-jfleg-20261027/'+p for p in retained_inputs]+['data/iteration-36-verification-20261027/'+p for p in verify_inputs]))
 if methods:g['commands'].append(dict(id='iteration36-evidence',runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_jfleg_acceptance'],cwd='.',env={},timeout_seconds=120,authority='local'))
 pending=next(c for c in g['commands'] if c['id']=='pending');pending['expected_markers']=[m for m in pending['expected_markers'] if not m.startswith('planned::I36::')]+[c['test_id'] for c in g['cases'] if c['id'].startswith('I36.') and c['state']=='planned'];save(BASE/'verification.json',g)
 props=[f'I36.P{i}' for i in range(1,8)];cases=[c for c in g['cases'] if c['property_id'] in props];save(HERE/'SELECTION.json',dict(iteration=36,property_ids=props,case_ids=[c['id'] for c in cases],expected_case_count=len(cases)))
 p=BASE/'completion-iterations.json';v=json.loads(p.read_text());v['iterations']=[r for r in v['iterations'] if r['iteration']!=36];v['iterations'].append(dict(iteration=36,title='Import available written-correction supplement',source_items=['SUP-04:JFLEG'],depends_on=[13,35],conditional_dependencies=[],requirement_ids=['I36'],verify_property_ids=props,track='implementation',visual_applicable=True,visual_scope='Supplemental Sources card, exact correction examples and dev/test dataset controls with safe recovery.',selection=str(HERE.relative_to(ROOT)/'SELECTION.json'),verify_command_ids=['iteration36-evidence'] if methods else ['pending']));save(p,v)
 p=BASE/'discovery.json';v=json.loads(p.read_text());ids=[c['test_id'] for c in cases];v['scope']['property_ids']=list(dict.fromkeys(v['scope']['property_ids']+props));v['scope']['test_ids']=[t for t in v['scope']['test_ids'] if 'I36::' not in t and 'test_jfleg_acceptance' not in t]+ids
 v['reviews']=[r for r in v['reviews'] if r['id']!='iteration36-jfleg'];v['reviews'].append(dict(id='iteration36-jfleg',question='Trace complete native JFLEG reference pairing, derived mappings and actual source/example/evaluation consumers.',disposition='current_change',rationale='The actual user selects the available JFLEG slice of SUP-04; acquired owner README dictates original/alternative/tool-native distinctions. Preserve all original11scopes and source terms without model calls.',property_ids=props,test_ids=ids,searches=[dict(kind='exact',status='completed',query='JFLEG primary archive/docs/count receipts; source registry/presets/staging/mapping/projection/commit/readback, Sources UI, portable datasets and deterministic Lab owners.',outcome='Complete acquired bytes identified, fixed independent baseline, exact hook/lineage/finalizers recorded before production edits.',results=[dict(path=o,classification='interface_dependency',reason='Actual owner and selected hook inspected.') for o in owners]),dict(kind='semantic',status='unavailable',query='Native JFLEG written correction import, multi-reference mappings and example/evaluation consumers.',reason='Actual jbcontext search/status: no index for github.com/jekamas/tangerine.',outcome='Direct exact-owner inspection used; no semantic evidence claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Native source/data conversion and local consumers; no PSI refactor.',reason='Known exact code/data and actual runtime tests answer this scope.',outcome='No IDE/index evidence claimed.',results=[])]));save(p,v);print(json.dumps(dict(cases=len(cases),implemented=len(methods))))
if __name__=='__main__':main()
