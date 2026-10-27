"""Record actual local tests once; reuse their exact output on unchanged inputs.

This development adapter never calls a provider. Replay emits the original
unittest transcript, not green lines manufactured from an audit verdict.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'data/iteration-33-diagnostics-20261027/native'
sys.path.insert(0, str(ROOT))
SUITES = {
    'category': ['tests.test_category_validation'],
    'category-evidence': ['tests.test_category_evidence'],
    'diagnostic': ['tests.test_saved_audio_diagnostics', 'tests.test_audio_diagnostics',
                   'tests.test_auditory_protocol', 'tests.test_selected_acoustic',
                   'tests.test_selected_listening_recovery',
                   'tests.test_completion_i26.CompletionI26.test_acoustic_positive',
                   'tests.test_completion_i26.CompletionI26.test_acoustic_negative'],
    'evidence': ['tests.test_saved_audio_acceptance'],
}
OWNERS = ['services/speech/category_validation.py', 'services/speech/diagnostic_models.py',
          'services/speech/diagnostic_context.py', 'services/speech/diagnostic_audio.py',
          'services/speech/diagnostic_runtime.py', 'services/speech/audio.py',
          'audit/iteration-26-acoustic-20261026/observe.py',
          'audit/iteration-26-acoustic-20261026/selection.json',
          'audit/iteration-26-acoustic-20261026/listening.py',
          'audit/iteration-25-qwen-20261026/player.py',
          'audit/iteration-33-diagnostics-20261027/reconcile.py',
          'audit/iteration-33-diagnostics-20261027/native_cases.py',
          'specification/v2/prompts/audio-category-probe-v1.txt',
          'specification/v2/prompts/audio-judge-v1.txt']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from ids(test)
        else:
            yield test.id()


def record(name):
    suite = unittest.defaultTestLoader.loadTestsFromNames(SUITES[name])
    selected = list(ids(suite)); output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT/(name+'.log'); path.write_text(output.getvalue())
    tests = list(dict.fromkeys('tests/'+s.removeprefix('tests.').split('.')[0]+'.py' for s in SUITES[name]))
    packet = dict(suite=name, test_ids=['unittest::'+t for t in selected],
                  tests_run=result.testsRun, failures=len(result.failures)+len(result.errors),
                  skips=len(result.skipped), exit_code=0 if result.wasSuccessful() else 1,
                  stdout=str(path.relative_to(ROOT)), stdout_sha256=digest(path),
                  source_sha256={p:digest(ROOT/p) for p in dict.fromkeys(OWNERS+tests)},
                  saved_input_policy='Original saved WAV/context/reply/measurement inputs were inspected by the actual tests once; no per-playback or runtime requalification.',
                  new_inference_calls=0, new_synthesis_calls=0)
    (OUT/(name+'.json')).write_text(json.dumps(packet, indent=2)+'\n')
    print(json.dumps({k:v for k,v in packet.items() if k not in ['test_ids','source_sha256']}))
    return packet['exit_code']


def errors(packet):
    problems = []
    if packet['exit_code'] or packet['failures'] or packet['skips']:
        problems.append('Original native run failed or skipped cases')
    if packet['tests_run'] != len(packet['test_ids']):
        problems.append('Original native run omitted an exact selected test')
    if digest(ROOT/packet['stdout']) != packet['stdout_sha256']:
        problems.append('Original native transcript changed')
    for path, sha in packet['source_sha256'].items():
        if digest(ROOT/path) != sha:
            problems.append('Changed semantic input: '+path)
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=SUITES, required=True)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    if args.record:
        return record(args.suite)
    packet = json.loads((OUT/(args.suite+'.json')).read_text())
    problems = errors(packet)
    if problems:
        raise SystemExit('\n'.join(problems))
    print('Reused original native unittest output; no test or model was redispatched.')
    print((ROOT/packet['stdout']).read_text(), end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
