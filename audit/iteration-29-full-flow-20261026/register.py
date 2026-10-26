"""Materialize I29 literal observations in the existing DAG; never run models."""
from pathlib import Path
import ast
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CHANGE = ROOT / 'openspec/changes/implement-teacher-error-trainer'
PROPS = ['FIN-FLOW.P1', 'FIN-VERIFY.I29']
SOURCE = 'tests/test_completion_i29.py'
DATA = 'data/iteration-29-full-flow-20261026/'
DEPS = [
    'services/api/internal/app/interpretation_claims.go',
    'services/api/internal/app/interpretation_shape.go',
    'services/api/internal/app/interpretation_relations.go',
    'services/api/internal/app/extraction_repair_guidance_test.go',
    'services/web/app/page.js', 'services/web/app/audio/page.js',
    'services/web/app/useSavedList.js', 'services/web/app/clientRequest.js',
    'services/web/app/requestError.js', 'services/web/app/RefreshButton.js',
    'tests/full_flow_browser_fixture_test.go', 'tests/native_gemini_test.go',
    'tests/full_flow_gateway.py', SOURCE,
    'docs/development/UI_UX_TYPOGRAPHY_VERIFICATION.md',
    'docs/development/AI_DEVELOPMENT.md', 'specification/v2/docs/ai-development.md',
    'specification/v2/docs/completion-contract-details.md',
    'audit/iteration-29-full-flow-20261026/REVIEW.json',
    'audit/iteration-29-full-flow-20261026/REUSE.md',
    'audit/iteration-29-full-flow-20261026/observe.py',
]
DEPS += [DATA + name for name in [
    'browser-observations.json', 'requests.jsonl', 'typography-controls.json',
    'preparation-options.json', 'answer-expectation.json', 'answer-expectation-original.json',
    'dispatches.json', 'documents.json', 'call-reconciliation.json',
    'native-relationships.json', 'native-repaired.jsonl',
    'extraction-red.jsonl', 'extraction-green.jsonl', 'extraction-detail-green.jsonl',
    'attachment-green.jsonl', 'reopen-before.json', 'reopen-after.json',
    'saved-reports.json', 'reports-0c7497c5-9a2a-4a5e-a6fe-5c777ed1114c.json',
    'saved-experiments.json', 'experiments-f9c3c69b-f854-4051-ad40-6272ebe221ae.json',
    'preparations/bc740ead-ff03-455f-805b-0fb4c7babcf1.json',
    'keys/bc740ead-ff03-455f-805b-0fb4c7babcf1.json',
    'attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5.json',
    'attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5-result.json',
    'assets/', 'result-history/', 'pictures/',
    'media-receipt.json', 'audio-video-match.json', 'gallery-observation.json',
    'share/exercise.wav', 'share/tangerine-observed-flow.mp4', 'lab-readback.json',
]]


def main():
    path = CHANGE / 'verification.json'
    graph = json.loads(path.read_text())
    old = [c for c in graph['cases'] if c['property_id'] in PROPS]
    templates = {p: copy.deepcopy(next(c for c in old if c['property_id'] == p)) for p in PROPS}
    bymethod = {c['test_id'].split('.')[-1]: c for c in old}
    graph['cases'] = [c for c in graph['cases'] if c['property_id'] not in PROPS]
    source = (ROOT / SOURCE).read_text()
    sha = hashlib.sha256(source.encode()).hexdigest()
    review_names = {'test_review_positive', 'test_ux_omission_negative', 'test_typography_omission_negative',
                    'test_evidence_mismatch_negative', 'test_layout_positive', 'test_keyboard_positive',
                    'test_actionable_caption_positive'}
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith('test_'):
            continue
        name = node.name
        prop = 'FIN-VERIFY.I29' if name in review_names else 'FIN-FLOW.P1'
        case = copy.deepcopy(bymethod.get(name, templates[prop]))
        case.update(
            id=bymethod[name]['id'] if name in bymethod else prop + '.' + name.removeprefix('test_'),
            property_id=prop, source_path=SOURCE, source_sha256=sha,
            state='implemented', command_id='completion-i29',
            test_id='unittest::tests.test_completion_i29.CompletionI29.' + name,
            polarity='negative' if name.endswith('negative') else 'positive',
            setup='Observe actual isolated native/CUA/provider/storage/media executions using the exact independent literal assertions below. The partial developer answer and report/reference rows are explicitly constructed. This observer makes no new native/browser/provider calls.',
            observable=ast.get_source_segment(source, node),
            green_expectation='Exact saved input/key/audio/answer, independent 60/100 arithmetic, optional explanation, finite native/UI/media and review expectations hold. Required full-flow/review positives also require actual successful recommendations; those remain failed while Gemini is unavailable.',
            red_expectation='A literal identity, arithmetic, persistence, source/repair meaning, route/keyboard/readability, recovery or evidence boundary is contradicted, or the required live recommendations remain incomplete.',
            invalidation_dependencies=DEPS)
        case['substitution'] = dict(
            classification='EXTERNAL_BOUNDARY',
            owner_replaced='Only isolated DB/media/configuration, constructed partial answer/reference rows and labelled HTTP read faults/presentation projection. Gemini replies, local Kokoro synthesis, native interpretation/scoring/storage and source-built UI are actual owners.',
            allowed_proof='The exact finite observed functional run and inspected interface. Original failures, repair iterations and missing recommendations remain explicit. Observer/export/reopen work adds zero inference.',
            forbidden_claims=[
                'A polished video or readable partial result closes the failed required recommendation stage',
                'Candidate key or model output is independent linguistic gold',
                'Constructed developer answers/reports are real learner populations or empirical coverage',
                'Local selected voices establish universal accent/pronunciation quality',
                'Controlled HTTP/presentation faults are spontaneous native failures',
                'Metadata alone establishes visual quality or successful file/media delivery',
                'Paid use, bulk/performance campaign, publication or deployment'])
        case.pop('blocker', None)
        graph['cases'].append(case)
    for p in graph['properties']:
        if p['id'] in PROPS:
            p['source_globs'] = list(dict.fromkeys(p.get('source_globs', []) + DEPS))
    for command in graph['commands']:
        if command['id'] == 'completion-i29':
            command.update(argv=['python3', '-B', '-m', 'unittest', '-v', 'tests.test_completion_i29'],
                           cwd='.', env={}, timeout_seconds=120, runner='python-unittest')
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    selected = [c for c in graph['cases'] if c['property_id'] in PROPS]
    (ROOT / 'audit/iteration-29-full-flow-20261026/SELECTION.json').write_text(json.dumps(dict(
        iteration=29, properties=PROPS, case_count=len(selected), case_ids=[c['id'] for c in selected],
        expected_open_cases=['FIN-FLOW.P1.flow_positive', 'FIN-VERIFY.I29.review_positive'],
        reason='Required actual recommendations remain unavailable; implementation is not acceptance.',
        new_calls_from_observer=0), indent=2) + '\n')
    path = CHANGE / 'discovery.json'
    discovery = json.loads(path.read_text())
    ids = [c['test_id'] for c in selected]
    discovery['scope']['test_ids'] = list(dict.fromkeys(discovery['scope']['test_ids'] + ids))
    discovery['reviews'] = [r for r in discovery['reviews'] if r['id'] != 'iteration29-real-flow-20261026']
    discovery['reviews'].append(dict(
        id='iteration29-real-flow-20261026', property_ids=PROPS, test_ids=ids, disposition='current_change',
        question='Inspect all eleven actual routes and the actual generated exercise through audio, immutable answer, interpretation, exact scoring, recommendations and reopening, with truthful current media/context evidence.',
        rationale='Existing single-purpose source-span, shape, relation and saved-list owners repair demonstrated failures. All old unaffected receipts retain their original scope; new exact I29 literals observe current native/CUA/media records. Temporary Gemini high-demand failures remain the open required recommendation stage, never a passed partial-flow claim.',
        searches=[dict(kind='exact', status='completed',
            query='Trace the named FIN-FLOW/I29 cases, current routes, useSavedList/clientRequest, native preparation/interpretation/span/relation/scoring/feedback owners and actual provider/storage/browser/media receipts.',
            outcome='Observed Library card loss/refresh duplication, misleading assembled-audio status and avoidable extraction format failures were repaired with positive/negative and sibling evidence. All eleven routes were inspected at desktop/narrow widths with controlled read recovery. Independent 60/100 arithmetic and optional100% explanation match the native score; recommendations remain unavailable after explicit feedback-only retries.',
            results=[dict(path=p, classification='change_candidate' if p in DEPS[:6] else 'interface_dependency', reason='Known exact owner, contract, executable literal or observed evidence inspected.') for p in DEPS if p.startswith(('services/', 'tests/', 'specification/'))]),
            dict(kind='semantic', status='not_applicable',
                 query='The continuation plan and preceding native qualifications name the exact routes, source/shape/relation and saved-list owners.',
                 reason='No unfamiliar ownership search or new index was required for exact source/receipt tracing.',
                 outcome='No semantic-index evidence claimed.', results=[]),
            dict(kind='jetbrains-index', status='not_applicable', query='Exact named Go/React sources; no symbol refactoring.',
                 reason='No PSI operation is needed for this bounded repair.', outcome='No IDE/index evidence claimed.', results=[])]))
    path.write_text(json.dumps(discovery, indent=2, ensure_ascii=False) + '\n')
    print('Registered', len(selected), 'implemented I29 cases; required full-flow positives remain unaccepted')


if __name__ == '__main__':
    main()
