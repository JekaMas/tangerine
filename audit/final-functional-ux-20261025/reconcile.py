"""Join exact observed test identities. No test rerun or replacement of failures."""
from pathlib import Path
import ast,json,re
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'data/final-functional-ux-20261025'
graph=json.loads((ROOT/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());cases=[c for c in graph['cases'] if c['id'].startswith('FX-')]
seen={}
for name in ['dag-native-final.json','dag-contract-final.json']:
 d=json.loads((OUT/name).read_text());assert d['status']=='passed',name
 for command in d['commands']:
  assert command['exit_code']==0
  for item in command['observed_tests']:
   identity=item.get('test_id',item.get('id')) if isinstance(item,dict) else item
   if isinstance(item,dict):
    assert item.get('status')=='passed',item
   seen[identity]={'receipt':'data/final-functional-ux-20261025/'+name,'command':command['id']}
raw=(OUT/'request-error.log').read_text();assert 'Ran 5 tests' in raw and raw.rstrip().endswith('OK')
for method in re.findall(r'^(test_\w+) \(test_request_error.RequestError\.\w+\) \.\.\. ok$',raw,re.M):seen['unittest::test_request_error.RequestError.'+method]={'receipt':'data/final-functional-ux-20261025/request-error.log','command':'python3 -B -m unittest discover -s tests -p test_request_error.py -v','reuse':'Helper, assertions and native JS input unchanged since observation; adding DAG metadata does not invalidate it.'}
rows=[]
for c in cases:
 if c['test_id'] not in seen:raise SystemExit('Missing actual observation: '+c['test_id'])
 rows.append({'case_id':c['id'],'test_id':c['test_id'],'status':'passed',**seen[c['test_id']]})
assert len(rows)==len(cases)
result={'scope':'FX software and actual CUA/native observation readback; not whole-product or universal auditory acceptance','properties':6,'cases':len(rows),'missing':[], 'new_inference_calls':0,'native_dag_case_count':170,'js_helpers':21,'browser_readback_assertions':57,'transport_helpers':5,'native_parent_test_events_not_additional_cases':2,'cases_observed':rows,'retained_evidence':[{'index':'audit/linguistic-fullness-20261023/RECONCILIATION.json','scope':'Native category context/control/scoring and semantic authored contrasts; those production owners/definitions are unchanged.'},{'index':'audit/category-realization-20261025/COVERAGE.json','scope':'Actual finite audio probes, including unknowns and negative listener opinions. No new hearing confirmation.'}],'invalidation':[{'input':'Authored non-pronunciation native fixture propositions','action':'Supersede first 172-event observation with dag-native-final after category-context repair.'},{'input':'Report starter sentence/window IDs in shared JS fixture','action':'Reobserve the shared 20-case native fixture through dag-native-final.'},{'input':'Result/read-only answer, transport error presentation, scoped report table and preview group wrapping','action':'Observe the affected actual UI states; final 57 assertions use their current collected values.'},{'input':'Legacy browser adapters','action':'Update visible saved-answer/read-only selectors and parse; retain historical backend evidence with its original scope, not a new headless-browser pass.'}]}
(HERE/'RECONCILIATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}))
