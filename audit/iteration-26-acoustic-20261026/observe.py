"""Finite selected saved-audio observations through the native diagnostic HTTP owner.

Import/read/compare/export dispatch nothing. Each explicit case freezes its
request before one foreground call; an interrupted request is never redispatched.
"""
import argparse
import base64
import http.client
import json
import logging
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'services/speech'))
from category_validation import blind_input, compare_probe, make_probe


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.partial')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(path)


def prepare(case_id):
    selected = json.loads((HERE/'selection.json').read_text())
    case = next(c for c in selected['cases'] if c['id'] == case_id)
    original = ROOT/'audit/category-realization-20261025'
    fixture = next(c for c in json.loads((original/'FIXTURES.json').read_text())['fixtures']
                   if c['taxonomy_id'] == case['category_id'])
    record = json.loads((ROOT/'data/category-realization-20261025/recordings'/case['category_id']/'index.json').read_text())
    fixture = {**fixture, **record.get('fixture_override', {}),
               'context': case['context'], 'control_context': case['control_context'],
               'question': case['question'], 'control_question': case['question']}
    paths = dict(record['paths'])
    if case.get('acceptable_from'):
        paths['acceptable'] = paths[case['acceptable_from']]
    previous = ROOT/'data/category-realization-20261025/observations-gemini31'/case['category_id']/'request.json'
    profile = json.loads(previous.read_text())['profile']
    probe = make_probe(fixture, paths, {**record['binding'], 'judge': profile}, 'I26-'+case_id)
    audio = [base64.b64encode((ROOT/r['audio_path']).read_bytes()).decode() for r in probe['withheld']]
    packet = dict(action='measure', method_id='gemini-audio-v1', profile=profile,
                  prompt=(ROOT/'specification/v2/prompts/audio-category-probe-v1.txt').read_text(),
                  input=blind_input(probe), audio_base64=audio[0], additional_audio_base64=audio[1:],
                  timeout_seconds=260)
    return dict(id=case_id, probe=probe, packet=packet, physical=record.get('physical'), repair=case['repair'])


class NativeDiagnostic:
    def __init__(self, endpoint, token, journal):
        parsed = urlsplit(endpoint)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
            raise ValueError('LOCAL_ENDPOINT_REQUIRED')
        self.host, self.port, self.token, self.journal = parsed.hostname, parsed.port, token, journal

    def __call__(self, packet):
        connection = http.client.HTTPConnection(self.host, self.port, timeout=269)
        observation = dict(origin='actual native diagnostic HTTP dispatch', started_at=time.time(),
                           action='measure', input=packet)
        save(self.journal, observation)
        try:
            connection.request('POST', '/internal/v1/measure', json.dumps(packet).encode(),
                               {'Authorization': 'Bearer '+self.token, 'Content-Type': 'application/json'})
            response = connection.getresponse()
            result = json.loads(response.read())
            observation.update(http_status=response.status,
                               outcome='failed' if response.status != 200 or result.get('error') else 'complete')
            return result
        except (Exception, KeyboardInterrupt) as error:
            observation.update(outcome='cancelled' if isinstance(error, KeyboardInterrupt) else 'failed',
                               exception_type=type(error).__name__)
            raise
        finally:
            connection.close()
            observation['finished_at'] = time.time()
            save(self.journal, observation)


def observe_case(case_id, output, dispatch):
    directory = Path(output)/case_id
    result = directory/'comparison.json'
    if result.exists():
        return json.loads(result.read_text())
    snapshot = directory/'frozen.json'
    response = directory/'response.json'
    if snapshot.exists():
        frozen = json.loads(snapshot.read_text())
        if not response.exists():
            return dict(id=case_id, audio_confirmation='not_run', error='INTERRUPTED_OBSERVATION',
                        message='The earlier observation has no saved result. Saved audio remains available; use a separately named experiment for another explicit attempt.')
    else:
        frozen = prepare(case_id)
        save(snapshot, frozen)
        try:
            save(response, dispatch(frozen['packet']))
        except (Exception, KeyboardInterrupt) as error:
            logging.warning('Selected acoustic observation interrupted: %s', type(error).__name__)
            raise
    actual = json.loads(response.read_text())
    if frozen.get('physical'):
        actual = {**actual, 'physical': frozen['physical']}
    comparison = compare_probe(frozen['probe'], actual)
    comparison.update(id=case_id, error=actual.get('error'), repair=frozen['repair'])
    save(result, comparison)
    return comparison


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=[c['id'] for c in json.loads((HERE/'selection.json').read_text())['cases']], required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8092')
    args = parser.parse_args()
    try:
        native = NativeDiagnostic(args.endpoint, os.environ['SPEECH_INTERNAL_TOKEN'], args.out/args.case/'dispatch.json')
        result = observe_case(args.case, args.out, native)
        print(json.dumps(dict(case=args.case, observation=result['audio_confirmation'],
                              message='Saved recordings and this observation remain available. Model agreement is limited to the selected example.')))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        logging.warning('Selected acoustic command stopped: %s', type(error).__name__)
        print('The selected observation could not finish. Saved audio and any completed results remain available; inspect the retained local diagnostic before a new explicit experiment.')
        return 130 if isinstance(error, KeyboardInterrupt) else 1


if __name__ == '__main__':
    sys.exit(main())
