"""Real native Qwen adapter with only the trained-model boundary substituted.

Runs in the existing dependency image. Controlled waves/tokens prove device,
cache and context wiring, never GPU execution or pronunciation quality.
"""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/speech'))
import backends


class QwenNativeRuntime(unittest.TestCase):
    def setUp(self):
        backends.CACHE.clear()

    def tearDown(self):
        backends.CACHE.clear()

    def model(self):
        import numpy as np
        class Decoder:
            def generate(self, **kwargs):
                return [[31, 47]]
        class ConstructedModel:
            model = Decoder()
            def _tokenize_texts(self, texts):
                return [[17, 23]]
            def generate_custom_voice(self, **kwargs):
                ids = self._tokenize_texts([kwargs['text']])
                self.model.generate(input_ids=ids, speaker=kwargs['speaker'], language=kwargs['language'])
                return [np.sin(np.arange(12000)*.06)*.2], 24000
        return ConstructedModel()

    def profile(self):
        return dict(id='qwen-custom-v1', provider='local_qwen3_tts', adapter_version='qwen-custom-v1',
                    model='Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice', billing_mode='local',
                    voices=[dict(id='Ryan', locale='en-US')])

    def turn(self):
        return dict(id='u1', voice_id='Ryan', locale='en-US', operations=[dict(kind='text', text='Compare the shoy-siz.')])

    def test_native_compute_context_positive(self):
        import torch
        from qwen_tts import Qwen3TTSModel
        model = self.model()
        manifest = dict(repo='constructed model boundary', revision='constructed', complete=True)
        with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE='mps', TANGERINE_QWEN_DTYPE='float16')), \
                patch.object(torch.backends.mps, 'is_available', return_value=True), \
                patch.object(backends, 'installed', return_value=(Path('/fixture-model'), manifest)), \
                patch.object(Qwen3TTSModel, 'from_pretrained', return_value=model) as factory:
            result = backends.render(self.profile(), self.turn())
        self.assertEqual(dict(device_map='mps', dtype=torch.float16, attn_implementation='eager', local_files_only=True), factory.call_args.kwargs)
        receipt = result['receipt']
        self.assertEqual('local', receipt['billing_mode'])
        self.assertEqual(self.turn(), receipt['input']['turn'])
        native = receipt['native']
        self.assertEqual(('mps', 'float16'), (native['execution_parameters']['device'], native['execution_parameters']['dtype']))
        self.assertIsNone(native['execution_parameters']['model_device'])
        self.assertIsNone(native['execution_parameters']['codec_device'])
        self.assertIsNone(native['execution_parameters']['model_dtype'])
        self.assertEqual(['_tokenize_texts', 'generate'], [c['method'] for c in native['model_visible_calls']])
        self.assertEqual([[17, 23]], native['model_visible_calls'][1]['kwargs']['input_ids'])
        self.assertEqual('Compare the shoy-siz.', native['model_visible_calls'][0]['args'][0][0])
        self.assertEqual(12000, result['sample_count'])

    def test_native_runtime_cache_separation_positive(self):
        from qwen_tts import Qwen3TTSModel
        import torch
        with patch.object(backends, 'installed', return_value=(Path('/fixture-model'), dict(repo='constructed'))), \
                patch.object(torch.backends.mps, 'is_available', return_value=True), \
                patch.object(Qwen3TTSModel, 'from_pretrained', side_effect=lambda *a, **k: self.model()) as factory:
            for device, dtype in [('cpu', 'float32'), ('cpu', 'float32'), ('mps', 'float16')]:
                with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE=device, TANGERINE_QWEN_DTYPE=dtype)):
                    backends.qwen(self.profile(), self.turn())
        self.assertEqual(2, factory.call_count)
        self.assertEqual({('/fixture-model', 'cpu', 'float32'), ('/fixture-model', 'mps', 'float16')}, set(backends.CACHE))

    def test_native_unavailable_device_negative(self):
        import torch
        from qwen_tts import Qwen3TTSModel
        turn = self.turn()
        turn['qwen_runtime'] = dict(device='mps', dtype='float32')
        with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE='cpu')), \
                patch.object(torch.backends.mps, 'is_available', return_value=False), \
                patch.object(Qwen3TTSModel, 'from_pretrained') as factory:
            result, status = backends.execute_packet(dict(profile=self.profile(), turn=turn))
        self.assertEqual(({'error': 'CAPABILITY_UNAVAILABLE'}, 1), (result, status))
        factory.assert_not_called()

    def test_native_frozen_runtime_positive(self):
        import torch
        from qwen_tts import Qwen3TTSModel
        turn = self.turn()
        turn['qwen_runtime'] = dict(device='cpu', dtype='float32')
        # The saved selection must be the consumed selection. A later server
        # environment must not turn a frozen CPU piece into an MPS invocation.
        with patch.dict(os.environ, dict(TANGERINE_QWEN_DEVICE='mps', TANGERINE_QWEN_DTYPE='float16')), \
                patch.object(torch.backends.mps, 'is_available', return_value=True), \
                patch.object(backends, 'installed', return_value=(Path('/fixture-model'), dict(repo='constructed'))), \
                patch.object(Qwen3TTSModel, 'from_pretrained', return_value=self.model()) as factory:
            result = backends.render(self.profile(), turn)
        self.assertEqual('cpu', factory.call_args.kwargs['device_map'])
        self.assertEqual(torch.float32, factory.call_args.kwargs['dtype'])
        self.assertEqual('cpu', result['receipt']['native']['execution_parameters']['device'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
