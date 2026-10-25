"""Reconcile retained exact observations without repeating green behavior."""
import collections, json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
O = R / 'data/recurring-errors-20261025'
BASE = '67c811bd4f7a942a2d7bf02618618e983c62167d'
sys.path.insert(0, str(R / '.agents/workflow/scripts'))
from requirement_tests import parse_go_events, parse_unittest_events

logs = [
    ('native-first.jsonl', 'go'), ('quota-negative-green.jsonl', 'go'),
    ('affected-native.jsonl', 'go'), ('speech-plan-native.jsonl', 'go'),
    ('projections-final-green.jsonl', 'go'), ('score-projection-final-green.jsonl', 'go'), ('persistence-projection-final-green.jsonl', 'go'), ('projection-adapter-accepted.jsonl', 'go'),
    ('request.log', 'python'), ('acoustic-compiler.log', 'python'),
    ('evidence-first.log', 'python'), ('evidence-controls-green.log', 'python'),
    ('evidence-preservation-green.log', 'python')]
observed = {}
for name, kind in logs:
    raw = (O / name).read_text()
    for identity, status in (parse_go_events if kind == 'go' else parse_unittest_events)(raw).items():
        observed[identity] = (status, name)
graph = json.loads((R / 'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
cases = []
for case in graph['cases']:
    if not case['id'].startswith('FOS-'):
        continue
    status, log = observed[case['test_id']]
    assert status == 'pass', (case['id'], status, log)
    cases.append(dict(id=case['id'], test_id=case['test_id'], polarity=case['polarity'], status='passed', receipt='data/recurring-errors-20261025/' + log, expectation=case['green_expectation']))
assert len(cases) == 30
protected = [p for p in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=R, text=True).splitlines() if p.startswith('services/api/internal/app/generationdata/') or p.startswith('services/api/internal/app/migrations/') or p in ['specification/v2/domain/error-taxonomy.v1.yaml', 'specification/v2/domain/mutation-recipes.v1.json', 'specification/v2/domain/metrics.v1.yaml', 'specification/v2/domain/corpus-sources.v1.yaml', 'specification/v2/domain/providers.v1.yaml']]
assert all(subprocess.check_output(['git', 'show', BASE + ':' + p], cwd=R) == (R / p).read_bytes() for p in protected)
lab = json.loads((O / 'mlflow.json').read_text())
assert lab['native_packet_readback'] == 17 and lab['export_inference_calls'] == 0
preserved = json.loads((O / 'preservation.json').read_text())
assert preserved['original_attempt_unchanged'] and preserved['configuration_restored']
result = dict(status='passed', base_revision=BASE, properties=4, selected_cases=len(cases), polarities=dict(collections.Counter(c['polarity'] for c in cases)), passed_cases=cases, protected_unchanged=protected, local_mlflow=lab,
    invalidation_decisions=[
        'New recurring owners/DTOs/prompts required the selected new cases and directly affected native/request/acoustic regressions.',
        'Quota-negative initially inspected the safe public error instead of the typed admission detail; that assertion alone was repaired and repeated.',
        'Actual evaluation-key and feedback-score counterexamples invalidated the persistence/score projection assertions and their actual live stages; only those were repaired/retried.',
        'The added summary negative first demanded a redundant range recheck of trusted data; it now checks a wrong-typed field. No repeated runtime range audit was introduced.',
        'The teacher disclosure fixture excludes native evidence_ids, as its existing contract requires; its corrected projection was observed separately.',
        'The two evidence assertion/collector repairs account for explicit frozen null defaults and nested native speech wire receipts; six prior artifact greens were retained.',
        'The web production build and unchanged request/accent/old native leaves retain their original valid receipts. Commit/report/task updates alone do not invalidate behavior.',
        'The saved-projection command adapter was aligned with the existing go-test-json argv contract and executed successfully; the workflow checker was unchanged.',
        'Final schema-copy/vector and DAG gates were rerun after actual contract/selected-case changes. No earlier failure was overwritten or presented as a pass.'],
    regressions=dict(affected_native_receipt='data/recurring-errors-20261025/affected-native.jsonl', existing_request_cases=8, existing_accent_request_cases=5, existing_acoustic_cases=3),
    proof_boundary=['Finite constructed literal admission/arithmetic tests and two actual authored answer probes; no universal LLM accuracy or exhaustive linguistic eligibility claim.', 'One actual local recurring pronunciation sample on each of Melo and Kokoro; exact scopes and correct-waveform preservation, not a perceptual guarantee for every operation/voice.', 'No real-person fossilization diagnosis or universal 70-95 percent research estimate.', 'Self-review of changed owners; no separate external reviewer, unselected provider qualification or renewed whole-release pass.'])
(R / 'audit/recurring-errors-20261025/RECONCILIATION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(dict(status='passed', cases=len(cases), polarities=result['polarities'], protected_unchanged=len(protected), mlflow_run=lab['run_id'])))
