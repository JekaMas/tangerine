"""Reparse the selected committed-clean native receipt; no inferred passes."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration6-review-20261020'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def snapshot(root,patterns):return base(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(root,tuple(patterns))
def main():
 graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer');command_ids={'iteration3-go','iteration3-native','iteration4-go','iteration5-go','iteration5-native','iteration6-go','iteration6-native'}
 required={k:v for k,v in graph.cases.items() if v['command_id'] in command_ids};assert len(required)==292
 path=E/'committed-native.json';receipt=json.loads(path.read_text());pin=receipt['git'];assert pin['status']=='known' and not pin['dirty'] and receipt['status']=='passed' and not receipt['substitution_gaps']
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',pin['head'],head],cwd=R,check=True)
 assert set(receipt['cases'])==set(required);assert receipt['manifest_sha256']==hashlib.sha256(graph.manifest_path.read_bytes()).hexdigest()
 commands={x['id']:x for x in receipt['commands']};assert set(commands)==command_ids;observed={}
 for key,c in commands.items():
  assert c['argv']==graph.commands[key]['argv'];stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text();tests=rt.parse_go_events(stdout) if graph.commands[key]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr)
  assert tests==c['observed_tests'];assert c['exit_code']==0 and c['status']=='exited' and tests and set(tests.values())=={'pass'};observed[key]=len(tests)
 for key,row in receipt['cases'].items():
  case=required[key];assert row['status']=='passed';assert commands[case['command_id']]['observed_tests'][case['test_id']]=='pass'
  for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(key,field)
  assert hashlib.sha256((R/case['source_path']).read_bytes()).hexdigest()==case['source_sha256'];assert rt.case_evidence_fingerprint(graph,key)==row['evidence_fingerprint'],key
 out={'status':'passed','candidate':pin['head'],'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'registered_cases':292,'iteration6_cases':72,'preparation_dependency_cases':48,'lab_dependency_cases':88,'provider_dependency_cases':84,'polarities':dict(Counter(c['polarity'] for c in required.values())),'actual_test_identities':observed,'proof_boundary':'Exact registered production-bound native/Go observations on the committed candidate; controlled remote response fixtures are explicit. Actual local model quality and MLflow reconciliation are separate LOCAL-OBSERVATIONS.json evidence. Later rendering/listening/scoring and hosted account admission are not asserted.'}
 target=E/'NATIVE-VERIFICATION.json'
 if sys.argv[1:]==['--check']:assert json.loads(target.read_text())==out
 else:assert not sys.argv[1:];target.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
