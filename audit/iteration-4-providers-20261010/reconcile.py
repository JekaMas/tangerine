"""Reparse native committed-clean observations; no failed/missing case counts green."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration4'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def snapshot(root,patterns):return base(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(root,tuple(patterns))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer');required={k:v for k,v in graph.cases.items() if v['property_id'].startswith(('I1-','I2-','I3-','I4-'))};assert len(required)==320
 names=json.loads((E/'RECEIPTS.json').read_text());observed={};commands={};sources=[];candidate=None
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 candidate=json.loads((E/names[-1]).read_text())['git']['head'];invalidated=[]
 for name in reversed(names):
  path=E/name;receipt=json.loads(path.read_text());pin=receipt['git'];assert pin['status']=='known' and not pin['dirty'];subprocess.run(['git','merge-base','--is-ancestor',pin['head'],candidate],cwd=R,check=True)
  subprocess.run(['git','merge-base','--is-ancestor',candidate,head],cwd=R,check=True)
  assert not receipt['substitution_gaps'];assert set(receipt['cases'])<=set(required);count=0
  rows={c['id']:c for c in receipt['commands']}
  for key,c in rows.items():
   assert c['argv']==graph.commands[key]['argv'];stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text()
   tests=rt.parse_go_events(stdout) if graph.commands[key]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr);assert tests==c['observed_tests']
   if c['exit_code']==0 and c['status']=='exited':
    assert tests and set(tests.values())=={'pass'};commands.setdefault(key,len(tests))
  for key,row in receipt['cases'].items():
   if row['status']!='passed':continue
   case=required[key];command=rows[case['command_id']]
   if command['exit_code']!=0 or command['status']!='exited':continue
   if rt.case_evidence_fingerprint(graph,key)!=row['evidence_fingerprint']:
    invalidated.append({'case':key,'receipt':name});continue
   if key in observed:continue
   assert command['observed_tests'][case['test_id']]=='pass'
   for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(key,field)
   assert sha(R/case['source_path'])==case['source_sha256'];assert rt.case_evidence_fingerprint(graph,key)==row['evidence_fingerprint'],key
   observed[key]=name;count+=1
  sources.append(dict(receipt=name,sha256=sha(path),original_status=receipt['status'],accepted_cases=count))
 assert set(observed)==set(required)
 out=dict(status='passed',full_iteration_status='blocked',candidate=candidate,required_cases=320,iteration4_cases=128,affected_previous_cases=192,polarities=dict(Counter(c['polarity'] for c in required.values())),native_counts=commands,receipts=sources,invalidated_historical_greens=invalidated,proof_boundary='Complete registered native provider and affected I1/I2/I3 behavior. Remote OAuth/model/inference responses are explicit test-owned protocol substitutions; no hosted admission, actual model quality or full iteration acceptance. LIVE-BLOCKER.json records missing live observations.')
 target=E/'NATIVE-VERIFICATION.json'
 if sys.argv[1:]==['--check']:assert json.loads(target.read_text())==out
 else:assert not sys.argv[1:];target.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
