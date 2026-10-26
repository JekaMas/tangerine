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
VERIFY_SOURCE = 'tests/test_completion_i29_verify.py'
NOTICE_SOURCE = 'tests/test_feedback_notice.py'
LOCAL_SOURCE = 'tests/test_completion_i29_local.py'
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
    'services/web/app/listen/checkingProgress.js',
    'services/web/app/listen/useListening.js', VERIFY_SOURCE, NOTICE_SOURCE, LOCAL_SOURCE,
    'services/web/app/listen/Results.js', 'services/web/app/styles/base.css',
    'services/api/internal/provider/transport.go', 'services/api/internal/provider/local_host_test.go',
    'services/api/internal/app/extraction_quote_projection_test.go',
    'specification/v2/docs/answer-interpretation-runtime.md',
    'tests/full_flow_local_fixture_test.go',
    'audit/iteration-29-full-flow-20261026/local_native.py',
    'audit/iteration-29-full-flow-20261026/build_completed_media.py',
    'audit/iteration-29-full-flow-20261026/complete_gallery.py',
    'audit/iteration-29-full-flow-20261026/compare_completed_audio.py',
    'audit/iteration-29-full-flow-20261026/export_completed_lab.py',
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
DEPS += ['data/iteration-29-verify-20261026/' + name for name in [
    'feedback-before.json', 'ui-observations.json', 'dispatch-delta.json',
    'ui-dispatches-before.json', 'ui-dispatches-after.json',
    'lab-readback.json', 'feedback-notice-green.log',
    'reply-red.json', 'reply-green.json', 'reply-restored-native.json',
    'reply-retention-green.log',
]]

DEPS += ['data/iteration-29-saved-case-flow-20261026/' + name for name in [
    'call-reconciliation.json', 'dispatches.json', 'documents.json', 'native-relationships.json',
    'answer-expectation.json', 'flow-selection.json', 'selected-attempt', 'selected-preparation',
    'preparations/', 'keys/', 'attempts/', 'assets/', 'ui-observations.json', 'pictures/',
    'requests.jsonl', 'reopen-before.json', 'reopen-after.json', 'observer-path-reconciliation.json',
    'quote-qualified-red.jsonl', 'quote-sibling-green.jsonl', 'provider-final-green.jsonl',
    'media-receipt.json', 'audio-video-match.json', 'gallery-observation.json', 'gallery-poster-before.json', 'lab-readback.json',
    'share/tangerine-complete-flow.mp4', 'share/exercise.wav',
]]
DEPS += ['data/iteration-29-local-full-flow-20261026/' + name for name in [
    'dispatches.json', 'documents.json', 'preparations/', 'installed-local-models.json',
    'installed-generation-model.json', 'host-api-read-probes.json',
]]

def main():
    path = CHANGE / 'verification.json'
    graph = json.loads(path.read_text())
    old = [c for c in graph['cases'] if c['property_id'] in PROPS]
    templates = {p: copy.deepcopy(next(c for c in old if c['property_id'] == p)) for p in PROPS}
    bymethod = {c['test_id'].split('.')[-1]: c for c in old}
    graph['cases'] = [c for c in graph['cases'] if c['property_id'] not in PROPS]
    review_names = {'test_review_positive', 'test_ux_omission_negative', 'test_typography_omission_negative',
                    'test_evidence_mismatch_negative', 'test_layout_positive', 'test_keyboard_positive',
                    'test_actionable_caption_positive', 'test_current_layout_keyboard_positive',
                    'test_feedback_linebreaks_positive', 'test_feedback_layout_and_data_negative',
                    'test_complete_playback_replay_layout_positive'}
    for source_path, classname in [(SOURCE, 'tests.test_completion_i29.CompletionI29'),
                                   (VERIFY_SOURCE, 'tests.test_completion_i29_verify.CompletionI29Verify'),
                                   (NOTICE_SOURCE, 'tests.test_feedback_notice.FeedbackNotice'),
                                   (LOCAL_SOURCE, 'tests.test_completion_i29_local.CompletionI29Local')]:
      source = (ROOT / source_path).read_text()
      sha = hashlib.sha256(source.encode()).hexdigest()
      for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith('test_'):
            continue
        name = node.name
        prop = 'FIN-VERIFY.I29' if name in review_names else 'FIN-FLOW.P1'
        case = copy.deepcopy(bymethod.get(name, templates[prop]))
        case.update(
            id=bymethod[name]['id'] if name in bymethod else prop + '.' + name.removeprefix('test_'),
            property_id=prop, source_path=source_path, source_sha256=sha,
            state='implemented', command_id='completion-i29',
            test_id='unittest::' + classname + '.' + name,
            polarity='negative' if name.endswith('negative') else 'positive',
            setup='Observe actual isolated native/CUA/provider/storage/media executions using the exact independent literal assertions below. The partial developer answer and report/reference rows are explicitly constructed. This observer makes no new native/browser/provider calls.',
            observable=ast.get_source_segment(source, node),
            green_expectation='Exact saved input/key/audio/answer, independent 60/100 arithmetic, optional explanation, finite native/UI/media and review expectations hold. Required full-flow/review positives require actual successful recommendations for the explicit selected attempt. The actual Gemini-generated/Kokoro case is reused with a new local-checker attempt; the unavailable old Gemini attempt remains unaccepted.',
            red_expectation='A literal identity, arithmetic, persistence, source/repair meaning, route/keyboard/readability, recovery or evidence boundary is contradicted, or the required live recommendations remain incomplete.',
            invalidation_dependencies=DEPS)
        case['substitution'] = dict(
            classification='EXTERNAL_BOUNDARY',
            owner_replaced='Only isolated DB/media/configuration, constructed partial answer/reference rows and labelled HTTP read faults/UI reply projections. A constructed complete HTTP reply proves UI retention only; that UI fixture never establishes live feedback. Actual Gemini generation/local Kokoro are reused on the identical case. The separate new local-checker attempt has actual native interpretation/scoring/comments/recommendations, with no replacement of model replies or saved results.',
            allowed_proof='The exact finite observed functional run and inspected interface. Original failed attempts, repair iterations and scope remain explicit; full selected flow needs actual completed feedback. Observer/export/reopen work adds zero inference.',
            forbidden_claims=[
                'A polished video or readable partial result closes the failed required recommendation stage',
                'Candidate key or model output is independent linguistic gold',
                'Constructed developer answers/reports are real learner populations or empirical coverage',
                'Local selected voices establish universal accent/pronunciation quality',
                'Controlled HTTP/presentation faults are spontaneous native failures',
                'A constructed complete HTTP UI reply is successful live recommendations',
                'Metadata alone establishes visual quality or successful file/media delivery',
                'Paid use, bulk/performance campaign, publication or deployment'])
        case.pop('blocker', None)
        graph['cases'].append(case)
    for p in graph['properties']:
        if p['id'] in PROPS:
            p['source_globs'] = list(dict.fromkeys(p.get('source_globs', []) + DEPS))
    for command in graph['commands']:
        if command['id'] == 'completion-i29':
            command.update(argv=['python3', '-B', '-m', 'unittest', '-v', 'tests.test_completion_i29',
                                 'tests.test_completion_i29_verify', 'tests.test_feedback_notice',
                                 'tests.test_completion_i29_local'],
                           cwd='.', env={}, timeout_seconds=120, runner='python-unittest')
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    selected = [c for c in graph['cases'] if c['property_id'] in PROPS]
    (ROOT / 'audit/iteration-29-full-flow-20261026/SELECTION.json').write_text(json.dumps(dict(
        iteration=29, properties=PROPS, case_count=len(selected), case_ids=[c['id'] for c in selected],
        expected_open_cases=[],
        reason='Actual complete selected saved-case/local-checker flow; original failed attempts remain retained. Committed-clean acceptance is recorded separately.',
        new_calls_from_observer=0), indent=2) + '\n')
    path = CHANGE / 'discovery.json'
    discovery = json.loads(path.read_text())
    ids = [c['test_id'] for c in selected]
    discovery['scope']['test_ids'] = list(dict.fromkeys(discovery['scope']['test_ids'] + ids))
    discovery['reviews'] = [r for r in discovery['reviews'] if r['id'] != 'iteration29-real-flow-20261026']
    discovery['reviews'].append(dict(
        id='iteration29-real-flow-20261026', property_ids=PROPS, test_ids=ids, disposition='current_change',
        question='Inspect all eleven actual routes and the actual generated exercise through audio, immutable answer, interpretation, exact scoring, recommendations and reopening, with truthful current media/context evidence.',
        rationale='Existing single-purpose source-span, shape, relation and saved-list owners repair demonstrated failures. All old unaffected receipts retain their original scope; new exact I29 literals observe current native/CUA/media records. The old Gemini high-demand failures remain unaccepted. A separate new ordinary attempt explicitly selects local checking on the identical real generated case and completes actual feedback; partial/constructed evidence never substitutes for it.',
        searches=[dict(kind='exact', status='completed',
            query='Trace the named FIN-FLOW/I29 cases, current routes, useSavedList/clientRequest, native preparation/interpretation/span/relation/scoring/feedback owners and actual provider/storage/browser/media receipts.',
            outcome='Observed Library card loss/refresh duplication, misleading assembled-audio status and avoidable extraction format failures were repaired with positive/negative and sibling evidence. All eleven routes were inspected at desktop/narrow widths with controlled read recovery. The original Gemini attempt has exact60/100 and optional100% but unavailable feedback. The explicitly selected new local-checker attempt on the same case now has actual completed comments/recommendations and the independently expected score.',
            results=[dict(path=p, classification='change_candidate' if p in DEPS[:6] else 'interface_dependency', reason='Known exact owner, contract, executable literal or observed evidence inspected.') for p in DEPS if p.startswith(('services/', 'tests/', 'specification/'))]),
            dict(kind='semantic', status='not_applicable',
                 query='The continuation plan and preceding native qualifications name the exact routes, source/shape/relation and saved-list owners.',
                 reason='No unfamiliar ownership search or new index was required for exact source/receipt tracing.',
                 outcome='No semantic-index evidence claimed.', results=[]),
            dict(kind='jetbrains-index', status='not_applicable', query='Exact named Go/React sources; no symbol refactoring.',
                 reason='No PSI operation is needed for this bounded repair.', outcome='No IDE/index evidence claimed.', results=[])]))
    discovery['reviews'][-1]['rationale'] += ' Fresh verify repairs an optimistic feedback retry notice and stops a follow-up result read from hiding an already returned result, through the existing listening controller/status owners. Current1280/390/320, safe transport-error/recovery, keyboard and saved navigation observations add zero inference. The constructed complete HTTP reply is UI-only; native recommendations remain unavailable. One necessary same-profile feedback retry received two503s; all29 hosted receipts remain matched and successful recommendations remain missing.'
    discovery['reviews'][-1]['rationale'] += ' This historical unavailable attempt is preserved. The final selection explicitly reuses its valid case generation/key/audio and creates a new local gpt-oss attempt. Actual60/100, optional100%, factual finding/miss components, recommendations, playback/reopen and37-text-receipt reconciliation (29 retained Gemini,8 local) complete. Native source-quote representation and Ollama Host repairs have positive/negative siblings. Current feedback line breaks are preserved and visually inspected at1280/390/320; no extra model call follows read/reopen/export.'
    path.write_text(json.dumps(discovery, indent=2, ensure_ascii=False) + '\n')
    print('Registered', len(selected), 'implemented I29 cases; actual complete selected flow, committed-clean acceptance separate')


if __name__ == '__main__':
    main()
