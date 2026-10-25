"""Register current I19 repair without relabelling old native/UI observations."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'openspec/changes/implement-teacher-error-trainer';A=ROOT/'audit/iteration-19-verification-20261026'
p=B/'verification.json';v=json.loads(p.read_text());v['cases']=[c for c in v['cases'] if '.verify19_' not in c['id']];props=['FIN-UI-02.P1','FIN-UI-03.P1','FIN-VERIFY.I19']
new=['services/web/app/savedList.js','services/web/app/useSavedList.js'];ui=new+['services/web/app/prepare/usePreparation.js','services/web/app/prepare/page.js','services/web/app/attempts/page.js','services/web/app/audio/page.js','services/web/app/reviews/ChooseCase.js']
evidence=['audit/iteration-19-verification-20261026/review.py','audit/iteration-19-verification-20261026/REVIEW.json','data/iteration-19-verification-20261026/observations.json','data/iteration-19-verification-20261026/requests.jsonl','data/iteration-19-verification-20261026/baseline.json']
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
for prop in v['properties']:
 if prop['id'] in props:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+ui+evidence+['tests/test_saved_list.py','tests/test_iteration19_verify.py']))
for c in v['cases']:
 if c['property_id'] in props:
  c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+new))
  if c['substitution']['classification']=='EXTERNAL_BOUNDARY' and 'Historical native/helper/settled-view' not in c['substitution']['allowed_proof']:c['substitution']['allowed_proof']+=' Historical native/helper/settled-view observations retain only unchanged behavior; changed read ordering/loading/recovery and current review are observed by the iteration19 verification cases. Receipt parsing is not a new UI/provider execution.'
commands=[('i19-list-owner','tests.test_saved_list'),('i19-current-verification','tests.test_iteration19_verify')]
for name,module in commands:
 if not any(c['id']==name for c in v['commands']):v['commands'].append(dict(id=name,runner='python-unittest',argv=['python3','-B','-m','unittest','-v',module],cwd='.',env={},timeout_seconds=30,authority='local'))
sub=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Test-owned list HTTP bodies/holds/failures and explicit action outcomes. The source-built Next.js views, clientFetch and shared savedList/useSavedList owners are actual implementation.',allowed_proof='Actual CUA read ordering, loading/error/empty, retention/recovery, pagination, action requests, identity links, loaded fonts and keyboard/layout facts. Original native storage/audio receipts remain separately retained.',forbidden_claims=['Fresh native write, LLM or speech execution from controlled HTTP outcomes','Acoustic/linguistic/provider quality','Independent human review','Deployment or all-product acceptance'])
owner_oracles={
 'test_unread_positive':'A pending first read has no accepted empty state, retains loading and no error.',
 'test_empty_positive':'A successful empty page is loaded, idle and free of errors.',
 'test_initial_failure_negative':'An initial failure remains unconfirmed-empty and uses authored guidance without backend text.',
 'test_retention_positive':'Failed populated reads retain accepted items/cursor; success clears guidance.',
 'test_old_success_negative':'An old success delivered after a newer success cannot replace its records.',
 'test_old_error_negative':'An obsolete failure cannot replace a newer success with error guidance.',
 'test_current_error_negative':'An old success cannot erase a newer failure or replace the last accepted records.',
 'test_pending_positive':'An obsolete completion cannot end the current pending read indicator.',
 'test_pagination_positive':'Append consumes the saved cursor once; a page failure retains accepted items/cursor.',
 'test_old_append_negative':'An old pending page cannot append into a newer refreshed list.',
 'test_unmounted_negative':'Cancelling read ownership prevents later UI state updates.',
 'test_logging_positive':'Unexpected parse/transport failures log redacted error kinds, never backend text.'}
ui_oracles={
 'test_initial_loading_positive':('FIN-UI-02.P1','Hold first reads in all four actual views: show loading with no false empty claim.'),
 'test_initial_failure_negative':('FIN-UI-02.P1','Initial failed reads retain unknown rather than empty; explicit retry restores records. Transient audio read makes three GET attempts.'),
 'test_empty_positive':('FIN-UI-03.P1','Only a successful empty read displays the appropriate empty state in each view.'),
 'test_latest_read_positive':('FIN-UI-03.P1','Actual requests finish3before2 in all four views; the newer snapshot remains visible and Refresh is reachable.'),
 'test_obsolete_failure_negative':('FIN-UI-02.P1','An older held403 delivered after newer success cannot add stale unavailable guidance.'),
 'test_latest_failure_negative':('FIN-UI-02.P1','A newer failed Audio read retains accepted native records and its guidance after an obsolete success.'),
 'test_retention_recovery_positive':('FIN-UI-02.P1','Populated failure retains identical full-ID links and titles; explicit Refresh recovers in all four views.'),
 'test_pagination_positive':('FIN-UI-03.P1','Three list adapters send page-two cursor, append the second record and remove exhausted Load more.'),
 'test_action_independent_positive':('FIN-UI-02.P1','Saved-history failure does not disable Generate or erase Topic; exactly one synthetic blueprint request is captured.'),
 'test_unreadable_negative':('FIN-UI-02.P1','An unreadable response reaches redacted diagnostics and authored recovery; explicit Refresh restores records without raw text.'),
 'test_layout_positive':('FIN-UI-03.P1','Actual12route/width views preserve17px body,14px wrapped identities, loaded Source Sans3 and no overflow.'),
 'test_keyboard_positive':('FIN-UI-03.P1','Four actual keyboard transitions retain visible3px focus, full matching ID details and operable mobile navigation.'),
 'test_resume_readback_positive':('FIN-UI-02.P1','One explicit controlled resume uses the existing URL, refreshes into complete state and survives reload. Native persistence proof is retained separately.'),
 'test_zero_dispatch_negative':('FIN-UI-02.P1','Only the explicit intercepted blueprint/resume POSTs occur; all inspection/error/retry/selection traffic is read-only.'),
 'test_review_positive':('FIN-VERIFY.I19','The current review matches actual UI interactions/fonts/layout and source-native identity; no unsupported provider or performance claim.'),
 'test_ux_omission_negative':('FIN-VERIFY.I19','Omitted interaction review or a build/screenshot-only claim fails current review.'),
 'test_typography_omission_negative':('FIN-VERIFY.I19','Omitted typography, a constructed10px identity or clipping facts fail review.'),
 'test_evidence_mismatch_negative':('FIN-VERIFY.I19','Wrong native/UI identities, planned-as-passed, candidate gold or bulk-model demands fail review.')}
def add(method,prop,source,klass,command,oracle,boundary):
 template=next(c for c in v['cases'] if c['property_id']==prop);identity=prop+'.verify19_'+klass+'_'+method
 if any(c['id']==identity for c in v['cases']):return
 v['cases'].append(dict(id=identity,property_id=prop,polarity='negative' if method.endswith('negative') else 'positive',scenario=template['scenario'],scenario_fingerprint=template['scenario_fingerprint'],setup='Use the literal controlled sequence/record inputs and actual production owner named in the observable.',observable=oracle,red_expectation='The actual observation contradicts: '+oracle,green_expectation=oracle,test_id='unittest::tests.'+Path(source).stem+'.'+klass+'.'+method,command_id=command,state='implemented',source_path=source,source_sha256=sha(source),invalidation_dependencies=list(dict.fromkeys(ui+evidence+[source])),substitution=boundary))
for method,oracle in owner_oracles.items():add(method,'FIN-UI-02.P1','tests/test_saved_list.py','SavedList','i19-list-owner',oracle,dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Controlled promise resolution/rejection supplies ordered read outcomes to the actual savedList state owner.',allowed_proof='Exact independent accepted items, cursor, loading/error, cancellation and redacted-log state only.',forbidden_claims=['HTTP/browser/native storage or provider execution from pure state inputs']))
for method,(prop,oracle) in ui_oracles.items():add(method,prop,'tests/test_iteration19_verify.py','Iteration19Verify','i19-current-verification',oracle,sub)
p.write_text(json.dumps(v,indent=2)+'\n');selected=[c for c in v['cases'] if c['property_id'] in props];assert len(selected)==55,len(selected)
(A/'SELECTION.json').write_text(json.dumps({'iteration':19,'properties':props,'expected_case_count':len(selected),'case_ids':[c['id'] for c in selected],'boundary':'25 prior exact regressions plus12 shared-owner and18 current browser/review cases. Unchanged native proof is retained; captured facts are not fresh provider/native execution.'},indent=2)+'\n')
p=B/'discovery.json';d=json.loads(p.read_text());ids=[c['test_id'] for c in selected];d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+ids));d['reviews'].append(dict(id='iteration19-verify-repair-20261026',question='Verify whole I19 and inspect nonblocking recovery and related list-owner siblings.',property_ids=props,test_ids=ids,disposition='current_change',rationale='Current user authorizes full repair, UX/typography inspection and clean scoped acceptance. Preserve native/source/AI semantics and prior valid proof.',searches=[dict(kind='exact',status='completed',query='Trace savedRecord/failureMessage, native metadata projections, all four list requests, RefreshButton and retained/error transitions. Inspect original25 receipts and exact contracts before repair.',outcome='Native metadata remains correct. Actual source-built counterexamples prove stale response overwrite and false unread/failed empty state. Shared savedList/useSavedList removes four independent lifecycle owners; current browser and pure owner regressions cover sibling ordering, retention, pagination and actions.',results=[dict(path=x,classification='interface_dependency',reason='Actual affected view/caller or shared read owner inspected and exercised.') for x in ui]),dict(kind='semantic',status='not_applicable',query='Known I19 owners and exact field/caller paths from the previous accepted increment.',reason='Ownership is known; direct inspection is appropriate. Current jbcontext status is retained separately; no semantic result/index creation is claimed.',outcome='Exact source, native contract and runtime tracing only.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known JavaScript state/presentation modules, no symbol refactor.',reason='No PSI-dependent investigation or index operation was needed.',outcome='No IDE semantic evidence claimed.',results=[])]));p.write_text(json.dumps(d,indent=2)+'\n');print('Registered',len(selected),'current I19 cases')
