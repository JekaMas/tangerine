from pathlib import Path
from functools import lru_cache
import json,sys
R=Path(__file__).resolve().parents[2]; A=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.agents/workflow/scripts')); import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def cached(root,paths):return base(root,list(paths))
rt.dependency_snapshot=lambda root,paths:cached(root,tuple(paths))
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer'); old=json.loads((R/'audit/iteration-5-preparation-20261010/NATIVE-VERIFICATION.json').read_text()); retained={}; invalid=[]
for id,row in old['cases'].items():
 if id.startswith('I5-'):continue
 if row['evidence_fingerprint']==rt.case_evidence_fingerprint(g,id):retained[id]=row
 else:invalid.append(id)
result=dict(semantic_inputs=['preparation.go: immutable operation result replay replaces current-head readback','native_preparation_test.go: four independently asserted replay scenarios','I5-12 native replay property and literal fixture/DAG bindings'],required_native_cases=len(old['cases'])+4,iteration5_cases=48,retained=retained,invalidated_predecessor_cases=sorted(invalid),invalidated_predecessor_commands=sorted({g.cases[id]['command_id'] for id in invalid}),iteration5_properties=[id for id in g.properties if id.startswith('I5-')],proof_boundary='Declared dependency closures invalidate exact current receipts. No previous receipt is rewritten. The original four standalone contract cases remain valid.')
(A/'SELECTION.json').write_text(json.dumps(result,indent=2)+'\n');print('retained',len(retained),'invalidated predecessors',len(invalid),'I5',48);print(result['invalidated_predecessor_commands'])
