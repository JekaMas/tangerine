"""Preserve old clean observations only when exact semantic fingerprints agree."""
from pathlib import Path
from functools import lru_cache
import json,sys
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';E=C/'evidence'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def snap(root,patterns):return base(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snap(root,tuple(patterns))
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');paths=[E/'iteration4-verification'/n for n in ['i4-browser-repaired-clean.json','predecessors-repaired-clean.json','foundation-driver-clean.json']]
retained={};prior={}
for path in paths:
 v=json.loads(path.read_text());assert v['git']['status']=='known' and not v['git']['dirty']
 for id,row in v['cases'].items():
  prior[id]=str(path.relative_to(R))
  command=next(x for x in v['commands'] if x['id']==g.cases[id]['command_id'])
  if row['status']=='passed' and command['exit_code']==0 and row['evidence_fingerprint']==rt.case_evidence_fingerprint(g,id):retained[id]=str(path.relative_to(R))
required={id for id,c in g.cases.items() if c['property_id'].startswith(('I1-','I2-','I3-','I4-'))};assert len(required)==332
invalidated=sorted(required-set(retained));commands=sorted({g.cases[id]['command_id'] for id in invalidated})
output=dict(baseline='9f8faf5ab192a24b3a620545cf8568d975e6b190',semantic_inputs=['New canonical preparation/application HTTP/domain/entrypoint and embedded registries','Registered version projection repair','AI-development inventory data and consumer; literal native Lab source helper/expectations','Exact source/fixture/dependency bindings changed; no old receipts or hashes rewritten'],required_previous_cases=len(required),retained_valid_cases=retained,invalidated_cases=invalidated,invalidated_commands=commands,old_source_receipts=[str(p.relative_to(R)) for p in paths],proof_boundary='Retention checks current exact graph fingerprints against original clean receipts; invalidated siblings require actual new observations. No hosted quality evidence is inferred.')
(R/'audit/iteration-5-preparation-20261010/INVALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k not in ('retained_valid_cases','invalidated_cases','old_source_receipts')}));print('retained',len(retained),'invalidated',len(invalidated))
