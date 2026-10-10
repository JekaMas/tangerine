"""Add literal owned-digest projection properties found during source review."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2';sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'domain/verification-fixtures.v1.json');sets=load(V/'domain/property-test-sets.v1.json');inventory=load(C/'property-inventory.json');d=load(C/'discovery.json');ledger=load(A/'CASES.json')
rid='I2-14';pid=rid+'.P1';title=rid+' Owned binding and render digest projections ignore only specified identity fields';owner='services/api/internal/contracts/digests.go';source='services/api/internal/contracts/contracts_test.go'
if any(x['id']==pid for x in g['properties']):raise SystemExit('Already registered')
p=C/'specs/iteration-two-storage/spec.md';p.write_text(p.read_text()+f'''### Requirement: {title}

Saved effective-binding hashes SHALL exclude id and binding_sha256 only. Render-plan hashes SHALL exclude id, schema_version and plan_sha256 only. Other payload changes SHALL fail under the unchanged digest, using independent literal golden expectations. No provider or acoustic observation is implied.

#### Scenario: {rid} packet 1

- **WHEN** binding identity or model content changes under the independently saved literal digest
- **THEN** the actual contract owner SHALL accept the identity change and reject changed model content

#### Scenario: {rid} packet 2

- **WHEN** render identity fields or frozen case lineage change under the independently saved literal digest
- **THEN** the actual digest owner SHALL accept the specified identity-field changes and reject changed case lineage

''')
spec=parse_delta_specs(C)['iteration-two-storage',title];scenarios=list(spec['scenarios']);g['requirements'].append({'id':rid,'capability':'iteration-two-storage','title':title,'fingerprint':spec['fingerprint']});oracle='Independent literal Python-generated JCS/SHA256 golden bytes; native Go typed binding validation and exact render hash function. No expected digest is obtained from the implementation.'
g['properties'].append({'id':pid,'requirement_id':rid,'statement':title,'scenarios':scenarios,'owner':owner,'oracle':oracle,'source_globs':[owner,source,'services/api/internal/contracts/**','tests/go-docker']});inventory.append({'id':rid,'capability':'iteration-two-storage','title':title,'statement':title,'scenarios':scenarios,'owner':owner,'source':'Iteration2 source review correction of specified owned-digest exclusions.'});pos=[];neg=[];base=None
rows=[('TestOwnedBindingIdentityPositive','positive',1,{'changed_field':'id','old':'binding-a','new':'binding-b'},{'both_valid':True}),('TestOwnedRenderIdentityPositive','positive',2,{'changed_fields':['id','schema_version']},{'both_owned_hash_valid':True}),('TestOwnedBindingContentNegative','negative',1,{'changed_field':'model','new':'changed-model'},{'typed_validation_error':True}),('TestOwnedRenderContentNegative','negative',2,{'changed_field':'case_version_id','new':'case-b'},{'owned_hash_error':True})]
for name,pol,packet,input,expected in rows:
 cid=f'{pid}.S{packet}.{pol.upper()}';fid=f'iteration2-owned-digests-packet{packet}';tid='tangerine.local/api/internal/contracts::'+name;scenario=scenarios[packet-1];plan={'case_id':cid,'property_id':pid,'polarity':pol,'scenario':scenario,'fixture_id':fid,'test_id':tid,'mode':'declared_behavior','action':'Execute '+name+' through the native Go owner in the pinned exact-checkout image.','initial_state':{'literal_golden_digest':True,'provider_calls':0},'input':input,'expected':expected,'independent_oracle':oracle,'observation_state':'not_run','existing_case_state':'implemented','historical_receipt_not_reused_as_new_fixture_observation':True};f['case_bindings'].append(plan);ledger['plans'].append(plan);fixture=next((x for x in f['fixtures'] if x['id']==fid),None)
 if fixture is None:fixture={'id':fid,'action':plan['action'],'initial_state':plan['initial_state'],'independent_oracle':oracle,'origin':'constructed_independent_digest_fixture'};f['fixtures'].append(fixture)
 fixture[pol]={'input':input,'expected':expected};base=base or fid
 g['cases'].append({'id':cid,'property_id':pid,'polarity':pol,'scenario':scenario,'scenario_fingerprint':spec['scenario_fingerprints'][scenario],'setup':plan['action']+' '+json.dumps(input,sort_keys=True),'observable':json.dumps(expected,sort_keys=True),'red_expectation':'Wrongly rejecting identity-only changes or accepting content changes fails.','green_expectation':'The literal independent golden digests agree exactly with the approved field projection.','test_id':tid,'command_id':'iteration2-contracts-go','state':'implemented','source_path':source,'source_sha256':hashlib.sha256((R/source).read_bytes()).hexdigest(),'invalidation_dependencies':['services/api/internal/contracts','services/api/go.mod','services/api/go.sum','services/api/Dockerfile','tests/go-docker'],'substitution':{'classification':'NO_TEST_DOUBLE','note':'Actual Go contract/digest owner, literal finite constructed inputs; no model or synthesis substitutes.'},'designed_fixture_id':fid,'fixture_observation_state':'not_run'});(pos if pol=='positive' else neg).append(cid)
f['property_bindings'].append({'property_id':pid,'fixture_id':base,'statement':title,'independent_oracle':oracle,'scenarios':scenarios,'observation_state':'not_run'});sets['properties'].append({'property_id':pid,'requirement_id':rid,'owner':owner,'scenario_names':scenarios,'positive_cases':pos,'negative_cases':neg,'proof_boundary':'Typed binding and pure owned-digest projections only; no model/provider/audio evidence.','runtime_set_observation':'not_run','positive_distinct_packets':2,'negative_distinct_packets':2});g['commands'].append({'id':'iteration2-contracts-go','runner':'go-test-json','argv':['./tests/go-docker','test','-json','-race','-count=1','./...'],'cwd':'.','env':{},'timeout_seconds':600,'authority':'local'})
# Preserve the actual caller context in asset idempotency, and literal valid raw input purpose.
for c in g['cases']:
 if c['property_id'].startswith('I2-') and c['source_path']=='tests/test_iteration2.py':c['source_sha256']=hashlib.sha256((R/c['source_path']).read_bytes()).hexdigest()
ledger['properties'].append(pid);ledger['parent_obligations'][pid]=['PER-01'];d['scope']['property_ids'].append(pid);d['scope']['test_ids'] += ['tangerine.local/api/internal/contracts::'+row[0] for row in rows];d['reviews'][-1]['property_ids'].append(pid);d['reviews'][-1]['test_ids']+=['tangerine.local/api/internal/contracts::'+row[0] for row in rows]
for p,v in [(C/'verification.json',g),(C/'property-inventory.json',inventory),(C/'discovery.json',d),(V/'domain/verification-fixtures.v1.json',f),(V/'domain/property-test-sets.v1.json',sets),(A/'CASES.json',ledger)]:save(p,v)
print('Registered owned-digest property and4 exact native Go cases; full iteration now88 cases.')
