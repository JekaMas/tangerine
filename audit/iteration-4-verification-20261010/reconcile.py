"""Reparse the two full clean native selections and exact current fingerprints."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration4-verification'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def snapshot(root,patterns):return base(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(root,tuple(patterns))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer');required={k:v for k,v in graph.cases.items() if v['property_id'].startswith(('I1-','I2-','I3-','I4-'))};assert len(required)==332
 names=['i4-browser-repaired-clean.json','predecessors-repaired-clean.json','foundation-driver-clean.json'];observed={};commands={};sources=[];candidate=None;head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 for name in names:
  path=E/name;receipt=json.loads(path.read_text());pin=receipt['git'];assert pin['status']=='known' and not pin['dirty'];assert receipt['status']==('passed' if name=='foundation-driver-clean.json' else 'failed');candidate=pin['head'];subprocess.run(['git','merge-base','--is-ancestor',candidate,head],cwd=R,check=True)
  assert not receipt['substitution_gaps'];assert set(receipt['cases'])<=set(required);rows={c['id']:c for c in receipt['commands']}
  for key,c in rows.items():
   if name=='i4-browser-repaired-clean.json' and key=='iteration4-native':continue
   if name=='predecessors-repaired-clean.json' and key in ('iteration1-native','iteration2-native'):continue
   assert c['argv']==graph.commands[key]['argv'];stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text();tests=rt.parse_go_events(stdout) if graph.commands[key]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr);assert tests==c['observed_tests'];assert c['exit_code']==0 and c['status']=='exited';assert tests and set(tests.values())=={'pass'};commands[key]=len(tests)
  for key,row in receipt['cases'].items():
   if name=='i4-browser-repaired-clean.json' and required[key]['command_id']=='iteration4-native':continue
   if name=='predecessors-repaired-clean.json' and required[key]['command_id'] in ('iteration1-native','iteration2-native'):continue
   assert row['status']=='passed';case=required[key];command=rows[case['command_id']];assert command['observed_tests'][case['test_id']]=='pass';assert rt.case_evidence_fingerprint(graph,key)==row['evidence_fingerprint'],key
   for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(key,field)
   assert sha(R/case['source_path'])==case['source_sha256'];assert key not in observed;observed[key]=name
  sources.append(dict(receipt=name,sha256=sha(path),status=receipt['status'],cases=len(receipt['cases']),retained_passed_cases=sum(v==name for v in observed.values())))
 assert set(observed)==set(required)
 assert set(json.loads((E/names[0]).read_text())['cases'])=={k for k,v in required.items() if v['property_id'].startswith('I4-')}
 assert len(json.loads((E/names[1]).read_text())['cases'])==192
 assert len(json.loads((E/names[2]).read_text())['cases'])==100
 out=dict(status='passed',full_iteration_status='blocked',candidate=candidate,required_cases=332,iteration4_cases=140,affected_previous_cases=192,polarities=dict(Counter(c['polarity'] for c in required.values())),native_counts=commands,receipts=sources,proof_boundary='Complete own 140-case committed-clean selection retained as its actual failed receipt; 232 exact current clean passed cases retained, all 100 invalidated foundation/storage/browser native cases repaired/rerun clean. The predecessor 192-case selection failed its separate Chrome dump-dom case, remains failed, and contributes only its still-valid 108 passed cases. No failed command or obsolete native case counts as green. Metadata repository and remote protocol substitutions are explicit; own ChatGPT admission, credit exclusion, account catalogue and included-only hosted inference remain unobserved. No full iteration acceptance claimed.')
 target=E/'NATIVE-VERIFICATION.json'
 if sys.argv[1:]==['--check']:assert json.loads(target.read_text())==out
 else:assert not sys.argv[1:];target.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
