"""Finite Qwen comparison through the native private speech HTTP owner.

Import, inspection and playback dispatch nothing. Explicit resume trusts the
saved plan and admitted responses; it never regenerates completed pieces.
"""
import argparse
import base64
import http.client
import io
import json
import logging
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit
import wave

ROOT = Path(__file__).resolve().parents[2]
MATERIAL = ROOT / 'audit/iteration-24-azure-20261026/material.json'
VOICES = {'s1': 'Ryan', 's2': 'Aiden'}
MODEL = 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice'
FOREGROUND_SECONDS = 270


class NativeFailure(ValueError):
    def __init__(self, code, status):
        super().__init__(code)
        self.status = status


def save(path, value):
    raw = json.dumps(value, ensure_ascii=False, indent=2).encode() + b'\n'
    temporary = path.with_suffix(path.suffix + '.partial')
    temporary.write_bytes(raw)
    temporary.replace(path)


def request_plan(material, runtime):
    profile = dict(id='qwen-custom-v1', provider='local_qwen3_tts',
                   adapter_version='qwen-custom-v1', model=MODEL,
                   billing_mode='local', voices=[dict(id=v, locale='en-US') for v in VOICES.values()])
    turns = []
    for variant in ('clean', 'mistakes'):
        for row in material['turns']:
            text = row['canonical_text']
            target = row['target']
            if variant == 'mistakes':
                text = text[:target['start']] + target['respelling'] + text[target['end']:]
            turns.append(dict(id=variant+'-'+row['id'], utterance_id=row['id'],
                              speaker_id=row['speaker_id'], voice_id=VOICES[row['speaker_id']],
                              locale='en-US', gap_after_ms=300,
                              qwen_runtime=dict(runtime),
                              operations=[dict(kind='text', text=text)]))
    return dict(source_preparation=material['source_preparation'], source_material=material,
                runtime=runtime, profile=profile, turns=turns,
                method='phonetic respelling approximation; no exact IPA or accent guarantee')


class NativeSpeech:
    def __init__(self, endpoint, token, output):
        parsed = urlsplit(endpoint)
        if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
            raise ValueError('LOCAL_ENDPOINT_REQUIRED')
        self.host, self.port = parsed.hostname, parsed.port
        self.token, self.output = token, output
        journal = output / 'dispatches.json'
        self.observed = json.loads(journal.read_text()) if journal.exists() else []

    def __call__(self, action, packet, timeout):
        # The socket belongs to this foreground call. Closing it on Ctrl-C or
        # timeout triggers the native server's existing child-group cleanup.
        connection = http.client.HTTPConnection(self.host, self.port, timeout=timeout)
        row = dict(action=action, input=packet, started_at=time.time(),
                   origin='actual private speech HTTP transport')
        self.observed.append(row)
        save(self.output / 'dispatches.json', self.observed)
        try:
            connection.request('POST', '/internal/v1/'+action,
                               body=json.dumps(packet).encode(),
                               headers={'Authorization': 'Bearer '+self.token,
                                        'Content-Type': 'application/json'})
            response = connection.getresponse()
            body = response.read()
            row['http_status'] = response.status
            try:
                result = json.loads(body)
            except (ValueError, UnicodeError):
                result = dict(error='SPEECH_UNAVAILABLE')
            code = result.get('error')
            if not 200 <= response.status < 300 or code:
                row['error'] = code or 'SPEECH_UNAVAILABLE'
                raise NativeFailure(row['error'], response.status)
            row['outcome'] = 'complete'
            return result
        except BaseException as error:
            row.update(outcome='cancelled' if isinstance(error, KeyboardInterrupt) else 'failed',
                       exception_type=type(error).__name__)
            raise
        finally:
            connection.close()
            row['finished_at'] = time.time()
            save(self.output / 'dispatches.json', self.observed)


def state(output, phase, completed, total, message):
    save(output / 'state.json', dict(state=phase, completed_pieces=completed,
                                   total_pieces=total, message=message))


def assemble(pieces, output, variant):
    destination = output / ('qwen-'+variant+'.wav')
    if destination.exists():
        return
    temporary = destination.with_suffix('.wav.partial')
    with wave.open(str(temporary), 'wb') as out:
        out.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        for i, piece in pieces:
            with wave.open(str(output / ('piece-'+str(i)+'.wav')), 'rb') as audio:
                out.writeframes(audio.readframes(audio.getnframes()))
            out.writeframes(b'\0\0' * (piece['gap_after_ms'] * 24))
    temporary.replace(destination)


def recovery(error):
    if isinstance(error, KeyboardInterrupt):
        reason = 'The comparison stopped at your request.'
    elif isinstance(error, (TimeoutError, http.client.RemoteDisconnected)) or str(error) == 'SPEECH_TIMEOUT':
        reason = 'This foreground run could not finish in time.'
    elif str(error) in ('MODEL_SETUP_REQUIRED', 'CAPABILITY_UNAVAILABLE'):
        reason = 'The selected local model or compute setup needs attention.'
    elif isinstance(error, (json.JSONDecodeError, UnicodeError)) or (isinstance(error, OSError) and not isinstance(error, ConnectionError)):
        return 'The comparison files could not be opened or saved. Check the selected local folder, then resume. Existing recordings are unchanged.'
    else:
        reason = 'The local speech service could not finish this run.'
    return reason+' Saved text and completed pieces are retained. Resume explicitly when ready; no provider was switched.'


def execute(plan, output, native, timeout=FOREGROUND_SECONDS, max_pieces=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    # A shorter test-owned deadline is permitted; production never exceeds270s.
    deadline = time.monotonic() + min(timeout, FOREGROUND_SECONDS)
    def remaining():
        value = deadline - time.monotonic()
        if value <= 0:
            raise TimeoutError()
        return value
    def dispatch(action, packet):
        for attempt in range(2):
            try:
                seconds = remaining()
                return native(action, dict(packet, timeout_seconds=seconds), seconds)
            except (ConnectionError, http.client.RemoteDisconnected, NativeFailure) as error:
                transient = not isinstance(error, NativeFailure) or error.status in (502, 503)
                if attempt or not transient:
                    raise
                logging.warning('Local Qwen %s temporarily unavailable: %s; retrying once', action, type(error).__name__)
                state(output, 'rendering', completed, len(pieces), 'Reconnecting to local speech. Saved recordings remain available.')
                time.sleep(min(1, remaining()))
    completed = 0
    pieces = plan.get('pieces', [])
    try:
        if 'pieces' not in plan:
            result = dispatch('plan', dict(profile=plan['profile'], plan=dict(turns=plan['turns'])))
            plan['pieces'] = pieces = result['pieces']
            save(output / 'plan.json', plan)
        completed = sum((output / ('piece-'+str(i)+'.wav')).exists() for i in range(len(pieces)))
        state(output, 'rendering', completed, len(pieces), 'Rendering the remaining pieces. Completed recordings remain available.')
        rendered = 0
        for variant in ('clean', 'mistakes'):
            selected = [(i, p) for i, p in enumerate(pieces) if p['id'].startswith(variant+'-')]
            for i, piece in selected:
                audio = output / ('piece-'+str(i)+'.wav')
                if audio.exists():
                    continue
                response = output / ('piece-'+str(i)+'-response.json')
                if response.exists():
                    result = json.loads(response.read_text())
                else:
                    if max_pieces is not None and rendered >= max_pieces:
                        message = 'This foreground step is saved. Resume to render the next piece; completed recordings remain available.'
                        state(output, 'paused', completed, len(pieces), message)
                        return dict(status='partial', completed_pieces=completed, total_pieces=len(pieces), runtime=plan['runtime'], message=message)
                    result = dispatch('piece', dict(profile=plan['profile'], turn=piece))
                    save(response, result)
                    rendered += 1
                temporary = audio.with_suffix('.wav.partial')
                temporary.write_bytes(base64.b64decode(result['audio_base64']))
                temporary.replace(audio)
                completed += 1
                state(output, 'rendering', completed, len(pieces), 'Rendering the remaining pieces. Completed recordings remain available.')
            assemble(selected, output, variant)
        result = dict(status='complete', variants=['qwen-clean.wav', 'qwen-mistakes.wav'],
                      source_preparation=plan['source_preparation'], completed_pieces=completed,
                      total_pieces=len(pieces), runtime=plan['runtime'], method=plan['method'])
        save(output / 'result.json', result)
        state(output, 'complete', completed, len(pieces), 'Both complete recordings are available.')
        return result
    except (Exception, KeyboardInterrupt) as error:
        logging.warning('Local Qwen comparison stopped: %s', type(error).__name__)
        try:
            state(output, 'paused', completed, len(pieces), recovery(error))
        except OSError as save_error:
            logging.warning('Local Qwen progress could not be saved: %s', type(save_error).__name__)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8091')
    parser.add_argument('--device', choices=['cpu', 'mps'], required=True)
    parser.add_argument('--dtype', choices=['float32', 'float16'], default='float32')
    parser.add_argument('--max-pieces', type=int, default=1,
                        help='New pieces per foreground step (default: one); saved pieces are reused.')
    args = parser.parse_args()
    try:
        args.out.mkdir(parents=True, exist_ok=True)
        saved = args.out / 'plan.json'
        plan = json.loads(saved.read_text()) if saved.exists() else request_plan(
            json.loads(MATERIAL.read_text()), dict(device=args.device, dtype=args.dtype))
        if not saved.exists():
            save(saved, plan)
        token = os.environ['SPEECH_INTERNAL_TOKEN']
        result = execute(plan, args.out, NativeSpeech(args.endpoint, token, args.out), max_pieces=max(1, args.max_pieces))
        print(json.dumps(result))
        return 0
    except (Exception, KeyboardInterrupt) as error:
        logging.warning('Local Qwen command stopped: %s', type(error).__name__)
        print(json.dumps(dict(status='paused', message=recovery(error))))
        return 130 if isinstance(error, KeyboardInterrupt) else 1


if __name__ == '__main__':
    sys.exit(main())
