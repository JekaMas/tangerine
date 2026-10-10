"""Rebind changed I3 inventory fixtures; historical observations remain immutable."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
g=json.loads((C/'verification.json').read_text());f=json.loads((V/'verification-fixtures.v1.json').read_text())
source='tests/test_iteration3.py';text=(R/source).read_text();sha=hashlib.sha256(text.encode()).hexdigest();bodies={x.name:ast.get_source_segment(text,x) for x in ast.walk(ast.parse(text)) if isinstance(x,ast.FunctionDef)}
for case in g['cases']:
 if case['source_path']!=source:continue
 case['source_sha256']=sha
 plan=next(x for x in f['case_bindings'] if x['case_id']==case['id']);name=case['test_id'].split('.')[-1]
 for key in ('executable_native_fixture','literal_executable_fixture'):
  if key in plan['input']:
   old=plan['input'][key];plan['input'][key]=bodies[name];case['setup']=case['setup'].replace(json.dumps(old),json.dumps(bodies[name]))
 if 'planned_surfaces' in plan['input']:
  plan['input']['planned_surfaces']=20;case['setup']=case['setup'].replace('"planned_surfaces": 21','"planned_surfaces": 20')
 if 'assertion_source' in plan['expected']:plan['expected']['assertion_source']=bodies[name]
 fixture=next(x for x in f['fixtures'] if x['id']==case['designed_fixture_id'])
 fixture[case['polarity']]['input']=plan['input'];fixture[case['polarity']]['expected']=plan['expected']
 case['observable']=json.dumps(plan['expected'],sort_keys=True)
 # The new canonical owner is an actual input of this inventory consumer.
 for path in ('services/api/internal/app/preparation.go','services/api/internal/app/preparation_content.go','services/api/internal/app/generationdata/**','services/api/internal/provider/definition.go','services/api/internal/app/provider_inference.go','specification/v2/domain/ai-development.v1.json'):
  if path not in case['invalidation_dependencies']:case['invalidation_dependencies'].append(path)
save(C/'verification.json',g);save(V/'verification-fixtures.v1.json',f)
print('Rebound36 changed native Lab source cases; old receipts untouched.')
