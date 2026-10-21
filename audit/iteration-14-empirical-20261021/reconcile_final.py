"""Full I14 reconciliation with original clean receipts, never rewritten passes."""
from pathlib import Path
import collections,json,subprocess,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;sys.path.insert(0,str(A));import dag
rt=dag.rt;load=lambda p:json.loads(p.read_text());plan=load(A/'FINAL-SELECTION.json');g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');sources=[]
for name in plan['source_receipts']:
 receipt=load(R/name);assert not receipt['git']['dirty'];old=json.loads(subprocess.check_output(['git','show',receipt['git']['head']+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));sources.append((name,receipt,{x['id']:x for x in old['cases']}))
allowed={'services/api/internal/lab/trace.go','services/api/internal/app/experiment.go','services/api/internal/app/experiment_storage.go','services/api/internal/app/experiment_scorer.go','services/api/internal/app/experiment_judge_projection.go','services/api/internal/experiment/metrics.go'};changed=set(subprocess.check_output(['git','diff','--name-only','2594009','--','services/api'],cwd=R,text=True).splitlines());assert not {p for p in changed if not p.endswith('_test.go') and p not in allowed}
records=[]
for cid in plan['retained_case_ids']:
 c=g.cases[cid];current=json.loads(c['observable']);found=None
 for path,receipt,cases in sources:
  for oldid,old in cases.items():
   if old['test_id']!=c['test_id'] or old['property_id']!=c['property_id'] or old['polarity']!=c['polarity'] or receipt['cases'].get(oldid,{}).get('status')!='passed':continue
   expected=json.loads(old['observable'])
   if expected['independent_literal_assertions'].strip()==current['independent_literal_assertions'].strip() and expected['oracle']==current['oracle']:found=(path,receipt,oldid);break
  if found:break
 assert found,(cid,'no unchanged clean independent assertion')
 path,receipt,oldid=found;records.append(dict(case_id=cid,status='passed',basis='retained_semantic_clean',original_case_id=oldid,test_id=c['test_id'],polarity=c['polarity'],receipt=path,source_commit=receipt['git']['head'],original_evidence_fingerprint=receipt['cases'][oldid]['evidence_fingerprint'],current_evidence_fingerprint=rt.case_evidence_fingerprint(g,cid),retention_reason='Unchanged literal inputs/expectations/helper setup and exercised branches; reviewed changed diagnostic or inspection paths are selected fresh. The original whole receipt remains failed, and none of its failed cases is retained as green.'))
if '--preflight' in sys.argv:print(json.dumps(dict(status='passed',retained=len(records),fresh_required=len(plan['fresh_case_ids']))));raise SystemExit(0)
freshpath=R/sys.argv[1];fresh=load(freshpath);assert fresh['status']=='passed' and not fresh['git']['dirty']
for cid in plan['fresh_case_ids']:
 c=g.cases[cid];v=fresh['cases'][cid];fp=rt.case_evidence_fingerprint(g,cid);assert v['status']=='passed' and fp==v['evidence_fingerprint'],cid;records.append(dict(case_id=cid,status='passed',basis='fresh_clean',test_id=c['test_id'],polarity=c['polarity'],receipt=str(freshpath.relative_to(R)),source_commit=fresh['git']['head'],original_evidence_fingerprint=fp,current_evidence_fingerprint=fp))
assert {v['case_id'] for v in records}=={p['case_id'] for p in load(A/'CASES.json')['plans']};counts=collections.Counter(v['polarity'] for v in records);result=dict(status='passed',candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),logical_cases=len(records),physical_tests=len({v['test_id'] for v in records}),positive=counts['positive'],negative=counts['negative'],fresh_cases=len(plan['fresh_case_ids']),retained_cases=len(plan['retained_case_ids']),source_receipts=plan['source_receipts']+[str(freshpath.relative_to(R))],reviewed_production_paths=sorted(changed),proof_boundary=plan['proof_boundary'],cases=records);(R/'data/iteration14/acceptance-reconciled.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
