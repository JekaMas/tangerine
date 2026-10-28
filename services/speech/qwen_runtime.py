"""Explicit local Qwen compute selection. No automatic device fallback."""
import os


def selection(frozen=None):
    if frozen is not None:
        value=dict(device=frozen['device'], dtype=frozen['dtype'])
        if 'codec_device' in frozen:value['codec_device']=frozen['codec_device']
        return value
    return dict(device=os.environ.get('TANGERINE_QWEN_DEVICE', 'cpu'),
                dtype=os.environ.get('TANGERINE_QWEN_DTYPE', 'float32'))


def configuration(torch, frozen=None):
    selected = selection(frozen)
    device, dtype = selected['device'], selected['dtype']
    if device not in ('cpu', 'mps') or dtype not in ('float32', 'float16'):
        raise ValueError('CAPABILITY_UNAVAILABLE')
    if device == 'mps' and not torch.backends.mps.is_available():
        raise ValueError('CAPABILITY_UNAVAILABLE')
    if 'codec_device' in selected and selected['codec_device']!='cpu':
        raise ValueError('CAPABILITY_UNAVAILABLE')
    return dict(**selected, attention_implementation='eager')
