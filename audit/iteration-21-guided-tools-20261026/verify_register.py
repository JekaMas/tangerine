"""Supersede I21 apply bindings with current verification and bounded reuse."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGE = ROOT / 'openspec/changes/implement-teacher-error-trainer'
AUDIT = ROOT / 'audit/iteration-21-guided-tools-20261026'
PREFIX = 'data/iteration-21-verify-20261026/'
PROPS = ['FIN-UI-08.P1', 'FIN-VERIFY.I21']
SOURCE = 'tests/test_iteration21_verify.py'
UI = ['services/web/app/reports/' + x for x in ['page.js', 'useReports.js', 'session.js', 'StarterForms.js',
      'starters.js', 'request.js', 'definitionFile.js', 'useDefinitionFile.js', 'metricDisplay.js']]
UI += ['services/web/app/cleanup/' + x for x in ['page.js', 'session.js', 'useCleanup.js', 'RecordPicker.js', 'labels.js']]
UI += ['services/web/app/styles/base.css', 'services/web/app/useSavedList.js', 'services/web/app/savedList.js',
       'services/web/app/clientRequest.js', 'services/web/app/requestError.js']
HELPERS = ['tests/test_reports_session.py', 'tests/test_cleanup_session.py', 'tests/test_guided_starters.py',
           'tests/test_final_functional_helpers.py', 'tests/guided_tools_fixture_test.go']
PROOF = [PREFIX + x for x in ['observations.json', 'baseline-observations.json', 'requests.jsonl',
         'native-write-responses.jsonl', 'native-fixture.json', 'native-final.json', 'native.jsonl', 'native-exit-code',
         'current-report.json', 'native-report-input.json', 'current-experiment.json', 'current-reused-experiment.json',
         'native-first-dataset.json', 'native-reused-dataset.json', 'native-frozen-config.json', 'imported-report.json',
         'reports-session-green.log', 'cleanup-owner-final.log', 'starters-green.log', 'existing-starters-green.log']]
PROOF += ['audit/iteration-21-guided-tools-20261026/' + x for x in ['VERIFY-SOURCE.json', 'VERIFY-REVIEW.json', 'verify_review.py']]
BOUNDARY = dict(classification='EXTERNAL_BOUNDARY',
    owner_replaced='Controlled GET503/404/default/empty/held replies and constructed native text/key/PCM/offline models. Production frontend/session/file/eligibility/presentation owners and real disposable API/Postgres/MinIO are observed. Three unchanged RecordPicker list-only CUA cases are retained.',
    allowed_proof='Current actual browser/native contents and17+15+7+6 observed helper assertions, with stable source bindings. Completion reads these receipts without rerunning their boundaries. Native erasure/arithmetic/config/dataset origin is real; no provider call occurs.',
    forbidden_claims=['Provider/acoustic/linguistic or authentic learner population qualification',
                      'New native/browser/helper execution merely from a receipt observer',
                      'Independent human review, PBT, deployment or later-iteration release acceptance'])


def main():
    p = CHANGE / 'verification.json'
    v = json.loads(p.read_text())
    old = [c for c in v['cases'] if c['property_id'] in PROPS]
    old_tests = {c['test_id'] for c in old}
    by_method = {c['test_id'].split('.')[-1]: c for c in old}
    methods = sorted(n.name for n in ast.walk(ast.parse((ROOT / SOURCE).read_text()))
                     if isinstance(n, ast.FunctionDef) and n.name.startswith('test_'))
    extras = {
        'test_report_retry_positive': 'After a failed saved-report GET, explicit Refresh retries that exact intended ID and restores its detail; safe reads leave both starter Save controls usable.',
        'test_old_refresh_negative': 'Held old collection/detail reads cannot replace the newer selected experiment; failed newly selected IDs remain the intended Refresh target.',
        'test_comparison_isolation_positive': 'A comparison-asset503 cannot hide the readable planned experiment or disable unrelated starter creation; the authored guidance names the optional detail recovery.',
        'test_comparison_retry_positive': 'Retry comparison details requests only that asset and clears its error; no experiment Run, provider call or repeated primary read is dispatched.',
        'test_pending_confirmation_negative': 'Pending replacement previews expose no old confirmation; newly returned previews are unchecked. Failed previews retain selection but cannot expose an old Apply.',
        'test_unavailable_profile_negative': 'A previously selected model that becomes unselected stays visibly setup-needed with the same topic/level/profile. One shared eligibility owner prevents an unusable Save without silently selecting another profile.',
        'test_missing_item_negative': 'A native404 becomes local choose/create guidance and leaves the report/experiment starter controls usable without raw backend text.',
        'test_record_identity_positive': 'Same-minute record buttons expose distinct full identities in readable14px stacked secondary controls at1280/390/320; the surrounding primary actions remain prominent.'}
    sha = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
    for method in methods:
        if method in by_method:
            c = by_method[method]
        else:
            prop = 'FIN-UI-08.P1'
            c = copy.deepcopy(next(c for c in old if c['property_id'] == prop))
            oracle = extras[method]
            c.update(id=prop + '.' + method.removeprefix('test_'), property_id=prop,
                     polarity='negative' if method.endswith('negative') else 'positive',
                     setup='Use current baseline/fixed browser/native observations and literal owner inputs in ' + SOURCE + ':' + method + '.',
                     observable=oracle, red_expectation='The actual result contradicts: ' + oracle, green_expectation=oracle)
            v['cases'].append(c)
        if method == 'test_cleanup_identity_negative':
            c['setup'] = 'Inspect an unconfirmed current native preview, change selection, and enter a shortened unknown ID. Actual native outcome is blocked with0 affected objects, not assumed422.'
            c['observable'] = c['green_expectation'] = 'No other record is selected or erased; selection change resets confirmation and unresolved/full-ID guidance is human-readable.'
        if method == 'test_retained_helper_receipts_positive':
            c['observable'] = c['green_expectation'] = 'The exact17 reports/file/metric/request,15 Cleanup,7 builder and6 existing starter assertions have observed current owner receipts and stable inputs; no helper/model campaign is redispatched by completion.'
        c.update(test_id='unittest::tests.test_iteration21_verify.Iteration21Verify.' + method,
                 command_id='completion-i21', state='implemented', source_path=SOURCE, source_sha256=sha,
                 invalidation_dependencies=list(dict.fromkeys(c['invalidation_dependencies'] + UI + HELPERS + PROOF + [SOURCE])),
                 substitution=BOUNDARY)
        c.pop('blocker', None)
    for prop in v['properties']:
        if prop['id'] in PROPS:
            prop['source_globs'] = list(dict.fromkeys(prop['source_globs'] + UI + HELPERS + PROOF + [SOURCE]))
    v['commands'] = [c for c in v['commands'] if c['id'] != 'iteration21-verify']
    command = next(c for c in v['commands'] if c['id'] == 'completion-i21')
    command['argv'] = ['python3', '-B', '-m', 'unittest', '-v', 'tests.test_iteration21_verify']
    p.write_text(json.dumps(v, indent=2) + '\n')
    selected = [c for c in v['cases'] if c['property_id'] in PROPS]
    assert len(selected) == len(methods) == 32
    (AUDIT / 'VERIFY-SELECTION.json').write_text(json.dumps(dict(iteration=21, baseline='438687b', properties=PROPS,
        expected_case_count=32, case_ids=[c['id'] for c in selected],
        boundary='32 exact current CUA/native/evidence oracle identities. Retain45 observed helper identities and1 fresh native race test; three unchanged list-adapter UI observations remain bounded reuse.'), indent=2) + '\n')
    ids = [c['test_id'] for c in selected]
    p = CHANGE / 'discovery.json'
    d = json.loads(p.read_text())
    d['scope']['test_ids'] = list(dict.fromkeys([x for x in d['scope']['test_ids'] if x not in old_tests] + ids))
    for prior in d['reviews']:
        if any(x in old_tests for x in prior.get('test_ids', [])):
            prior['test_ids'] = list(dict.fromkeys([x for x in prior['test_ids'] if x not in old_tests] + ids))
    d['reviews'] = [r for r in d['reviews'] if r['id'] != 'iteration21-verify-repair-20261026']
    d['reviews'].append(dict(id='iteration21-verify-repair-20261026', question='Verify and repair the complete UX-08 iteration without blocking unrelated work on reads, diagnostics or errors.',
        property_ids=PROPS, test_ids=ids, disposition='current_change',
        rationale='Actual438687b browser counterexamples and model-builder red supersede the apply no-findings conclusion. Single reports/file/Cleanup/eligibility/presentation owners are repaired, current native/browser proof is added, and unchanged list/source/math/provider observations are retained.',
        searches=[dict(kind='exact', status='completed', query='Inspect every I21 page/form/request/session/file/selection path and native counterpart, including pending/error/refresh/unmount and original literal tests.',
            outcome='Confirmed intended-ID Refresh/ordering, optional comparison, pending-preview confirmation, unavailable model and sibling error/file/identity issues. Repair without schema-byte archives, stored-data rescans, new API/approval gate or provider inference.',
            results=[dict(path=x, classification='interface_dependency', reason='Actual selected owner or directly inspected caller/dependency.') for x in UI]),
            dict(kind='semantic', status='not_applicable', query='Exact selected owners are known from the canonical DAG and apply source.', reason='No unknown ownership or semantic lookup needed.', outcome='No semantic/index evidence claimed.', results=[]),
            dict(kind='jetbrains-index', status='not_applicable', query='Known JavaScript owners; no index-sensitive refactor.', reason='No PSI operation required.', outcome='No IDE index claim.', results=[])]))
    p.write_text(json.dumps(d, indent=2) + '\n')
    print('Registered32 implemented I21 verification cases')


if __name__ == '__main__':
    main()
