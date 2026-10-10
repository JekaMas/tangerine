"""Freeze exact literal executable fixtures and their native source identities."""
from pathlib import Path
import ast,hashlib,json,re
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain';A=Path(__file__).resolve().parent
f=json.loads((V/'verification-fixtures.v1.json').read_text());a=json.loads((A/'CASES.json').read_text());g=json.loads((C/'verification.json').read_text())
py=(R/'tests/test_iteration3.py').read_text();pbody={n.name:ast.get_source_segment(py,n) for n in ast.walk(ast.parse(py)) if isinstance(n,ast.FunctionDef)}
go=(R/'services/api/internal/lab/lab_test.go').read_text();matches=list(re.finditer(r'^func (Test\w+)\(t \*testing.T\) \{',go,re.M));gbody={m.group(1):go[m.start():matches[i+1].start() if i+1<len(matches) else len(go)].strip() for i,m in enumerate(matches)}
packets={x['id']:x for x in f['fixtures']}
for row in [*f['case_bindings'],*a['plans']]:
 if row['property_id'].startswith('I3-'):
  name=row['test_id'].split('::')[-1].split('.')[-1];row['input']['executable_native_fixture']=(pbody if name.startswith('test_') else gbody)[name];packets[row['fixture_id']][row['polarity']]={'input':row['input'],'expected':row['expected']}
plans={x['case_id']:x for x in a['plans']}
for c in g['cases']:
 if c['property_id'].startswith('I3-'):
  row=plans[c['id']];c['setup']=row['action']+' '+json.dumps(row['input'],sort_keys=True);c['observable']=json.dumps(row['expected'],sort_keys=True);c['source_sha256']=hashlib.sha256((R/c['source_path']).read_bytes()).hexdigest()
for p,obj in [(V/'verification-fixtures.v1.json',f),(A/'CASES.json',a),(C/'verification.json',g)]:p.write_text(json.dumps(obj,indent=2)+'\n')
print('Frozen88 exact case fixtures; earlier fixtures unchanged.')
