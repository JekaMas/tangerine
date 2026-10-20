"""Reparse disjoint clean graph selections and their actual native test events."""
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
 graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer')
 groups={'lab':('lab-native.json',{'iteration3-go','iteration3-native'}),'provider':('provider-native.json',{'iteration4-go'}),'preparation':('preparation-native.json',{'iteration5-go','iteration5-native'}),'mutation-go':('mutation-before-watchdog.json',{'iteration6-go'}),'mutation-native':('mutation-native.json',{'iteration6-native'})}
 command_ids=set().union(*(ids for _,ids in groups.values()));required={k:v for k,v in graph.cases.items() if v['command_id'] in command_ids};assert len(required)==308
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();observed={};pins=set();seen=set();receipts=[]
 for name,(filename,ids) in groups.items():
  path=E/filename;receipt=json.loads(path.read_text());pin=receipt['git'];assert pin['status']=='known' and not pin['dirty'] and not receipt['substitution_gaps'];assert receipt['status']=='passed' or name=='mutation-go'
  pins.add(pin['head']);subprocess.run(['git','merge-base','--is-ancestor',pin['head'],head],cwd=R,check=True)
  selected={k:v for k,v in required.items() if v['command_id'] in ids};assert (set(receipt['cases']).issuperset(selected) if name=='mutation-go' else set(receipt['cases'])==set(selected));assert not seen.intersection(selected);seen.update(selected)
  assert receipt['manifest_sha256']==hashlib.sha256(graph.manifest_path.read_bytes()).hexdigest()
  commands={x['id']:x for x in receipt['commands'] if x['id'] in ids};assert set(commands)==ids
  for key,c in commands.items():
   assert c['argv']==graph.commands[key]['argv'];stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text();tests=rt.parse_go_events(stdout) if graph.commands[key]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr)
   assert tests==c['observed_tests'];assert c['exit_code']==0 and c['status']=='exited' and tests and set(tests.values())=={'pass'};observed[key]=len(tests)
  for key in selected:
   row=receipt['cases'][key]
   case=selected[key];assert row['status']=='passed';assert commands[case['command_id']]['observed_tests'][case['test_id']]=='pass'
   for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(key,field)
   assert hashlib.sha256((R/case['source_path']).read_bytes()).hexdigest()==case['source_sha256'];assert rt.case_evidence_fingerprint(graph,key)==row['evidence_fingerprint'],key
  receipts.append({'selection':name,'artifact':path.name,'candidate':pin['head'],'aggregate_status':receipt['status'],'retained_unchanged_command':name=='mutation-go','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'registered_cases':len(selected)})
 assert seen==set(required)
 out={'status':'passed','candidate':receipts[-1]['candidate'],'source_revisions':sorted(pins),'receipts':receipts,'registered_cases':308,'iteration6_cases':88,'preparation_dependency_cases':48,'lab_dependency_cases':88,'provider_dependency_cases':84,'polarities':dict(Counter(c['polarity'] for c in required.values())),'actual_test_identities':observed,'proof_boundary':'Committed-clean graph observations cover the complete iteration6 set and its selected dependency closure. Unchanged companion-command greens are retained from the interrupted aggregate only when their command, cases, source and dependency fingerprints still match; every interrupted native case is supplied by the repaired native run. All tested revisions are ancestors of this checkout. Native PostgreSQL/MinIO/HTTP/Go observations retain explicit controlled model replies. Actual local model quality/context/MLflow observations are separate. No hosted entitlement, all122 empirical quality, speech, grading or full-product acceptance is asserted.'}
 target=E/'NATIVE-VERIFICATION.json'
 if sys.argv[1:]==['--check']:assert json.loads(target.read_text())==out
 else:assert not sys.argv[1:];target.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
