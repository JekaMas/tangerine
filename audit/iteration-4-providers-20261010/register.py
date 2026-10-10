"""Register exact I4 executable cases; protocol fixtures do not claim live inference."""
from pathlib import Path
import ast,json,hashlib,re,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=load(C/'verification.json');f=load(V/'verification-fixtures.v1.json');sets=load(V/'property-test-sets.v1.json');inv=load(C/'property-inventory.json');d=load(C/'discovery.json')
if any(p['id'].startswith('I4-') for p in g['properties']):raise SystemExit('Already registered')
groups=[
('Protected installation identity and credential persistence','connection_test.go','HostStable HostDistinct HostDamaged CredentialsMode'),
('Exact loopback PKCE authorization','connection_test.go','PKCE PendingSeparate CallbackHost CallbackPath'),
('Single-use pending state and bounded callback lifetime','connection_test.go','StateOneUse DeniedNoExchange WrongState ExpiredAttempt'),
('Signed issuer audience nonce and subject validation','connection_test.go','OIDC AudienceArray Nonce Signature'),
('Reconnect identity and restart isolation','connection_test.go','Reconnect RestartPending ReconnectClient ReconnectSubject'),
('Required direct usage scope and explicit credit exclusion','connection_test.go','ScopeGranted CreditConfirmation ScopeAbsent CreditEnabled'),
('Serialized refresh rotation and transient grant retention','connection_test.go','Refresh RefreshSerialized RefreshInvalid RefreshTransient'),
('Frozen registration selection and explicit disconnect','connection_test.go','Disconnect SelectionFrozen DisconnectRevocation SelectionUnknown'),
('Actual account model bytes order and visibility','connection_test.go','Models ModelsEmpty ModelsQuota ModelsMalformed'),
('Explicit stateless Responses wire projection','transport_test.go','Wire WireReasoning WireUnsupported WireSystem'),
('Included local or confirmed free access only','transport_test.go','LocalPolicy IncludedProfile Metered BillingFallback'),
('Completed-only streaming with retained partial output','transport_test.go','CompletedStream CompletedOutput PartialStream LateQuota'),
('Actual request and response metadata with credential and refusal failures','transport_test.go','ActualRequest Nonstream MissingCredential Refusal'),
('Cancellation deadlines and incomplete stream outcomes','transport_test.go','Cancelled Deadline IncompleteEvent MalformedEvent'),
('Unambiguous lossless JSON projection','execute_test.go','ProjectionFence ProjectionIdentical ProjectionAmbiguous ProjectionMissing'),
('Bounded same-profile transport retry and structured fallback','execute_test.go','Retry Fallback RetryBound RefusalNoRetry'),
('One owned semantic repair retains original candidate evidence','execute_test.go','Repair RepairSemantic RepairExhausted RepairQuota'),
('Native evidence finalization precedes output use','execute_test.go','SaveBeforeUse CancelReceipt SaveFailure DeadlineShared')]
rows=[]
for title,file,names in groups:
 names=names.split();names=['TestProvider'+x+('Positive' if i<2 else 'Negative') for i,x in enumerate(names)];rows.append((title,'CAP-02' if file=='connection_test.go' else 'CAP-03',names,'services/api/internal/provider/'+file,'iteration4-go','tangerine.local/api/internal/provider'))
for title,names in [
('Durable safe registration metadata and catalogue references','Metadata Selection MetadataFailure CatalogueReference'),
('Configuration readback idempotency revision and reference rejection','Configuration ConfigurationView ConfigurationRevision ConfigurationReferences'),
('Explicit frozen profile overrides without fallback','Frozen Override FrozenMissing FrozenMetered'),
('Actual native receipt context and failure-byte persistence','Receipt Snapshot Partial Quota'),
('Saved result replay and restart readback preserve operation identity','Replay RestartReadback ReplayChanged ReplayIncomplete'),
('Private immutable diagnostics retain failed execution','Diagnostic FailedDiagnostic DiagnosticMissing DiagnosticChanged'),
('Complete configuration digest and permitted readiness','DefaultProfiles ScopedSettings ConfigurationHash ReadinessMissing'),
('Same application CLI and frozen run scoped diagnostic controls','CLI CLIOverlay CLIMalformed CLIMetered'),
('Sanitized native diagnostic copies preserve originals and ephemeral credentials','DiagnosticOriginal DiagnosticReplay DiagnosticCanary DiagnosticSecretStorage'),
('Cross process grant leases release safely and cancel without admission','Serialization SerializationParallel SerializationCancelled SerializationFailure')]:
 names=['TestNativeProvider'+x+('Positive' if i<2 else 'Negative') for i,x in enumerate(names.split())];rows.append((title,'PRV-02',names,'tests/native_provider_test.go','iteration4-go-storage','tangerine.local/api/internal/app'))
for title,names in [
('Native Settings saved error rejection and recovery views','settings_initial_positive settings_saved_positive settings_failure_negative settings_invalid_negative'),
('Public configuration and saved metadata retain local selection and reject conflicts','connection_metadata_positive configuration_local_positive configuration_stale_negative connection_unknown_negative'),
('Visible actual model selection and private catalogue access','models_selected_positive models_readback_positive models_unlinked_negative models_unknown_negative'),
('Independent dispatch native context and actual Lab readback','lab_transport_positive lab_failed_call_positive lab_missing_negative lab_mismatch_negative')]:rows.append((title,'DEV-12' if title.startswith('Independent') else 'CAP-01',['test_'+x for x in names.split()],'tests/test_iteration4.py','iteration4-native','unittest::test_iteration4.Iteration4Tests'))
source_bodies={}
for source in {x[3] for x in rows}:
 text=(R/source).read_text()
 if source.endswith('.py'):source_bodies[source]={n.name:ast.get_source_segment(text,n) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef)}
 else:
  matches=list(re.finditer(r'^func (Test\w+)\(t \*testing.T\)\s*\{',text,re.M));source_bodies[source]={m.group(1):text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)].strip() for i,m in enumerate(matches)}
cap='iteration-four-providers';path=C/'specs'/cap/'spec.md';path.parent.mkdir(exist_ok=True);text='# Iteration four provider connections and transport\n\n## ADDED Requirements\n'
for i,(title,parent,names,source,command,package) in enumerate(rows,1):
 rid=f'I4-{i:02}';text+=f'\n### Requirement: {rid} {title}\n\nThe application SHALL implement this bounded obligation of {parent} through the real owner and exact native fixtures retained in audit/iteration-4-providers-20261010/CASES.json. Controlled remote protocol substitutions SHALL remain explicit and SHALL NOT establish hosted admission, real LLM quality or later generation and scoring pipeline completion.\n'
 for packet in (1,2):text+=f'\n#### Scenario: {rid} packet {packet}\n\n- **WHEN** the exact positive or negative native fixture for packet {packet} executes\n- **THEN** its independently asserted bytes, state, call count and failure behavior SHALL hold\n'
path.write_text(text);specs=parse_delta_specs(C);plans=[];props=[];tests=[]
deps=['services/api/internal/provider','services/api/internal/app/provider_inference.go','services/api/internal/app/provider_connections.go','services/api/internal/app/provider_configuration.go','services/api/internal/app/provider-default.json','services/api/internal/app/provider_command.go','services/api/internal/app/http.go','services/api/internal/app/domain.go','services/api/internal/contracts','services/api/cmd/tangerine/main.go','services/api/Dockerfile','services/web/app/settings','services/web/app/auth','services/web/app/api','deploy/local/compose.yaml','deploy/local/lab.py']
for i,(title,parent,names,source,command,package) in enumerate(rows,1):
 rid=f'I4-{i:02}';pid=rid+'.P1';props.append(pid);rt=rid+' '+title;spec=specs[cap,rt];scenarios=list(spec['scenarios']);oracle='Independent literal native test assertions, test-owned observed HTTP wire bytes and call counts, actual PostgreSQL/MinIO readback, real browser rendering and actual MLflow SDK/artifact download. Hosted inference, entitlement and model quality require separate live evidence.'
 owner='services/api/internal/provider' if command=='iteration4-go' else 'services/api/internal/app' if command=='iteration4-go-storage' else 'services/web/app/settings/page.js'
 g['requirements'].append(dict(id=rid,capability=cap,title=rt,fingerprint=spec['fingerprint']));g['properties'].append(dict(id=pid,requirement_id=rid,statement=title,scenarios=scenarios,owner=owner,oracle=oracle,source_globs=[x+'/**' if (R/x).is_dir() else x for x in deps]+[source]));inv.append(dict(id=rid,capability=cap,title=rt,statement=title,scenarios=scenarios,owner=owner,source='Authorized iteration4 provider implementation; original complete feature requirements preserved.'));pos=[];neg=[]
 for j,name in enumerate(names):
  polarity='positive' if j<2 else 'negative';packet=1 if j in (0,2) else 2;scenario=scenarios[packet-1];cid=f'{pid}.S{packet}.{polarity.upper()}';fid=f'iteration4-{rid}-packet{packet}';tid=package+('::' if command!='iteration4-native' else '.')+name;tests.append(tid);body=source_bodies[source][name]
  inp={'exact_native_test':name,'literal_executable_fixture':body};exp={'independent_literal_expectations':'All exact independently authored assertions in the fixture must pass; failures and forbidden effects are asserted explicitly.','assertion_source':body};plan=dict(case_id=cid,property_id=pid,polarity=polarity,scenario=scenario,fixture_id=fid,test_id=tid,mode='declared_behavior',action='Execute '+name+' through '+owner,initial_state={'isolated_native_dependencies':command!='iteration4-go','external_protocol_substitution':command!='iteration4-native'},input=inp,expected=exp,independent_oracle=oracle,observation_state='not_run',existing_case_state='implemented',historical_receipt_not_reused_as_new_fixture_observation=True);plans.append(plan);f['case_bindings'].append(plan)
  fixture=next((x for x in f['fixtures'] if x['id']==fid),None)
  if fixture is None:fixture=dict(id=fid,action=plan['action'],initial_state=plan['initial_state'],independent_oracle=oracle,origin='constructed_native_provider_protocol');f['fixtures'].append(fixture)
  fixture[polarity]=dict(input=inp,expected=exp)
  sub={'classification':'EXTERNAL_BOUNDARY','owner_replaced':'Hosted provider authorization/OIDC/model/Responses remote protocol only','proof_claims':['Production protocol handling and native persistence of controlled exact replies'],'forbidden_claims':['Hosted admission','Actual LLM inference or semantic quality','Full later trainer pipeline'],'note':oracle} if command!='iteration4-native' else {'classification':'NO_TEST_DOUBLE','note':oracle}
  g['cases'].append(dict(id=cid,property_id=pid,polarity=polarity,scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup=plan['action']+' '+json.dumps(inp,sort_keys=True),observable=json.dumps(exp,sort_keys=True),red_expectation='Incorrect bytes, identity, terminal state, hidden billing/fallback/retry or missing native/export evidence fails.',green_expectation='Exact native independently asserted behavior passes.',test_id=tid,command_id=command,state='implemented',source_path=source,source_sha256=sha(R/source),invalidation_dependencies=deps+[source],substitution=sub,designed_fixture_id=fid,fixture_observation_state='not_run'));(pos if polarity=='positive' else neg).append(cid)
 f['property_bindings'].append(dict(property_id=pid,fixture_id=f'iteration4-{rid}-packet1',statement=title,independent_oracle=oracle,scenarios=scenarios,observation_state='not_run'));sets['properties'].append(dict(property_id=pid,requirement_id=rid,owner=owner,scenario_names=scenarios,positive_cases=pos,negative_cases=neg,proof_boundary=oracle,runtime_set_observation='not_run',positive_distinct_packets=2,negative_distinct_packets=2))
env={'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock'}
g['commands'] += [dict(id='iteration4-go',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','./internal/provider'],cwd='.',env=env,timeout_seconds=600,authority='local'),dict(id='iteration4-go-storage',runner='go-test-json',argv=['./tests/native-providers','test','-json','-race','-count=1','./internal/app'],cwd='.',env=env,timeout_seconds=600,authority='local'),dict(id='iteration4-native',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_iteration4.py','-v'],cwd='.',env={**env,'TANGERINE_TEST_PAUSE_PROJECT':'tangerine-i1'},timeout_seconds=1000,authority='local')]
d['scope']['property_ids']+=props;d['scope']['test_ids']+=tests;d['reviews'].append(dict(id='iteration4-providers-20261010',question='Trace account grant, actual model catalogue, frozen configuration, final wire, terminal replies and native/Lab lineage through production owners.',property_ids=props,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Exact Settings/router/storage/provider/receipt/context/Lab owners and literal cases',outcome='Verified shared native owner and private credential lineage; hosted admission remains separate.',results=[dict(path=p,classification='change_candidate',reason='Current production owner.') for p in deps if (R/p).is_file()]),dict(kind='semantic',status='unavailable',query='jbcontext provider storage and transport ownership in isolated checkout',reason='Context explorer reported no semantic index for this exact checkout.',outcome='No semantic evidence claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='No PSI refactor required',reason='Known exact owners; no IDE operation required for this increment.',outcome='No new IDE evidence claimed.',results=[])],disposition='current_change',rationale='Complete authorized provider scope while retaining all later product and live provider obligations.'))
for p,v in [(C/'verification.json',g),(C/'property-inventory.json',inv),(C/'discovery.json',d),(V/'verification-fixtures.v1.json',f),(V/'property-test-sets.v1.json',sets),(A/'CASES.json',dict(properties=props,plans=plans))]:save(p,v)
print('Registered',len(props),'properties',len(plans),'exact cases')
