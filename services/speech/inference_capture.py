"""Observe the actual local tokenizer/decoder call, without invoking it twice."""
from contextlib import contextmanager


def values(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): values(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [values(v) for v in value]
    if hasattr(value, 'detach'):
        return {'dtype': str(value.dtype), 'shape': list(value.shape),
                'values': value.detach().cpu().tolist()}
    if hasattr(value, 'tolist'):
        return values(value.tolist())
    return {'inspection_limit': type(value).__name__}


@contextmanager
def observe_method(owner, name, events, capture_result=True):
    original = getattr(owner, name)

    def observed(*args, **kwargs):
        row = {'method': name, 'args': values(args), 'kwargs': values(kwargs)}
        events.append(row)
        try:
            result = original(*args, **kwargs)
            row['outcome'] = 'complete'
            if capture_result:
                row['result'] = values(result)
            return result
        except Exception as error:
            row['outcome'] = 'failed'
            row['exception_type'] = type(error).__name__
            raise

    setattr(owner, name, observed)
    try:
        yield
    finally:
        setattr(owner, name, original)
