"""Project actual decoder durations. These are model-derived, not heard phones."""
import copy, uuid

FRAME_SAMPLES = 600


def phone_interval(decoder, start, end, sample_count):
    if decoder.get('phone_intervals') is not None:
        rows=decoder['phone_intervals']
        if start is None or end is None or not 0 <= start < end <= len(rows):raise ValueError('ALIGNMENT_UNAVAILABLE')
        a,b=rows[start]['start'],rows[end-1]['end']
        if a>=b:raise ValueError('ALIGNMENT_UNAVAILABLE')
        return a,b
    durations = decoder['pred_dur']
    # Exactly one source target, framed with BOS/EOS by the actual model.
    if durations and isinstance(durations[0], list):
        durations = durations[0]
    count = len(durations) - 2
    if start is None or end is None or not 0 <= start < end <= count:
        raise ValueError('ALIGNMENT_UNAVAILABLE')
    offset = max(0, durations[0] - 3)
    a = min(sample_count, round(FRAME_SAMPLES * (offset + sum(durations[1:1 + start]))))
    b = min(sample_count, round(FRAME_SAMPLES * (offset + sum(durations[1:1 + end]))))
    if a >= b:
        raise ValueError('ALIGNMENT_UNAVAILABLE')
    return a, b


def matching_scope(scopes, unit, surface=None):
    return next((r for r in scopes if r['unit_id']==unit and (surface is None or r.get('surface_scope') is None or r['surface_scope']==surface)),None)


def scope_key(unit, surface):
    return f"{unit}:{surface['start']}:{surface['end']}"


def resolve(turn, native, sample_count, source_piece_id):
    """Compile only against the accepted generated clip and its real timing."""
    steps = []
    decoders = native.get('decoder', [])
    for ordinal, edit in enumerate(turn.get('acoustic_edits', [])):
        p = copy.deepcopy(edit['parameters'])
        start, end = p.get('phone_start'), p.get('phone_end')
        scope=matching_scope(native.get('acoustic_scopes',[]),edit['unit_id'],edit['scope'])
        if scope is not None:
            if start is not None and edit['controller']!='phone_pair':
                a,b=phone_interval(scope,start,end if end is not None else start+1,sample_count)
            else:a,b=scope['start'],scope['end']
        elif edit['controller']=='phone_pair':a,b=0,sample_count
        elif start is not None:
            if len(decoders)!=1:raise ValueError('ALIGNMENT_UNAVAILABLE')
            a,b=phone_interval(decoders[0],start,end if end is not None else start+1,sample_count)
        else:a,b=0,sample_count
        step_id = str(uuid.uuid5(uuid.NAMESPACE_OID, source_piece_id + ':' + str(ordinal)))
        steps.append({'id': step_id, 'unit_id': edit['unit_id'], 'controller': edit['controller'],
                      'source_piece_id': source_piece_id, 'surface_scope': edit['scope'], 'source_interval': {'start': a, 'end': b},
                      'parameters': p, 'reference_piece_id': source_piece_id if edit['controller'] == 'phone_pair' else None,
                      'taxonomy_id': edit.get('taxonomy_id')})
    return steps


def words_from_tokens(tokens, sample_count):
    """Keep upstream join_timestamps output, without treating it as ASR review."""
    rows = []
    for token in tokens or []:
        start, end = getattr(token, 'start_ts', None), getattr(token, 'end_ts', None)
        if start is None or end is None:
            continue
        a, b = max(0, round(start * 24000)), min(sample_count, round(end * 24000))
        if b > a:
            rows.append({'text': token.text, 'start_sample': a, 'end_sample': b,
                         'phonemes': getattr(token, 'phonemes', None), 'basis': 'kokoro_decoder_join_timestamps'})
    return rows


def project_native(native, rows, sample_count):
    """Carry model-derived intervals through the actual transform clock map."""
    result=copy.deepcopy(native)
    def point(value, end=False):
        candidates=[r for r in rows if r['source_start'] <= value <= r['source_end'] and r['source_end'] > r['source_start']]
        if not candidates:return min(sample_count,max(0,value))
        row=candidates[0] if end else candidates[-1]
        source=row['source_end']-row['source_start'];output=row['final_end']-row['final_start']
        return min(sample_count,max(0,round(row['final_start']+(value-row['source_start'])*output/source)))
    for decoder in result.get('decoder',[]):
        if decoder.get('phone_intervals') is None:
            duration=decoder['pred_dur'];duration=duration[0] if duration and isinstance(duration[0],list) else duration
            offset=max(0,duration[0]-3)
            decoder['phone_intervals']=[{'start':min(decoder['sample_count'],round(600*(offset+sum(duration[1:1+i])))),
                                         'end':min(decoder['sample_count'],round(600*(offset+sum(duration[1:2+i]))))} for i in range(len(duration)-2)]
        for row in decoder['phone_intervals']:
            row['start'],row['end']=point(row['start']),point(row['end'],True)
        for row in decoder.get('word_tokens',[]):
            row['start_sample'],row['end_sample']=point(row['start_sample']),point(row['end_sample'],True)
        decoder['sample_count']=sample_count;decoder['timing_basis']='decoder_proposal_mapped_through_native_transform'
    for scope in result.get('acoustic_scopes',[]):
        scope['start'],scope['end']=point(scope['start']),point(scope['end'],True)
        for row in scope['phone_intervals']:
            row['start'],row['end']=point(row['start']),point(row['end'],True)
    return result


def mapped_point(value, rows, end=False):
    candidates=[r for r in rows if r['source_start']<=value<=r['source_end'] and r['source_end']>r['source_start']]
    if not candidates:return value
    row=candidates[0] if end else candidates[-1]
    return round(row['final_start']+(value-row['source_start'])*(row['final_end']-row['final_start'])/(row['source_end']-row['source_start']))


def retain_pauses(native, result, piece_id):
    """Keep exact inserted silence through later gain/clock correspondence."""
    pauses=[(mapped_point(a,result['clock_mapping']),mapped_point(b,result['clock_mapping'],True)) for a,b in native.get('inserted_pauses',[])]
    pauses += [(r['final_start'],r['final_end']) for r in result['sample_rows'] if r['kind']=='pause']
    merged=[]
    for a,b in sorted(set(pauses)):
        if a>=b:continue
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])
    rows=[]
    for row in result['sample_rows']:
        spans=[(row['final_start'],row['final_end'])]
        for a,b in merged:
            spans=[p for c,d in spans for p in ((c,min(d,a)),(max(c,b),d)) if p[1]>p[0]]
        for c,d in spans:
            span=row['final_end']-row['final_start'];source=row['source_end']-row['source_start']
            rows.append({**row,'final_start':c,'final_end':d,
                         'source_start':row['source_start']+round((c-row['final_start'])*source/span),
                         'source_end':row['source_start']+round((d-row['final_start'])*source/span)})
    for a,b in merged:
        rows.append(dict(piece_id=piece_id,source_audio_sha256=None,source_sample_rate_hz=None,source_start=0,source_end=0,final_start=a,final_end=b,kind='pause',transform_id=result['receipt']['id'],crossfade_group_id=None))
    result['sample_rows']=sorted(rows,key=lambda r:(r['final_start'],r['final_end']))
    result['native']['inserted_pauses']=merged
    return result


def compile_scopes(piece,edits,offset,vocabulary):
    """Bind exact surface tokens to complete phrase phone sequences before inference."""
    surface=piece['operations'][0]['text'];tokens=piece['g2p_tokens'];cursor=0
    for token in tokens:
        a=surface.find(token['text'],cursor)
        if a<0:raise ValueError('ALIGNMENT_UNAVAILABLE')
        token['start_cp'],token['end_cp']=a+offset,a+offset+len(token['text']);cursor=a+len(token['text'])
    groups={}
    for edit in edits:
        a,b=edit['scope']['start'],edit['scope']['end']
        matched=[i for i,t in enumerate(tokens) if t['end_cp']>a and t['start_cp']<b]
        if not matched or tokens[matched[0]]['start_cp']!=a or tokens[matched[-1]]['end_cp']!=b:raise ValueError('ALIGNMENT_UNAVAILABLE')
        groups.setdefault((matched[0],matched[-1]+1),[]).append(edit)
    # Collapse a selected multi-token reference into one exact grapheme/phone
    # association. No punctuation or whitespace token is synthesized alone.
    for (a,b),group in sorted(groups.items(),reverse=True):
        pairs=[e for e in group if e['controller']=='phone_pair']
        if pairs:
            references={e['parameters']['reference_ipa'] for e in pairs}
            if len(references)!=1:raise ValueError('CONSTRAINT_CONFLICT')
            first,last=tokens[a],tokens[b-1]
            tokens[a:b]=[{'text':surface[first['start_cp']-offset:last['end_cp']-offset],
                          'phonemes':next(iter(references)),'whitespace':last['whitespace'],
                          'start_cp':first['start_cp'],'end_cp':last['end_cp']}]
    groups={}
    for e in edits:
        a,b=e['scope']['start'],e['scope']['end']
        matched=[i for i,t in enumerate(tokens) if t['end_cp']>a and t['start_cp']<b]
        groups.setdefault((matched[0],matched[-1]+1),[]).append(e)
    def sequence(ts):return ''.join((t['phonemes'] or '')+(' ' if t['whitespace'] else '') for t in ts).strip()
    piece['compiled_phonemes']=sequence(tokens)
    scopes=[];variants={}
    for (a,b),group in groups.items():
        first=len(''.join((t['phonemes'] or '')+(' ' if t['whitespace'] else '') for t in tokens[:a]))
        count=len(sequence(tokens[a:b]))
        for e in group:
            if matching_scope(scopes,e['unit_id'],e['scope']) is None:scopes.append({'unit_id':e['unit_id'],'surface_scope':e['scope'],'phone_start':first,'phone_end':first+count})
    scopes.sort(key=lambda row:(row['phone_start'],row['phone_end'],row['unit_id']))
    # Combine non-overlapping differences within a complete target sequence.
    # All units in the same target receive the final combined target, so a later
    # pair cannot silently erase a previous phone mutation in that scope.
    for (ta,tb),group in groups.items():
        pairs=[e for e in group if e['controller']=='phone_pair']
        if not pairs:continue
        reference=pairs[0]['parameters']['reference_ipa'];changes=[]
        for e in pairs:
            changed=e['parameters']['mutated_ipa'];left=0
            while left<min(len(reference),len(changed)) and reference[left]==changed[left]:left+=1
            right=0
            while right<min(len(reference),len(changed))-left and reference[-1-right]==changed[-1-right]:right+=1
            changes.append((left,len(reference)-right,changed[left:len(changed)-right if right else None]))
        ordered=sorted(set(changes))
        if any(b>c for (a,b,_),(c,d,_) in zip(ordered,ordered[1:])):raise ValueError('CONSTRAINT_CONFLICT')
        changed=reference
        for a,b,value in reversed(ordered):changed=changed[:a]+value+changed[b:]
        scope=matching_scope(scopes,pairs[0]['unit_id'],pairs[0]['scope']);a,b=scope['phone_start'],scope['phone_end']
        delta=len(changed)-(b-a)
        projected=[]
        for row in scopes:
            x,y=row['phone_start'],row['phone_end']
            if x==a and y==b:y+=delta
            elif x>=b:x+=delta;y+=delta
            projected.append({**row,'phone_start':x,'phone_end':y})
        for e in pairs:
            key=scope_key(e['unit_id'],e['scope']) if sum(x['unit_id']==e['unit_id'] for x in scopes)>1 else e['unit_id']
            variants[key]={'compiled_phonemes':piece['compiled_phonemes'][:a]+changed+piece['compiled_phonemes'][b:], 'scopes':projected}
    # A declared recurring rule shares one full-phrase model variant. Each
    # occurrence still has its own projected scope/crop. Ordinary independent
    # scopes keep their existing variants and semantics.
    for unit in piece.get('recurring_unit_ids',[]):
        selected=[s for s in scopes if s['unit_id']==unit and scope_key(unit,s['surface_scope']) in variants]
        if len(selected)<2:continue
        phones=piece['compiled_phonemes'];projected=copy.deepcopy(scopes)
        for target in sorted(selected,key=lambda s:s['phone_start'],reverse=True):
            variant=variants.pop(scope_key(unit,target['surface_scope']))
            actual=matching_scope(variant['scopes'],unit,target['surface_scope'])
            replacement=variant['compiled_phonemes'][actual['phone_start']:actual['phone_end']]
            a,b=target['phone_start'],target['phone_end'];delta=len(replacement)-(b-a)
            phones=phones[:a]+replacement+phones[b:]
            for row in projected:
                if row['phone_start']==a and row['phone_end']==b:row['phone_end']+=delta
                elif row['phone_start']>=b:row['phone_start']+=delta;row['phone_end']+=delta
        variants[unit]={'compiled_phonemes':phones,'scopes':projected}
    for phones in [piece['compiled_phonemes']]+[v['compiled_phonemes'] for v in variants.values()]:
        if len(phones)>510:raise ValueError('INPUT_CAPACITY_EXCEEDED')
        if any(c not in vocabulary for c in phones):raise ValueError('CAPABILITY_UNAVAILABLE')
    piece['acoustic_token_scopes']=scopes;piece['phone_variants']=variants


def decoder_scopes(turn,decoder):
    scopes=[]
    for row in turn.get('acoustic_token_scopes',[]):
        a,b=row['phone_start'],row['phone_end'];n=decoder['sample_count']
        start,end=phone_interval(decoder,a,b,n)
        intervals=[]
        for i in range(a,b):
            # Zero-duration stress markers remain addressable together with a
            # real phone; do not reject them in the retained correspondence.
            d=decoder['pred_dur'];d=d[0] if d and isinstance(d[0],list) else d
            x=min(n,600*(max(0,d[0]-3)+sum(d[1:1+i])));y=min(n,600*(max(0,d[0]-3)+sum(d[1:2+i])))
            intervals.append({'start':x,'end':y})
        scopes.append({'unit_id':row['unit_id'],'surface_scope':row.get('surface_scope'),'start':start,'end':end,'phonemes':decoder['phonemes'][a:b],'phone_intervals':intervals})
    return scopes


def reference_tokens(tokens,text,edits):
    """Supply explicit whole-scope references before upstream empty-phone filtering.

    This retains literal targets such as currency symbols; it does not feed
    embedded pronunciation markup to Misaki or split surrounding phrase audio.
    """
    rows=[];cursor=0
    for token in tokens:
        a=text.find(token.text,cursor)
        if a<0:raise ValueError('ALIGNMENT_UNAVAILABLE')
        b=a+len(token.text);rows.append((a,b,copy.deepcopy(token)));cursor=b
    groups={}
    for e in edits:groups.setdefault((e['scope']['start'],e['scope']['end']),set()).add(e['parameters']['reference_ipa'])
    for (a,b),references in sorted(groups.items(),reverse=True):
        if len(references)!=1:raise ValueError('CONSTRAINT_CONFLICT')
        matched=[i for i,(x,y,t) in enumerate(rows) if y>a and x<b]
        if not matched or rows[matched[0]][0]!=a or rows[matched[-1]][1]!=b:raise ValueError('ALIGNMENT_UNAVAILABLE')
        i,j=matched[0],matched[-1]+1;first=rows[i][2];first.text=text[a:b];first.phonemes=next(iter(references));first.whitespace=rows[j-1][2].whitespace;rows[i:j]=[(a,b,first)]
    return [t for a,b,t in rows]
