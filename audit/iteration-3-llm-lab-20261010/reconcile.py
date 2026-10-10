"""Independent committed-clean receipt, native byte and unchanged-input readback."""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import base64,hashlib,json,shutil,sqlite3,subprocess,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;E=R/'openspec/changes/implement-teacher-error-trainer/evidence/iteration3'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
import requirement_tests as rt
original=rt.dependency_snapshot
@lru_cache(maxsize=None)
def snapshot(root,patterns):return original(root,list(patterns))
rt.dependency_snapshot=lambda root,patterns:snapshot(root,tuple(patterns))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify_receipt(graph,path,prefix,count):
 receipt=json.loads(path.read_text());selected={k:v for k,v in graph.cases.items() if v['property_id'].startswith(prefix)}
 assert len(selected)==count and set(receipt['cases'])==set(selected)
 assert receipt['status']=='passed' and receipt['git']['status']=='known' and not receipt['git']['dirty'] and not receipt['substitution_gaps']
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',receipt['git']['head'],head],cwd=R,check=True)
 commands={c['id']:c for c in receipt['commands']};counts={}
 for cid,c in commands.items():
  assert c['exit_code']==0 and c['status']=='exited' and c['argv']==graph.commands[cid]['argv']
  stdout=(E/Path(c['stdout_artifact']).name).read_text();stderr=(E/Path(c['stderr_artifact']).name).read_text();native=rt.parse_go_events(stdout) if graph.commands[cid]['runner']=='go-test-json' else rt.parse_unittest_events(stdout+'\n'+stderr)
  assert native==c['observed_tests'] and native and set(native.values())=={'pass'};counts[cid]=len(native)
 for cid,c in selected.items():
  observed=receipt['cases'][cid];assert observed['status']=='passed' and observed['test_id']==c['test_id'];assert commands[c['command_id']]['observed_tests'][c['test_id']]=='pass';assert sha(R/c['source_path'])==c['source_sha256'];assert rt.case_evidence_fingerprint(graph,cid)==observed['evidence_fingerprint'],cid
 return {'candidate':receipt['git']['head'],'receipt':str(path.relative_to(R)),'receipt_sha256':sha(path),'required_cases':count,'polarities':dict(Counter(c['polarity'] for c in selected.values())),'native_counts':counts}
def retain_native():
 source=R/'data/iteration3/native';dest=E/'actual';dest.mkdir(exist_ok=True)
 for p in source.iterdir():
  if p.is_file():shutil.copyfile(p,dest/p.name)
 with sqlite3.connect(dest/'actual-mlflow.db') as db:
  assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';runs={r[0] for r in db.execute('SELECT run_uuid FROM runs')};assert db.execute('SELECT count(*) FROM registered_models').fetchone()[0]==18;assert db.execute('SELECT count(*) FROM model_versions').fetchone()[0]==19;assert db.execute('SELECT count(*) FROM spans').fetchone()[0]==1
 for p in (source/'actual-artifacts').rglob('*'):
  if not p.is_file():continue
  run=next((x for x in p.parts if x in runs),None)
  if run is None:continue
  index=p.parts.index(run);target=dest/'mlflow-artifacts'/run/Path(*p.parts[index+1:]);target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert target.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,target)
 for name in ['actual-mlflow-export.json','development-lab-export.json']:
  packet=json.loads((dest/name).read_text())
  for artifact in packet['artifacts']:
   p=dest/'mlflow-artifacts'/artifact['run']/'artifacts'/artifact['artifact'];assert sha(p)==artifact['sha256']
 trace=json.loads((dest/'actual-otlp-trace.json').read_text());assert hashlib.sha256(base64.b64decode(trace['otlp_base64'])).hexdigest()==trace['native_sha256'];assert trace['provider_calls']==0 and trace['traces']==1
 rows=[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(dest.rglob('*')) if p.is_file()]
 (E/'NATIVE-ARTIFACTS.json').write_text(json.dumps({'origin':'Actual disposable PostgreSQL/MinIO/MLflow tooling and constructed deterministic diagnostics; zero model calls','files':rows},indent=2)+'\n')
def main():
 graph=rt.EvidenceGraph(R,'implement-teacher-error-trainer');lab=verify_receipt(graph,E/'clean.json','I3-',88);foundation=verify_receipt(graph,E/'clean-foundation.json','I1-',32);assert lab['candidate']==foundation['candidate']
 out={'status':'passed','candidate':lab['candidate'],'required_cases':120,'iteration3':lab,'affected_foundation':foundation,'proof_boundary':'Complete iteration3 tooling plus affected source-ZIP/build/launcher closure.21 model/speech execution surfaces remain planned; zero inference is N/A and does not certify AI integration or whole-product completion.'}
 path=E/'ACCEPTANCE.json'
 if sys.argv[1:]==['--check']:assert json.loads(path.read_text())==out
 else:
  assert not sys.argv[1:];retain_native();path.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out))
if __name__=='__main__':main()
