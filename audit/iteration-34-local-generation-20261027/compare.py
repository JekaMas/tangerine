"""Independent fixed-target assessment; never modifies/adopts model output."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/iteration-34-local-generation-20261027'

def read(p):return json.loads(p.read_text())

def rates(tp,fp,fn,tn):
    return dict(TP=tp,FP=fp,FN=fn,TN=tn,precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None,
                accuracy=(tp+tn)/(tp+fp+fn+tn) if tp+fp+fn+tn else None)

def control_claimed(control, turns, units):
    """A false alarm follows the selected heard span, including wider scopes.

    TN is a distinct control type. Any claimed occurrence removes that type
    from TN; an accepted variant or the same words in another turn does not.
    This is assessment of retained packets, never another runtime admission.
    """
    for unit in units:
        if unit.get('expected_judgment') != 'true_error':
            continue
        if unit.get('realization', {}).get('surface_text') == control:
            return True
        for span in unit.get('text_spans', []):
            row = turns.get(span['utterance_id'])
            if row is None:
                continue
            scope = span['span']
            start, end = int(scope['start_cp']), int(scope['end_cp'])
            for occurrence in re.finditer(re.escape(control), row['surface_text']):
                if start < occurrence.end() and end > occurrence.start():
                    return True
    return False

def quality(case, clean, candidate):
    """Literal authored contrasts own truth, not admission/model judgments."""
    if clean is None or candidate is None:
        return dict(observed=False,qualified=False,reason='No complete output to assess; failure is not a zero-error success',**{k:None for k in ['TP','FP','FN','TN','precision','recall','accuracy']})
    ct={u['id']:u['canonical_text'] for u in clean['utterances']}
    turns={u['id']:u for u in candidate['utterances']}
    units=candidate['planned_units']
    findings=[]
    expected_surface=dict(ct)
    for e in case['expected']:
        ids=[i for i,text in ct.items() if e['canonical'] in text]
        if len(ids)!=1 or ct[ids[0]].count(e['canonical'])!=1:
            findings.append('Clean target absent or not unique: '+e['canonical']);continue
        i=ids[0];expected_surface[i]=expected_surface[i].replace(e['canonical'],e['surface'],1)
    if set(ct)!=set(turns):findings.append('Turn identities changed')
    for i,text in expected_surface.items():
        if i not in turns or turns[i]['canonical_text']!=ct[i] or turns[i]['surface_text']!=text:
            findings.append('Mutation differs from independent exact expected replacements: '+i)
    matched=set();tp=0;fp=0
    for u in units:
        found=False
        spans=u.get('text_spans',[])
        for n,e in enumerate(case['expected']):
            if n in matched or u.get('primary_taxonomy_id')!=e['category_id'] or u.get('expected_judgment')!='true_error':continue
            for span in spans:
                row=turns.get(span['utterance_id']);s=span['span']
                if not row or e['surface'] not in row['surface_text']:continue
                text=row['surface_text'];a=text.index(e['surface']);b=a+len(e['surface'])
                start,end=int(s['start_cp']),int(s['end_cp'])
                if not (start<b and end>a) or text[start:end]!=s['exact_text']:continue
                options=[c for c in u.get('corrections',[]) if c.get('canonical') is True]
                if len(options)!=1:continue
                c=options[0]
                repaired=text[:start]+str(c.get('text',''))+text[end:]
                expected_repair=text[:a]+e['preferred_correction']+text[b:]
                if c.get('kind')=='replace' and repaired==expected_repair:
                    tp+=1;matched.add(n);found=True;break
            if found:break
        if not found:fp+=1;findings.append('Unsupported or incorrectly corrected unit: '+str(u.get('id')))
    tn=0;missing_controls=[];construction_deviations=[]
    for control in case['correct_controls']:
        clean_count=sum(t.count(control) for t in ct.values())
        surface_count=sum(t['surface_text'].count(control) for t in turns.values())
        claimed=control_claimed(control,turns,units)
        if clean_count!=1:construction_deviations.append(dict(control=control,requested_occurrences=1,actual_clean_occurrences=clean_count))
        # PLAN's TN is a distinct declared correct control preserved without
        # an error unit. Repeating correct text is not a linguistic false alarm.
        # Keep the topic's separate use-once instruction deviation observable.
        if clean_count>=1 and surface_count==clean_count and not claimed:tn+=1
        else:
            findings.append('Correct control missing, changed or claimed: '+control)
            if clean_count<1 or surface_count!=clean_count:missing_controls.append(control)
    score=rates(tp,fp,len(case['expected'])-tp,tn)
    if missing_controls:score['accuracy']=None
    return dict(observed=True,qualified=not findings and fp==0 and tp==len(case['expected']) and len(units)==case['mutation_count'],findings=findings,missing_controls=missing_controls,construction_deviations=construction_deviations,**score)

def replay(clean,manifest):
    texts={u['id']:u['canonical_text'] for u in clean['utterances']}
    grouped={}
    for e in manifest['edits']:grouped.setdefault(e['utterance_id'],[]).append(e)
    for i,edits in grouped.items():
        original=texts[i]
        for e in sorted(edits,key=lambda r:(r['start_cp'],r['end_cp']),reverse=True):
            a,b=int(e['start_cp']),int(e['end_cp'])
            if original[a:b]!=e['original_text']:raise ValueError('Independent manifest original-text mismatch')
            texts[i]=texts[i][:a]+e['replacement_text']+texts[i][b:]
    return texts

def dataset(directory, plan):
    observations=read(directory/'observations.json')
    dispatches=read(directory/'dispatches.json')
    rows=[]
    for row in observations:
        case=next(c for c in plan['cases'] if c['id']==row['case']);prefix=row['id']+'-'
        path=directory/(prefix+'canonical_asset_id.json');clean=read(path) if path.exists() else None
        path=directory/(prefix+'mutated_asset_id.json');candidate=read(path) if path.exists() else None
        q=quality(case,clean,candidate)
        if candidate is not None:
            manifest=read(directory/(prefix+'mutation_manifest_asset_id.json'))
            if replay(clean,manifest)!={u['id']:u['surface_text'] for u in candidate['utterances']}:raise ValueError('Independent manifest replay differs')
        blueprint=read(directory/(prefix+'blueprint.json'))['id']
        calls=[]
        for d in dispatches:
            for item in d['request']['input']:
                value=item.get('content','')
                if isinstance(value,str) and value.startswith('Complete stage input: '):
                    data=json.loads(value.removeprefix('Complete stage input: '))
                    if data.get('blueprint',{}).get('id')==blueprint:calls.append(d)
        usage=[d.get('response',{}).get('usage',{}) for d in calls]
        measured=dict(dispatches=len(calls),usage_observed_calls=sum(bool(u) for u in usage),input_tokens=sum(u.get('input_tokens',0) for u in usage),output_tokens=sum(u.get('output_tokens',0) for u in usage),http_errors=sum(d.get('http_status',200)>=400 for d in calls))
        rows.append(dict(**row,directory=str(directory.relative_to(ROOT)),quality=q,model=plan['model'],measured=measured))
    return rows,dispatches

def native_join(directory):
    docs=read(directory/'documents.json');receipts=[d for d in docs if 'wire_request_asset_id' in d and 'http_status' in d]
    contexts={d['id']:d for d in docs if 'rendered_request_asset_id' in d}
    bindings={d['binding_sha256']:d for d in docs if 'prompt_id' in d}
    remaining=list(receipts);joined=[]
    for d in read(directory/'dispatches.json'):
        matches=[r for r in remaining if read(directory/'assets'/(r['wire_request_asset_id']+'.json'))==d['request']]
        if not matches:raise ValueError('Actual dispatch missing native receipt')
        r=matches[0];remaining.remove(r);c=contexts[r['context_snapshot_id']];b=bindings[r['binding_sha256']]
        if c['receipt_id']!=r['id'] or c['rendered_request_asset_id']!=r['wire_request_asset_id'] or c['binding_sha256']!=b['binding_sha256']:raise ValueError('Wrong native context/binding association')
        if d.get('http_status')!=r['http_status']:raise ValueError('Wrong native HTTP status')
        if r['wire_response_asset_id'] and read(directory/'assets'/(r['wire_response_asset_id']+'.json'))!=d.get('response'):raise ValueError('Wrong native response')
        if not r['wire_response_asset_id'] and 'transport_error' not in d:raise ValueError('Missing actual response without transport failure')
        if b['billing_mode']!='local' or b['provider']!='local_responses' or b['model']!=d['request']['model']:raise ValueError('Nonlocal or wrong frozen model')
        joined.append(dict(receipt_id=r['id'],context_id=c['id'],phase=c['phase'],binding_id=b['id'],model=b['model'],outcome=r['outcome'],budget_method=c['budget_method'],input_budget_used=c['input_budget_used'],request_asset_id=r['wire_request_asset_id'],response_asset_id=r['wire_response_asset_id'],directory=str(directory.relative_to(ROOT))))
    if remaining:raise ValueError('Native receipt lacks independent dispatch')
    return joined

def main():
    plan=read(HERE/'PLAN.json');rows,dispatches=dataset(OUT,plan)
    joined=native_join(OUT)
    alternatives_plan=plan['alternatives']
    for directory,plan_file in [('repair','REPAIR-PLAN.json'),('final','FINAL-PLAN.json'),('repaired','REPAIRED-PLAN.json'),('deadline-profile','DEADLINE-PROFILE-PLAN.json'),('qwen-repaired','QWEN-REPAIRED-PLAN.json')]:
        if (OUT/directory/'documents.json').exists():
            repair_plan=read(HERE/plan_file);rr,rd=dataset(OUT/directory,repair_plan)
            rows+=rr;dispatches+=rd;joined+=native_join(OUT/directory);alternatives_plan+=repair_plan['alternatives']
    replay_calls=[]
    if (OUT/'projection-replay/documents.json').exists():
        rr,_=dataset(OUT/'projection-replay',read(HERE/'QWEN-REPAIRED-PLAN.json'))
        for row in rr:
            source=next(r for r in rows if r['alternative']=='qwen-repaired-plain' and r['case']==row['case'])
            row['retained_usage']=row['measured'];row['measured']={k:0 for k in ['dispatches','usage_observed_calls','input_tokens','output_tokens','http_errors']}
            row['source_case']=source['id'];row['source_generation_seconds']=source['total_seconds']
        rows+=rr;replay_calls=native_join(OUT/'projection-replay')
        alternatives_plan.append(dict(id='projection-replay',origin='Current native mechanical projection/persistence of retained actual Qwen replies; no new inference'))
    alternatives=[]
    for a in alternatives_plan:
        selected=[r for r in rows if r['alternative']==a['id']]
        scored=[r['quality'] for r in selected if r['quality']['observed']]
        quality_summary=rates(*(sum(r[k] for r in scored) for k in ['TP','FP','FN','TN']))
        if len(scored)!=len(plan['cases']) or any(r.get('missing_controls') for r in scored):quality_summary['accuracy']=None
        alternatives.append(dict(id=a['id'],requests=len(selected),admitted=sum(r['admitted'] for r in selected),qualified=len(selected)==len(plan['cases']) and all(r['admitted'] and r['quality']['qualified'] for r in selected),semantic_observed=len(scored),quality=quality_summary,seconds=[r['total_seconds'] for r in selected],measured={k:sum(r['measured'][k] for r in selected) for k in ['dispatches','usage_observed_calls','input_tokens','output_tokens','http_errors']}))
    chosen=next((a['id'] for a in alternatives if a['qualified']),None)
    usage=[r.get('response',{}).get('usage',{}) for r in dispatches]
    result=dict(plan='audit/iteration-34-local-generation-20261027/PLAN.json',repair_plan='audit/iteration-34-local-generation-20261027/REPAIR-PLAN.json',origin=plan['origin'],rows=rows,alternatives=alternatives,selected=chosen,dispatch_count=len(dispatches),native_calls=joined,native_replays=replay_calls,http_statuses=[r.get('http_status') for r in dispatches],usage=usage,input_tokens=sum(r['input_tokens'] for r in usage if isinstance(r.get('input_tokens'),int)),output_tokens=sum(r['output_tokens'] for r in usage if isinstance(r.get('output_tokens'),int)),api_charge_usd=0,electricity='unmeasured',proof_limit=plan['proof_limit']+' The final mechanical projection is reobserved through native persistence using retained actual replies, with identity rebound only; it is not new inference or a new generation-latency observation.')
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['alternatives','selected','dispatch_count','api_charge_usd']}))

if __name__=='__main__':main()
