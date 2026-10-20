"""Pure acoustic intent compilation. No synthesis, storage, or waveform processing."""
import copy, math

CONTROLLERS = {'phone_pair', 'vowel_duration', 'pitch_duration', 'pause_insert', 'vot_edit'}
ORDER = {'phone_pair': 0, 'vot_edit': 1, 'vowel_duration': 2, 'pitch_duration': 2, 'pause_insert': 3}


def meaningful(edit):
    """Admit a new operation once, before any model/transform dispatch."""
    kind, p = edit['controller'], edit['parameters']
    if kind not in CONTROLLERS:
        raise ValueError('CAPABILITY_UNAVAILABLE')
    ratio = p.get('duration_ratio')
    if ratio is not None and (not math.isfinite(ratio) or ratio <= 0):
        raise ValueError('CONSTRAINT_CONFLICT')
    points = p.get('pitch_points', [])
    if any(not math.isfinite(x['semitones']) or not 0 <= x['fraction'] <= 1 for x in points) or any(a['fraction'] >= b['fraction'] for a, b in zip(points, points[1:])):
        raise ValueError('CONSTRAINT_CONFLICT')
    if p.get('gain_db') is not None and not math.isfinite(p['gain_db']):
        raise ValueError('CONSTRAINT_CONFLICT')
    used = {'phone_pair': {'reference_ipa', 'mutated_ipa', 'phone_start', 'phone_end'},
            'vowel_duration': {'duration_ratio', 'phone_start', 'phone_end'},
            'pitch_duration': {'duration_ratio', 'gain_db', 'pitch_points', 'phone_start', 'phone_end'},
            'pause_insert': {'pause_ms', 'phone_start'},
            'vot_edit': {'vot_ms', 'phone_start', 'phone_end'}}[kind]
    for key in ('duration_ratio', 'gain_db', 'pitch_points', 'pause_ms', 'vot_ms', 'reference_ipa', 'mutated_ipa', 'phone_start', 'phone_end'):
        if key not in used and p.get(key) not in (None, []):
            raise ValueError('CONSTRAINT_CONFLICT')
    if kind == 'phone_pair' and (not p.get('reference_ipa') or not p.get('mutated_ipa')):
        raise ValueError('CONSTRAINT_CONFLICT')
    if kind == 'vowel_duration' and (ratio is None or p.get('phone_start') is None or p.get('phone_end') is None):
        raise ValueError('CONSTRAINT_CONFLICT')
    if kind == 'pitch_duration' and ratio is None and p.get('gain_db') is None and not points and edit.get('taxonomy_id') not in ('pronunciation.suprasegmental.pitch_range', 'fluency.speech_rate'):
        raise ValueError('CONSTRAINT_CONFLICT')
    for key in ('pause_ms', 'vot_ms'):
        if key in used and (not isinstance(p.get(key), int) or p[key] < 0):
            raise ValueError('CONSTRAINT_CONFLICT')
    start, end = p.get('phone_start'), p.get('phone_end')
    if start is not None and (start < 0 or end is not None and end <= start):
        raise ValueError('CONSTRAINT_CONFLICT')
    if kind == 'pitch_duration' and (start is None) != (end is None):
        raise ValueError('CONSTRAINT_CONFLICT')


def scopes(turn):
    """Partition complete literal text into context and whole controlled scopes."""
    text = ''.join(op['text'] for op in turn['operations'])
    edits = turn.get('acoustic_edits', [])
    groups = {}
    for edit in edits:
        meaningful(edit)
        a, b = edit['scope']['start'], edit['scope']['end']
        if not 0 <= a < b <= len(text):
            raise ValueError('CONSTRAINT_CONFLICT')
        # A partial word is not an independently renderable target. Select its
        # whole spelling and use decoder token indexes for internal controls.
        if a and text[a - 1].isalnum() and text[a].isalnum() or b < len(text) and text[b - 1].isalnum() and text[b].isalnum():
            raise ValueError('ALIGNMENT_UNAVAILABLE')
        groups.setdefault((a, b), []).append(edit)
    spans = sorted(groups)
    if any(b > c for (a, b), (c, d) in zip(spans, spans[1:])):
        raise ValueError('CONSTRAINT_CONFLICT')
    result, pos = [], 0
    for a, b in spans:
        same = groups[a, b]
        # Distinct intervals can be resolved later; same-scope replacements or
        # duplicate timing controllers have no unambiguous composition.
        for i,left in enumerate(same):
            for right in same[i+1:]:
                lp,rp=left['parameters'],right['parameters']
                la,lb=lp.get('phone_start'),lp.get('phone_end');ra,rb=rp.get('phone_start'),rp.get('phone_end')
                disjoint=la is not None and lb is not None and ra is not None and rb is not None and (lb<=ra or rb<=la)
                if disjoint:continue
                if left['controller']==right['controller'] and left['controller'] in ('phone_pair','vot_edit','pause_insert'):
                    raise ValueError('CONSTRAINT_CONFLICT')
                if lp.get('duration_ratio') is not None and rp.get('duration_ratio') is not None or lp.get('pitch_points') and rp.get('pitch_points'):
                    raise ValueError('CONSTRAINT_CONFLICT')
        compiled=[]
        for original in same:
            item=copy.deepcopy(original);p=item['parameters']
            if item['controller']=='pitch_duration' and p.get('gain_db') is not None and (p.get('duration_ratio') is not None or p.get('pitch_points')):
                gain=copy.deepcopy(item);gain['parameters']['duration_ratio']=None;gain['parameters']['pitch_points']=[]
                p['gain_db']=None;compiled.extend([item,gain])
            else:compiled.append(item)
        def order(e):
            p=e['parameters'];gain_only=e['controller']=='pitch_duration' and p.get('gain_db') is not None and p.get('duration_ratio') is None and not p.get('pitch_points')
            return (4 if gain_only else ORDER[e['controller']],-(p.get('phone_start') or 0))
        if a > pos:
            result.append((pos, a, []))
        result.append((a, b, sorted(compiled,key=order)))
        pos = b
    if pos < len(text):
        result.append((pos, len(text), []))
    return [(text[a:b], a, b, copy.deepcopy(ops)) for a, b, ops in result] or [(text, 0, len(text), [])]
