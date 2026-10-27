"""Reconcile I33 apply receipts with only the verification-invalidated tests.

Original outputs and hashes stay unchanged. The two changed owners invalidate
their callers, not unrelated transport, storage or saved physical tests. This
adapter is development evidence only, never a playback or learner gate.
"""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'data/iteration-33-diagnostics-20261027/native'
OUT=ROOT/'data/iteration-33-verification-20261027'
ENTRY='9efdb13a4a0c2a82dcffc90a9715f94d20359a5f'
CHANGED={'services/speech/category_validation.py',
         'audit/iteration-26-acoustic-20261026/listening.py'}
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('i33_apply_native',Path(__file__).with_name('native_cases.py'))
apply=importlib.util.module_from_spec(spec);spec.loader.exec_module(apply)


def original_packets():
    return [json.loads((OLD/(name+'.json')).read_text())
            for name in ['category','category-evidence','diagnostic']]


def invalidated(identity):
    """Exact traced callers of make/compare_probe or the changed listening page."""
    if '.CategoryComparisons.' in identity:return True
    if '.CategoryValidation.' in identity:
        source=ast.parse((ROOT/'tests/test_category_validation.py').read_text())
        cls=next(c for c in source.body if isinstance(c,ast.ClassDef) and c.name=='CategoryValidation')
        method=next(m for m in cls.body if isinstance(m,ast.FunctionDef) and m.name==identity.rsplit('.',1)[1])
        return any(isinstance(c,ast.Call) and ast.unparse(c.func) in
                   ['probe','make_probe','compare_probe'] for c in ast.walk(method))
    if '.CategoryEvidence.' in identity:return identity.endswith('.test_blind_actual_observation_positive')
    if '.SavedAudioDiagnostics.' in identity:
        return identity.rsplit('.',1)[1] in [
            'test_ambiguous_fixture_positive','test_judge_support_cannot_resolve_ambiguous_fixture_negative',
            'test_correct_variants_positive','test_valid_question_false_alarm_negative',
            'test_failed_observation_cannot_confirm_negative',
            'test_physical_change_does_not_make_valid_contour_wrong_negative']
    # RetainedAudioDiagnostics.setUpClass rebuilds future fixture expectations.
    if any(c in identity for c in ['.RetainedAudioDiagnostics.','.SelectedListening.',
                                   '.SelectedListeningRecovery.']):return True
    if '.SelectedAcoustic.' in identity:
        return not identity.endswith(('.test_native_http_failure_retention_negative',
                                      '.test_remote_endpoint_rejected_negative'))
    return identity=='unittest::tests.test_completion_i26.CompletionI26.test_acoustic_positive'


def selected_ids():
    return [t for p in original_packets() for t in p['test_ids'] if invalidated(t)]


def record():
    names=[t.removeprefix('unittest::') for t in selected_ids()]
    suite=unittest.defaultTestLoader.loadTestsFromNames(names);stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    path=OUT/'native-invalidated.log';path.write_text(stream.getvalue())
    sources=list(dict.fromkeys(apply.OWNERS+[
        'tests/'+n.split('.')[1]+'.py' for n in names]+[
        str(Path(__file__).relative_to(ROOT))]))
    packet=dict(test_ids=['unittest::'+n for n in names],tests_run=result.testsRun,
                failures=len(result.failures)+len(result.errors),skips=len(result.skipped),
                exit_code=0 if result.wasSuccessful() else 1,stdout=str(path.relative_to(ROOT)),
                stdout_sha256=apply.digest(path),source_sha256={p:apply.digest(ROOT/p) for p in sources},
                new_inference_calls=0,new_synthesis_calls=0,
                invalidation='Changed fresh probe/comparison and saved-listening page; exact callers selected. Original unrelated greens retained.')
    (OUT/'native-invalidated.json').write_text(json.dumps(packet,indent=2)+'\n')
    print(json.dumps({k:v for k,v in packet.items() if k not in ['test_ids','source_sha256']}))
    return packet['exit_code']


def original_errors(packet):
    """Original observation checks, retaining the exact original output."""
    problems=[]
    if packet['exit_code'] or packet['failures'] or packet['skips']:
        problems.append('Original native run failed or skipped cases')
    if packet['tests_run']!=len(packet['test_ids']):
        problems.append('Original native run omitted an exact selected test')
    if apply.digest(ROOT/packet['stdout'])!=packet['stdout_sha256']:
        problems.append('Original native transcript changed')
    return problems


def errors(packet):
    problems=original_errors(packet)
    for path,sha in packet['source_sha256'].items():
        if path not in CHANGED and apply.digest(ROOT/path)!=sha:
            problems.append('Changed semantic input: '+path)
    current=json.loads((OUT/'native-invalidated.json').read_text())
    problems.extend(apply.errors(current))
    required={t for t in packet['test_ids'] if invalidated(t)}
    if not required<=set(current['test_ids']):problems.append('Missing invalidated native observation')
    return problems


def observations():
    sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
    from requirement_tests import parse_unittest_events
    current=json.loads((OUT/'native-invalidated.json').read_text())
    fresh=parse_unittest_events((ROOT/current['stdout']).read_text());rows=[]
    for packet in original_packets():
        if errors(packet):raise AssertionError(errors(packet))
        old=parse_unittest_events((ROOT/packet['stdout']).read_text())
        for identity in packet['test_ids']:
            replaced=invalidated(identity)
            rows.append(dict(test_id=identity,status=(fresh if replaced else old)[identity],
                             receipt=current['stdout'] if replaced else packet['stdout'],
                             disposition='reobserved_changed_owner' if replaced else 'retained_unchanged_dependency',
                             nondependency_scope=None if replaced else 'Changed make/compare_probe and page are not called; unchanged blind_input/coverage/cache symbols and other owner/test bindings retain the original receipt.'))
    return rows


if __name__=='__main__':
    if '--record' in sys.argv:sys.exit(record())
    rows=observations()
    (OUT/'native-reuse.json').write_text(json.dumps(dict(entry=ENTRY,observations=rows,
        reobserved=sum(r['disposition']=='reobserved_changed_owner' for r in rows),
        reused=sum(r['disposition']=='retained_unchanged_dependency' for r in rows),
        original_hashes_preserved=True),indent=2)+'\n')
    print(json.dumps(dict(total=len(rows),reobserved=sum(invalidated(r['test_id']) for r in rows))))
