"""Reconcile current native cases without rewriting any observation."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];A=R/'audit/iteration-5-verification-20261010';E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration5-review'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def cached(root,paths):return base(root,list(paths))
rt.dependency_snapshot=lambda root,paths:cached(root,tuple(paths))
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');selection=json.loads((A/'SELECTION.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();reports={};checked={};results={}
required={id for id in g.cases if id.startswith(('I1-','I2-','I3-','I4-','I5-'))};assert len(required)==380
own=str((E/'i5-own-clean.json').relative_to(R));previous=str((E/'predecessors-clean.json').relative_to(R))
lab=str((E/'lab-clean.json').relative_to(R))
for path in (own,previous,lab):
 v=json.loads((R/path).read_text());assert v['git']['dirty'] is False;assert v['status']==('failed' if path==previous else 'passed');reports[path]=v
assert set(reports[own]['cases'])=={id for id in required if id.startswith('I5-')} and len(reports[own]['cases'])==48
assert set(reports[previous]['cases'])==set(selection['invalidated_predecessor_cases']) and len(reports[previous]['cases'])==136
assert len(reports[lab]['cases'])==36 and all(g.cases[id]['command_id']=='iteration3-native' for id in reports[lab]['cases'])
for id in sorted(required):
 receipt=own if id.startswith('I5-') else lab if id in reports[lab]['cases'] else previous if id in selection['invalidated_predecessor_cases'] else selection['retained'][id]['receipt']
 if receipt not in reports:reports[receipt]=json.loads((R/receipt).read_text())
 report=reports[receipt];assert report['git']['status']=='known' and not report['git']['dirty'];subprocess.run(['git','merge-base','--is-ancestor',report['git']['head'],head],cwd=R,check=True)
 row=report['cases'][id];case=g.cases[id];assert row['status']=='passed' and row['evidence_fingerprint']==rt.case_evidence_fingerprint(g,id),(id,'fingerprint')
 for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(id,field)
 assert hashlib.sha256((R/case['source_path']).read_bytes()).hexdigest()==case['source_sha256']
 command=next(v for v in report['commands'] if v['id']==case['command_id']);assert command['exit_code']==0 and command['status']=='exited' and command['observed_tests'][case['test_id']]=='pass'
 key=(receipt,command['id'])
 if key not in checked:
  folder=(R/receipt).parent;stdout=folder/Path(command['stdout_artifact']).name;stderr=folder/Path(command['stderr_artifact']).name
  if not stdout.exists():
   folder=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration5-verification';stdout=folder/Path(command['stdout_artifact']).name;stderr=folder/Path(command['stderr_artifact']).name
  a=stdout.read_text();b=stderr.read_text();observed=rt.parse_go_events(a) if g.commands[command['id']]['runner']=='go-test-json' else rt.parse_unittest_events(a+'\n'+b)
  assert observed==command['observed_tests'] and set(observed.values())=={'pass'};assert command['argv']==g.commands[command['id']]['argv'];checked[key]=len(observed)
 results[id]={'status':'passed','test_id':case['test_id'],'polarity':case['polarity'],'receipt':receipt,'evidence_fingerprint':row['evidence_fingerprint'],'observation':'retained' if id in selection['retained'] else 'new'}
result={'native_status':'passed','full_iteration_status':'blocked','candidate':reports[own]['git']['head'],'native_cases':380,'iteration5_cases':48,'new_observations':184,'retained_observations':196,'polarities':dict(Counter(v['polarity'] for v in results.values())),'commands':[{'receipt':k[0],'command':k[1],'observed_tests':v} for k,v in checked.items()],'cases':results,'live_witness':'audit/iteration-5-verification-20261010/LIVE-READBACK.json','proof_boundary':'The complete48-case own I5 selection passed on a clean committed revision. The affected136 predecessor selection retained100 passed cases from successful commands, but remains failed because Lab startup reached zero cases while its port was occupied. Those36 cases passed their own clean rerun after pausing/restoring the unchanged preview Lab.196 exact unchanged predecessor observations are retained. Native fixtures substitute only remote model protocol and do not prove actual included-only hosted generation, linguistic quality or hosted MLflow observations. Missing own grant/model and current unsuccessful API HTTPS probe keep full hosted acceptance blocked.'}
p=A/'NATIVE-VERIFICATION.json'
if sys.argv[1:]==['--check']:assert json.loads(p.read_text())==result
else:
 assert not sys.argv[1:];p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','commands')},indent=2))
