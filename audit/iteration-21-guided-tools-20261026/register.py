"""Bind I21 literal cases to actual UI/native observations and retained owners."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGE = ROOT / 'openspec/changes/implement-teacher-error-trainer'
AUDIT = ROOT / 'audit/iteration-21-guided-tools-20261026'
PREFIX = 'data/iteration-21-guided-tools-20261026/'
PROPS = ['FIN-UI-08.P1', 'FIN-VERIFY.I21']
SOURCE = 'tests/test_completion_i21.py'
UI = ['services/web/app/reports/' + x for x in ['page.js', 'StarterForms.js', 'starters.js', 'useReports.js', 'request.js']]
UI += ['services/web/app/cleanup/' + x for x in ['page.js', 'RecordPicker.js', 'session.js', 'useCleanup.js', 'labels.js']]
OWNERS = ['services/api/internal/app/' + x for x in ['empirical_reports.go', 'experiment_admit.go', 'deletion.go']]
OWNERS += ['services/web/app/useSavedList.js', 'services/web/app/clientRequest.js', 'services/web/app/requestError.js',
           'services/web/app/savedRecord.js', 'services/web/app/styles/base.css',
           'tests/test_guided_starters.py', 'tests/test_cleanup_session.py', 'tests/test_final_functional_helpers.py',
           'tests/guided_tools_fixture_test.go', 'data/final-functional-ux-20261025/lab-defaults.json']
PROOF = [PREFIX + x for x in ['observations.json', 'requests.jsonl', 'native-write-responses.jsonl', 'native-fixture.json',
         'native-final.json', 'native.jsonl', 'native-exit-code', 'constructed-report.json', 'report-input.json',
         'first-experiment.json', 'reused-experiment.json', 'first-dataset.json', 'reused-dataset.json',
         'frozen-config.json', 'file-report-definition.json', 'starters-green.log', 'cleanup-owner-final.log',
         'retained-starter-regression.log']]
PROOF += ['audit/iteration-21-guided-tools-20261026/' + x for x in ['REVIEW.json', 'review.py', 'SOURCE.json']]
BOUNDARY = dict(
    classification='EXTERNAL_BOUNDARY',
    owner_replaced='Controlled option/list503, empty/page and delayed-preview HTTP responses; independently authored constructed text/key/PCM and offline profile fixtures. Actual source-built UI, native API, PostgreSQL/MinIO save/reopen/explicit erasure and helper/session owners are observed.',
    allowed_proof='Literal form, exact full references, arithmetic, native persistence/shared-media retention, controlled failure/recovery/order, keyboard/typography and zero dispatch. Completion rechecks captured facts and retained unchanged helper/native receipts; it does not rerun their boundaries.',
    forbidden_claims=['Model/speech/acoustic or real learner population quality from constructed data',
                      'Fresh browser/native/helper execution merely from the receipt observer',
                      'Independent human review, provider qualification or deployment'])


def main():
    p = CHANGE / 'verification.json'
    v = json.loads(p.read_text())
    sha = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
    dependencies = UI + OWNERS + PROOF + [SOURCE]
    for prop in v['properties']:
        if prop['id'] in PROPS:
            prop['source_globs'] = list(dict.fromkeys(prop['source_globs'] + dependencies))
    selected = [c for c in v['cases'] if c['property_id'] in PROPS]
    planned = {c['test_id'].split('.')[-1]: c for c in selected}
    oracle = {
        'test_saved_dataset_freeze_positive': 'Actual saved dataset contents/input/expectation references and digest are retained through native admission; selected profile is frozen, other stage override fields retain their null inheritance, no semantic gold is invented.',
        'test_options_recovery_positive': 'Option failure/retry preserves authored topic, level and chosen configured profile; initial failure leaves report creation available and recovers with the typed topic retained.',
        'test_save_recovery_positive': 'One failed report POST is not automatically replayed; fields and prior computed report remain, explicit new Save succeeds with the retained title and no raw backend detail.',
        'test_file_import_positive': 'Actual file chooser input populates the Advanced definition; native POST stores the exact imported population and the authored file title.',
        'test_missing_selected_dataset_negative': 'A removed selected dataset remains explicitly unavailable with its original full ID. Save gives retained-input guidance and dispatches no POST rather than switching to a new authored request.',
        'test_cleanup_race_negative': 'A held first preview cannot replace or unconfirm the newer selected second attempt after its real native preview completes.',
        'test_cleanup_list_recovery_positive': 'A failed saved-record list retains selected full IDs and a usable preview; explicit Refresh clears the error without losing selection.',
        'test_cleanup_pagination_positive': 'Actual UI sends limit50/cursor i21-second-page, accumulates two separately named full IDs and retains the selected first ID while the other list can be unavailable.',
        'test_cleanup_empty_positive': 'Empty named choices show Prepare guidance and preserve the manual full identity and existing preview; no fake choices or implicit deletion.',
        'test_keyboard_layout_positive': 'Six actual report/Cleanup layouts at1280/390/320 retain loaded Source Sans3,17px/24.65px body, readable controls/helper text, visible3px keyboard focus and no horizontal page overflow.',
        'test_catalogue_scope_positive': 'Show unannotated categories exposes all122 distinct original categories with real unavailable annotations; the selected collocation arithmetic remains1/1,1/2,1/2,125/1.',
        'test_zero_dispatch_negative': 'All observed writes are explicit report/experiment saves or Cleanup preview/apply; two experiments remain planned/not_run with no output/receipts and native provider receipt count stays zero.',
        'test_native_receipt_positive': 'Retained real disposable API/PostgreSQL/MinIO race observation has exact TestGuidedToolsNativeFixture pass and exit0, with no failure event. This is receipt reuse, not another native run.',
        'test_retained_helper_receipts_positive': 'Retain the exact6 new builder,12 session/label and6 existing starter helper passes after their actual owner edits. Assert the observed identities and stable source binding without redispatching unrelated or already-green helpers.'}
    methods = sorted(n.name for n in ast.walk(ast.parse((ROOT / SOURCE).read_text()))
                     if isinstance(n, ast.FunctionDef) and n.name.startswith('test_'))
    for method in methods:
        if method in planned:
            c = planned[method]
        else:
            prop = 'FIN-VERIFY.I21' if method in ['test_keyboard_layout_positive', 'test_native_receipt_positive', 'test_retained_helper_receipts_positive'] else 'FIN-UI-08.P1'
            c = copy.deepcopy(next(c for c in selected if c['property_id'] == prop))
            expected = oracle[method]
            c.update(id=prop + '.' + method.removeprefix('test_'), property_id=prop,
                     polarity='negative' if method.endswith('negative') else 'positive',
                     setup='Use the exact authored inputs and current/retained observation boundary in ' + SOURCE + ':' + method + '.',
                     observable=expected, red_expectation='The observed outcome contradicts: ' + expected, green_expectation=expected)
            v['cases'].append(c)
        if method == 'test_cleanup_positive':
            c['setup'] = 'Choose one disposable Café opening attempt by name while its same-title second attempt and shared audio also exist; preview, then explicitly confirm/apply only the first.'
        if method == 'test_cleanup_identity_negative':
            c['setup'] = 'Inspect an exact native preview without confirming Apply, change selection, and inspect the shortened-ID input during a dependency failure. The latter is UI retention, not native UUID422 qualification.'
        c.update(test_id='unittest::tests.test_completion_i21.CompletionI21.' + method,
                 command_id='completion-i21', state='implemented', source_path=SOURCE, source_sha256=sha,
                 invalidation_dependencies=list(dict.fromkeys(dependencies + c['invalidation_dependencies'])),
                 substitution=BOUNDARY)
        c.pop('blocker', None)
    p.write_text(json.dumps(v, indent=2) + '\n')
    cases = [c for c in v['cases'] if c['property_id'] in PROPS]
    assert len(cases) == len(methods) == 24
    (AUDIT / 'SELECTION.json').write_text(json.dumps(dict(iteration=21, properties=PROPS,
        expected_case_count=len(cases), case_ids=[c['id'] for c in cases],
        boundary='24 current CUA/native/evidence oracle tests. Retains24 separately observed helper methods and1 real Go-race fixture; no repeat stack/model/provider execution.'), indent=2) + '\n')
    p = CHANGE / 'discovery.json'
    d = json.loads(p.read_text())
    ids = [c['test_id'] for c in cases]
    d['scope']['test_ids'] = list(dict.fromkeys(d['scope']['test_ids'] + ids))
    d['reviews'] = [r for r in d['reviews'] if r['id'] != 'iteration21-guided-tools-20261026']
    d['reviews'].append(dict(id='iteration21-guided-tools-20261026',
        question='Apply UX-08 guided reports/experiments and named Cleanup without JSON/hash/ID editing or implicit calls/deletion.',
        property_ids=PROPS, test_ids=ids, disposition='current_change',
        rationale='Existing native schemas and source/scoring catalogues stay intact. Forms and sessions own presentation, selection, request construction and obsolete delivery; native owners own persistence/arithmetic/freezing/deletion.',
        searches=[dict(kind='exact', status='completed', query='Trace selected reports/page/StarterForms/starters and Cleanup/RecordPicker owners to saved metadata, defaults, empirical submission, AdmitExperiment and PlanDeletion/ApplyDeletion; reuse existing saved-list/client-request and literal FX helpers.',
            outcome='Extend existing builders with named accepted population/dataset inputs. Use one report session and one Cleanup selection/preview/apply owner. Test real native save/reopen/shared-media retention, controlled failures/races, labels and responsive typography. No new backend/schema validation or learner gate.',
            results=[dict(path=x, classification='interface_dependency', reason='Actual selected owner or direct native/interface dependency, inspected and exercised.') for x in UI + OWNERS[:7]]),
            dict(kind='semantic', status='not_applicable', query='Known owners supplied by the selected DAG and accepted ownership map.', reason='No unknown ownership discovery or semantic tool is needed; no index creation or semantic evidence is claimed.', outcome='Exact source and actual runtime tracing only.', results=[]),
            dict(kind='jetbrains-index', status='not_applicable', query='Known JavaScript owners; no PSI refactor.', reason='No index-dependent operation is required.', outcome='No IDE semantic evidence claimed.', results=[])]))
    p.write_text(json.dumps(d, indent=2) + '\n')
    print('Registered', len(cases), 'implemented I21 cases')


if __name__ == '__main__':
    main()
