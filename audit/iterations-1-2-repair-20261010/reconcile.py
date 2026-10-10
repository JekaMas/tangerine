"""Readback audit for both iterations' native committed-clean repair acceptance."""
from pathlib import Path
from collections import Counter
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';E=C/'evidence/iterations12-repair'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import EvidenceGraph,case_evidence_fingerprint,parse_go_events,parse_unittest_events
import requirement_tests
from functools import lru_cache
# One readback audit observes a stable source batch; repeated identical dependency
# selectors share the exact snapshot, without changing the pinned workflow.
_original_snapshot=requirement_tests.dependency_snapshot
@lru_cache(maxsize=None)
def _snapshot(root,patterns):return _original_snapshot(root,list(patterns))
requirement_tests.dependency_snapshot=lambda root,patterns:_snapshot(root,tuple(patterns))

def main():
 graph=EvidenceGraph(R,'implement-teacher-error-trainer');p=E/'clean-full.json';receipt=json.loads(p.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 selected={k:v for k,v in graph.cases.items() if v['property_id'].startswith(('I1-','I2-'))}
 assert len(selected)==104 and set(receipt['cases'])==set(selected)
 assert receipt['status']=='passed' and receipt['git']['status']=='known' and not receipt['git']['dirty']
 subprocess.run(['git','merge-base','--is-ancestor',receipt['git']['head'],head],cwd=R,check=True)
 assert not receipt['substitution_gaps']
 commands={c['id']:c for c in receipt['commands']};counts={}
 for cid,c in commands.items():
  assert c['exit_code']==0 and c['status']=='exited'
  stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text()
  native=parse_go_events(stdout) if graph.commands[cid]['runner']=='go-test-json' else parse_unittest_events(stdout+'\n'+stderr)
  assert native==c['observed_tests'] and native and set(native.values())=={'pass'}
  assert c['argv']==graph.commands[cid]['argv'];counts[cid]=len(native)
 cases={}
 for cid,c in selected.items():
  observation=receipt['cases'][cid]
  assert observation['status']=='passed' and observation['test_id']==c['test_id']
  assert commands[c['command_id']]['observed_tests'][c['test_id']]=='pass'
  assert hashlib.sha256((R/c['source_path']).read_bytes()).hexdigest()==c['source_sha256']
  assert case_evidence_fingerprint(graph,cid)==observation['evidence_fingerprint'],cid
  cases[cid]={'status':'passed','test_id':c['test_id'],'polarity':c['polarity'],'evidence_fingerprint':observation['evidence_fingerprint']}
 out={'status':'passed','candidate':receipt['git']['head'],'required_cases':104,'polarities':dict(Counter(c['polarity'] for c in selected.values())),'native_counts':counts,'receipt':str(p.relative_to(R)),'receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof_boundary':'Both complete iteration1/2 selections and all repaired findings; later trainer/provider/speech/scoring features remain pending.','cases':cases}
 assert out['polarities']=={'negative':52,'positive':52}
 dest=E/'ACCEPTANCE.json'
 if sys.argv[1:]==['--check']:assert json.loads(dest.read_text())==out
 else:
  assert not sys.argv[1:];dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
if __name__=='__main__':main()
