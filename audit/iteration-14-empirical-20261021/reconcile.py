"""Join bounded retained clean behavior with freshly invalidated clean observations.
Original receipts/fingerprints remain unchanged, including the failed first run.
"""
from pathlib import Path
import json,subprocess,sys,collections
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
sys.path.insert(0,str(A));import dag
rt=dag.rt;load=lambda p:json.loads(p.read_text());plan=load(A/'REPAIR-SELECTION.json');old=load(R/plan['base_receipt']);assert not old['git']['dirty']
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');scope=load(A/'CASES.json');ids={p['case_id'] for p in scope['plans']};oldg=json.loads(subprocess.check_output(['git','show',plan['base']+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));oldcases={v['id']:v for v in oldg['cases']};records=[]
allowed={'services/api/internal/app/experiment_scorer.go','services/api/internal/app/experiment_judge_projection.go','services/api/internal/experiment/metrics.go'}
changed=set(subprocess.check_output(['git','diff','--name-only',plan['base'],'--','services/api'],cwd=R,text=True).splitlines());assert not {v for v in changed if not v.endswith('_test.go') and v not in allowed},changed
# These three production changes and their exercised branches are reviewed in
# SELF-REVIEW.md; fresh selection covers every affected diagnostic/judge branch.
for cid in plan['retained_case_ids']:
 c=g.cases[cid];current=json.loads(c['observable']);matches=[]
 for prior_id,v in oldcases.items():
  if v['test_id']!=c['test_id'] or v['property_id']!=c['property_id'] or v['polarity']!=c['polarity'] or old['cases'].get(prior_id,{}).get('status')!='passed':continue
  previous=json.loads(v['observable'])
  if previous['independent_literal_assertions'].strip()==current['independent_literal_assertions'].strip() and previous['oracle']==current['oracle']:matches.append((prior_id,v))
 assert matches,(cid,'no identical independent clean assertion')
 prior_id,v=matches[0]
 records.append(dict(case_id=cid,status='passed',basis='retained_semantic_clean',original_case_id=prior_id,test_id=c['test_id'],polarity=c['polarity'],receipt=plan['base_receipt'],source_commit=old['git']['head'],original_evidence_fingerprint=old['cases'][prior_id]['evidence_fingerprint'],current_evidence_fingerprint=rt.case_evidence_fingerprint(g,cid),retention_reason='Identical literal input/assertion/fixture helpers and unchanged exercised production branches; only the reviewed non-applicable diagnostic/judge branches changed. Original receipt remains a failed whole run because its actual local cases failed.'))
if '--preflight' in sys.argv:
 print(json.dumps(dict(status='passed',retained=len(records),fresh_required=len(plan['fresh_case_ids']),reviewed_production_paths=sorted(changed))));raise SystemExit(0)
fresh_path=R/sys.argv[1];fresh=load(fresh_path);assert fresh['status']=='passed' and not fresh['git']['dirty']
for cid in plan['fresh_case_ids']:
 c=g.cases[cid];r=fresh['cases'][cid];assert r['status']=='passed';fp=rt.case_evidence_fingerprint(g,cid);assert fp==r['evidence_fingerprint'],(cid,'fresh input invalidated')
 records.append(dict(case_id=cid,status='passed',basis='fresh_clean',test_id=c['test_id'],polarity=c['polarity'],receipt=str(fresh_path.relative_to(R)),source_commit=fresh['git']['head'],original_evidence_fingerprint=fp,current_evidence_fingerprint=fp))
assert {r['case_id'] for r in records}==ids;assert {r['test_id'] for r in records}=={g.cases[c]['test_id'] for c in ids}
counts=collections.Counter(r['polarity'] for r in records);result=dict(status='passed',candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),logical_cases=len(records),physical_tests=len({r['test_id'] for r in records}),positive=counts['positive'],negative=counts['negative'],fresh_cases=len(plan['fresh_case_ids']),retained_cases=len(plan['retained_case_ids']),source_receipts=[plan['base_receipt'],str(fresh_path.relative_to(R))],reviewed_production_paths=sorted(changed),proof_boundary=plan['retention_rule'],cases=records)
(R/'data/iteration14/acceptance-reconciled.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
