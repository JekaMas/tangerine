"""Reconcile bounded semantic retention with exact fresh clean observations.

Original receipts remain unchanged. Changed fingerprints are shown explicitly.
This is a reviewed semantic retention report, not a claim that old tests executed
at the repair revision or that the failed first whole selection passed.
"""
from pathlib import Path
from functools import lru_cache
import collections,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
load=lambda p:json.loads(p.read_text())
plan=load(A/'REPAIR-SELECTION.json');base=load(R/plan['base_receipt']);assert base['git']['dirty'] is False
oldg=json.loads(subprocess.check_output(['git','show',plan['base']+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));oldcases={c['id']:c for c in oldg['cases']}
oldlibrary=json.loads(subprocess.check_output(['git','show',plan['base']+':audit/iteration-13-source-imports-20261021/FIXTURE-LIBRARY.json'],cwd=R));library=load(A/'FIXTURE-LIBRARY.json')
# Snapshot the stable checkout once per declared dependency-pattern set. The
# runner and original receipts are not changed or made to accept stale hashes.
original=rt.dependency_snapshot
@lru_cache(None)
def snapshot(patterns):return original(R,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(tuple(patterns))
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');records=[]
allowed={'services/api/internal/source/stream.go','services/api/internal/source/legacy.go','services/api/internal/source/presets.go','services/api/internal/app/source_upload.go','services/api/internal/app/source_staging.go'}
changed=set(subprocess.check_output(['git','diff','--name-only',plan['base'],'--','services/api'],cwd=R,text=True).splitlines());unexpected={p for p in changed if not p.endswith('_test.go') and p not in allowed};assert not unexpected,unexpected
codepatch=subprocess.check_output(['git','diff',plan['base'],'--',*sorted(allowed)],cwd=R,text=True)
for cid in plan['retained_case_ids']:
 current=g.cases[cid]
 candidates=[(oldid,c) for oldid,c in oldcases.items() if c['property_id']==current['property_id'] and c['test_id']==current['test_id'] and c['polarity']==current['polarity'] and base['cases'].get(oldid,{}).get('status')=='passed']
 assert candidates,(cid,'no original passed observation')
 expected=json.loads(current['observable']);match=None
 for oldid,c in candidates:
  previous=json.loads(c['observable'])
  if previous['independent_literal_assertions'].strip()==expected['independent_literal_assertions'].strip() and previous['oracle']==expected['oracle']:match=(oldid,c);break
 assert match,(cid,'literal assertions/oracle changed')
 oldid,previous=match;src=current['source_path'];assert src==previous['source_path'];assert library[src]['fixture_source']==oldlibrary[src]['fixture_source'],(cid,'fixture/helper code changed')
 assert hashlib.sha256((R/src).read_bytes()).hexdigest()==previous['source_sha256'],(cid,'physical test source changed')
 records.append(dict(case_id=cid,status='passed',basis='retained_semantic',original_case_id=oldid,test_id=current['test_id'],polarity=current['polarity'],receipt=plan['base_receipt'],source_commit=base['git']['head'],original_evidence_fingerprint=base['cases'][oldid]['evidence_fingerprint'],current_evidence_fingerprint=rt.case_evidence_fingerprint(g,cid),reviewed_change_scope=plan['semantic_changes']))
if '--preflight' in sys.argv:
 print(json.dumps(dict(status='retention_preflight_passed',retained=len(records),changed_production_paths=sorted(changed),fresh_required=len(plan['fresh_case_ids']))));raise SystemExit(0)
freshpath=R/sys.argv[1];fresh=load(freshpath);assert fresh['status']=='passed' and fresh['git']['dirty'] is False
for cid in plan['fresh_case_ids']:
 c=g.cases[cid];observation=fresh['cases'][cid];assert observation['status']=='passed';fp=rt.case_evidence_fingerprint(g,cid);assert fp==observation['evidence_fingerprint'],(cid,'fresh observation invalidated')
 records.append(dict(case_id=cid,status='passed',basis='fresh_clean',test_id=c['test_id'],polarity=c['polarity'],receipt=str(freshpath.relative_to(R)),source_commit=fresh['git']['head'],original_evidence_fingerprint=fp,current_evidence_fingerprint=fp))
selection=load(A/'ACCEPTANCE-SELECTION.json');assert {c['case_id'] for c in records}==set(selection['case_ids']);counts=collections.Counter(c['polarity'] for c in records)
result=dict(status='passed',candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),logical_cases=len(records),physical_tests=len({c['test_id'] for c in records}),positive=counts['positive'],negative=counts['negative'],fresh_cases=len(plan['fresh_case_ids']),retained_cases=len(plan['retained_case_ids']),source_receipts=[plan['base_receipt'],str(freshpath.relative_to(R))],reviewed_production_patch_sha256=hashlib.sha256(codepatch.encode()).hexdigest(),changed_production_paths=sorted(changed),proof_boundary=plan['retention_rule'],cases=records)
(R/'data/iteration13/acceptance-reconciled.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
