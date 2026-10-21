"""Retain unchanged I10/I11/provider/numeric proof across an unused adjudication prompt update.
Original receipts remain intact; this is not a generic fingerprint-match claim.
"""
from pathlib import Path
import json,subprocess,collections,hashlib
R=Path.cwd();A=R/'audit/iteration-12-review-20261021';anchor='e6a2bd4a068ca9c5624173124d13039e4426cce3'
load=lambda p:json.loads(Path(p).read_text())
old=lambda p:json.loads(subprocess.check_output(['git','show',anchor+':'+p],text=True))
plan=load(A/'DEPENDENCY-PLAN.json');graph_path='openspec/changes/implement-teacher-error-trainer/verification.json';before=old(graph_path);after=load(graph_path)
a={x['id']:x for x in before['cases']};b={x['id']:x for x in after['cases']};ac={x['id']:x for x in before['commands']};bc={x['id']:x for x in after['commands']}
builtin='services/api/internal/lab/builtin.json';prior=old(builtin);current=load(builtin)
assert len(prior)==len(current)
changed=[]
for x,y in zip(prior,current):
 if x!=y:
  assert x['stage']==y['stage']=='adjudication'
  assert {k:v for k,v in x.items() if k not in ['template','prompt_sha256']}=={k:v for k,v in y.items() if k not in ['template','prompt_sha256']}
  changed.append(x['prompt_id'])
assert changed==['adjudication-v1']
# All selected non-review production owners and native contracts remain byte-identical. The only changed Go owner is the isolated review admission; its changed tests are covered by the new full I12 gate.
for path in subprocess.check_output(['git','ls-files','services/api','services/web','services/speech'],text=True).splitlines():
 if path in [builtin,'services/api/internal/app/review_output.go','services/api/internal/app/review_test.go']:continue
 assert Path(path).read_bytes()==subprocess.check_output(['git','show',anchor+':'+path]),path
sources=[(plan['fresh_case_ids'],'data/iteration12/dependencies-e6a2bd4.json','unchanged selected interpretation/scoring stages'),(plan['provider_case_ids'],'data/iteration12/provider-e6a2bd4.json','unchanged provider/schema owners and assertions'),(plan['retained_case_ids'],plan['retained_receipt'],'unchanged pure numeric owner')]
records=[]
for ids,path,reason in sources:
 receipt=load(path);assert receipt['status']=='passed' and receipt['git']['dirty'] is False
 for cid in ids:
  assert a[cid]==b[cid],cid
  case=b[cid];cmd=case['command_id'];assert ac[cmd]==bc[cmd],cmd
  src=case['source_path'];assert Path(src).read_bytes()==subprocess.check_output(['git','show',anchor+':'+src]),src
  rec=receipt['cases'][cid];assert rec['status']=='passed'
  records.append(dict(case_id=cid,polarity=rec['polarity'],test_id=rec['test_id'],original_receipt=path,original_commit=receipt['git']['head'],original_evidence_fingerprint=rec['evidence_fingerprint'],retention_reason=reason))
counts=collections.Counter(x['polarity'] for x in records)
result=dict(status='passed',candidate=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),comparison_anchor=anchor,cases=len(records),polarities=dict(counts),application_cases=len(plan['fresh_case_ids']),provider_cases=len(plan['provider_case_ids']),numeric_cases=len(plan['retained_case_ids']),changed_unused_stage=changed,source_routing='services/api/internal/lab/bundle.go:225 selects exactly Pair(stage, phase); selected I10 extraction/mapping/audit and I11 feedback stages are byte-identical. No adjudication operation occurs in these selected commands.',proof_boundary='Semantic retention of original green receipts, not a claim that broad dependency-cache fingerprints match: only the unused adjudication template/hash changed in the shipped bundle; normalizeReviewShape/admitReview changes are invoked only by RunReview, not these selected named cases. All selected non-review production owners/contracts/web/speech, selected case and command definitions and their literal executable test sources are byte-identical to the clean e6a2bd4 observations. The78 numeric observations retain their original010a4d5 proof. Original receipt hashes/statuses are never refreshed. Current I12/adjudication cases require the new committed-clean full run.',records=records)
(R/'data/iteration12/semantic-dependency-retention.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
