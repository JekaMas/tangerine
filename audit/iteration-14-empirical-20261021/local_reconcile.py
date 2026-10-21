"""Inspect actual saved local-model dispatch/native/MLflow correspondence. No inference."""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2]
def main():
 root=R/sys.argv[1];receipt=json.loads((root/'receipt.json').read_text());assert receipt['status']=='passed'
 assert set(receipt['observed_tests'])=={'TestNativeQualityLocalPositive','TestNativeQualityLocalNegative'}
 directory=root/'actual-local';plan=json.loads((directory/'experiment.json').read_text());assert plan['status']=='completed' and len(plan['rows'])==2
 dispatch=[json.loads(l) for l in (directory/'dispatch-observations.jsonl').read_text().splitlines()];assert all(d['fixture_response'] is False and d['billing_mode']=='local' and d['status']==200 for d in dispatch)
 native=[];contexts=[];bindings=[];seen=set();exports=[];sha=lambda b:hashlib.sha256(b).hexdigest()
 for path in sorted(directory.glob('diagnostic-*.json')):
  packet=json.loads(path.read_text());body=json.loads(packet['artifacts'][0]['body']);assets={v['asset_id']:v for v in body['wire_assets']}
  for doc in body['documents']:
   value=doc['payload']
   if doc['kind']=='provider-receipt':
    assert value['id'] not in seen;seen.add(value['id']);request=assets[value['wire_request_asset_id']];response=assets[value['wire_response_asset_id']]
    assert sha(request['body'].encode())==request['sha256'] and sha(response['body'].encode())==response['sha256'];native.append((request['sha256'],response['sha256'],value['http_status'],value))
   elif doc['kind']=='llm-context-snapshot':contexts.append(value)
   elif doc['kind']=='effective-binding':bindings.append(value)
 command=['docker','exec','-i',os.environ['TANGERINE_QUALITY_LAB_CONTAINER'],'python','/tangerine/lab.py']
 def sdk(action,packet):
  p=subprocess.run(command+[action],input=json.dumps(packet),capture_output=True,text=True,timeout=90)
  if p.returncode:raise RuntimeError(action+' failed: '+p.stderr[-2500:])
  return json.loads(p.stdout)
 packet=json.loads((directory/'quality-export.json').read_text());result=sdk('quality-sync',packet);(root/'MLFLOW-EXPORT.json').write_text(json.dumps(result,indent=2)+'\n')
 for export in [result]+result['native_exports']:
  verified=sdk('verify',export);assert verified['status']=='observed' and verified['provider_calls']==0 and not verified['discrepancies'];exports.append(verified)
 assert collections.Counter((r[0],r[1],r[2]) for r in native)==collections.Counter((r['request_sha256'],r['response_sha256'],r['status']) for r in dispatch)
 assert len(contexts)==len(native)==len(bindings)==len(dispatch) and len(dispatch)>=4 and {v[3]['stage'] for v in native}=={'blind_claim_extraction','linguistic_audit'}
 assert collections.Counter(stage for stage in {v[3]['operation_id']:v[3]['stage'] for v in native}.values())=={'blind_claim_extraction':2,'linguistic_audit':2}
 assert len(result['native_exports'])==4 and all(t['state']=='exported' for e in result['native_exports'] for t in e['trace_exports'])
 metrics_code="import json;from mlflow import MlflowClient;c=MlflowClient();r=c.get_run(__import__('sys').argv[1]);print(json.dumps({'metrics':r.data.metrics,'params':r.data.params,'tags':r.data.tags}))"
 p=subprocess.run(command[:5]+['-c',metrics_code,result['run']],capture_output=True,text=True,timeout=30,check=True);metrics=json.loads(p.stdout);assert metrics['metrics']['variant0/llm_lab.completion_rate']==1 and metrics['metrics']['variant1/llm_lab.completion_rate']==1
 assert 'variant0/llm_lab.cost_total_usd' not in metrics['metrics'];assert metrics['params']['variant0.profile']
 assert packet['development_run_id'] and metrics['tags']['tangerine.development_run_id']==packet['development_run_id']
 span_code="import json,sqlite3,sys;ids=json.load(sys.stdin);db=sqlite3.connect('/lab/mlflow.db');out=[]\nfor i in ids:\n r=db.execute('SELECT trace_id,span_id,name,content FROM spans WHERE span_id=?',(i,)).fetchone();assert r is not None;out.append({'trace_id':r[0],'span_id':r[1],'name':r[2],'content':json.loads(r[3])})\nprint(json.dumps(out))"
 p=subprocess.run(command[:5]+['-c',span_code],input=json.dumps([v[3]['span_id'] for v in native]),capture_output=True,text=True,timeout=30,check=True);spans=json.loads(p.stdout);index={v['span_id']:v for v in spans}
 for _,_,_,r in native:
  attrs=index[r['span_id']]['content']['attributes'];assert json.loads(attrs['receipt_id'])==r['id'] and json.loads(attrs['context_snapshot_id'])==r['context_snapshot_id'] and json.loads(attrs['tangerine.development_run_id'])==packet['development_run_id']
 verdicts=[]
 for path in sorted(directory.glob('variant-*-output.json')):
  row=json.loads(path.read_text());values={v['proposition_id']:v for v in row['judge']['verdicts']};assert values['preserved_quote']['verdict']=='supported' and values['invented_quote']['verdict']=='unsupported' and values['unheard_audio']['verdict']=='unknown';verdicts.append(values)
 out=dict(status='observed',source_receipt=receipt,actual_dispatches=len(dispatch),native_receipts=len(native),context_snapshots=len(contexts),effective_bindings=len(bindings),mlflow_run=result['run'],native_mlflow_runs=[e['run'] for e in result['native_exports']],span_count=len(spans),independent_verdict_packets=len(verdicts),paid_provider_calls=0,source_populations='constructed authored assertions; actual installed local model inference',proof_boundary='Finite two-variant extraction and diagnostic judge observations; known true/false/unsupported-audio propositions. No hosted entitlement, all122quality or hidden model-server tokenizer coverage claim.',metrics=metrics,spans=spans)
 (root/'LOCAL-OBSERVATIONS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['source_receipt','metrics','spans']}))
if __name__=='__main__':main()
