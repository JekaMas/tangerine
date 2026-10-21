"""Export/read back controlled conditional-mapper success and failed-resume paths.
Native HTTP/context/persistence evidence, zero actual model inference.
"""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2];root=R/sys.argv[1];allrows=[];experiments=[];checks=[]
for name in ['TestNativeReviewConditionalMappingPositive','TestNativeReviewConditionalFailureNegative']:
 directory=root/name;counts=json.loads((directory/'protocol-counts.json').read_text());assert counts['actual_model_inference'] is False
 rows=[]
 for path in directory.glob('diagnostic-*.json'):
  packet=json.loads(path.read_text());assert packet['capture'] and packet['trace_enabled'];body=json.loads(packet['artifacts'][0]['body']);assets={x['asset_id']:x for x in body['wire_assets']}
  for document in body['documents']:
   if document['kind']=='provider-receipt':
    v=document['payload'];rows.append(v)
    for field in ['wire_request_asset_id','wire_response_asset_id']:
     if v[field] is None:
      assert field=='wire_response_asset_id' and v['http_status']==503 and v['outcome']=='transport_error';continue # actual test-owned503 has an empty body
     asset=assets[v[field]];assert hashlib.sha256(asset['body'].encode()).hexdigest()==asset['sha256']
  command=['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','/tangerine/lab.py']
  p=subprocess.run(command+['sync'],input=json.dumps(packet),capture_output=True,text=True,timeout=60,check=True);export=json.loads(p.stdout)
  p=subprocess.run(command+['verify'],input=json.dumps(export),capture_output=True,text=True,timeout=60,check=True);verified=json.loads(p.stdout)
  assert export['provider_calls']==verified['provider_calls']==0 and verified['status']=='observed' and not verified['discrepancies']
  (directory/('export-'+packet['operation']+'.json')).write_text(json.dumps(export,indent=2)+'\n');(directory/('verify-'+packet['operation']+'.json')).write_text(json.dumps(verified,indent=2)+'\n');experiments.append(export['run'])
 actual=collections.Counter(v['stage'] for v in rows);assert actual=={'adjudication':counts['adjudication_requests'],'claim_mapping':counts['mapper_requests']};assert all(v['http_status'] in [200,503] for v in rows)
 if name.endswith('FailureNegative'):assert any(v['outcome']=='transport_error' and v['http_status']==503 for v in rows)
 checks.append(dict(test=name,receiver_counts=dict(actual),status='observed',actual_model_inference=False));allrows+=rows
code="import json,sqlite3,sys; db=sqlite3.connect('/lab/mlflow.db'); out=[]\nfor i in json.load(sys.stdin):\n row=db.execute('SELECT content FROM spans WHERE span_id=?',(i,)).fetchone(); assert row; out.append(json.loads(row[0]))\nprint(json.dumps(out))"
p=subprocess.run(['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','-c',code],input=json.dumps([x['span_id'] for x in allrows]),capture_output=True,text=True,timeout=60,check=True);spans=json.loads(p.stdout)
for row,span in zip(allrows,spans):assert json.loads(span['attributes']['receipt_id'])==row['id'] and json.loads(span['attributes']['context_snapshot_id'])==row['context_snapshot_id']
result=dict(status='observed',actual_model_inference=False,provider_calls=0,native_receipts=len(allrows),independently_observed_receiver_requests=len(allrows),contexts=len(allrows),mlflow_spans=len(spans),lab_runs=experiments,cases=checks,private_root=str(root.relative_to(R)),proof_boundary='Constructed remote protocol through actual review/conditional mapper/persistence/foreground resume; actual native context/receipts and MLflow readback. No model semantic quality or actual model inference claim.')
(root/'PROTOCOL-OBSERVATIONS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
