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
    points = p.get('pitch_points') or []
    shape = tuple((r['fraction'], r['semitones']) for r in points)
    relative_contours = (
        ((0, 0), (1, 5)), ((0, 0), (1, -5)),
        ((0, 0), (.5, -3), (1, 3)), ((0, 0), (.5, 3), (1, -3)),
    )
    if step.get('taxonomy_id') in ('pronunciation.suprasegmental.intonation_contour','pronunciation.suprasegmental.intonation_function') and shape in relative_contours:
        if observation['median_f0_hz'] is None:raise Unmeasurable(observation['reason'],observation)
        median=12*math.log2(observation['median_f0_hz']/100)
        voiced=observation['pitch_points']
        if len(voiced)<len(points):raise Unmeasurable('insufficient_voiced_frames',observation)
        p['pitch_points']=[{'fraction':voiced[round(x['fraction']*(len(voiced)-1))]['fraction'],
                            'semitones':median+x['semitones']} for x in points]
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
        merged=[]
        for w in sorted(lexical,key=lambda r:r['start_sample']):
            a,b=w['start_sample'],w['end_sample']
            if merged and a<=merged[-1]['end']:merged[-1]['end']=max(b,merged[-1]['end'])
            else:merged.append({'start':a,'end':b})
        step['duration_regions']=merged
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



def resynthesize_regions(source, regions, parameters, start, end):
    """Change timed speech while retaining intervening PCM and its exact clock."""
    chunks=[];clock=[];rows=[];cursor=start;output=start
    for region in regions:
        a,b=region['start'],region['end']
        if a>cursor:
            chunks.append(source[cursor:a]);clock.append(dict(source_start=cursor,source_end=a,final_start=output,final_end=output+a-cursor));rows.append((cursor,a,output,output+a-cursor,'copy'));output+=a-cursor
        changed=praat_transform(source[a:b],parameters);chunks.append(changed)
        clock.append(dict(source_start=a,source_end=b,final_start=output,final_end=output+len(changed)));rows.append((a,b,output,output+len(changed),'duration'));output+=len(changed);cursor=b
    if cursor<end:
        chunks.append(source[cursor:end]);clock.append(dict(source_start=cursor,source_end=end,final_start=output,final_end=output+end-cursor));rows.append((cursor,end,output,output+end-cursor,'copy'));output+=end-cursor
    clock=[dict(source_start=0,source_end=start,final_start=0,final_end=start)]+clock+[dict(source_start=end,source_end=len(source),final_start=output,final_end=output+len(source)-end)]
    return np.concatenate(chunks),clock,rows


def crossfade_rows(rows, start, end, changed_size, fade, digest, transform_id):
    """Split every affected correspondence row around the actual two-source mix."""
    def clip(row,a,b):
        scale=(row['source_end']-row['source_start'])/(row['final_end']-row['final_start'])
        return {**row,'source_start':row['source_start']+round((a-row['final_start'])*scale),'source_end':row['source_start']+round((b-row['final_start'])*scale),'final_start':a,'final_end':b}
    out=[]
    for row in rows:
        remaining=[row]
        for a,b,old in [(start,start+fade,start),(start+changed_size-fade,start+changed_size,end-fade)]:
            next_rows=[]
            for part in remaining:
                x,y=max(a,part['final_start']),min(b,part['final_end'])
                if x>=y:next_rows.append(part);continue
                if part['final_start']<x:next_rows.append(clip(part,part['final_start'],x))
                if y<part['final_end']:next_rows.append(clip(part,y,part['final_end']))
                mixed={**clip(part,x,y),'kind':'splice','transform_id':transform_id,'crossfade_group_id':transform_id+':'+str(a)}
                original={**mixed,'source_audio_sha256':digest,'source_start':old+x-a,'source_end':old+y-a}
                out.extend([original,mixed])
            remaining=next_rows
        out.extend(remaining)
    return sorted(out,key=lambda r:(r['final_start'],r['final_end']))


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
    before = features(target); landmarks = None; warnings = []; fade = 0; clock = None; timed_rows = None
    if kind == 'phone_pair':
        if replacement is None: raise ValueError('CONSTRAINT_CONFLICT')
        crop_start=(replacement_interval or {}).get('start',0)
        changed = samples(replacement)[crop_start:(replacement_interval or {}).get('end')]
    elif kind in ('vowel_duration', 'pitch_duration'):
        if step.get('duration_regions'):
            changed,clock,timed_rows=resynthesize_regions(source,step['duration_regions'],p,a,b)
        else:changed = praat_transform(target, p)
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
        n=p['vot_ms']*24
        clock=[dict(source_start=0,source_end=a+x,final_start=0,final_end=a+x),dict(source_start=a+x,source_end=a+y,final_start=a+x,final_end=a+x+n),dict(source_start=a+y,source_end=len(source),final_start=a+x+n,final_end=len(source)-(y-x)+n)]
        timed_rows=[(0,a+x,0,a+x,'copy'),(a+x,a+y,a+x,a+x+n,'duration'),(a+y,len(source),a+x+n,len(source)-(y-x)+n,'copy')]
    else: raise ValueError('CAPABILITY_UNAVAILABLE')
    if kind != 'pause_insert':
        if p.get('gain_db') is not None: changed = changed * 10 ** (p['gain_db'] / 20)
        # Blend only inside the declared changed interval. Outside stays exact.
        fade = 0 if kind == 'vot_edit' else min(120, len(changed) // 2, len(target) // 2)
        if step.get('duration_regions'):fade=min(fade,(timed_rows[0][3]-timed_rows[0][2])//2,(timed_rows[-1][3]-timed_rows[-1][2])//2)
        if fade:
            theta = np.linspace(0, np.pi / 2, fade)
            changed[:fade] = target[:fade] * np.cos(theta) + changed[:fade] * np.sin(theta)
            changed[-fade:] = changed[-fade:] * np.cos(theta) + target[-fade:] * np.sin(theta)
        result = np.concatenate([source[:a], changed, source[b:]])
        rows = timed_rows if timed_rows is not None else [(0, a, 0, a, 'copy'), (a, b, a, a + len(changed), 'duration' if kind == 'vowel_duration' or p.get('duration_ratio') else 'splice'), (b, len(source), a + len(changed), len(result), 'copy')]
        if step.get('duration_regions'):rows=[(0,a,0,a,'copy')]+rows+[(b,len(source),a+len(changed),len(result),'copy')]
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
    if fade:
        mappings=crossfade_rows(mappings,a,b,len(changed),fade,digest,transform_id)
    return {'audio_base64': base64.b64encode(output).decode(), 'sample_count': len(result),
            'sample_rows': mappings, 'clock_mapping': clock if clock is not None else
                ([{'source_start':0,'source_end':a,'final_start':0,'final_end':a},
                  {'source_start':a,'source_end':len(source),'final_start':a+len(changed),'final_end':len(result)}] if kind=='pause_insert' else
                 [{'source_start':0,'source_end':a,'final_start':0,'final_end':a},
                  {'source_start':a,'source_end':b,'final_start':a,'final_end':a+len(changed)},
                  {'source_start':b,'source_end':len(source),'final_start':a+len(changed),'final_end':len(result)}]), 'observations': {'before': before, 'after': features(samples(output)[a:a + len(changed)]),
                'landmarks': landmarks, 'requested': p, 'warnings': warnings, 'fade_samples': fade,
                'basis': 'native_waveform_measurement', 'perceived_feature': None},
            'receipt': {'id': str(uuid.uuid4()), 'provider': 'native_acoustic', 'model': None, 'model_calls': 0,
                        'input': {'step': step, 'source_audio_sha256': digest}, 'audio_sha256': hashlib.sha256(output).hexdigest()}}
