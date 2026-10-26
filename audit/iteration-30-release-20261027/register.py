"""Bind implemented I30 literal tests to the existing properties; no execution."""
from pathlib import Path
import ast
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CHANGE = ROOT / 'openspec/changes/implement-teacher-error-trainer'
SOURCE = 'tests/test_completion_i30.py'
PROPERTIES = ['FIN-DELIVERY.P1', 'FIN-VERIFY.I30']
DEPENDENCIES = [
    'README.md', 'LICENSE', '.env.example', '.dockerignore', 'scripts', 'deploy',
    'services', 'specification/v2', SOURCE,
    'audit/iteration-30-release-20261027/native_release.py',
    'audit/iteration-30-release-20261027/launcher_fixture.sh',
    'audit/iteration-30-release-20261027/readiness_forwarder.py',
    'audit/iteration-30-release-20261027/REVIEW.json',
    'docs/development/UI_UX_TYPOGRAPHY_VERIFICATION.md',
    'data/iteration-30-release-20261027/publication.json',
    'data/iteration-30-release-20261027/native.json',
    'data/iteration-30-release-20261027/launcher-negative.json',
    'data/iteration-30-release-20261027/ui-observations.json',
    'data/iteration-30-release-20261027/preservation-before.json',
    'data/iteration-30-release-20261027/preservation-after.json',
    'data/iteration-30-release-20261027/native-origin-fixture-failure.json',
    'data/iteration-30-release-20261027/native-header-fixture-failure.json',
    'data/iteration-30-release-20261027/readiness-header-discriminator.json',
    'data/iteration-30-release-20261027/archive-native-readback.json',
    'data/iteration-30-release-20261027/public-main.zip',
]


def main():
    path = CHANGE / 'verification.json'
    graph = json.loads(path.read_text())
    selected = [row for row in graph['cases'] if row['property_id'] in PROPERTIES]
    templates = {p: copy.deepcopy(next(row for row in selected if row['property_id'] == p)) for p in PROPERTIES}
    previous = {row['test_id'].split('.')[-1]: row for row in selected}
    graph['cases'] = [row for row in graph['cases'] if row['property_id'] not in PROPERTIES]
    source = (ROOT / SOURCE).read_text()
    sha = hashlib.sha256(source.encode()).hexdigest()
    reviews = {'test_review_positive', 'test_ux_omission_negative', 'test_partial_review_negative',
               'test_typography_omission_negative', 'test_evidence_mismatch_negative'}
    tests = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith('test_'):
            continue
        prop = 'FIN-VERIFY.I30' if node.name in reviews else 'FIN-DELIVERY.P1'
        row = copy.deepcopy(previous.get(node.name, templates[prop]))
        identity = 'unittest::tests.test_completion_i30.CompletionI30.' + node.name
        row.update(id=previous[node.name]['id'] if node.name in previous else prop + '.' + node.name.removeprefix('test_'),
                   property_id=prop, test_id=identity, state='implemented',
                   command_id='completion-i30', source_path=SOURCE, source_sha256=sha,
                   polarity='negative' if node.name.endswith('negative') else 'positive',
                   setup='Real disposable Git operations, damaged-source launcher cases and actual retained native GitHub/ZIP/Docker/CUA observations, including failed origin/header isolation counterexamples. Independent literal expectations are the test body; this observer dispatches no model/provider call.',
                   observable=ast.get_source_segment(source, node),
                   green_expectation='The literal expected Git state, actual public ref/archive, unchanged downloaded source startup, private configuration and persisted workspace/settings, or inspected layout/review relation holds. Missing actual evidence fails rather than passing from a label.',
                   red_expectation='The exact Git state, required source input, actual ZIP/native/UI relationship, private-state preservation or review dimension contradicts its independently specified expected value.',
                   invalidation_dependencies=DEPENDENCIES)
        row.pop('blocker', None)
        row['substitution'] = dict(
            classification='EXTERNAL_BOUNDARY',
            owner_replaced='Only isolated constructed Git repositories and damaged-source inputs; actual ZIP startup uses the real Docker engine with a test-only port overlay and transparent Host/Origin projection to the unchanged localhost:3000 application origin. Exact response headers/status/body are forwarded. No GitHub/archive/application reply is replaced.',
            allowed_proof='Exact finite Git failure/preservation behavior, actual selected published source and native Docker-only startup/restart, and inspected fresh-install browser/typography. Review counterexamples prove development bookkeeping only.',
            proof_claims=['The literal selected release, startup/persistence and reviewed interface boundary only.'],
            forbidden_claims=['Universal platform/provider/acoustic/corpus qualification',
                              'Independent review from self-review',
                              'A real GitHub archive or visual acceptance from a constructed response/green label',
                              'A new learner qualification or stored-data consistency gate'])
        graph['cases'].append(row); tests.append(identity)
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    path = CHANGE / 'discovery.json'
    discovery = json.loads(path.read_text())
    discovery['scope']['test_ids'] = list(dict.fromkeys(discovery['scope']['test_ids'] + tests))
    discovery['reviews'] = [r for r in discovery['reviews'] if r['id'] != 'iteration30-source-delivery-20261027']
    discovery['reviews'].append(dict(
        id='iteration30-source-delivery-20261027', property_ids=PROPERTIES, test_ids=tests,
        disposition='current_change',
        question='Trace actual main/GitHub source publication and Docker-only downloaded ZIP startup/persistence, preserving unrelated work and inspecting fresh-install UI/typography.',
        rationale='Git and GitHub own source/ref delivery. Actual public repository/main and both immutable/unauthenticated source ZIPs are observed. The existing launcher, configuration, Compose, Dockerfiles and locks own initialization/restart. Test-only network isolation preserves app3000 and changes no downloaded source. Wrong origin and omitted readiness headers were demonstrated and repaired only in the shared isolation harness. Partial UI remains unaccepted while computer control is unavailable. No application feature, provider call, paid use or new runtime gate is added.',
        searches=[
            dict(kind='exact', status='completed',
                 query='Inspect FIN-DELIVERY.P1, FIN-VERIFY.I30, actual refs/remotes, source launcher/Compose/build inputs, release tests and native/browser publication records.',
                 outcome='Named source/ref/startup owners and full required inputs traced. Canonical main is an ancestor and its unrelated GAPS edit is unchanged by the release branch. No remote or existing JekaMas/tangerine repository existed at entry.',
                 results=[dict(path=p, classification='change_candidate', reason='Exact release owner, literal test or native observation driver inspected.')
                          for p in ['scripts/tangerine', 'scripts/workspace-env', 'deploy/local/compose.yaml',
                                    'services/api/Dockerfile', 'services/web/Dockerfile', 'services/speech/Dockerfile',
                                    'specification/v2/docs/local-delivery.md', SOURCE]]),
            dict(kind='semantic', status='unavailable',
                 query='Where are the source release archive completeness checks and the Docker-only launcher tests that validate required build inputs and persistence after restart?',
                 outcome='No semantic results were available; direct named-file and native evidence tracing was used.',
                 reason='jbcontext reports no index for this exact checkout; no semantic evidence is claimed.', results=[]),
            dict(kind='jetbrains-index', status='not_applicable',
                 query='Known release files and Git/GitHub/native process boundaries; no symbol discovery or refactor requested.',
                 outcome='Exact named files and real Git/Docker boundaries were inspected without an IDE index.',
                 reason='No code structure changes or IDE index claim; exact named paths and native behavior supply the relevant evidence.', results=[])]))
    path.write_text(json.dumps(discovery, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'properties': PROPERTIES, 'implemented_cases': len(tests), 'execution': 'not performed by registration'}))


if __name__ == '__main__':
    main()
