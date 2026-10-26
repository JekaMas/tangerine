"""Reconcile selected retained dispatch/native evidence. Zero inference."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-23-gemini-20261026'
def read(name):return json.loads((OUT/name).read_text())
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
docs=read('resume/documents.json')
receipts=[x for x in docs if 'wire_request_asset_id' in x and x.get('stage')!='tts']
candidate=[];errors=[]
for folder,dispatches in [('live',read('live/dispatches.json')[:3]),('resume',read('resume/dispatches.json'))]:
 for dispatch in dispatches:
  hits=[]
  for receipt in receipts:
   try:
    request=read('resume/assets/'+receipt['wire_request_asset_id']+'.json')
    response=read('resume/assets/'+receipt['wire_response_asset_id']+'.json')
   except (ValueError,FileNotFoundError,TypeError):continue
   if request==dispatch['request'] and response==dispatch['response']:hits.append(receipt)
  if len(hits)!=1:
   errors.append({'dispatch':folder+':'+str(dispatch['index']),'native_matches':len(hits)});continue
  r=hits[0];snapshot=next((x for x in docs if x.get('id')==r['context_snapshot_id']),None)
  if not snapshot or snapshot.get('receipt_id')!=r['id']:errors.append({'snapshot_missing':r['id']})
  candidate.append({'dispatch':folder+':'+str(dispatch['index']),'receipt_id':r['id'],'snapshot_id':r['context_snapshot_id'],'stage':r['stage'],'outcome':r['outcome'],'http_status':r['http_status'],'input_tokens':r['input_tokens'],'output_tokens':r['output_tokens'],'request_asset_id':r['wire_request_asset_id'],'response_asset_id':r['wire_response_asset_id']})
packet={'scope':'Successful candidate: retained unchanged generation/mutation and repaired final interpretation. Controlled errors and failed baseline stay separately retained. Native exact wires/outputs are read for evidence inspection; no runtime gate or repeated stored-data qualification.',
 'independent_dispatches':3+len(read('resume/dispatches.json')),'native_receipts':len(candidate),'native_snapshots':len(candidate),'discrepancies':errors,'matches':candidate,
 'baseline_limit':{'live_initial_semantics':'Prior uncertainty retained with three complete native receipts.','repair':'Two real extraction calls. The second returned before the pre-fix recorder panic. Observer request/response survives; no completed receipt/snapshot was written. This failed baseline is incomplete, never counted as completed candidate.'},
 'hosted_dispatches_total':sum(len(read(folder+'/dispatches.json')) for folder in ['live','repair','resume']),
 'purchased_credits':'Forbidden. Existing project observed No billing account; no billing/settings changed.','export_inference_calls':0}
write('candidate-reconciliation.json',packet)
facts={'layouts':read('layouts.json'),'reopened_url':read('reopened.json')['url'],
 'keyboard':'Refresh to stored audio; mobile menu opened and closed with Enter; visible focus retained.',
 'recovery':'Original model-attribution uncertainty and native recorder panic inspected. Cause repaired; Refresh and explicit Resume retain exact answer, key/audio and frozen profile. Reload/settings navigation adds zero inference.',
 'readback_primary':read('reopened.json')['primary'],'media':'Actual 28.875-second stored WAV, two local Kokoro voices; no phonetic target requested.',
 'proof_limits':['One generated grammar exercise; no corpus or universal quality claim.','Original failed baseline missing one native receipt remains explicit.','No UI/CSS redesign, source imports, performance or bulk campaign.']}
write('observations.json',facts)
print(json.dumps({'candidate_dispatches':packet['independent_dispatches'],'native_matches':len(candidate),'discrepancies':errors,'total_hosted_dispatches':packet['hosted_dispatches_total']}))
