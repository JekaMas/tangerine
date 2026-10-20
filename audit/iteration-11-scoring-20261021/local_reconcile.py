"""Reconcile actual local dispatch/native context/MLflow; export/readback only."""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2]
def main():
 root=R/sys.argv[1];receipt=json.loads((root/'receipt.json').read_text())
 assert receipt['status']=='passed' and receipt['require_clean'] and not receipt['git']['dirty'] and receipt['git']==receipt['git_after']
 expected={'TestLocalScoringRepairPositive','TestLocalScoringReasonPositive','TestLocalScoringWrongRepairNegative','TestLocalScoringMissNegative','TestLocalScoringRussianPositive','TestLocalScoringFalseReasonNegative'}
 assert set(receipt['observed_tests'])==expected
 dispatch=[];native=[];packets={};rows=[];contexts=[];bindings=[];exports=[]
 sha=lambda b:hashlib.sha256(b).hexdigest()
 for test in sorted(expected):
  directory=root/test;dispatch += [json.loads(x) for x in (directory/'dispatch-observations.jsonl').read_text().splitlines()]
  state=json.loads((directory/'state.json').read_text());assert state['status']=='complete'
  expected_case=json.loads((directory/'expectation.json').read_text());result=json.loads((directory/'result.json').read_text())
  assert result['score']['composite']['display']==expected_case['grade'] and result['feedback_status']=='complete'
  assert any(v['text'].strip() and (v['kind']=='missed' if expected_case['feedback_subject']=='missed' else v['kind'] in ('detected','correction','explanation') and v['decision_ids']) for v in result['feedback']['items'])
  for path in directory.glob('diagnostic-*.json'):
   p=json.loads(path.read_text());assert p['capture'] and p['trace_enabled'];body=json.loads(p['artifacts'][0]['body'])
   if any(v['kind']=='provider-receipt' and v['payload']['stage']=='feedback' for v in body['documents']):packets[p['operation']]=(p,path)
 for operation,(p,path) in sorted(packets.items()):
  artifact=p['artifacts'][0];assert sha(artifact['body'].encode())==artifact['sha256'];body=json.loads(artifact['body']);assets={x['asset_id']:x for x in body['wire_assets']}
  for doc in body['documents']:
   v=doc['payload']
   if doc['kind']=='provider-receipt':
    request=assets[v['wire_request_asset_id']];response=assets[v['wire_response_asset_id']]
    assert sha(request['body'].encode())==request['sha256'] and sha(response['body'].encode())==response['sha256'];native.append((request['sha256'],response['sha256'],v['http_status']));rows.append(v)
   elif doc['kind']=='llm-context-snapshot':contexts.append(v)
   elif doc['kind']=='effective-binding':bindings.append(v)
  command=['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','/tangerine/lab.py']
  out=subprocess.run(command+['sync'],input=json.dumps(p),capture_output=True,text=True,timeout=60,check=True);export=json.loads(out.stdout);(root/('export-'+operation+'.json')).write_text(json.dumps(export,indent=2)+'\n')
  out=subprocess.run(command+['verify'],input=json.dumps(export),capture_output=True,text=True,timeout=60,check=True);verified=json.loads(out.stdout);(root/('verify-'+operation+'.json')).write_text(json.dumps(verified,indent=2)+'\n')
  assert verified['status']=='observed' and verified['provider_calls']==0 and not verified['discrepancies'];assert export['provider_calls']==0 and all(v['state']=='exported' for v in export['trace_exports']);exports.append(export)
 assert collections.Counter(native)==collections.Counter((v['wire_request_sha256'],v['wire_response_sha256'],v['http_status']) for v in dispatch)
 assert all(v['fixture_response'] is False and v['billing_mode']=='local' and v['endpoint']=='http://127.0.0.1:11434/v1/responses' and v['http_status']==200 for v in dispatch)
 assert len(contexts)==len(rows) and {v['stage'] for v in rows}=={'feedback'}
 assert len(packets)==6 and sum(v['outcome']=='complete' for v in rows)>=6
 code="import json,sqlite3,sys; ids=json.load(sys.stdin); db=sqlite3.connect('/lab/mlflow.db'); out=[]\nfor i in ids:\n r=db.execute('SELECT trace_id,span_id,name,content FROM spans WHERE span_id=?',(i,)).fetchone(); assert r is not None; out.append({'trace_id':r[0],'span_id':r[1],'name':r[2],'content':json.loads(r[3])})\nprint(json.dumps(out))"
 out=subprocess.run(['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','-c',code],input=json.dumps([v['span_id'] for v in rows]),capture_output=True,text=True,timeout=60,check=True);spans=json.loads(out.stdout);index={v['span_id']:v for v in spans}
 for row in rows:
  attrs=index[row['span_id']]['content']['attributes'];assert json.loads(attrs['receipt_id'])==row['id'] and json.loads(attrs['context_snapshot_id'])==row['context_snapshot_id'] and json.loads(attrs['tangerine.operation_id'])==row['operation_id']
 (root/'mlflow-spans.json').write_text(json.dumps(spans,indent=2)+'\n')
 result=dict(status='observed',candidate=receipt['git']['head'],model=receipt['model'],models_by_stage=receipt['models_by_stage'],billing_mode='local',paid_provider_calls=0,observed_tests=sorted(expected),actual_dispatches=len(dispatch),native_receipts=len(rows),contexts=len(contexts),bindings=len(bindings),lab_operations=len(packets),lab_runs=[v['run'] for v in exports],span_count=len(spans),private_root=str(root.relative_to(R)),proof_boundary='Six independent correct/incorrect/missed/reason/Russian feedback cases through actual local inference over constructed source-bound semantic judgments and native exact scores, with dispatch/context/receipt/MLflow readback. No hosted entitlement, universal linguistic quality, extraction-model or audio-realization claim.')
 (root/'LOCAL-OBSERVATIONS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
