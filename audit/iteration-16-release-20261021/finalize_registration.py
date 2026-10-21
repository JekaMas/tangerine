"""Update current test-source declarations; never rewrite observations/receipts."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer'
load=lambda p:json.loads(p.read_text());save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=load(C/'verification.json');changes={}
for c in g['cases']:
 p=R/c['source_path']
 if c['state']!='implemented' or not p.is_file():continue
 digest=sha(p)
 if c.get('source_sha256')==digest:continue
 entry=changes.setdefault(c['source_path'],dict(path=c['source_path'],previous_hashes=[],current_sha256=digest,case_ids=[]))
 if c.get('source_sha256') not in entry['previous_hashes']:entry['previous_hashes'].append(c.get('source_sha256'))
 entry['case_ids'].append(c['id']);c['source_sha256']=digest
# Literal historical expectations remain intact. Current shared helper sources
# are retained separately from the original Git/evidence snapshots.
for p in (R/'audit').glob('*/FIXTURE-LIBRARY.json'):
 if p.parent==A:continue
 try:library=load(p)
 except ValueError:continue
 if not isinstance(library,dict):continue
 updated=False
 for key,row in library.items():
  if not isinstance(row,dict):continue
  source=row.get('source_path',key)
  if source in changes and (R/source).is_file():
   row['source_sha256']=sha(R/source);row['fixture_source']=(R/source).read_text();updated=True
 if updated:save(p,library)
save(C/'verification.json',g)
save(A/'SOURCE-PIN-CHANGES.json',dict(status='current_declarations_updated_not_behavior_acceptance',base='5900b4d50de4b52b89fd19b4598fd153b40e0e94',files=list(changes.values()),policy='Original observations are immutable. Per-case semantic invalidations and retained boundaries are in INVALIDATION.md; a current source declaration alone is never green evidence.'))
print(json.dumps(dict(updated_files=len(changes),updated_case_edges=sum(len(x['case_ids']) for x in changes.values()))))
