"""Independent literal expectations; local model replies are constructed here.

The real comparison/planning/storage and private HTTP child owners execute.
Only model output/timing is substituted; no acoustic quality claim follows.
"""
import base64
import contextlib
import copy
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/speech'))
import audio
import backends
import qwen_runtime
import server


def load(name):
    spec = importlib.util.spec_from_file_location('qwen_comparison_'+name, ROOT/('audit/iteration-25-qwen-20261026/'+name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


comparison, player = load('compare'), load('player')


class QwenComparison(unittest.TestCase):
    def plan(self):
        plan = comparison.request_plan(json.loads(comparison.MATERIAL.read_text()), dict(device='cpu', dtype='float32'))
        plan['pieces'] = backends.plan(plan['profile'], dict(turns=plan['turns']))['pieces']
        return plan

    def reply(self, packet):
        # Distinct independently known sample per piece, not candidate speech.
        pcm = b'\0\x10' * 2400
        return dict(audio_base64=base64.b64encode(audio.wav_bytes(pcm)).decode(),
                    receipt=dict(origin='constructed local model output', input=packet))

    def test_plan_targets_and_voices_positive(self):
        plan = self.plan()
        self.assertEqual(['Ryan', 'Aiden', 'Ryan', 'Aiden']*2, [t['voice_id'] for t in plan['turns']])
        self.assertEqual('local', plan['profile']['billing_mode'])
        replacements = [('choices', 'shoy-siz'), ('companies', 'kum-PAN-eez'), ('another', 'uh-NUH-zer'), ('Collision', 'KAH-li-zhun')]
        for i, (old, new) in enumerate(replacements):
            clean, changed = plan['turns'][i], plan['turns'][i+4]
            original = clean['operations'][0]['text']
            self.assertEqual(original.replace(old, new, 1), changed['operations'][0]['text'])
        for turn in plan['turns']:
            pieces = [p for p in plan['pieces'] if p['id'] == turn['id']]
            self.assertEqual(turn['operations'][0]['text'], ''.join(p['operations'][0]['text'] for p in pieces))
            self.assertEqual([0]*(len(pieces)-1)+[300], [p['gap_after_ms'] for p in pieces])
            self.assertTrue(all(p['qwen_runtime'] == dict(device='cpu', dtype='float32') for p in pieces))

    def test_plan_freezes_default_runtime_positive(self):
        plan = self.plan()
        turn = copy.deepcopy(plan['turns'][0])
        turn.pop('qwen_runtime')
        with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE='cpu', TANGERINE_QWEN_DTYPE='float32')):
            original = backends.plan(plan['profile'], dict(turns=[turn]))['pieces']
        self.assertTrue(all(p['qwen_runtime'] == dict(device='cpu', dtype='float32') for p in original))
        with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE='mps', TANGERINE_QWEN_DTYPE='float16')):
            resumed = backends.plan(plan['profile'], dict(turns=original))['pieces']
        self.assertTrue(all(p['qwen_runtime'] == dict(device='cpu', dtype='float32') for p in resumed))

    def test_complete_pair_assembly_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, plan = Path(tmp), self.plan()
            calls = []
            def native(action, packet, timeout):
                self.assertEqual('piece', action)
                self.assertGreater(timeout, 0)
                self.assertLessEqual(timeout, 270)
                calls.append(packet)
                return self.reply(packet)
            result = comparison.execute(plan, out, native)
            self.assertEqual(('complete', len(plan['pieces'])), (result['status'], len(calls)))
            for variant in ['clean', 'mistakes']:
                pieces = [p for p in plan['pieces'] if p['id'].startswith(variant+'-')]
                with wave.open(str(out/('qwen-'+variant+'.wav'))) as recording:
                    self.assertEqual((1, 2, 24000), (recording.getnchannels(), recording.getsampwidth(), recording.getframerate()))
                    self.assertEqual(2400*len(pieces)+4*7200, recording.getnframes())
                    expected = b''.join(b'\0\x10'*2400+b'\0\0'*(p['gap_after_ms']*24) for p in pieces)
                    self.assertEqual(expected, recording.readframes(recording.getnframes()))
            self.assertEqual('complete', json.loads((out/'state.json').read_text())['state'])

    def test_resume_saved_responses_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, plan = Path(tmp), self.plan()
            comparison.save(out/'piece-0-response.json', self.reply({'origin': 'previous admitted response'}))
            count = 0
            def native(action, packet, timeout):
                nonlocal count
                count += 1
                return self.reply(packet)
            comparison.execute(plan, out, native)
            self.assertEqual(len(plan['pieces'])-1, count)
            with patch.object(comparison, 'NativeSpeech', side_effect=AssertionError('replay must make no model call')):
                comparison.execute(plan, out, lambda *a: self.fail('unexpected inference'))

    def test_partial_cancel_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, plan, count = Path(tmp), self.plan(), 0
            def native(action, packet, timeout):
                nonlocal count
                count += 1
                if count == 3:
                    raise KeyboardInterrupt()
                return self.reply(packet)
            with self.assertRaises(KeyboardInterrupt):
                comparison.execute(plan, out, native)
            self.assertEqual(2, len(list(out.glob('piece-*.wav'))))
            self.assertFalse((out/'result.json').exists())
            self.assertFalse((out/'qwen-clean.wav').exists())
            state = json.loads((out/'state.json').read_text())
            self.assertEqual(('paused', 2), (state['state'], state['completed_pieces']))
            self.assertIn('stopped at your request', state['message'])
            comparison.execute(plan, out, lambda a, p, t: self.reply(p))
            self.assertEqual('complete', json.loads((out/'result.json').read_text())['status'])

    def test_reference_survives_later_failure_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, plan = Path(tmp), self.plan()
            def native(action, packet, timeout):
                if packet['turn']['id'].startswith('mistakes-'):
                    raise ValueError('SYNTHESIS_FAILED')
                return self.reply(packet)
            with self.assertRaisesRegex(ValueError, 'SYNTHESIS_FAILED'):
                comparison.execute(plan, out, native)
            page = player.page(out, 'controlled')
            self.assertIn('src="/qwen-clean.wav"', page)
            self.assertNotIn('src="/qwen-mistakes.wav"', page)
            self.assertNotIn('Both complete recordings are available.', page)
            self.assertNotIn('SYNTHESIS_FAILED', page)

    def test_foreground_deadline_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, plan = Path(tmp), self.plan()
            clock = iter([0, 271])
            with patch.object(comparison.time, 'monotonic', side_effect=lambda: next(clock)):
                with self.assertRaises(TimeoutError):
                    comparison.execute(plan, out, lambda *a: self.fail('expired invocation dispatched'), timeout=999)
            self.assertFalse((out/'result.json').exists())
            self.assertIn('could not finish in time', json.loads((out/'state.json').read_text())['message'])

    def test_preview_is_incomplete_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out/'qwen-native-partial-preview.wav').write_bytes(audio.wav_bytes(b'\0\x10'*134400))
            page = player.page(out)
            self.assertNotIn('<audio ', page)
            self.assertIn('comparison is incomplete', page)
            self.assertNotIn('Both complete recordings are available.', page)

    def test_runtime_selection_positive(self):
        torch = types.SimpleNamespace(backends=types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: True)))
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(dict(device='cpu', dtype='float32', attention_implementation='eager'), qwen_runtime.configuration(torch))
        with patch.dict(os.environ, {'TANGERINE_QWEN_DEVICE': 'mps', 'TANGERINE_QWEN_DTYPE': 'float16'}):
            self.assertEqual(dict(device='mps', dtype='float16', attention_implementation='eager'), qwen_runtime.configuration(torch))

    def test_runtime_no_fallback_negative(self):
        torch = types.SimpleNamespace(backends=types.SimpleNamespace(mps=types.SimpleNamespace(is_available=lambda: False)))
        for settings in [{'TANGERINE_QWEN_DEVICE': 'mps'}, {'TANGERINE_QWEN_DEVICE': 'auto'}, {'TANGERINE_QWEN_DTYPE': 'unavailable'}]:
            with self.subTest(settings=settings), patch.dict(os.environ, settings, clear=True):
                with self.assertRaisesRegex(ValueError, 'CAPABILITY_UNAVAILABLE'):
                    qwen_runtime.configuration(torch)

    def test_player_private_routes_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            listener = player.ThreadingHTTPServer(('127.0.0.1', 0), player.handler(Path(tmp)))
            thread = threading.Thread(target=listener.serve_forever, daemon=True)
            thread.start()
            try:
                for path in ['/plan.json', '/dispatches.json', '/../../data/config/runtime.env']:
                    conn = http.client.HTTPConnection('127.0.0.1', listener.server_port)
                    conn.request('GET', path)
                    response = conn.getresponse()
                    self.assertEqual(404, response.status)
                    response.read()
                    conn.close()
            finally:
                listener.shutdown(); listener.server_close(); thread.join()

    def test_cli_human_failure_negative(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, dict(SPEECH_INTERNAL_TOKEN='fixture-token')):
            stdout = io.StringIO()
            with patch.object(sys, 'argv', ['compare', '--out', tmp, '--device', 'cpu']), \
                    patch.object(comparison.NativeSpeech, '__call__', side_effect=ConnectionError('private-canary')), \
                    contextlib.redirect_stdout(stdout):
                code = comparison.main()
            self.assertEqual(1, code)
            self.assertIn('retained', stdout.getvalue())
            self.assertNotIn('private-canary', stdout.getvalue())
            self.assertNotIn('Traceback', stdout.getvalue())
            self.assertEqual('paused', json.loads((Path(tmp)/'state.json').read_text())['state'])
            self.assertTrue((Path(tmp)/'plan.json').exists())


class QwenForeground(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        # Replace the local model import/timing only. Real backends.py and the
        # real HTTP/process-group owner still execute and must release the child.
        (root/'qwen_tts.py').write_text('import time\ntime.sleep(90)\n')
        self.env = patch.dict(os.environ, dict(SPEECH_INTERNAL_TOKEN='owned-qwen-token', PYTHONPATH=str(root)))
        self.env.start()
        self.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.processes = []
        native = server.subprocess.Popen
        def observe(*args, **kwargs):
            p = native(*args, **kwargs)
            self.processes.append(p)
            return p
        self.popen = patch.object(server.subprocess, 'Popen', side_effect=observe)
        self.popen.start()

    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); self.thread.join()
        self.popen.stop(); self.env.stop(); self.tmp.cleanup()

    def packet(self, timeout):
        plan = comparison.request_plan(json.loads(comparison.MATERIAL.read_text()), dict(device='cpu', dtype='float32'))
        return dict(profile=plan['profile'], turn=plan['turns'][0], timeout_seconds=timeout)

    def test_native_deadline_releases_child_negative(self):
        conn = http.client.HTTPConnection('127.0.0.1', self.http.server_port, timeout=5)
        try:
            conn.request('POST', '/internal/v1/piece', json.dumps(self.packet(1)), {'Content-Type': 'application/json', 'Authorization': 'Bearer owned-qwen-token'})
            response = conn.getresponse()
            self.assertEqual((504, {'error': 'SPEECH_TIMEOUT'}), (response.status, json.loads(response.read())))
            self.assertEqual(1, len(self.processes))
            self.assertEqual(-9, self.processes[0].wait(timeout=5))
        finally:
            conn.close()

    def test_native_disconnect_releases_child_negative(self):
        body = json.dumps(self.packet(270)).encode()
        conn = socket.create_connection(('127.0.0.1', self.http.server_port))
        conn.sendall(b'POST /internal/v1/piece HTTP/1.1\r\nHost: local\r\nAuthorization: Bearer owned-qwen-token\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body)
        try:
            for _ in range(100):
                if self.processes:
                    break
                time.sleep(.01)
            self.assertEqual(1, len(self.processes))
        finally:
            conn.close()
        self.assertEqual(-9, self.processes[0].wait(timeout=5))

    def test_client_timeout_closes_native_child_negative(self):
        native = comparison.NativeSpeech('http://127.0.0.1:'+str(self.http.server_port), 'owned-qwen-token', Path(self.tmp.name))
        with self.assertRaises(TimeoutError):
            native('piece', self.packet(270), .2)
        self.assertEqual(1, len(self.processes))
        self.assertEqual(-9, self.processes[0].wait(timeout=5))
        facts = json.loads((Path(self.tmp.name)/'dispatches.json').read_text())
        self.assertEqual('failed', facts[0]['outcome'])
        self.assertEqual('TimeoutError', facts[0]['exception_type'])
        self.assertNotIn('owned-qwen-token', json.dumps(facts))

    def test_native_deadline_is_capped_negative(self):
        ticks = iter([0, 270.5])
        clock = types.SimpleNamespace(monotonic=lambda: next(ticks))
        conn = http.client.HTTPConnection('127.0.0.1', self.http.server_port, timeout=5)
        try:
            with patch.object(server, 'time', clock):
                conn.request('POST', '/internal/v1/piece', json.dumps(self.packet(999)), {'Content-Type': 'application/json', 'Authorization': 'Bearer owned-qwen-token'})
                response = conn.getresponse()
                self.assertEqual((504, {'error': 'SPEECH_TIMEOUT'}), (response.status, json.loads(response.read())))
            self.assertEqual(-9, self.processes[0].wait(timeout=5))
        finally:
            conn.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
