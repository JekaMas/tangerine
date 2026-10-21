"""Reconcile exact unchanged dependency receipts; never execute or relabel tests."""
from pathlib import Path
from functools import lru_cache
import collections,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
load=lambda name:json.loads((R/name).read_text());plan=load('audit/iteration-12-review-20261021/DEPENDENCY-PLAN.json')
# One read-only source snapshot per declared pattern set during this operation.
original=rt.dependency_snapshot
@lru_cache(None)
def snapshot(patterns):return original(R,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(tuple(patterns))
graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer');records=[];heads={};failed=[]
for ids,path in [(plan['fresh_case_ids'],plan.get('fresh_receipt','data/iteration12/dependencies-7b9f593.json')),(plan['retained_case_ids'],plan['retained_receipt']), (plan.get('provider_case_ids',[]),plan.get('provider_receipt','data/iteration11/verify-provider-2b74329.json'))]:
 if not ids:continue
 receipt=load(path);assert receipt['status']=='passed' and receipt['git']['dirty'] is False;heads[path]=receipt['git']['head']
 for cid in ids:
  old=receipt['cases'][cid];fp=rt.case_evidence_fingerprint(graph,cid)
  if old['status']!='passed' or fp!=old['evidence_fingerprint']:failed.append(cid)
  records.append(dict(case_id=cid,status=old['status'],test_id=old['test_id'],polarity=old['polarity'],source_commit=receipt['git']['head'],receipt=path,original_evidence_fingerprint=old['evidence_fingerprint'],current_evidence_fingerprint=fp))
counts=collections.Counter(x['polarity'] for x in records);result=dict(status='passed' if not failed else 'stale',candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),cases=len(records),positive=counts['positive'],negative=counts['negative'],fresh_source_cases=len(plan['fresh_case_ids']),unchanged_numeric_cases=len(plan['retained_case_ids']),provider_cases=len(plan.get('provider_case_ids',[])),stale_cases=failed,receipt_sources=heads,records=records,proof_boundary='Exact current per-case/dependency/command fingerprints equal original passed clean receipts. Snapshots are cached only for this read-only comparison; original receipts and their hashes are never refreshed.')
(R/'data/iteration12/dependency-retention-final.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}));sys.exit(bool(failed))
