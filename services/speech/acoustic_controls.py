"""Native PCM controllers and measurements. No model, network, or persistence."""
import base64, hashlib, math, uuid
import numpy as np
from audio import wav_bytes,admit

RATE = 24000


from acoustic_measurements import features,vot_landmarks,Unmeasurable


def samples(audio):
    # Called for already admitted internal WAVs, not another stored-byte audit.
    return np.frombuffer(audio, dtype='<i2', offset=44).astype(np.float64) / 32768


def encode(values):
    if not np.isfinite(values).all():raise ValueError('AUDIO_FORMAT_INVALID')
    return wav_bytes(np.rint(np.clip(values, -1, 32767 / 32768) * 32768).astype('<i2').tobytes())



def resolve_parameters(step, audio, words=None, gap_samples=0, target_wpm=None):
    """Resolve signal-dependent targets once, before storing the production child."""
    import copy
    step = copy.deepcopy(step)
    a, b = step['source_interval']['start'], step['source_interval']['end']; p = step['parameters']
    source = samples(audio)[a:b]; observation = features(source)
    if step.get('taxonomy_id') in ('pronunciation.suprasegmental.intonation_contour','pronunciation.suprasegmental.intonation_function') and p.get('pitch_points')==[{'fraction':0,'semitones':0},{'fraction':1,'semitones':5}]:
        if observation['median_f0_hz'] is None:raise Unmeasurable(observation['reason'],observation)
        median=12*math.log2(observation['median_f0_hz']/100)
        p['pitch_points']=[{'fraction':0,'semitones':median},{'fraction':1,'semitones':median+5}]
    if step.get('taxonomy_id') == 'pronunciation.suprasegmental.pitch_range':
        points = observation['pitch_points']
        if not points: raise Unmeasurable(observation['reason'], observation)
        median = float(np.median([r['semitones'] for r in points]))
        p['pitch_points'] = [{'fraction': r['fraction'], 'semitones': median + 2 * (r['semitones'] - median)} for r in points]
    if step.get('taxonomy_id') == 'fluency.speech_rate' and p.get('duration_ratio') is None:
        lexical = [{**r,'start_sample':max(a,r['start_sample']),'end_sample':min(b,r['end_sample'])} for r in words or [] if any(c.isalpha() for c in r['text']) and r.get('phonemes') and r['start_sample']<b and r['end_sample']>a]
        if not lexical or not target_wpm: raise Unmeasurable('timed_lexical_tokens_unavailable')
        # Decoder token/word association is retained as model-derived evidence;
        # never claim independent ASR or auditory review from these projections.
        p['duration_ratio']=duration_ratio_for_rate(lexical,target_wpm)
        step['source_interval']={'start':lexical[0]['start_sample'],'end':lexical[-1]['end_sample']}
    step.pop('taxonomy_id', None)
    return step, observation



def duration_ratio_for_rate(words,target_wpm,internal_gap_samples=0):
    if not words or not target_wpm or target_wpm<=0:raise Unmeasurable('timed_lexical_tokens_unavailable')
    merged=[]
    for a,b in sorted((w['start_sample'],w['end_sample']) for w in words):
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    speech=sum(b-a for a,b in merged)
    silence=merged[-1][1]-merged[0][0]-speech+internal_gap_samples
    remaining=60*len(words)*RATE/target_wpm-silence
    if speech<=0 or remaining<=0:raise ValueError('CONSTRAINT_CONFLICT')
    return remaining/speech


def praat_transform(values, parameters):
    import parselmouth
    from parselmouth.praat import call
    sound = parselmouth.Sound(values, RATE)
    ratio, points = parameters.get('duration_ratio'), parameters.get('pitch_points', [])
    if not ratio and not points: return values.copy()
    try:
        manipulation = call(sound, 'To Manipulation', .01, 60, 500)
        if points:
            observed = features(values)
            if observed['voiced_frames'] < 3: raise Unmeasurable(observed['reason'] or 'insufficient_voiced_frames', observed)
            tier = call('Create PitchTier', 'target', 0, sound.duration)
            for point in points:
                call(tier, 'Add point', point['fraction'] * sound.duration, 100 * 2 ** (point['semitones'] / 12))
            call([tier, manipulation], 'Replace pitch tier')
        if ratio is not None:
            tier = call('Create DurationTier', 'target', 0, sound.duration)
            call(tier, 'Add point', sound.duration / 2, ratio)
            call([tier, manipulation], 'Replace duration tier')
        return call(manipulation, 'Get resynthesis (overlap-add)').values[0].copy()
    except parselmouth.PraatError as e:
        raise Unmeasurable('praat_resynthesis_unavailable') from e



def aspiration(values, count):
    if count == 0: return np.empty(0)
    if len(values) == 0: raise Unmeasurable('no_aspiration_samples')
    out = values[:count].copy()
    while len(out) < count:
        fade = min(120, len(values) // 2, len(out) // 2)
        if fade:
            theta = np.linspace(0, np.pi / 2, fade)
            joined = out[-fade:] * np.cos(theta) + values[:fade] * np.sin(theta)
            out = np.concatenate([out[:-fade], joined, values[fade:]])
        else: out = np.concatenate([out, values])
    return out[:count]


def transform(audio, step, replacement=None, replacement_interval=None):
    """Apply one resolved step, retaining all other PCM samples and accounting."""
    source = samples(audio); a, b = step['source_interval']['start'], step['source_interval']['end']
    if not 0 <= a < b <= len(source): raise ValueError('ALIGNMENT_UNAVAILABLE')
    p, kind = step['parameters'], step['controller']; target = source[a:b]
    before = features(target); landmarks = None; warnings = []; fade = 0
    if kind == 'phone_pair':
        if replacement is None: raise ValueError('CONSTRAINT_CONFLICT')
        crop_start=(replacement_interval or {}).get('start',0)
        changed = samples(replacement)[crop_start:(replacement_interval or {}).get('end')]
    elif kind in ('vowel_duration', 'pitch_duration'):
        changed = praat_transform(target, p)
    elif kind == 'pause_insert':
        # Fade adjoining samples first; inserted zeros stay exactly zero.
        n = min(120, a // 2, (len(source) - a) // 2) if p["pause_ms"] else 0
        result = source.copy()
        if n:
            theta = np.linspace(0, np.pi / 2, n)
            result[a - n:a] *= np.cos(theta); result[a:a + n] *= np.sin(theta)
        changed = np.zeros(p['pause_ms'] * 24)
        result = np.concatenate([result[:a], changed, result[a:]])
        rows = [(0, a - n, 0, a - n, 'copy'), (a - n, a, a - n, a, 'splice'),
                (a, a, a, a + len(changed), 'pause'), (a, a + n, a + len(changed), a + len(changed) + n, 'splice'),
                (a + n, len(source), a + len(changed) + n, len(result), 'copy')]
    elif kind == 'vot_edit':
        landmarks = step.get('landmarks') or vot_landmarks(target)
        x, y = landmarks['burst_end_sample'], landmarks['voicing_onset_sample']
        changed = np.concatenate([target[:x], aspiration(target[x:y], p['vot_ms'] * 24), target[y:]])
        warnings.append('release_boundary_not_faded')
    else: raise ValueError('CAPABILITY_UNAVAILABLE')
    if kind != 'pause_insert':
        if p.get('gain_db') is not None: changed = changed * 10 ** (p['gain_db'] / 20)
        # Blend only inside the declared changed interval. Outside stays exact.
        fade = 0 if kind == 'vot_edit' else min(120, len(changed) // 2, len(target) // 2)
        if fade:
            theta = np.linspace(0, np.pi / 2, fade)
            changed[:fade] = target[:fade] * np.cos(theta) + changed[:fade] * np.sin(theta)
            changed[-fade:] = changed[-fade:] * np.cos(theta) + target[-fade:] * np.sin(theta)
        result = np.concatenate([source[:a], changed, source[b:]])
        rows = [(0, a, 0, a, 'copy'), (a, b, a, a + len(changed), 'duration' if kind == 'vowel_duration' or p.get('duration_ratio') else 'splice'),
                (b, len(source), a + len(changed), len(result), 'copy')]
    if np.max(np.abs(result)) >= 1: warnings.append('clipping')
    output = encode(result)
    admit(output)
    digest = hashlib.sha256(audio).hexdigest(); transform_id = step['id']
    mappings = [{'piece_id': step['source_piece_id'], 'source_audio_sha256': None if k=='pause' else digest, 'source_sample_rate_hz': None if k=='pause' else RATE,
                 'source_start': x, 'source_end': y, 'final_start': u, 'final_end': v, 'kind': k,
                 'transform_id': transform_id if k != 'copy' else None, 'crossfade_group_id': None}
                for x, y, u, v, k in rows if v > u]
    if kind=='phone_pair':
        replacement_digest=hashlib.sha256(replacement).hexdigest()
        for row in mappings:
            if row['kind']=='splice' and row['final_start']==a and row['final_end']==a+len(changed):
                row['source_audio_sha256']=replacement_digest;row['source_start']=crop_start;row['source_end']=crop_start+len(changed)
    # Explicit two-source overlap provenance for boundary crossfades. The main
    # transformed row covers the range; split it around those overlap ranges.
    if fade:
        row = mappings[1 if a else 0]; base = dict(row)
        left, right = row['final_start'], row['final_end']; mappings.remove(row)
        for start, end in ((left, left + fade), (right - fade, right)):
            group = transform_id + ':' + str(start)
            source_scale=(base['source_end']-base['source_start'])/(right-left)
            altered = {**base, 'source_start':base['source_start']+round((start-left)*source_scale),
                       'source_end':base['source_start']+round((end-left)*source_scale),
                       'final_start': start, 'final_end': end, 'kind': 'splice', 'crossfade_group_id': group}
            oldstart = a if start == left else b - fade
            original = {**altered, 'source_audio_sha256':digest,'source_start': oldstart, 'source_end': oldstart + fade}
            mappings.extend([original, altered])
        if right - left > 2 * fade: mappings.append({**base, 'source_start':base['source_start']+round(fade*(base['source_end']-base['source_start'])/(right-left)),'source_end':base['source_end']-round(fade*(base['source_end']-base['source_start'])/(right-left)), 'final_start': left + fade, 'final_end': right - fade})
        mappings.sort(key=lambda r: (r['final_start'], r['final_end']))
    return {'audio_base64': base64.b64encode(output).decode(), 'sample_count': len(result),
            'sample_rows': mappings, 'clock_mapping':
                ([{'source_start':0,'source_end':a,'final_start':0,'final_end':a},
                  {'source_start':a,'source_end':len(source),'final_start':a+len(changed),'final_end':len(result)}] if kind=='pause_insert' else
                 [{'source_start':0,'source_end':a,'final_start':0,'final_end':a},
                  {'source_start':a,'source_end':b,'final_start':a,'final_end':a+len(changed)},
                  {'source_start':b,'source_end':len(source),'final_start':a+len(changed),'final_end':len(result)}]), 'observations': {'before': before, 'after': features(samples(output)[a:a + len(changed)]),
                'landmarks': landmarks, 'requested': p, 'warnings': warnings, 'fade_samples': fade,
                'basis': 'native_waveform_measurement', 'perceived_feature': None},
            'receipt': {'id': str(uuid.uuid4()), 'provider': 'native_acoustic', 'model': None, 'model_calls': 0,
                        'input': {'step': step, 'source_audio_sha256': digest}, 'audio_sha256': hashlib.sha256(output).hexdigest()}}
