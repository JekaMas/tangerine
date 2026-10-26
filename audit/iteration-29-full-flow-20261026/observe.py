"""Reconcile actual finite I29 observations; no inference or runtime admission."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/iteration-29-full-flow-20261026'

def load(name): return json.loads((DATA/name).read_text())
def asset(id): return load('assets/'+id+'.json')

def main():
    dispatch=load('dispatches.json')
    docs=load('documents.json')
    all_receipts=sorted([d for d in docs if 'http_status' in d and 'wire_request_asset_id' in d],key=lambda d:d['started_at'])
    receipts=[r for r in all_receipts if r['stage']!='tts']
    contexts={d['id']:d for d in docs if 'rendered_request_asset_id' in d}
    bindings={d['binding_sha256']:d for d in docs if 'prompt_id' in d}
    rows=[]
    unused=list(receipts)
    for observed in [d for d in dispatch if d['kind']=='gemini_free']:
        match=next((r for r in unused if asset(r['wire_request_asset_id'])==observed['request']),None)
        if match is None: raise AssertionError('Unreconciled actual dispatch '+str(observed['index']))
        unused.remove(match)
        context=contexts[match['context_snapshot_id']]
        binding=bindings[match['binding_sha256']]
        if context['receipt_id']!=match['id'] or context['rendered_request_asset_id']!=match['wire_request_asset_id']:
            raise AssertionError('The native context names another request/receipt')
        if observed.get('http_status')!=match['http_status']:
            raise AssertionError('The retained HTTP status differs')
        if match['wire_response_asset_id']:
            if asset(match['wire_response_asset_id'])!=observed.get('response'):
                raise AssertionError('The native reply differs from the actual boundary')
        elif 'transport_error' not in observed:
            raise AssertionError('Missing response lacks an actual transport failure')
        rows.append({'dispatch_index':observed['index'],'receipt_id':match['id'],'stage':match['stage'],'http_status':match['http_status'],'outcome':match['outcome'],'context_id':context['id'],'binding_id':binding['id'],'wire_request_asset_id':match['wire_request_asset_id'],'wire_response_asset_id':match['wire_response_asset_id'],'model':binding['model'],'billing_mode':binding['billing_mode'],'component_kinds':[c['kind'] for c in context['components']]})
    if unused: raise AssertionError('Native receipt has no independent dispatch observation')
    speech=[]
    unused=[r for r in all_receipts if r['stage']=='tts']
    for observed in [d for d in dispatch if d['kind']=='speech_worker' and d['url'].endswith('/piece')]:
        r=next((r for r in unused if asset(r['wire_request_asset_id'])==observed['request']),None)
        if r is None or asset(r['wire_response_asset_id'])!=observed['response']:raise AssertionError('Speech boundary/native reply mismatch')
        unused.remove(r)
        context=asset(r['context_snapshot_id'])
        if context['wire_request_asset_id']!=r['wire_request_asset_id'] or context['profile']!=observed['request']['profile']:raise AssertionError('Another speech context')
        speech.append({'dispatch_index':observed['index'],'receipt_id':r['id'],'context_asset_id':r['context_snapshot_id'],'binding_sha256':r['binding_sha256'],'profile':context['profile'],'wire_request_asset_id':r['wire_request_asset_id'],'wire_response_asset_id':r['wire_response_asset_id']})
    if unused:raise AssertionError('Native synthesis receipt lacks its boundary observation')
    prep=next((DATA/'preparations').glob('*.json'))
    preparation=json.loads(prep.read_text())
    key=load('keys/'+preparation['id']+'.json')
    attempt=load('attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5.json')['Attempt']
    result=load('attempts/'+attempt['attempt_id']+'-result.json')
    relation=next(x for x in load('native-relationships.json') if x['case_version_id']==attempt['case_version_id'])
    output={'origin':'actual native HTTP/storage observations; self-review, not independent linguistic gold','provider_dispatches':len(rows),'native_receipts':len(receipts),'calls':rows,'speech_calls':speech,'unmatched_dispatches':[],'unmatched_receipts':[],'speech_worker_requests':len([d for d in dispatch if d['kind']=='speech_worker']),'local_synthesis_requests':len(speech),'preparation_id':preparation['id'],'source_key_id':preparation['key_id'],'case_version_id':attempt['case_version_id'],'attempt_id':attempt['attempt_id'],'audio_asset_id':preparation['audio_asset_id'],'audio_sha256':preparation['audio_sha256'],'relation':relation,'key_verification':sorted({u['verification'] for u in key['units']}),'primary_score':result['score']['composite']['exact_value_0_100'],'feedback_status':result['feedback_status'],'complete_flow':result['feedback_status']=='complete' and bool(result['feedback']),'performance_campaign':'excluded','export_inference_calls':0}
    (DATA/'call-reconciliation.json').write_text(json.dumps(output,indent=2)+'\n')
    print({k:v for k,v in output.items() if k not in ['calls','speech_calls','relation']})

if __name__=='__main__': main()
