"""Production speech owner against a test-owned HTTP provider, zero hosted calls."""
import base64
import copy
import json
import math
import os
from pathlib import Path
import struct
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services/speech'))
import backends
from audio import wav_bytes


def profile(endpoint='http://127.0.0.1:1', model='eleven_flash_v2'):
    return dict(id='elevenlabs-i22', provider='elevenlabs', adapter_version='elevenlabs-dictionary-v1',
                endpoint=endpoint, model=model, billing_mode='free_tier', overage_disabled=True,
                capabilities=['plain_text', 'ipa', 'prosody', 'timed_pause', 'multi_turn'],
                voices=[dict(id='Sarah', locale='en-US'), dict(id='George', locale='en-GB')],
                voice_settings=dict(stability=.5, similarity_boost=.75, speed=1))


def turn(text='I think we should think again.', speaker='s1', voice='Sarah', locale='en-US'):
    return dict(id='u1' if speaker == 's1' else 'u2', utterance_id='u1' if speaker == 's1' else 'u2',
                speaker_id=speaker, voice_id=voice, locale=locale, gap_after_ms=250,
                operations=[dict(kind='text', text=text)])


def edited():
    t = turn()
    t['acoustic_edits'] = [dict(unit_id='target', taxonomy_id='pronunciation.segmental.th_fronting',
                               controller='phone_pair', scope=dict(start=18, end=23),
                               parameters=dict(reference_ipa='θɪŋk', mutated_ipa='sɪŋk'))]
    return t


class ElevenLabsDictionary(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.bad_dictionary = None
        self.status = None
        self.sample = wav_bytes(b''.join(struct.pack('<h', round(7000 * math.sin(2 * math.pi * i / 120)))
                                         for i in range(2400)))
        case = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = self.rfile.read(int(self.headers['Content-Length']))
                case.calls.append(dict(path=self.path, body=body, content_type=self.headers['Content-Type'],
                                       key=self.headers.get('xi-api-key')))
                if case.status:
                    self.send_response(case.status)
                    self.end_headers()
                    self.wfile.write(b'{"detail":"controlled provider failure"}')
                elif 'add-from-file' in self.path:
                    n = len([c for c in case.calls if 'add-from-file' in c['path']])
                    value = case.bad_dictionary if case.bad_dictionary is not None else dict(id='dict-' + str(n), version_id='version-' + str(n))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps(value).encode())
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(case.sample)

        self.http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.p = profile('http://127.0.0.1:' + str(self.http.server_port))
        self.env = patch.dict(os.environ, {'ELEVENLABS_API_KEY': 'owned-fixture-key'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)

    def planned(self, t=None):
        return backends.plan(self.p, dict(turns=[t or edited(), turn('I think so.', 's2', 'George', 'en-GB')]))

    def test_scope_positive(self):
        result = self.planned()
        pieces = result['pieces']
        self.assertEqual(['I think we should ', 'think', ' again.', 'I think so.'],
                         [x['operations'][0]['text'] for x in pieces])
        self.assertEqual(['Sarah', 'Sarah', 'Sarah', 'George'], [x['voice_id'] for x in pieces])
        self.assertEqual([0, 0, 250, 250], [x['gap_after_ms'] for x in pieces])
        self.assertEqual([1], [i for i, x in enumerate(pieces) if x.get('pronunciation_dictionary_locators')])
        self.assertEqual(dict(start=18, end=23), pieces[1]['surface_scope'])
        self.assertEqual(2, len(self.calls))
        for c, expected in zip(self.calls, ['θɪŋk', 'sɪŋk']):
            self.assertEqual('/v1/pronunciation-dictionaries/add-from-file', c['path'])
            self.assertIn('multipart/form-data; boundary=', c['content_type'])
            self.assertIn(b'<grapheme>think</grapheme>', c['body'])
            self.assertIn(('<phoneme>' + expected + '</phoneme>').encode(), c['body'])
            self.assertEqual('owned-fixture-key', c['key'])

    def test_dictionary_transport_positive(self):
        piece = self.planned()['pieces'][1]
        result = backends.render(self.p, piece)
        tts = [c for c in self.calls if 'text-to-speech' in c['path']]
        self.assertEqual(2, len(tts))
        for c, n in zip(tts, [1, 2]):
            body = json.loads(c['body'])
            self.assertEqual('eleven_flash_v2', body['model_id'])
            self.assertEqual('think', body['text'])
            self.assertEqual([dict(pronunciation_dictionary_id='dict-' + str(n), version_id='version-' + str(n))], body['pronunciation_dictionary_locators'])
        self.assertEqual(2400, result['sample_count'])
        self.assertIn('paired_mutation', result['receipt']['native'])
        self.assertNotIn('owned-fixture-key', json.dumps(result))

    def test_dialogue_transport_positive(self):
        self.p['model'] = 'eleven_v4'
        piece = self.planned()['pieces'][1]
        backends.render(self.p, piece)
        calls = [c for c in self.calls if 'text-to-dialogue' in c['path']]
        self.assertEqual(2, len(calls))
        body = json.loads(calls[1]['body'])
        self.assertEqual([dict(text='think', voice_id='Sarah')], body['inputs'])
        self.assertEqual('eleven_v4', body['model_id'])
        self.assertNotIn('voice_settings', body)
        self.assertEqual('dict-2', body['pronunciation_dictionary_locators'][0]['pronunciation_dictionary_id'])

    def test_saved_bindings_positive(self):
        # Serialization models accepted plan transport; the native test owns DB resume.
        piece = json.loads(json.dumps(self.planned()['pieces'][1]))
        self.bad_dictionary = {'id': 'new-invalid-version'}
        backends.render(self.p, piece)
        self.assertEqual(2, len([c for c in self.calls if 'add-from-file' in c['path']]))
        self.assertEqual(2, len([c for c in self.calls if 'text-to-speech' in c['path']]))

    def test_dictionary_admission_negative(self):
        for bad in [dict(id='only-id'), dict(id='', version_id='v'), dict(id='d', version_id=None),
                    dict(id=['d'], version_id='v'), []]:
            with self.subTest(bad=bad):
                self.calls.clear()
                self.bad_dictionary = bad
                with self.assertRaisesRegex(ValueError, '^PROVIDER_FAILED$'):
                    self.planned()
                self.assertEqual(1, len(self.calls))
                self.assertIn('add-from-file', self.calls[0]['path'])

    def test_unsupported_model_negative(self):
        for model in ['eleven_flash_v2_5', 'eleven_multilingual_v2']:
            self.p['model'] = model
            with self.assertRaisesRegex(ValueError, '^CAPABILITY_UNAVAILABLE$'):
                self.planned()
        self.assertEqual([], self.calls)

    def test_quota_negative(self):
        self.status = 429
        with self.assertRaisesRegex(ValueError, '^PROVIDER_QUOTA$'):
            self.planned()
        self.assertEqual(1, len(self.calls))
        self.status = 400
        with self.assertRaisesRegex(ValueError, '^PROVIDER_FAILED$'):
            self.planned()
        self.assertEqual(2, len(self.calls))

    def test_text_only_no_dictionary_positive(self):
        result = backends.plan(self.p, dict(turns=[turn()]))
        backends.render(self.p, result['pieces'][0])
        self.assertEqual(1, len(self.calls))
        self.assertNotIn('pronunciation_dictionary_locators', json.loads(self.calls[0]['body']))

    def test_partial_word_negative(self):
        t = edited()
        t['acoustic_edits'][0]['scope']['start'] = 19
        with self.assertRaisesRegex(ValueError, '^ALIGNMENT_UNAVAILABLE$'):
            self.planned(t)
        self.assertEqual([], self.calls)

    def test_unsupported_phone_timing_negative(self):
        t = edited()
        t['acoustic_edits'][0].update(controller='vowel_duration', parameters=dict(duration_ratio=1.4, phone_start=1, phone_end=2))
        with self.assertRaisesRegex(ValueError, '^CAPABILITY_UNAVAILABLE$'):
            self.planned(t)
        self.assertEqual([], self.calls)

    def test_xml_case_sensitive_positive(self):
        t = edited()
        t['operations'][0]['text'] = 'I think we should Think again.'
        self.planned(t)
        self.assertIn(b'<grapheme>Think</grapheme>', self.calls[0]['body'])
        self.assertNotIn(b'<grapheme>think</grapheme>', self.calls[0]['body'])

    def test_long_context_coordinates_positive(self):
        t = turn('I think ' * 400)
        result = backends.plan(self.p, dict(turns=[t, edited()]))
        context = [x for x in result['pieces'] if not x.get('acoustic_edits')][:2]
        self.assertEqual(2, len(context))
        for left, right in zip(context, context[1:]):
            self.assertEqual(left['surface_scope']['end'], right['surface_scope']['start'])
        self.assertEqual(0, context[0]['surface_scope']['start'])
        self.assertEqual(3200, context[-1]['surface_scope']['end'])

    def test_hosted_interval_basis_positive(self):
        from acoustic_runtime import resolve_acoustic
        piece = self.planned()['pieces'][1]
        result = backends.render(self.p, piece)
        out = resolve_acoustic(dict(audio_base64=result['audio_base64'], turn=piece,
                                    native=result['receipt']['native'], piece_id='owned-piece'))
        self.assertEqual('generated_piece_interval_24000', out['alignment_basis'])
        self.assertEqual(dict(start=0, end=2400), out['steps'][0]['source_interval'])
        self.assertNotIn('kokoro', out['alignment_basis'])

    def test_decoder_basis_positive(self):
        from acoustic_runtime import resolve_acoustic
        t = edited()
        native = {'decoder': [{'timing_basis': 'kokoro_decoder_600_samples_v1'}]}
        out = resolve_acoustic(dict(audio_base64=base64.b64encode(self.sample).decode(),
                                    turn=t, native=native, piece_id='owned-decoder'))
        self.assertEqual('kokoro_decoder_600_samples_v1', out['alignment_basis'])
        self.assertEqual(dict(start=0, end=2400), out['steps'][0]['source_interval'])

    def test_phone_pair_coordinates_positive(self):
        # Native recipes identify the changed phone as well as supplying the
        # complete reference/contrast IPA. A whole-word PLS needs no word timing.
        t = edited()
        t['acoustic_edits'][0]['parameters'].update(phone_start=0, phone_end=1)
        result = self.planned(t)
        self.assertEqual('think', result['pieces'][1]['operations'][0]['text'])
        self.assertEqual(2, len(self.calls))
        self.assertEqual(0, result['pieces'][1]['acoustic_edits'][0]['parameters']['phone_start'])

    def test_billing_negative(self):
        self.p['billing_mode'] = 'metered'
        with self.assertRaisesRegex(ValueError, '^PAID_USE_FORBIDDEN$'):
            self.planned()
        self.assertEqual([], self.calls)


if __name__ == '__main__':
    unittest.main()
