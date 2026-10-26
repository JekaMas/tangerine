"""Explicit local Qwen compute selection. No automatic device fallback."""
import os


def configuration(torch):
    device = os.environ.get('TANGERINE_QWEN_DEVICE', 'cpu')
    dtype = os.environ.get('TANGERINE_QWEN_DTYPE', 'float32')
    if device not in ('cpu', 'mps') or dtype not in ('float32', 'float16'):
        raise ValueError('CAPABILITY_UNAVAILABLE')
    if device == 'mps' and not torch.backends.mps.is_available():
        raise ValueError('CAPABILITY_UNAVAILABLE')
    return dict(device=device, dtype=dtype, attention_implementation='eager')
