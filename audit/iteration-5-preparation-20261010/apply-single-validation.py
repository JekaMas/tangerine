"""Bind the user's replacement single-admission policy to current native cases.
Historical plans/receipts stay historical; only active DAG fixtures are revised.
"""
from pathlib import Path
import ast,re,json,hashlib,sys
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'verification-fixtures.v1.json');inventory=load(C/'property-inventory.json');d=load(C/'discovery.json');sets=load(V/'property-test-sets.v1.json')
parsed=parse_delta_specs(C)
changed=['I2-08','I2-12','I2-18']
for rid in changed:
 row=next(x for x in g['requirements'] if x['id']==rid)
 (cap,title),spec=next((key,val) for key,val in parsed.items() if key[0]==row['capability'] and key[1].startswith(rid+' '))
 row.update(title=title,fingerprint=spec['fingerprint'])
 prop=next(x for x in g['properties'] if x['requirement_id']==rid)
 prop['statement']=title+'; new input is admitted once and accepted storage is trusted under single-validation-policy.md.'
 prop['oracle']='Independent literal new-input/accepted-read/operation/reachability outcomes; no repeated catalogue or content audit.'
 for case in g['cases']:
  if case['property_id']==prop['id']:case['scenario_fingerprint']=spec['scenario_fingerprints'][case['scenario']]
 for x in inventory:
  if x['id']==rid:x['title']=title;x['statement']=prop['statement'];x['source']='User replacement policy on2026-10-10; historical repeated audit obligation superseded.'
 for x in f['property_bindings']:
  if x['property_id']==prop['id']:x['statement']=prop['statement'];x['independent_oracle']=prop['oracle']
 for x in sets['properties']:
  if x['property_id']==prop['id']:x['proof_boundary']=prop['oracle']
names={'TestNativeGuardEnabledPositive':'TestNativeDatabaseReachablePositive','TestNativeGuardRestoredPositive':'TestNativeDatabaseReopenPositive','TestNativeGuardDisabledNegative':'TestNativeDatabaseClosedNegative','TestNativeGuardMisboundNegative':'TestNativeDatabaseCancelledNegative'}
sources=['tests/test_iteration1.py','tests/test_iteration2.py','tests/native_storage_regression_test.go']
for source in sources:
 text=(R/source).read_text();sha=hashlib.sha256(text.encode()).hexdigest()
 if source.endswith('.py'):bodies={x.name:ast.get_source_segment(text,x) for x in ast.walk(ast.parse(text)) if isinstance(x,ast.FunctionDef)}
 else:
  matches=list(re.finditer(r'^func (Test\w+)\(t \*testing.T\)\s*\{',text,re.M));bodies={m.group(1):text[m.start():matches[j+1].start() if j+1<len(matches) else len(text)].strip() for j,m in enumerate(matches)}
 for case in g['cases']:
  if case['source_path']!=source:continue
  name=case['test_id'].split('::')[-1].split('.')[-1];new=names.get(name,name)
  case['test_id']=case['test_id'].replace(name,new);case['source_sha256']=sha
  plan=next(x for x in f['case_bindings'] if x['case_id']==case['id']);plan['test_id']=case['test_id'];plan['input']={'exact_native_test':new,'literal_executable_fixture':bodies[new]};plan['expected']={'assertion_source':bodies[new],'independent_literal_expectations':'Exact literal independently authored states, actual dependency errors and counters; accepted data is trusted, with one admission step for new input.'};plan['action']='Execute '+new+' through the actual native owner.';plan['independent_oracle']=plan['expected']['independent_literal_expectations']
  case['setup']=plan['action']+' '+json.dumps(plan['input'],sort_keys=True);case['observable']=json.dumps(plan['expected'],sort_keys=True)
  fixture=next(x for x in f['fixtures'] if x['id']==case['designed_fixture_id']);fixture[case['polarity']]={'input':plan['input'],'expected':plan['expected']}
# The deleted archive/source-audit files are not active behavior dependencies.
for case in g['cases']:
 case['invalidation_dependencies']=[p for p in case['invalidation_dependencies'] if p not in ('services/api/internal/provider/definition.go','services/api/internal/app/required_columns.json','services/api/internal/app/required_column_types.json')]
for old,new in names.items():
 def walk(x):
  if isinstance(x,str):return x.replace(old,new)
  if isinstance(x,list):return [walk(y) for y in x]
  if isinstance(x,dict):return {k:walk(v) for k,v in x.items()}
  return x
 d=walk(d)
for p,v in [(C/'verification.json',g),(C/'property-inventory.json',inventory),(C/'discovery.json',d),(V/'verification-fixtures.v1.json',f),(V/'property-test-sets.v1.json',sets)]:save(p,v)
print('Bound user replacement policy, active native fixtures and availability cases; historical observations unchanged.')
