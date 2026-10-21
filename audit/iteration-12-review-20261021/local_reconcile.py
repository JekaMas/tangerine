"""Read/export actual local native observations and MLflow; never invokes a model."""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2]
def main():
 root=R/sys.argv[1];receipt=json.loads((root/'receipt.json').read_text());failed='--allow-failed' in sys.argv;dirty='--allow-dirty' in sys.argv
 if not failed:assert receipt['status']=='passed' and set(receipt['observed_tests'])==set(receipt['expected_tests'])
 if not dirty:assert receipt['require_clean'] and not receipt['git']['dirty'] and receipt['git']==receipt['git_after']
 dispatch=[];native=[];packets={};rows=[];contexts=[];bindings=[];exports=[];semantic=[]
 sha=lambda b:hashlib.sha256(b).hexdigest()
 for test in receipt['expected_tests']:
  directory=root/test
  if not directory.exists():continue
  if (directory/'dispatch-observations.jsonl').exists():dispatch += [json.loads(x) for x in (directory/'dispatch-observations.jsonl').read_text().splitlines()]
  if (directory/'output.json').exists():
   expected=json.loads((directory/'expectation.json').read_text());out=json.loads((directory/'output.json').read_text());semantic.append(dict(test=test,reference=expected['semantic_reference'],resolution=out['resolution'],actual_reason=out['reason']))
  for path in directory.glob('diagnostic-*.json'):
   p=json.loads(path.read_text())
   if not p.get('capture') or not p.get('trace_enabled') or not p.get('artifacts'):continue # uncaptured constructed baseline; actual dispatch joins below remain mandatory
   assert p['capture'] and p['trace_enabled'];body=json.loads(p['artifacts'][0]['body'])
   if any(v['kind']=='provider-receipt' and v['payload']['stage'] in ['case_review','adjudication'] for v in body['documents']):packets[p['operation']]=(p,path)
 for operation,(p,path) in sorted(packets.items()):
  artifact=p['artifacts'][0];assert sha(artifact['body'].encode())==artifact['sha256'];body=json.loads(artifact['body']);assets={x['asset_id']:x for x in body['wire_assets']}
  for doc in body['documents']:
   v=doc['payload']
   if doc['kind']=='provider-receipt':
    request=assets[v['wire_request_asset_id']];response=assets.get(v['wire_response_asset_id']);assert sha(request['body'].encode())==request['sha256']
    if response:assert sha(response['body'].encode())==response['sha256']
    native.append((request['sha256'],response['sha256'] if response else None,v['http_status']));rows.append(v)
   elif doc['kind']=='llm-context-snapshot':contexts.append(v)
   elif doc['kind']=='effective-binding':bindings.append(v)
  command=['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','/tangerine/lab.py']
  out=subprocess.run(command+['sync'],input=json.dumps(p),capture_output=True,text=True,timeout=60,check=True);export=json.loads(out.stdout);(root/('export-'+operation+'.json')).write_text(json.dumps(export,indent=2)+'\n')
  out=subprocess.run(command+['verify'],input=json.dumps(export),capture_output=True,text=True,timeout=60,check=True);verified=json.loads(out.stdout);(root/('verify-'+operation+'.json')).write_text(json.dumps(verified,indent=2)+'\n')
  assert verified['status']=='observed' and verified['provider_calls']==0 and not verified['discrepancies'];assert export['provider_calls']==0 and all(v['state']=='exported' for v in export['trace_exports']);exports.append(export)
 if not failed:
  assert collections.Counter(native)==collections.Counter((v['wire_request_sha256'],v['wire_response_sha256'],v['http_status']) for v in dispatch)
 else:assert collections.Counter(v[0] for v in native)==collections.Counter(v['wire_request_sha256'] for v in dispatch)
 assert all(v['fixture_response'] is False and v['billing_mode']=='local' and v['endpoint']=='http://127.0.0.1:11434/v1/responses' for v in dispatch)
 assert len(contexts)==len(rows) and {v['stage'] for v in rows} <= {'case_review','adjudication'}
 code="import json,sqlite3,sys; ids=json.load(sys.stdin); db=sqlite3.connect('/lab/mlflow.db'); out=[]\nfor i in ids:\n r=db.execute('SELECT trace_id,span_id,name,content FROM spans WHERE span_id=?',(i,)).fetchone(); assert r is not None; out.append({'trace_id':r[0],'span_id':r[1],'name':r[2],'content':json.loads(r[3])})\nprint(json.dumps(out))"
 out=subprocess.run(['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','-c',code],input=json.dumps([v['span_id'] for v in rows]),capture_output=True,text=True,timeout=60,check=True);spans=json.loads(out.stdout);index={v['span_id']:v for v in spans}
 for row in rows:
  attrs=index[row['span_id']]['content']['attributes'];assert json.loads(attrs['receipt_id'])==row['id'] and json.loads(attrs['context_snapshot_id'])==row['context_snapshot_id'] and json.loads(attrs['tangerine.operation_id'])==row['operation_id']
 (root/'mlflow-spans.json').write_text(json.dumps(spans,indent=2)+'\n');(root/'semantic-comparison-input.json').write_text(json.dumps(semantic,indent=2)+'\n')
 result=dict(status='observed',test_status=receipt['status'],candidate=receipt['git']['head'],git=receipt['git'],require_clean=receipt['require_clean'],model='gpt-oss:20b',models_by_stage=receipt['models_by_stage'],billing_mode='local',paid_provider_calls=0,observed_tests=receipt['observed_tests'],expected_tests=receipt['expected_tests'],actual_dispatches=len(dispatch),native_receipts=len(rows),contexts=len(contexts),bindings=len(bindings),lab_operations=len(packets),lab_runs=[v['run'] for v in exports],span_count=len(spans),private_root=str(root.relative_to(R)),proof_boundary='Actual local optional review/adjudication on independent authored text/key/answer cases, with native exact scores, dispatch/context/receipt/MLflow readback. Failures retain their original status. No hosted entitlement, universal linguistic quality, independent human review or auditory realization claim.')
 (root/'LOCAL-OBSERVATIONS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
