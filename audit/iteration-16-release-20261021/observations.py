"""Read original native event receipts; never execute/relabel a behavior test."""
from pathlib import Path
import collections,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_unittest_events,parse_go_events
G=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());selected=[c for c in G['cases'] if c['id'].startswith('I16-')];observations=collections.defaultdict(list)
for path in sorted((R/'data/iteration16').iterdir()):
 if not path.is_file() or path.suffix not in ['.stdout','.stderr','.jsonl','.log'] or '-red.' in path.name:continue
 text=path.read_text(errors='replace');go=[]
 for line in text.splitlines():
  try:row=json.loads(line)
  except ValueError:continue
  if isinstance(row,dict) and 'Action' in row and 'Package' in row:go.append(line)
 events={**parse_unittest_events(text),**parse_go_events('\n'.join(go))}
 for identity,status in events.items():
  identity=identity.replace('unittest::tests.','unittest::')
  eligible=True
  if identity in ['tangerine.local/api/internal/app::TestNativeDiagnosticActualAuditoryPositive','tangerine.local/api/internal/app::TestNativeDiagnosticActualAuditoryContrastNegative']:eligible=path.name.startswith('auditory-native-quality-sdpa')
  if identity.startswith('unittest::test_release_diagnostic_lab.ReleaseDiagnosticLabTests.'):eligible=path.name.startswith(('diagnostic-quality-lab','diagnostic-lab-'))
  if identity=='unittest::test_release_current_source.CurrentSourceTests.test_current_arm64_source_positive':eligible=path.name.startswith('current-startup-')
  if status in ['pass','fail']:observations[identity].append(dict(status=status,path=str(path.relative_to(R)),mtime=path.stat().st_mtime,eligible_for_current_contract=eligible))
# The prior clean I15 launcher cases are unaffected: only start/build and
# maintenance wait changed; these cases exercise lab routing before either.
old=R.parent/'tangerine_iteration15_20261021/data/iteration15/verify-acceptance-fresh.json'
x=json.loads(old.read_text());assert x['status']=='passed' and x['git']['dirty'] is False
for case in x['cases'].values():
 if case['status']=='passed' and any(n in case['test_id'] for n in ['test_selected_lab_positive','test_explicit_lab_override_positive','test_selected_lab_missing_runtime_negative']):
  observations[case['test_id']].append(dict(status='pass',path=str(old),mtime=old.stat().st_mtime,source_revision=x['git']['head'],retention_reason='Exact unchanged lab-routing assertions/fixture and exercised launcher branch; new start/build/wait owners are not used.'))
rows={};missing=[]
for case in selected:
 identity=case['test_id']
 if identity in rows:continue
 history=sorted(observations.get(identity,[]),key=lambda x:x['mtime']);options=[o for o in history if o.get('eligible_for_current_contract',True)]
 if not options or options[-1]['status']!='pass':missing.append(identity)
 rows[identity]=dict(latest=options[-1] if options else None,history=history)
result=dict(required=len(rows),observed=len(rows)-len(missing),missing=missing,records=rows)
return_value=result
