"""Join original clean passes with the exact invalidated-case clean repair.
Never modifies either source receipt or replaces its original fingerprint.
"""
from pathlib import Path
import collections,hashlib,json,subprocess,re
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());g=load(R/'openspec/changes/implement-teacher-error-trainer/verification.json');selection=load(A/'SELECTION.json');scope=load(A/'REPAIR-SELECTION.json');prior=load(R/'data/iteration15/acceptance-clean.json');repair=load(R/'data/iteration15/acceptance-repair.json');fresh=set(scope['fresh']);expected=set(selection['selection']['cases'])
assert len(expected)==74 and set(prior['cases'])==expected and set(repair['cases'])==fresh
assert prior['git']['dirty'] is False and repair['git']['dirty'] is False and repair['status']=='passed'
assert not prior['substitution_gaps'] and not repair['substitution_gaps']
# Only fixture capture/evidence metadata changed after the complete run.
changed=subprocess.check_output(['git','diff','--name-only',prior['git']['head'],repair['git']['head']],cwd=R,text=True).splitlines()
assert not any(p.startswith(('services/','scripts/','deploy/')) for p in changed),changed
old_graph=json.loads(subprocess.check_output(['git','show',prior['git']['head']+':openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=R));old_cases={c['id']:c for c in old_graph['cases']};current={c['id']:c for c in g['cases']};out={}
for cid in sorted(expected):
 source=repair if cid in fresh else prior;row=source['cases'][cid];assert row['status']=='passed',(cid,row['status'])
 now=selection['nodes']['cases'][cid]['current_evidence_fingerprint']
 if cid in fresh:assert row['evidence_fingerprint']==now
 else:
  old=old_cases[cid];new=current[cid];assert old['test_id']==new['test_id'];assert old['scenario_fingerprint']==new['scenario_fingerprint'];assert old['command_id']==new['command_id']
  assert json.loads(old['observable'])['independent_literal_assertions']==json.loads(new['observable'])['independent_literal_assertions']
  assert next(c for c in old_graph['commands'] if c['id']==old['command_id'])==next(c for c in g['commands'] if c['id']==new['command_id'])
 out[cid]={'status':'passed','test_id':row['test_id'],'source_revision':source['git']['head'],'source_receipt':'data/iteration15/acceptance-repair.json' if cid in fresh else 'data/iteration15/acceptance-clean.json','original_evidence_fingerprint':row['evidence_fingerprint'],'current_evidence_fingerprint':now,'retained':cid not in fresh,'reason':'Fresh directly affected native capture or actual local MLflow observation.' if cid in fresh else 'Original committed-clean exact test passed. Production, assertion, exercised command and used fixture semantics unchanged; unused shared capture helper/file metadata changes are explicitly retained.'}
lab_pointer=load(R/'data/iteration15/receipts/lab-current.json');lab=load(R/lab_pointer['result']);assert lab_pointer['source_revision']==repair['git']['head'];assert lab['status']=='observed' and lab['artifact_exact'] and lab['missing_artifact_rejected']
counts=collections.Counter(current[c]['polarity'] for c in expected)
result={'status':'passed','iteration':15,'scope':'Recovery and complete usability only','properties':selection['selection']['properties'],'requirements':selection['selection']['requirements'],'case_edges':74,'registered_physical_tests':len({out[c]['test_id'] for c in out}),'polarities':dict(counts),'retained_clean_edges':len(expected-fresh),'fresh_clean_edges':len(fresh),'source_executions':[{'receipt':'data/iteration15/acceptance-clean.json','git':prior['git'],'status':prior['status'],'original_passes':70,'original_failures':4},{'receipt':'data/iteration15/acceptance-repair.json','git':repair['git'],'status':repair['status'],'passes':4}],'manifest_sha256':hashlib.sha256((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_bytes()).hexdigest(),'cases':out,'actual_local_mlflow':lab,'mlflow_private_result':lab_pointer['result'],'retention_proof':str((A/'REPAIR-SELECTION.json').relative_to(R)),'production_changes_after_full_run':[],'preservation':load(A/'PRESERVATION.json'),'language':load(A/'LANGUAGE.json'),'limits':['Constructed text/speech responses and PCM prove their labelled native coordination/storage/Chrome boundaries, not actual model or accent quality.','No trusted prompt, model, speech controller or native scoring semantics changed; prior actual stage/model observations retain their original proof scope.','Actual local MLflow records deterministic control evidence, two constructed text dispatches/two text receipts/two snapshots and one constructed speech dispatch/receipt; genuine inference calls are zero.','Unchanged cached speech runtime reused; no fresh cold dependency rebuild or architecture matrix is inferred.','Earlier I8/I12 acceptance and whole-product release remain outside this iteration.']}
(A/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n');(R/'data/iteration15/acceptance-reconciled.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','case_edges','registered_physical_tests','polarities','retained_clean_edges','fresh_clean_edges']}))
