"""Export/read back owned native review paths and actual local model observations.
No inference. Controlled mapper packets stay explicitly distinct from model calls.
"""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2]
def main():
 root=R/sys.argv[1];receipt=json.loads((root/'receipt.json').read_text());failed='--allow-failed' in sys.argv;dirty='--allow-dirty' in sys.argv;legacy='--allow-legacy-protocol' in sys.argv
 if not failed:assert receipt['status']=='passed' and set(receipt['observed_tests'])==set(receipt['expected_tests'])
 if not dirty:assert receipt['require_clean'] and not receipt['git']['dirty'] and receipt['git']==receipt['git_after']
 dispatch=[];native=[];controlled=[];packets={};rows=[];contexts=[];bindings=[];exports=[];semantic=[];receiver=0
 sha=lambda b:hashlib.sha256(b).hexdigest()
 for test in receipt['expected_tests']:
  directory=root/test
  if not directory.exists():continue
  if (directory/'dispatch-observations.jsonl').exists():dispatch += [json.loads(x) for x in (directory/'dispatch-observations.jsonl').read_text().splitlines()]
  if (directory/'output.json').exists():
   expected=json.loads((directory/'expectation.json').read_text());out=json.loads((directory/'output.json').read_text());semantic.append(dict(test=test,reference=expected['semantic_reference'],resolution=out['resolution'],actual_reason=out['reason']))
  count=directory/'protocol-counts.json'
  if count.exists():receiver+=json.loads(count.read_text())['controlled_mapper_http_requests']
  elif not legacy:raise AssertionError('Missing independent mapper receiver count: '+test)
  state=directory/'state.json';operations=set()
  if state.exists():operations={x['result']['operation_id'] for x in json.loads(state.read_text()).get('stages',[]) if x['result'].get('operation_id')}
  for path in directory.glob('diagnostic-*.json'):
   p=json.loads(path.read_text())
   if p['operation'] not in operations:continue
   assert p['capture'] and p['trace_enabled'] and p['artifacts'];packets[p['operation']]=(p,path)
 for operation,(p,path) in sorted(packets.items()):
  artifact=p['artifacts'][0];assert sha(artifact['body'].encode())==artifact['sha256'];body=json.loads(artifact['body']);assets={x['asset_id']:x for x in body['wire_assets']}
  for doc in body['documents']:
   v=doc['payload']
   if doc['kind']=='provider-receipt':
    assert v['stage'] in ['case_review','adjudication','claim_mapping'];request=assets[v['wire_request_asset_id']];response=assets.get(v['wire_response_asset_id']);assert sha(request['body'].encode())==request['sha256']
    if response:assert sha(response['body'].encode())==response['sha256']
    item=(request['sha256'],response['sha256'] if response else None,v['http_status']);(controlled if v['stage']=='claim_mapping' else native).append(item);rows.append(v)
   elif doc['kind']=='llm-context-snapshot':contexts.append(v)
   elif doc['kind']=='effective-binding':bindings.append(v)
  command=['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','/tangerine/lab.py']
  out=subprocess.run(command+['sync'],input=json.dumps(p),capture_output=True,text=True,timeout=60,check=True);export=json.loads(out.stdout);(root/('export-'+operation+'.json')).write_text(json.dumps(export,indent=2)+'\n')
  out=subprocess.run(command+['verify'],input=json.dumps(export),capture_output=True,text=True,timeout=60,check=True);verified=json.loads(out.stdout);(root/('verify-'+operation+'.json')).write_text(json.dumps(verified,indent=2)+'\n')
  assert verified['status']=='observed' and verified['provider_calls']==0 and not verified['discrepancies'];assert export['provider_calls']==0 and all(v['state']=='exported' for v in export['trace_exports']);exports.append(export)
 if not failed:assert collections.Counter(native)==collections.Counter((v['wire_request_sha256'],v['wire_response_sha256'],v['http_status']) for v in dispatch)
 else:assert collections.Counter(v[0] for v in native)==collections.Counter(v['wire_request_sha256'] for v in dispatch)
 if not legacy:assert receiver==len(controlled)
 assert all(v['fixture_response'] is False and v['billing_mode']=='local' and v['endpoint']=='http://127.0.0.1:11434/v1/responses' for v in dispatch)
 assert len(contexts)==len(rows)
 code="import json,sqlite3,sys; ids=json.load(sys.stdin); db=sqlite3.connect('/lab/mlflow.db'); out=[]\nfor i in ids:\n r=db.execute('SELECT trace_id,span_id,name,content FROM spans WHERE span_id=?',(i,)).fetchone(); assert r is not None; out.append({'trace_id':r[0],'span_id':r[1],'name':r[2],'content':json.loads(r[3])})\nprint(json.dumps(out))"
 out=subprocess.run(['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','-c',code],input=json.dumps([v['span_id'] for v in rows]),capture_output=True,text=True,timeout=60,check=True);spans=json.loads(out.stdout);index={v['span_id']:v for v in spans}
 for row in rows:
  attrs=index[row['span_id']]['content']['attributes'];assert json.loads(attrs['receipt_id'])==row['id'] and json.loads(attrs['context_snapshot_id'])==row['context_snapshot_id'] and json.loads(attrs['tangerine.operation_id'])==row['operation_id']
 (root/'mlflow-spans.json').write_text(json.dumps(spans,indent=2)+'\n');(root/'semantic-comparison-input.json').write_text(json.dumps(semantic,indent=2)+'\n')
 actual_contexts={v['context_snapshot_id'] for v in rows if v['stage']!='claim_mapping'}
 result=dict(status='observed',test_status=receipt['status'],candidate=receipt['git']['head'],git=receipt['git'],require_clean=receipt['require_clean'],model=next(iter(set(receipt['models_by_stage'].values()))) if len(set(receipt['models_by_stage'].values()))==1 else 'stage-specific local models',models_by_stage=receipt['models_by_stage'],billing_mode='local',paid_provider_calls=0,observed_tests=receipt['observed_tests'],expected_tests=receipt['expected_tests'],actual_dispatches=len(dispatch),native_receipts=len(native),contexts=len(actual_contexts),bindings=len(bindings),controlled_mapper_receipts=len(controlled),controlled_mapper_receiver_observations=receiver if not legacy else None,lab_operations=len(packets),lab_runs=[v['run'] for v in exports],span_count=len(spans),actual_model_span_count=len(native),controlled_mapper_span_count=len(controlled),private_root=str(root.relative_to(R)),proof_boundary='Actual local optional review/adjudication on independent authored text/key/answer cases with exact native scores and dispatch/context/receipt/MLflow readback. Conditional mapper protocol fixtures are separate, with receiver-side counts when available; never labelled actual model inference. Failed variants retain their original status. No hosted entitlement, universal linguistic quality, human review or auditory realization claim.')
 (root/'LOCAL-OBSERVATIONS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
