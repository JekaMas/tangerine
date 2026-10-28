"""I25 retained real observations and independent evidence counterexamples.

These readers dispatch no model. Missing actual Qwen/audio/browser evidence is
skipped and therefore prevents iteration acceptance; it is never fixture green.
"""
import base64
import io
import json
from pathlib import Path
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/iteration-25-qwen-20261026'
FOLLOWUP = ROOT/'data/completion-leftovers-20261028'
AUDIT = ROOT/'audit/iteration-25-qwen-20261026'
SOURCE = '9dbf8c95-51a3-4c0f-9395-b3a77a824d22'


def review_errors(packet):
    errors = []
    for dimension in ['ui_ux', 'typography', 'evidence']:
        if not packet.get(dimension, {}).get('observations'):
            errors.append(dimension+' omitted')
    if packet.get('source_preparation') != SOURCE:
        errors.append('source mismatch')
    if packet.get('requested_benchmark_calls', 0):
        errors.append('excluded performance campaign')
    if packet.get('reference_origin') != 'independently authored literal expectations':
        errors.append('reference origin')
    if packet.get('claims_full_completion') and packet.get('missing_inputs'):
        errors.append('missing evidence claimed green')
    if packet.get('claims_full_completion') and packet.get('audio_scope') != 'complete four-turn pair':
        errors.append('partial audio claimed complete')
    return errors


def constructed_packet():
    return dict(source_preparation=SOURCE, reference_origin='independently authored literal expectations',
                requested_benchmark_calls=0, claims_full_completion=False,
                audio_scope='constructed evidence-policy fixture', missing_inputs=['actual pair and browser activation'],
                ui_ux=dict(observations='Constructed scope reason, not a UI pass.'),
                typography=dict(observations='Constructed scope reason, not a visual pass.'),
                evidence=dict(observations='Constructed evidence-policy fixture only.'))


class CompletionI25(unittest.TestCase):
    def test_qwen_positive(self):
        out = FOLLOWUP/'qwen-mps-float32-cpu-codec'
        if not (out/'result.json').exists():
            self.skipTest('The selected native runtime has not retained both complete Qwen variants.')
        result = json.loads((out/'result.json').read_text())
        plan = json.loads((out/'plan.json').read_text())
        self.assertEqual(('complete', SOURCE), (result['status'], result['source_preparation']))
        self.assertEqual(json.loads((ROOT/'audit/iteration-24-azure-20261026/material.json').read_text()), plan['source_material'])
        self.assertEqual(8, len(plan['turns']))
        self.assertEqual('local', plan['profile']['billing_mode'])
        self.assertEqual(dict(device='mps',dtype='float32',codec_device='cpu'),plan['runtime'])
        self.assertGreater(len(plan['pieces']), 0)
        self.assertEqual(len(plan['pieces']), result['completed_pieces'])
        actual_calls = json.loads((out/'dispatches.json').read_text())
        successful = [c for c in actual_calls if c['action'] == 'piece' and c.get('outcome') == 'complete']
        self.assertEqual(len(plan['pieces']), len(successful))
        for i, piece in enumerate(plan['pieces']):
            native = json.loads((out/('piece-'+str(i)+'-response.json')).read_text())
            receipt = native['receipt']
            self.assertEqual(piece, receipt['input']['turn'])
            self.assertEqual(plan['profile'], receipt['input']['profile'])
            context = receipt['native']
            self.assertEqual('Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice', context['model_manifest']['repo'])
            self.assertEqual('85e237c12c027371202489a0ec509ded67b5e4b5', context['model_manifest']['revision'])
            self.assertEqual(plan['runtime']['device'], context['execution_parameters']['device'])
            self.assertEqual(plan['runtime']['dtype'], context['execution_parameters']['dtype'])
            self.assertEqual(('cpu','cpu','mps:0'),tuple(context['execution_parameters'][key] for key in ['requested_codec_device','codec_device','model_device']))
            self.assertEqual('Ryan' if piece['speaker_id'] == 's1' else 'Aiden', context['speaker'])
            self.assertEqual(['_tokenize_texts', 'generate'], [c['method'] for c in context['model_visible_calls']])
            self.assertTrue(all(c['outcome'] == 'complete' for c in context['model_visible_calls']))
            self.assertTrue(native['sample_count'])
        for variant in ['clean', 'mistakes']:
            expected = []
            for i, piece in enumerate(plan['pieces']):
                if piece['id'].startswith(variant+'-'):
                    with wave.open(str(out/('piece-'+str(i)+'.wav'))) as audio:
                        expected.append(audio.readframes(audio.getnframes())+b'\0\0'*(piece['gap_after_ms']*24))
            with wave.open(str(out/('qwen-'+variant+'.wav'))) as audio:
                self.assertEqual((1, 2, 24000), (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()))
                self.assertEqual(b''.join(expected), audio.readframes(audio.getnframes()))
        lab = json.loads((FOLLOWUP/'qwen-lab-readback.json').read_text())
        self.assertTrue(lab['readback'])
        self.assertEqual(0, lab['export_inference_calls'])
        self.assertEqual(len(plan['pieces']), lab['matched_successful_model_calls'])

    def test_review_positive(self):
        self.assertEqual([], review_errors(constructed_packet()))
        browser = FOLLOWUP/'qwen-browser/browser-observations.json'
        if not browser.exists():
            self.skipTest('Actual selected comparison/player observations are not yet retained.')
        facts = json.loads(browser.read_text())
        if not facts.get('actual_pair_playback_observed') or not facts.get('activation_observed'):
            self.skipTest('Actual pair playback/keyboard/click activation remains incomplete; controlled rendering is separate.')
        self.assertEqual(SOURCE, facts['source_preparation'])
        self.assertEqual(['/qwen-clean.wav','/qwen-mistakes.wav'],[row['src'] for row in facts['audio']])
        self.assertTrue(all(row['advanced_time']>0 and row['error'] is None for row in facts['audio']))
        self.assertTrue(facts['keyboard_observed'] and facts['refresh_observed'] and facts['single_player_observed'])
        self.assertEqual([1280, 390, 320], [p['width'] for p in facts['layouts']])
        for layout in facts['layouts']:
            self.assertEqual(layout['width'], layout['pageWidth'])
            self.assertEqual(('17px', '24.65px'), (layout['size'], layout['line']))
            self.assertTrue(layout['fontLoaded'])

    def test_actual_cpu_timeout_negative(self):
        facts = json.loads((ROOT/'data/iteration-25-verify-20261026/cpu-timeout-observation.json').read_text())
        request = facts['request']
        self.assertEqual(('piece', 'failed', 'TimeoutError'),
                         (request['action'], request['outcome'], request['exception_type']))
        self.assertEqual(dict(device='cpu', dtype='float32'), request['input']['turn']['qwen_runtime'])
        self.assertLessEqual(request['finished_at']-request['started_at'], 270.5)
        self.assertEqual(('paused', 0, 26),
                         (facts['progress']['state'], facts['progress']['completed_pieces'], facts['progress']['total_pieces']))
        self.assertEqual([], facts['saved_piece_waves'])
        self.assertFalse(facts['result_exists'])
        self.assertIn('Saved text and completed pieces are retained', facts['progress']['message'])
        self.assertEqual(2, len(facts['worker_processes_after_deadline']))  # Header and the native server; no synthesis child.
        self.assertEqual(1, facts['actual_native_piece_requests'])
        self.assertIsNone(facts['model_call_count'])
        self.assertFalse(facts['paid_use'])

    def test_ux_omission_negative(self):
        packet = constructed_packet()
        packet.pop('ui_ux')
        self.assertEqual(['ui_ux omitted'], review_errors(packet))

    def test_typography_omission_negative(self):
        packet = constructed_packet()
        packet.pop('typography')
        self.assertEqual(['typography omitted'], review_errors(packet))

    def test_evidence_mismatch_negative(self):
        for change, expected in [({'source_preparation': 'other exercise'}, 'source mismatch'),
                                 ({'claims_full_completion': True}, 'missing evidence claimed green'),
                                 ({'requested_benchmark_calls': 50}, 'excluded performance campaign'),
                                 ({'reference_origin': 'candidate generated'}, 'reference origin'),
                                 ({'claims_full_completion': True, 'missing_inputs': [], 'audio_scope': '5.6-second preview'}, 'partial audio claimed complete')]:
            packet = constructed_packet()
            packet.update(change)
            self.assertIn(expected, review_errors(packet))


if __name__ == '__main__':
    unittest.main(verbosity=2)
