"""Exact repair DAG bindings; historical receipts remain unchanged."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'domain/verification-fixtures.v1.json');sets=load(V/'domain/property-test-sets.v1.json');inventory=load(C/'property-inventory.json');d=load(C/'discovery.json')
rows=[('I2-15','Guarded upload progress does not need an additional pool connection','services/api/internal/app/assets.go','I2-08',[
 ('TestNativePoolSameAssetPositive','positive',{'bytes':'review','winner':'blocked native reader','duplicate_waiters':9,'pool_capacity':10},{'winner':'success','all_waiters':'success','linked_bytes':'review'}),
 ('TestNativePoolDistinctAssetsPositive','positive',{'bytes':'review','concurrent_assets':20,'pool_capacity':10},{'all_verified':20,'all_linked_readbacks':'review'}),
 ('TestNativePoolCancelledWaiterNegative','negative',{'bytes':'review','blocked_winner':True,'waiter_timeout_ms':100},{'waiter':'rejected','winner':'success','next_upload':'success without leaked lock'}),
 ('TestNativePoolWrongBytesNegative','negative',{'intended':'review','wrong':'wrong!','concurrent_rejections':20},{'all_rejected':True,'object_after_rejection':'NoSuchKey','valid_upload_after':'success'})]),
 ('I2-16','Evidence-parent DAG roles and graph invariants apply to every document publication','services/api/internal/app/domain.go','I2-04',[
 ('TestNativeGraphEvidenceAcyclicPositive','positive',{'child_before_parent':True,'typed_evidence_parent_relation':'parent-evidence'},{'both_readback':'success'}),
 ('TestNativeGraphLinkAcyclicPositive','positive',{'owner_revision':0,'new_asset_reference':'asset-bytes','parent':'old immutable case'},{'link':'success','owner_revision':1}),
 ('TestNativeGraphParentRoleNegative','negative',{'self_parent_relations':['parent','parent-evidence'],'two_node_cycle':True},{'each_rejected':'reference_error','cycle_documents':0}),
 ('TestNativeGraphLinkCycleNegative','negative',{'self_cycle_owner':True,'then_bad_envelope':'bad-envelope'},{'link_rejected':'reference_error','asset_state':'bytes_verified','owner_revision':0,'new_document_count':0,'bad_envelope':'rejected'})]),
 ('I2-17','Interrupted multipart failure retains immutable lineage and explicit new-key retry','services/api/internal/app/multipart.go','I2-09',[
 ('TestNativeRecoveryCompletedPositive','positive',{'completed_native_object':'review','reservation_state':'reserved'},{'recovered':'bytes_verified','linked_readback':'review'}),
 ('TestNativeRecoveryRetryPositive','positive',{'partial_native_part':'rev','intended':'review','reopen_storage':True,'explicit_new_key':True},{'original_state':'failed','asset_state':'orphaned','typed_error_and_asset_result':'same after reopen and repeat recovery','old_upload_id':'NoSuchUpload','retry':'different asset/operation, idempotent, linked','original_receipt':'unchanged'}),
 ('TestNativeRecoveryOldKeyNegative','negative',{'partial_native_part':'rev','old_key_repeat':True,'old_asset_upload_and_link':True},{'reservation':'same orphaned asset','old_upload_link':'asset_unavailable','same_key_retry':'conflict','original':'failed with saved error and result'}),
 ('TestNativeRecoveryChangedIntentNegative','negative',{'changed_retry_fields':['path','body','query','sha','size','mime','purpose','revision']},{'each_rejected':'conflict','new_operation_rows':0})]),
 ('I2-18','Readiness verifies enabled exact immutability guards and recovers after repair','services/api/internal/app/storage.go','I2-12',[
 ('TestNativeGuardEnabledPositive','positive',{'guards':'original enabled bindings','document_update':'{}'},{'readiness':'ready','immutable_update':'rejected','readiness_after':'ready'}),
 ('TestNativeGuardRestoredPositive','positive',{'document_guard':'disable then ENABLE ALWAYS'},{'disabled':'not ready','restored':'ready'}),
 ('TestNativeGuardDisabledNegative','negative',{'disabled_guards':['document_immutable','audit_immutable','schema_immutable','migration_backup_immutable']},{'each':'not ready','restored':'ready'}),
 ('TestNativeGuardMisboundNegative','negative',{'function_body':'no-op RETURN NEW','then_function_binding':'regression_guard'},{'each':'not ready','restored':'ready'})])]
if any(p['id']=='I2-15.P1' for p in g['properties']):raise SystemExit('Already registered')
path=C/'specs/iteration-two-storage/spec.md';text=path.read_text()
for rid,title,owner,parent,cases in rows:
 text+=f'\n### Requirement: {rid} {title}\n\nThe storage owner SHALL preserve this invariant through {owner}. Parent obligation: {parent}; the approved persistence and runtime/storage contracts remain unchanged.\n\n'
 for packet in [1,2]:text+=f'#### Scenario: {rid} repair packet {packet}\n\n- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet {packet} executes\n- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state\n\n'
path.write_text(text);specs=parse_delta_specs(C);source='tests/native_storage_regression_test.go';newprops=[];newtests=[];plans=[]
for rid,title,owner,parent,cases in rows:
 pid=rid+'.P1';rt=rid+' '+title;spec=specs['iteration-two-storage',rt];scenarios=list(spec['scenarios']);newprops.append(pid)
 oracle='Literal UTF8 native bytes and independent SHA256; actual shared production pool, native multipart identity, exact SQL committed rows/revisions/receipts and frozen guard identity. No test double or LLM observation.'
 g['requirements'].append({'id':rid,'capability':'iteration-two-storage','title':rt,'fingerprint':spec['fingerprint']})
 g['properties'].append({'id':pid,'requirement_id':rid,'statement':title,'scenarios':scenarios,'owner':owner,'oracle':oracle,'source_globs':[owner,'services/api/**',source,'tests/native-storage-regressions']})
 inventory.append({'id':rid,'capability':'iteration-two-storage','title':rt,'statement':title,'scenarios':scenarios,'owner':owner,'source':'Authorized both-iteration repair, 2026-10-10; all wider features preserved.'})
 pos=[];neg=[]
 for j,(name,pol,input,expected) in enumerate(cases):
  packet=1 if j in [0,2] else 2;cid=f'{pid}.S{packet}.{pol.upper()}';fid=f'iteration2-repair-{rid}-packet{packet}';scenario=scenarios[packet-1];tid='tangerine.local/api/internal/app::'+name;newtests.append(tid)
  plan={'case_id':cid,'property_id':pid,'polarity':pol,'scenario':scenario,'fixture_id':fid,'test_id':tid,'mode':'declared_behavior','action':'Execute '+name+' through native production owner.','initial_state':{'fresh_disposable_postgres_minio':True,'provider_calls':0},'input':input,'expected':expected,'independent_oracle':oracle,'observation_state':'not_run','existing_case_state':'implemented','historical_receipt_not_reused_as_new_fixture_observation':True}
  plans.append(plan);f['case_bindings'].append(plan);fixture=next((x for x in f['fixtures'] if x['id']==fid),None)
  if fixture is None:fixture={'id':fid,'action':plan['action'],'initial_state':plan['initial_state'],'independent_oracle':oracle,'origin':'constructed_native_storage_regression'};f['fixtures'].append(fixture)
  fixture[pol]={'input':input,'expected':expected}
  g['cases'].append({'id':cid,'property_id':pid,'polarity':pol,'scenario':scenario,'scenario_fingerprint':spec['scenario_fingerprints'][scenario],'setup':plan['action']+' '+json.dumps(input,sort_keys=True),'observable':json.dumps(expected,sort_keys=True),'red_expectation':'Any false success, deadlock, accepted cycle, partial commit, lost failure lineage or wrong guard readiness fails.','green_expectation':'All independently specified bytes, database state and native object observations agree.','test_id':tid,'command_id':'iteration2-repair-native','state':'implemented','source_path':source,'source_sha256':hashlib.sha256((R/source).read_bytes()).hexdigest(),'invalidation_dependencies':['services/api','deploy/local/minio.Dockerfile','deploy/local/probe.go',source,'tests/native-storage-regressions','specification/v2/contracts'],'substitution':{'classification':'NO_TEST_DOUBLE','note':oracle},'designed_fixture_id':fid,'fixture_observation_state':'not_run'});(pos if pol=='positive' else neg).append(cid)
 f['property_bindings'].append({'property_id':pid,'fixture_id':f'iteration2-repair-{rid}-packet1','statement':title,'independent_oracle':oracle,'scenarios':scenarios,'observation_state':'not_run'})
 sets['properties'].append({'property_id':pid,'requirement_id':rid,'owner':owner,'scenario_names':scenarios,'positive_cases':pos,'negative_cases':neg,'proof_boundary':'Native iteration1/2 storage infrastructure only, no later trainer semantics.','runtime_set_observation':'not_run','positive_distinct_packets':2,'negative_distinct_packets':2})
g['commands'].append({'id':'iteration2-repair-native','runner':'go-test-json','argv':['./tests/native-storage-regressions', 'test', '-json', '-race', '-count=1', './internal/app'],'cwd':'.','env':{},'timeout_seconds':600,'authority':'local'})
invalid=[]
for case in g['cases']:
 if case['state']=='implemented' and case['property_id'].startswith(('I1-','I2-')) and case['property_id'] not in newprops:
  invalid.append({'case_id':case['id'],'previous':dict(case),'reason':'Actual shared storage/domain/asset/recovery/readiness production inputs changed; test_iteration2.py now observes durable failed receipt and explicit new-key retry; combined closure must be re-observed.'})
  case['source_sha256']=hashlib.sha256((R/case['source_path']).read_bytes()).hexdigest()
# Correct the previously weakened terminal-recovery oracle; retain old row above.
terminal=next(b for b in f['case_bindings'] if b['case_id']=='I2-09.P1.S2.NEGATIVE');terminal['expected']['partial_recovery_state']='orphaned';terminal['expected'].update(operation_state='failed',error_and_result_receipts=True,explicit_new_key_retry='linked with old failure retained')
next(x for x in f['fixtures'] if x['id']==terminal['fixture_id'])['negative']['expected']=terminal['expected']
c=next(c for c in g['cases'] if c['id']==terminal['case_id']);c['observable']='Compare actual observations with '+json.dumps(terminal['expected'],sort_keys=True)
# Rejected initialization, service operation and recovery are now actually tested.
b=next(b for b in f['case_bindings'] if b['case_id']=='I2-12.P1.S2.NEGATIVE');b['expected'].update(corrupt_initialize='nonzero',liveness=200,library_during_checksum_damage=200,library_during_missing_column=503)
next(x for x in f['fixtures'] if x['id']==b['fixture_id'])['negative']['expected']=b['expected'];next(c for c in g['cases'] if c['id']==b['case_id'])['observable']='Compare actual observations with '+json.dumps(b['expected'],sort_keys=True)
d['scope']['property_ids']+=newprops;d['scope']['test_ids']+=newtests
d['reviews'].append({'id':'iterations1-2-native-repair-20261010','question':'Trace all guarded storage reads/writes, document-producing finalizers, interrupted upload lineage and actual guard readiness against both-iteration native counterexamples.','property_ids':newprops,'test_ids':newtests,'searches':[{'kind':'exact','status':'completed','query':'Shared production domain/assets/multipart/storage owners and recorded native counterexamples; actual transaction, frozen request, advisory lock and guard consumers.','outcome':'Four aligned repair groups, complete native positive/negative cases; previous I1 readiness and Library browser findings revalidated.','results':[{'path':p,'classification':'change_candidate','reason':'Exact known production owner and native regression.'} for p in ['services/api/internal/app/domain.go','services/api/internal/app/assets.go','services/api/internal/app/multipart.go','services/api/internal/app/storage.go',source]]},{'kind':'semantic','status':'not_applicable','query':'Known exact owners from native reproduction','reason':'No unknown owner discovery or semantic index claim; source and runtime tracing use exact verified files.','outcome':'Exact owner tracing suffices for this repair.','results':[]},{'kind':'jetbrains-index','status':'not_applicable','query':'No structural PSI operation','reason':'No IDE refactor/index task required for known owners.','outcome':'No current-index claim.','results':[]}],'disposition':'current_change','rationale':'Fix all verified iteration1/2 findings without weakening original contracts.'})
for p,obj in [(C/'verification.json',g),(C/'property-inventory.json',inventory),(C/'discovery.json',d),(V/'domain/verification-fixtures.v1.json',f),(V/'domain/property-test-sets.v1.json',sets),(A/'CASES.json',{'properties':newprops,'plans':plans}),(A/'INVALIDATED.json',invalid)]:save(p,obj)
print('Registered4 properties16 cases; complete both-iteration selection104 cases.')
