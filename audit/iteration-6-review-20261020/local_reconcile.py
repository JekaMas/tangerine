"""Explicit actual-local dispatch/native/Lab reconciliation; never inference."""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2];E=R/'data/iteration6-review-20261020/local-reconciliation'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 root=R/sys.argv[1];receipt=json.loads((root/'receipt.json').read_text());assert receipt['status']=='passed' and receipt['require_clean'] and not receipt['git']['dirty'] and receipt['git']==receipt['git_after']
 assert set(receipt['observed_tests'])=={'TestNativeLocalMutationPositive','TestNativeLocalZeroMutationNegative'}
 dispatch=[];packets={};contexts=[];bindings=[];rows=[]
 for path in root.glob('TestNativeLocal*/dispatch-observations.jsonl'):
  dispatch.extend(json.loads(x) for x in path.read_text().splitlines())
 for path in root.glob('TestNativeLocal*/diagnostic-*.json'):
  p=json.loads(path.read_text());packets[p['operation']]=(p,path)
 native=[];exports=[]
 for operation,(p,path) in sorted(packets.items()):
  assert p['capture'] and p['trace_enabled'];a=p['artifacts'][0];assert sha(a['body'].encode())==a['sha256'];body=json.loads(a['body']);assets={x['asset_id']:x for x in body['wire_assets']}
  for d in body['documents']:
   if d['kind']=='provider-receipt':
    row=d['payload'];request=assets[row['wire_request_asset_id']];response=assets[row['wire_response_asset_id']]
    assert sha(request['body'].encode())==request['sha256'] and sha(response['body'].encode())==response['sha256']
    native.append((request['sha256'],response['sha256'],row['http_status']))
    rows.append(row)
   elif d['kind']=='llm-context-snapshot':contexts.append(d['payload'])
   elif d['kind']=='effective-binding':bindings.append(d['payload'])
  out=root/('export-'+operation+'.json');verified=root/('verify-'+operation+'.json')
  command=['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','/tangerine/lab.py']
  result=subprocess.run(command+['sync'],input=json.dumps(p),capture_output=True,text=True,timeout=60,check=True,env=os.environ);v=json.loads(result.stdout);out.write_text(json.dumps(v,indent=2)+'\n')
  result=subprocess.run(command+['verify'],input=json.dumps(v),capture_output=True,text=True,timeout=60,check=True,env=os.environ);check=json.loads(result.stdout);verified.write_text(json.dumps(check,indent=2)+'\n');assert check['status']=='observed' and check['provider_calls']==0 and not check['discrepancies'];assert v['provider_calls']==0 and all(x['state']=='exported' for x in v['trace_exports']);exports.append(v)
 expected=collections.Counter((x['wire_request_sha256'],x['wire_response_sha256'],x['http_status']) for x in dispatch)
 assert expected==collections.Counter(native) and all(x['http_status']==200 and x['fixture_response'] is False and x['billing_mode']=='local' and x['endpoint']=='http://127.0.0.1:11434/v1/responses' for x in dispatch)
 assert len(contexts)==len(rows) and len(bindings)==4 and len(packets)==4
 # Read real MLflow spans and their linkage; an HTTP200 export alone is insufficient.
 script="import json,sqlite3,sys; ids=json.load(sys.stdin); db=sqlite3.connect('/lab/mlflow.db'); out=[]\nfor i in ids:\n r=db.execute('SELECT trace_id,span_id,name,content FROM spans WHERE span_id=?',(i,)).fetchone(); assert r is not None; out.append({'trace_id':r[0],'span_id':r[1],'name':r[2],'content':json.loads(r[3])})\nprint(json.dumps(out))"
 result=subprocess.run(['docker','exec','-i',os.environ['TANGERINE_LOCAL_LAB_CONTAINER'],'python','-c',script],input=json.dumps([x['span_id'] for x in rows]),capture_output=True,text=True,timeout=60,check=True,env=os.environ);spans=json.loads(result.stdout)
 by_span={x['span_id']:x for x in spans}
 for row in rows:
  attrs=by_span[row['span_id']]['content']['attributes']
  assert json.loads(attrs['receipt_id'])==row['id'] and json.loads(attrs['context_snapshot_id'])==row['context_snapshot_id'] and json.loads(attrs['tangerine.operation_id'])==row['operation_id']
 (root/'mlflow-spans.json').write_text(json.dumps(spans,indent=2)+'\n')
 quality=json.loads((root/'quality-independent.json').read_text());assert quality['status']=='supported' and quality['observed_preferred_correction']==quality['expected_preferred_correction']
 samples=[]
 for path in root.glob('TestNativeLocal*/state.json'):
  state=json.loads(path.read_text());assert state['origin']=='actual_local_ollama_with_native_preparation_storage';p=state['preparation'];assert p['phase_states']['mutation']=='complete';c=json.loads((path.parent/(p['mutated_asset_id']+'.bytes')).read_text());samples.append({'test':path.parent.name,'preparation_id':p['id'],'canonical_asset_id':p['canonical_asset_id'],'mutated_asset_id':p['mutated_asset_id'],'manifest_asset_id':p['mutation_manifest_asset_id'],'units':len(c['planned_units'])})
 result={'status':'observed','candidate':receipt['git']['head'],'model':'gpt-oss:20b','model_identity_ref':'audit/iteration-6-mutations-20261011/local-model-info.json','billing_mode':'local','paid_provider_calls':0,'cases':samples,'independent_quality_expectation':quality,'actual_dispatches':len(dispatch),'native_receipts':len(rows),'contexts':len(contexts),'operations':len(packets),'lab_runs':[x['run'] for x in exports],'span_count':len(spans),'private_evidence_root':str(root.relative_to(R)),'receipt_sha256':sha((root/'receipt.json').read_bytes()),'proof_boundary':'Actual local canonical/mutation execution for one agreement mutation and an empty key, with native context/output/dispatch and MLflow readback. No hosted entitlement, all122 empirical linguistic qualification, speech or grading claim.'}
 E.mkdir(parents=True,exist_ok=True);(E/'LOCAL-OBSERVATIONS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
