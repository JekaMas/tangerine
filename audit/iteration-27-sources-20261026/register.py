"""Materialize I27 literals through the existing native import/status owners."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
PROPS=['FIN-SOURCES.P1','FIN-VERIFY.I27'];SOURCE='tests/test_completion_i27.py'
DEPS=['services/api/internal/app/'+name for name in ['source_types.go','source_import.go','source_summary.go','source_full_scope.go','source_counts.go','source_status.go','source_storage.go','source_registry.go']]
DEPS+=['services/web/app/sources/page.js','services/web/app/clientRequest.js','services/web/app/styles/base.css',SOURCE,'tests/native_source_test.go','tests/native_source_repair_test.go','tests/native_source_completion_test.go','tests/native_source_full_test.go','tests/source_completion_browser_fixture_test.go','tests/source-native','tests/source-full-native','services/api/internal/source/archive.go','services/api/internal/source/archive_pax_test.go','services/api/internal/source/kaldi.go','services/api/internal/source/kaldi_delimiter_test.go','specification/v2/contracts/import-report.schema.json','specification/v2/contracts/source-status.schema.json','specification/v2/docs/sources/acquisition-and-rights.md']
DEPS+=['services/api/internal/app/source_http.go','services/api/internal/app/source_presentation_test.go','services/web/app/sources/sourceSession.js','services/web/app/sources/sourceRequest.js','services/web/app/sources/sourceCache.js','services/web/app/sources/remote.js','tests/test_source_session.py','tests/source_session.test.mjs']
DEPS+=['data/iteration-27-verify-20261026/'+name for name in ['status-native.jsonl','status-red.jsonl','http-native.jsonl','browser/fixture.json','browser/observations.json','browser/requests.jsonl','browser/native-final.json']]
DEPS+=['audit/iteration-27-sources-20261026/'+name for name in ['ACQUISITIONS.json','NATIVE-SELECTION.json']]
DEPS+=['data/iteration-27-sources-20261026/'+name for name in ['native-regressions.jsonl','selection-repair.jsonl','component-positive.jsonl','pax-native.jsonl','kaldi-native.jsonl','speech-join-repair.jsonl','recovery-final.jsonl','media-scope.jsonl','speechocean-native-counts.json','speechocean-report.json','full-native.jsonl','speechocean-final.jsonl','browser/fixture.json','browser/observations.json','browser/requests.jsonl','browser/native-final.json','research/l2-official-confirmed.json','research/l2-official-inventory.json']]

def main():
 path=CHANGE/'verification.json';graph=json.loads(path.read_text())
 original=[c for c in graph['cases'] if c['property_id'] in PROPS];templates={p:copy.deepcopy(next(c for c in original if c['property_id']==p)) for p in PROPS}
 bymethod={c['test_id'].split('.')[-1]:c for c in original};graph['cases']=[c for c in graph['cases'] if c['property_id'] not in PROPS]
 text=(ROOT/SOURCE).read_text();sha=hashlib.sha256(text.encode()).hexdigest()
 for node in ast.walk(ast.parse(text)):
  if not isinstance(node,ast.FunctionDef) or not node.name.startswith('test_'):continue
  method=node.name;prop='FIN-VERIFY.I27' if method in ['test_review_positive','test_layout_positive','test_unavailable_recovery_negative','test_zero_inference_negative','test_ux_omission_negative','test_typography_omission_negative','test_evidence_mismatch_negative'] else 'FIN-SOURCES.P1'
  case=copy.deepcopy(bymethod.get(method,templates[prop]));literal=ast.get_source_segment(text,node)
  case.update(id=bymethod[method]['id'] if method in bymethod else prop+'.'+method.removeprefix('test_'),property_id=prop,
   source_path=SOURCE,source_sha256=sha,state='implemented',command_id='completion-i27',
   test_id='unittest::tests.test_completion_i27.CompletionI27.'+method,polarity='negative' if method.endswith('negative') else 'positive',
   setup='Use actual native/acquisition/browser observations and the independently authored exact inputs/assertions in '+SOURCE+':'+method+'. Native source records and private dictionaries used for counterexamples are explicitly constructed.',
   observable=literal,green_expectation='The exact literal assertions hold through the stated current or retained native observation. Missing owner releases and actual browser activation skip and do not establish acceptance.',
   red_expectation='An exact expected state, release association, retained count/byte provenance or honest evidence boundary is contradicted.',invalidation_dependencies=DEPS)
  case['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Constructed private/raw/mirror counterexample inputs and test-owned HTTP503 responses only. Production importer, PostgreSQL/MinIO, native status and source-built UI are real. Completion reads retained actual observations without redispatch.',allowed_proof='Exact native completeness/lineage/persistence, actual downloaded source provenance, responsive rendering and page reload; actual input activation is separately incomplete.',forbidden_claims=['Constructed private fixtures are acquired owner releases','A public analysis companion is its full derivative','Mirrors imply official byte equivalence','Rendered UI or HTTP tests prove pointer/keyboard activation','New inference or independent linguistic/human evaluation'])
  case.pop('blocker',None)
  if method=='test_selected_owner_releases_positive':case['blocker']='Six complete Cambridge/study/vendor owner releases/dictionaries/terms remain unavailable; concrete acquisition test skips, never passes.'
  if method=='test_review_positive':case['blocker']='IAB inputs did not activate selected reads. Existing installed-Chrome selection is unanswered. Actual rendering/focus/reload are retained separately.'
  graph['cases'].append(case)
 # Native JavaScript assertions exercise the actual Sources owners. Their
 # controlled HTTP inputs do not replace the separately required real browser.
 session_source='tests/test_source_session.py'
 session_text=(ROOT/session_source).read_text()
 js=(ROOT/'tests/source_session.test.mjs').read_text()
 session_deps=['services/web/app/sources/sourceSession.js','services/web/app/sources/sourceRequest.js','services/web/app/sources/sourceCache.js','services/web/app/sources/page.js','services/web/app/sources/remote.js','services/web/app/clientRequest.js','services/web/app/requestError.js',session_source,'tests/source_session.test.mjs']
 for node in ast.walk(ast.parse(session_text)):
  if not isinstance(node,ast.FunctionDef) or not node.name.startswith('test_'):continue
  name=node.name.removeprefix('test_');start=js.index("test('"+name+"',");end=js.find('\ntest(',start+1)
  literal=js[start:end if end>=0 else len(js)].strip()
  prop='FIN-SOURCES.P1';case=copy.deepcopy(templates[prop])
  case.update(id=prop+'.source_session_'+name,property_id=prop,source_path=session_source,source_sha256=hashlib.sha256(session_text.encode()).hexdigest(),state='implemented',command_id='source-session-i27',test_id='unittest::tests.test_source_session.SourceSession.'+node.name,polarity='negative' if name.endswith('negative') else 'positive',setup='Execute the real sourceSession/sourceRequest/clientFetch production owners with the independently authored controlled records and transport responses in tests/source_session.test.mjs::'+name,observable=literal,green_expectation='Every exact literal assertion for selected state, human guidance, safe retry or preserved association holds.',red_expectation='Wrong source/report/rows/files, stale resolved error, missing resume association, leaked diagnostics or unsafe repeated write is observed.',invalidation_dependencies=session_deps)
  case['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='HTTP transport responses and state publication callback only; actual source session/request/retry owners execute.',allowed_proof='Selected state, authored guidance and retry/association ownership with exact controlled expectations.',forbidden_claims=['Real browser pointer/keyboard activation','Acquired missing owner corpus or permission','Live provider, acoustic or linguistic qualification'])
  case.pop('blocker',None);graph['cases'].append(case)
 if not any(c['id']=='source-session-i27' for c in graph['commands']):
  graph['commands'].append(dict(id='source-session-i27',argv=['python3','-B','-m','unittest','-v','tests.test_source_session'],cwd='.',env={},timeout_seconds=120,runner='python-unittest'))
 for p in graph['properties']:
  if p['id'] in PROPS:p['source_globs']=list(dict.fromkeys(p.get('source_globs',[])+DEPS))
 for command in graph['commands']:
  if command['id']=='completion-i27':command.update(argv=['python3','-B','-m','unittest','-v','tests.test_completion_i27'],cwd='.',env={},timeout_seconds=120,runner='python-unittest')
 # Current source facts changed after actual acquisition/import, while every
 # retained DATAFULL scenario/expectation remains unchanged. Record this scope
 # explicitly instead of refreshing historical case/receipt fingerprints.
 import sys
 sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
 from requirement_tests import parse_delta_specs
 specs=parse_delta_specs(CHANGE);updates=[]
 changed={'DATAFULL-02','DATAFULL-03','DATAFULL-04','DATAFULL-05','FIN-SOURCES'}
 prop_requirements={p['id']:p['requirement_id'] for p in graph['properties']}
 for requirement in graph['requirements']:
  if requirement['id'] not in changed:continue
  spec=specs[(requirement['capability'],requirement['title'])]
  for case in graph['cases']:
   if prop_requirements[case['property_id']]==requirement['id']:
    assert case['scenario_fingerprint']==spec['scenario_fingerprints'][case['scenario']],case['id']
  if requirement['fingerprint']!=spec['fingerprint']:
   updates.append(dict(requirement_id=requirement['id'],previous_fingerprint=requirement['fingerprint'],current_fingerprint=spec['fingerprint'],reason='Actual current source delivery/import facts and selected saved-assessment/lineage contracts; no retained scenario/assertion or original receipt is relabelled.',evidence=['data/iteration-27-sources-20261026/full-native.jsonl','data/iteration-27-sources-20261026/speechocean-final.jsonl','audit/iteration-27-sources-20261026/L2-OFFICIAL.json','tests/test_completion_i27.py']))
  requirement['fingerprint']=spec['fingerprint']
  raw=(ROOT/spec['path']).read_text().split('### Requirement: '+requirement['title'],1)[1].split('#### Scenario:',1)[0].strip()
  for prop in graph['properties']:
   if prop['requirement_id']==requirement['id']:
    prop['statement']=raw;prop['owner']='services/api/internal/app'
    prop['source_globs']=list(dict.fromkeys(prop.get('source_globs',[])+['services/api/internal/app/source*.go','services/api/internal/source/**','specification/v2/docs/sources/**','specification/v2/domain/corpus-sources.v1.yaml']))
 if updates:
  (ROOT/'audit/iteration-27-sources-20261026/SPEC-RECONCILIATION.json').write_text(json.dumps(dict(updates=updates,retained_scenarios_unchanged=True,original_case_and_receipt_fingerprints_refreshed=False,proof_boundary='Requirements metadata synchronized only after actual newly observed delivery/import evidence. Existing source cases keep their original scopes/receipts;I27 receipt observers and direct source-session cases cover the selected current outcomes.'),indent=2)+'\n')
 # Whole-file test identities changed in three shared native fixture files.
 # Keep original receipts and scenarios. Only the two tab fixtures and recovery
 # assertion changed behavior; their fresh exact native observations are retained.
 source_updates=[]
 changed_sources={'tests/native_source_test.go','tests/native_source_repair_test.go','tests/native_source_full_test.go'}
 digests={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in changed_sources}
 fresh={'TestNativeSourceSpeechPositive':'data/iteration-27-sources-20261026/speech-join-repair.jsonl',
        'TestNativeSourceSpeechNegative':'data/iteration-27-sources-20261026/speech-join-repair.jsonl',
        'TestNativeSourceReadFailurePositive':'data/iteration-27-sources-20261026/recovery-final.jsonl',
        'TestNativeSourceReadFailureNegative':'data/iteration-27-sources-20261026/recovery-final.jsonl',
        'TestNativeSourceFullFCEPositive':'data/iteration-27-sources-20261026/full-native.jsonl',
        'TestNativeSourceFullWIPositive':'data/iteration-27-sources-20261026/full-native.jsonl'}
 for case in graph['cases']:
  name=case.get('source_path')
  if name not in changed_sources or case.get('source_sha256')==digests[name]:continue
  method=case['test_id'].split('::')[-1].split('/')[0]
  source_updates.append(dict(case_id=case['id'],test_id=case['test_id'],source_path=name,previous_source_sha256=case.get('source_sha256'),current_source_sha256=digests[name],disposition='fresh exact observation' if method in fresh else 'unchanged literal assertion/helper scope retained; only shared-file identity changes',receipt=fresh.get(method),scope='Tab-delimited Speech fixture and recovered-issue assertions are freshly observed. Existing BEA helper arguments stay bea/BEA-v2.1 and their whole native imports passed. Other native method bodies/helpers are unchanged; original receipts and their historical fingerprints are not rewritten.'))
  case['source_sha256']=digests[name]
 if source_updates:
  (ROOT/'audit/iteration-27-sources-20261026/TEST-RECONCILIATION.json').write_text(json.dumps(dict(source_updates=source_updates,original_receipts_rewritten=False,claim='Current source bindings only; this is not blanket current-head acceptance of the older iteration13 cases.'),indent=2)+'\n')
 path.write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
 selected=[c for c in graph['cases'] if c['property_id'] in PROPS]
 (ROOT/'audit/iteration-27-sources-20261026/SELECTION.json').write_text(json.dumps(dict(iteration=27,properties=PROPS,case_ids=[c['id'] for c in selected],case_count=len(selected),proof_boundary='Retained actual native/API/browser/acquisition readers; zero inference. Restricted source and actual activation cases remain skips; direct source-session assertions exercise controlled transport/state publication.'),indent=2)+'\n')
 path=CHANGE/'discovery.json';d=json.loads(path.read_text());ids=[c['test_id'] for c in selected]
 d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+ids));d['reviews']=[r for r in d['reviews'] if r['id']!='iteration27-sources-20261026']
 d['reviews'].append(dict(id='iteration27-sources-20261026',question='Complete authorized selected full-source intake/provenance without companion/mirror/vendor substitution or repeated stored-row validation.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Reuse existing source import/mapping/summary/native fixture owners. Persist one completion assessment, project report IDs per actual release, preserve all raw data and eleven identities; actual owner access and IAB activation remain concrete external inputs. Verification repairs source selection/read recovery, late-response ownership, human issue history and truthful status classification; controlled JS transport cases and fresh native HTTP/status tests are separately scoped.',searches=[dict(kind='exact',status='completed',query='Read selected I27 DAG literal cases and trace source_registry/import/summary/counts/full_scope/status, source page, native I13 fixtures and retained full corpus/acquisition receipts.',outcome='Four native failing assessment/lineage/legacy counterexamples observed; missing-component fixture first hit immutable-record setup, then correct new-version registration verifies the repair. Full native sources and current owner access are separately observed.',results=[dict(path=p,classification='change_candidate' if p in ['services/api/internal/app/source_types.go','services/api/internal/app/source_summary.go','services/api/internal/app/source_status.go','services/web/app/sources/page.js'] else 'interface_dependency',reason='Known affected owner, exact native fixture or source contract inspected.') for p in DEPS if p.startswith(('services/','specification/','tests/'))]),dict(kind='semantic',status='not_applicable',query='Existing I27 DAG and I13 acceptance identify the exact source/import/projection owners.',reason='No unfamiliar ownership search or semantic index creation is needed.',outcome='Exact source/receipt tracing; no semantic proof claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Go/JavaScript source and native tests; no PSI refactor.',reason='No IDE symbol operation is required for this scoped implementation.',outcome='No index-dependent evidence claimed.',results=[])]))
 path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print('Registered',len(selected),'I27 executable cases')
if __name__=='__main__':main()
