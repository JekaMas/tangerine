"""Reconcile exact native cases using retained valid and repaired clean observations."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import json,sys,subprocess,hashlib
R=Path(__file__).resolve().parents[2];A=R/'audit/iteration-5-preparation-20261010';E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration5-verification'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
base=rt.dependency_snapshot
@lru_cache(None)
def snapshot(root,patterns):return base(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(root,tuple(patterns))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=rt.EvidenceGraph(R,'implement-teacher-error-trainer');selection=json.loads((A/'FOUNDATION-REPAIR-SELECTION.json').read_text());new_path=E/'foundation-policy-clean.json';new=json.loads(new_path.read_text());assert new['status']=='passed' and new['git']['dirty'] is False
required={id for id,c in g.cases.items() if c['property_id'].startswith(('I1-','I2-','I3-','I4-','I5-'))};assert len(required)==376
assert set(new['cases'])==set(selection['invalidated_cases']) and len(new['cases'])==140
reports={str(new_path.relative_to(R)):new};results={};commands={};head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
for id in sorted(required):
 name=str(new_path.relative_to(R)) if id in new['cases'] else selection['retained_cases'][id]
 if name=='data/iteration5/single-admission-complete-clean.json':name=str((E/'single-admission-complete-clean.json').relative_to(R))
 if name not in reports:reports[name]=json.loads((R/name).read_text())
 report=reports[name];assert report['git']['status']=='known' and not report['git']['dirty'];subprocess.run(['git','merge-base','--is-ancestor',report['git']['head'],head],cwd=R,check=True)
 row=report['cases'][id];assert row['status']=='passed' and row['evidence_fingerprint']==rt.case_evidence_fingerprint(g,id),id
 case=g.cases[id]
 for field in ('test_id','property_id','polarity','scenario','scenario_fingerprint','setup','observable','red_expectation','green_expectation','invalidation_dependencies','source_path','source_sha256'):assert row[field]==case[field],(id,field)
 assert sha(R/case['source_path'])==case['source_sha256']
 cmd=next(x for x in report['commands'] if x['id']==case['command_id']);assert cmd['exit_code']==0 and cmd['status']=='exited';assert cmd['observed_tests'][case['test_id']]=='pass'
 key=(name,cmd['id'])
 if key not in commands:
  stdout_path=E/Path(cmd['stdout_artifact']).name;stderr_path=E/Path(cmd['stderr_artifact']).name
  if not stdout_path.exists():stdout_path=(R/name).parent/Path(cmd['stdout_artifact']).name;stderr_path=(R/name).parent/Path(cmd['stderr_artifact']).name
  stdout=stdout_path.read_text();stderr=stderr_path.read_text();observed=rt.parse_go_events(stdout) if g.commands[cmd['id']]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr)
  assert observed==cmd['observed_tests'] and observed and set(observed.values())=={'pass'};assert cmd['argv']==g.commands[cmd['id']]['argv'];commands[key]=len(observed)
 results[id]=dict(status='passed',test_id=case['test_id'],polarity=case['polarity'],receipt=name,evidence_fingerprint=row['evidence_fingerprint'],observation='repaired' if id in new['cases'] else 'retained')
output=dict(status='passed',full_iteration_status='blocked',candidate=new['git']['head'],required_native_cases=len(results),iteration5_cases=44,repaired_cases=140,retained_cases=236,polarities=dict(Counter(x['polarity'] for x in results.values())),iterations=dict(Counter(id.split('-')[0] for id in results)),native_commands=[dict(receipt=k[0],command=k[1],observed_tests=v) for k,v in commands.items()],cases=results,live_witness='audit/iteration-5-preparation-20261010/LIVE-BLOCKER.json',proof_boundary='All376 required native cases have exact current clean passed observations. The first372-case selection failed four legacy assertions in foundation/provider commands and remains failed; only its still-valid passed cases from successful commands contribute. All140 source/fixture/helper-dependent cases were repaired and passed a new committed-clean selection. Four original still-valid contract cases retain their historical clean receipts. Controlled HTTP provider replies do not establish hosted subscription admission, actual LLM linguistic quality, or mutation/audio/scoring functionality beyond this stage. Full hosted iteration5 acceptance remains blocked.')
if sys.argv[1:]==['--check']:assert json.loads((E/'NATIVE-VERIFICATION.json').read_text())==output
else:
 assert not sys.argv[1:];(E/'NATIVE-VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');(A/'NATIVE-VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='cases'},indent=2))
