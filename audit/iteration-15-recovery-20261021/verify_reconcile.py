"""Reconcile full I15 scope without rerunning unchanged observed green cases."""
from pathlib import Path
import collections, hashlib, json, subprocess
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
s=load(A/'VERIFY-SELECTION.json');prior=load(A/'ACCEPTANCE.json');fresh=load(R/'data/iteration15/verify-acceptance-fresh.json')
current=load(R/'openspec/changes/implement-teacher-error-trainer/verification.json')
base='0517e1e4026bc49b3c08aa2255e83688916ff413'
old=json.loads(subprocess.check_output(['git','show',base+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R))
old_cases={c['id']:c for c in old['cases']};new_cases={c['id']:c for c in current['cases']}
commands=lambda g:{c['id']:c for c in g['commands']}
selected=set(s['selection']['cases']);affected={cid for cid,row in s['nodes']['cases'].items() if row['command_id'] in {'iteration15-2-workspace','iteration15-4-launcher','iteration15-5-native-repair','iteration15-6-lifecycle-repair'}}
assert len(selected)==82 and len(affected)==61
assert set(fresh['cases'])==affected and fresh['status']=='passed' and fresh['git']['dirty'] is False and not fresh['substitution_gaps']
# Runtime changes are limited to reviewed deletion, lifecycle and workspace routing.
changed=subprocess.check_output(['git','diff','--name-only',base,fresh['git']['head']],cwd=R,text=True).splitlines()
production={p for p in changed if p.startswith(('services/','scripts/','deploy/')) and not p.endswith('_test.go')}
assert production=={'services/api/internal/app/deletion_plan.go','services/api/internal/app/deletion_sources.go','services/api/internal/localctl/recovery.go','scripts/tangerine','scripts/lab','scripts/workspace-env'},production
out={}
for cid in sorted(selected):
 node=s['nodes']['cases'][cid];new=new_cases[cid]
 if cid in affected:
  row=fresh['cases'][cid];assert row['status']=='passed' and row['evidence_fingerprint']==node['current_evidence_fingerprint']
  out[cid]={'status':'passed','test_id':row['test_id'],'source_revision':fresh['git']['head'],'source_receipt':'data/iteration15/verify-acceptance-fresh.json','original_evidence_fingerprint':row['evidence_fingerprint'],'current_evidence_fingerprint':node['current_evidence_fingerprint'],'retained':False,'reason':'Exact invalidated or added lifecycle/deletion/workspace case passed on committed-clean repair.'}
 else:
  row=prior['cases'][cid];before=old_cases[cid]
  assert row['status']=='passed' and before['test_id']==new['test_id'] and before['scenario_fingerprint']==new['scenario_fingerprint']
  assert commands(old)[before['command_id']]==commands(current)[new['command_id']]
  assert json.loads(before['observable'])['independent_literal_assertions'].rstrip()==json.loads(new['observable'])['independent_literal_assertions'].rstrip(),cid
  assert not any(v in new['test_id'] for v in ['Deletion','Referenced','ChangedPlan','CancelNegative','LocalRecovery','Workspace','Launcher'])
  out[cid]={**row,'retained':True,'current_evidence_fingerprint':node['current_evidence_fingerprint'],'reason':'Retained exact committed-clean pass. Archive codec, generation/replay/transport or deterministic MLflow owner, exercised command, literal assertion and used fixture semantics are unchanged; appended tests, unused broad dependencies and documentation do not invalidate this observation.'}
result={'status':'passed','scope':'Iteration 15 only','review_base':base,'reviewed_revision':fresh['git']['head'],'case_edges':len(out),'registered_physical_tests':len({r['test_id'] for r in out.values()}),'properties':s['selection']['properties'],'requirements':s['selection']['requirements'],'polarities':dict(collections.Counter(new_cases[c]['polarity'] for c in out)),'fresh_clean_edges':len(affected),'retained_clean_edges':len(selected-affected),'cases':out,'production_changes':sorted(production),'manifest_sha256':hashlib.sha256((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_bytes()).hexdigest(),'source_executions':[{'receipt':'data/iteration15/verify-acceptance-fresh.json','git':fresh['git'],'status':fresh['status']}],'retained_prior_acceptance':'audit/iteration-15-recovery-20261021/ACCEPTANCE.json','source_selection':'audit/iteration-15-recovery-20261021/VERIFY-SELECTION.json','proof_limits':prior['limits']}
(A/'VERIFY-ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','production_changes','properties','requirements','proof_limits')}))
