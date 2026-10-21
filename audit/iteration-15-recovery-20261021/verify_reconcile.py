"""Full I15 join: preserve actual original/first-review passes and rerun affected ownership cases."""
from pathlib import Path
import collections, hashlib, json, subprocess
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
s=load(A/'VERIFY-SELECTION.json');first=load(A/'VERIFY-ACCEPTANCE-63329a1.json');fresh=load(R/'data/iteration15/verify-reference-acceptance.json')
current=load(R/'openspec/changes/implement-teacher-error-trainer/verification.json')
base='63329a116c410b52574dd36d66e14f3f3e97dc7e'
old=json.loads(subprocess.check_output(['git','show',base+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R))
old_cases={c['id']:c for c in old['cases']};new_cases={c['id']:c for c in current['cases']}
commands=lambda g:{c['id']:c for c in g['commands']}
selected=set(s['selection']['cases']);affected={cid for cid,row in s['nodes']['cases'].items() if row['command_id']=='iteration15-5-native-repair'}
assert len(selected)==83 and len(affected)==14
assert first['status']=='passed' and first['case_edges']==82 and first['fresh_clean_edges']==61 and first['retained_clean_edges']==21
assert set(fresh['cases'])==affected and fresh['status']=='passed' and fresh['git']['dirty'] is False and not fresh['substitution_gaps']
changed=subprocess.check_output(['git','diff','--name-only',base,fresh['git']['head']],cwd=R,text=True).splitlines()
production={p for p in changed if p.startswith(('services/','scripts/','deploy/')) and not p.endswith('_test.go')}
assert production=={'services/api/internal/app/deletion_plan.go'},production
out={}
for cid in sorted(selected):
 node=s['nodes']['cases'][cid];new=new_cases[cid]
 if cid in affected:
  row=fresh['cases'][cid];assert row['status']=='passed' and row['evidence_fingerprint']==node['current_evidence_fingerprint']
  out[cid]={'status':'passed','test_id':row['test_id'],'source_revision':fresh['git']['head'],'source_receipt':'data/iteration15/verify-reference-acceptance.json','original_evidence_fingerprint':row['evidence_fingerprint'],'current_evidence_fingerprint':node['current_evidence_fingerprint'],'retained':False,'reason':'Fresh committed-clean native deletion/shared/active/stale closure after the final retained-experiment guard.'}
 else:
  row=first['cases'][cid];before=old_cases[cid]
  assert row['status']=='passed' and before['test_id']==new['test_id'] and before['scenario_fingerprint']==new['scenario_fingerprint']
  assert commands(old)[before['command_id']]==commands(current)[new['command_id']]
  assert json.loads(before['observable'])['independent_literal_assertions'].rstrip()==json.loads(new['observable'])['independent_literal_assertions'].rstrip(),cid
  assert not any(v in new['test_id'] for v in ['Deletion','Referenced','ChangedPlan','CancelNegative','ExperimentReference'])
  reason='Exact earlier clean pass retained. Only new retained-experiment deletion guard changed after the complete first-review boundary; real workspace fixture has no quality_experiment rows, so the guard has no applicable input. Its command, literal assertions, tested lifecycle/CLI/UI behavior and source owners are unchanged.' if new['command_id']=='iteration15-2-workspace' else 'Exact earlier clean pass retained. Archive codec, generation/replay, lifecycle, shell routing or deterministic MLflow owner, used command/assertions/fixture semantics are unchanged; appended tests, broad unused dependencies and evidence metadata do not invalidate it.'
  out[cid]={**row,'retained':True,'current_evidence_fingerprint':node['current_evidence_fingerprint'],'reason':reason}
legacy=load(A/'ACCEPTANCE.json')
result={'status':'passed','scope':'Iteration 15 only','review_base':'0517e1e4026bc49b3c08aa2255e83688916ff413','reviewed_revision':fresh['git']['head'],'case_edges':len(out),'registered_physical_tests':len({r['test_id'] for r in out.values()}),'properties':s['selection']['properties'],'requirements':s['selection']['requirements'],'polarities':dict(collections.Counter(new_cases[c]['polarity'] for c in out)),'fresh_clean_edges':len(affected),'retained_clean_edges':len(selected-affected),'cases':out,'production_changes_after_complete_first_review':sorted(production),'manifest_sha256':hashlib.sha256((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_bytes()).hexdigest(),'source_executions':[{'receipt':'data/iteration15/verify-acceptance-fresh.json','git':first['source_executions'][0]['git'],'status':'passed','case_edges':61},{'receipt':'data/iteration15/verify-reference-acceptance.json','git':fresh['git'],'status':fresh['status'],'case_edges':14}],'retained_prior_joins':['audit/iteration-15-recovery-20261021/ACCEPTANCE.json','audit/iteration-15-recovery-20261021/VERIFY-ACCEPTANCE-63329a1.json'],'source_selection':'audit/iteration-15-recovery-20261021/VERIFY-SELECTION.json','actual_local_mlflow':legacy['actual_local_mlflow'],'proof_limits':legacy['limits']}
(A/'VERIFY-ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','production_changes_after_complete_first_review','properties','requirements','proof_limits','actual_local_mlflow')}))
