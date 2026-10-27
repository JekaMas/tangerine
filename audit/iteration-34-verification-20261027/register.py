"""Append verification cases; keep all original apply/history registrations."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'openspec/changes/implement-teacher-error-trainer'


def main():
    graph = json.loads((BASE / 'verification.json').read_text())
    source = 'tests/test_local_generation_review.py'
    raw = (ROOT / source).read_text()
    methods = {m.name: ast.get_source_segment(raw, m) for c in ast.parse(raw).body if isinstance(c, ast.ClassDef)
               for m in c.body if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')}
    graph['cases'] = [c for c in graph['cases'] if c.get('command_id') != 'iteration34-review']
    for case in graph['cases']:
        if case['id'].startswith('I34.'):
            s = ROOT / case['source_path']
            case['source_sha256'] = hashlib.sha256(s.read_bytes()).hexdigest()
            current = s.read_text()
            name = case['test_id'].rsplit('.', 1)[-1]
            method = next(m for c in ast.parse(current).body if isinstance(c, ast.ClassDef)
                          for m in c.body if isinstance(m, ast.FunctionDef) and m.name == name)
            case['observable'] = ast.get_source_segment(current, method)
            if case['property_id']=='I34.P4':
                case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+[
                    'data/iteration-34-verification-20261027/lab.json',
                    'data/iteration-34-verification-20261027/lab-readback/compare.py']))
    for name, literal in methods.items():
        pid = 'I34.P2' if '_ui_' in name else 'I34.P3'
        template = next(c for c in graph['cases'] if c['property_id'] == pid)
        case = dict(template)
        case.update(id=pid+'.'+name, polarity='negative' if name.endswith('negative') else 'positive',
                    setup='Retained actual local native packets and authored counterexamples; actual current web UI with isolated controlled HTTP outcomes. No new inference.',
                    observable=literal, test_id='unittest::tests.test_local_generation_review.LocalGenerationReview.'+name,
                    command_id='iteration34-review', state='implemented', source_path=source,
                    source_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                    invalidation_dependencies=[source, 'audit/iteration-34-local-generation-20261027/compare.py',
                        'audit/iteration-34-verification-20261027/browser_fixture.py',
                        'audit/iteration-34-verification-20261027/build_video.py', 'services/web/app/prepare/**',
                        'services/web/app/clientRequest.js', 'services/web/app/requestError.js',
                        'services/web/app/styles/**',
                        'data/iteration-34-local-generation-20261027/comparison.json',
                        'data/iteration-34-local-generation-20261027/*/*asset_id.json',
                        'data/iteration-34-verification-20261027/browser/observations.json',
                        'data/iteration-34-verification-20261027/browser/requests.jsonl',
                        'data/iteration-34-verification-20261027/browser/video-probe.json',
                        'data/iteration-34-verification-20261027/browser/pictures/*.png',
                        'data/iteration-34-verification-20261027/browser/preparation-recovery.mp4'],
                    distinct_reason='I34 verification: '+name)
        graph['cases'].append(case)
    graph['commands'] = [c for c in graph['commands'] if c['id'] != 'iteration34-review']
    graph['commands'].append(dict(id='iteration34-review', runner='python-unittest',
        argv=['python3','-B','-m','unittest','-v','tests.test_local_generation_review'], cwd='.', env={}, timeout_seconds=120, authority='local'))
    def save(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
    save(BASE/'verification.json',graph)
    cases = [c for c in graph['cases'] if c['id'].startswith('I34.')]
    save(HERE/'SELECTION.json',dict(iteration=34,case_ids=[c['id'] for c in cases],expected_case_count=len(cases)))
    discovery = json.loads((BASE/'discovery.json').read_text())
    ids = [c['test_id'] for c in cases]
    discovery['scope']['test_ids'] = list(dict.fromkeys(discovery['scope']['test_ids']+ids))
    discovery['reviews'] = [r for r in discovery['reviews'] if r['id'] != 'iteration34-verification']
    discovery['reviews'].append(dict(id='iteration34-verification',question='Is the chosen installed-local repair supported by independent metrics, native/Lab and actual preparation recovery UI?',
        disposition='current_change',rationale='Repair correct-control accounting through its comparison owner; retain unchanged native/model evidence and separately observe current web recovery/typography. See PROGRESS.md.',
        property_ids=['I34.P2','I34.P3'],test_ids=[i for i in ids if 'LocalGenerationReview' in i],
        searches=[dict(kind='exact',status='completed',query='I34 PLAN, comparisons, normalizers, native/context/Lab and preparation recovery owners.',
            outcome='Single comparison oracle defect demonstrated; no production projection defect demonstrated.', results=[dict(path='audit/iteration-34-local-generation-20261027/compare.py',classification='change_candidate',reason='Correct-control false alarm counterexample.')]),
            dict(kind='semantic',status='unavailable',query='Preparation generation/resume UI and local provider recovery owners.',reason='Exact-worktree jbcontext reported no index for github.com/jekamas/tangerine.',outcome='Read the known preparation, request and recovery owners directly; no semantic proof.',results=[]),
            dict(kind='jetbrains-index',status='not_applicable',query='Named Python comparison and JS recovery functions; no symbol refactor.',reason='Direct source, independent counterexamples and actual browser/native receipts answer this review.',outcome='No PSI or IDE diagnostic claim.',results=[])]))
    save(BASE/'discovery.json',discovery)
    iterations = json.loads((BASE/'completion-iterations.json').read_text())
    i = next(i for i in iterations['iterations'] if i['iteration']==34)
    i.update(visual_applicable=True,visual_scope='Preparation errors, explicit resume/read recovery, retained inputs, typography and keyboard; controlled HTTP UI only, no inference.',
        selection=str((HERE/'SELECTION.json').relative_to(ROOT)),verify_command_ids=['iteration34-evidence','iteration34-review'])
    save(BASE/'completion-iterations.json',iterations)
    print(json.dumps(dict(selected_cases=len(cases),review_methods=len(methods))))


if __name__ == '__main__': main()
