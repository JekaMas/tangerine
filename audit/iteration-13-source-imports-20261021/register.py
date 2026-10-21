"""Bind actual source-import tests to literal plans and the existing DAG; no run claim."""
from pathlib import Path
import ast,collections,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2'
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
load=lambda p:json.loads(p.read_text());save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=load(C/'verification.json');f=load(V/'domain/verification-fixtures.v1.json');sets=load(V/'domain/property-test-sets.v1.json');inventory=load(C/'property-inventory.json');discovery=load(C/'discovery.json');plan=load(A/'PLAN.json')
unit='services/api/internal/source/source_test.go';app='services/api/internal/app/source_contract_test.go';native='tests/native_source_test.go';full='tests/native_source_full_test.go';acquired='tests/native_source_data_test.go';browser='tests/test_source_browser.py'
repair='tests/native_source_repair_test.go'
extras=['services/api/internal/source/textgrid_encoding_test.go','services/api/internal/source/legacy_ambiguity_test.go','services/api/internal/source/essay_group_test.go']
files=[unit,app,native,full,acquired,browser,'services/api/internal/app/review_test.go']+extras+[repair];names={};bodies={};library={};classes={}
for p in files:
 text=(R/p).read_text();library[p]=dict(source_path=p,source_sha256=sha(R/p),origin='Constructed literal native cases and independent assertions; complete acquired bytes separately labelled.',fixture_source=text)
 if p==browser:
  for cls in [x for x in ast.parse(text).body if isinstance(x,ast.ClassDef)]:
   for fn in [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')]:names[fn.name]=p;bodies[fn.name]=ast.get_source_segment(text,fn);classes[fn.name]=cls.name
 else:
  funcs=list(re.finditer(r'^func (\w+)\(',text,re.M))
  for j,m in enumerate(funcs):
   if m[1].startswith('Test'):names[m[1]]=p;bodies[m[1]]=text[m.start():funcs[j+1].start() if j+1<len(funcs) else len(text)]
def match(prefix,source=None):return [n for n,p in names.items() if n.startswith(prefix) and (source is None or p==source)]
def positive(n):return n.endswith('Positive') or n.endswith('_positive')
groups={
'I13-01':match('TestSourceArchive')+match('TestNativeSourceIntake')+match('TestNativeSourceArchive')+match('TestNativeSourceNestedArchive'),
'I13-02':[n for n in names if names[n].startswith('services/api/internal/source/') and any(n.startswith('TestSource'+x) for x in ['JSON','Delimited','XML','Workbook','M2','TextGrid','Kaldi','Encoding','PhoneCase'])],
'I13-03':match('TestSourceMapping')+match('TestSourceSpan')+match('TestSourceIdentity')+match('TestSourceDecimal')+match('TestSourceLearner')+match('TestSourceParserDisposition')+match('TestNativeSourceMapping')+match('TestNativeSourcePrivateScope')+match('TestNativeSourceEfcamdat'),
'I13-04':match('TestSourceSources')+match('TestSourcePublic')+match('TestSourceCompleteness')+match('TestNativeSourceSources')+match('TestNativeSourceFullScope')+match('TestSourceGold')+match('TestSourceAcousticBounds')+match('TestNativeSourceSpeech')+match('TestNativeSourceEssayGroup')+match('TestNativeSourceGold')+match('TestNativeSourceCounts')+match('TestNativeSourceFull'),
'I13-05':sum((match('TestNativeSource'+p) for p in ['NativeImport','Resume','History','Cancel','Failure','Issues','Upgrade','Sequence','Transformation','Ordering','ScopeCount','FrozenPermissions','MissingBytes','ProjectionBatch','AdmissionReplay','ReadFailure']),[])+match('TestSourceProgress')+match('TestSourceCorpus'),
'I13-06':match('TestSourceRemote')+sum((match('TestNativeSource'+p) for p in ['Rights','Remote','Connector','ReviewTerms']),[]),
'I13-07':match('test_',browser),
'I13-08':match('TestAcquiredSource')+['TestNativeSourceFullScopeNegative','TestSourceCompletenessNegative'],
}
# Keep requirements and packet meanings; collapse only unaccepted planning nodes
# into eight properties with sets of genuinely distinct positive/negative cases.
old_ids={c['test_id'] for c in g['cases'] if c['id'].startswith('I13-')}
for key in ['requirements','properties','cases']:g[key]=[x for x in g[key] if not x['id'].startswith('I13-')]
g['commands']=[x for x in g['commands'] if not x['id'].startswith('iteration13-')];inventory=[x for x in inventory if not x['id'].startswith('I13-')]
for key in ['property_bindings','case_bindings']:f[key]=[x for x in f[key] if not x['property_id'].startswith('I13-')]
f['fixtures']=[x for x in f['fixtures'] if not x['id'].startswith('iteration13-')];sets['properties']=[x for x in sets['properties'] if not x['property_id'].startswith('I13-')]
discovery['scope']['property_ids']=[x for x in discovery['scope']['property_ids'] if not x.startswith('I13-')];discovery['scope']['test_ids']=[x for x in discovery['scope']['test_ids'] if x not in old_ids];discovery['reviews']=[x for x in discovery['reviews'] if x['id']!='iteration13-source-review-20261021']
cap='iteration-thirteen-sources';lines=['## ADDED Requirements','']
for rid,title,owner,rule,packets in plan:
 tests=list(dict.fromkeys(groups[rid]));groups[rid]=tests;count=collections.Counter('positive' if positive(n) else 'negative' for n in tests);assert min(count.values())>=2,(rid,count)
 lines += [f'### Requirement: {rid} {title}','','The application SHALL '+rule,'']
 for j in range(1,min(count.values())+1):lines += [f'#### Scenario: {rid} packet {j}','','- **WHEN** the declared literal supported or violating source/state case reaches the actual production owner','- **THEN** its independent native values, source scope, exact counts, preserved bytes, persisted state and forbidden effects SHALL hold','']
(C/'specs'/cap/'spec.md').write_text('\n'.join(lines));parsed=parse_delta_specs(C)
plans=[];pids=[];tids=[]
base=['services/api/internal/source/**','services/api/internal/app/source_*.go','services/api/internal/app/migrations/007_source_imports.sql','services/api/internal/app/http.go','services/api/internal/app/assets.go','services/api/internal/app/storage*.go','services/api/internal/app/domain.go','services/api/internal/app/migration*.go','services/api/internal/contracts/**','services/api/go.mod','services/api/go.sum','services/api/Dockerfile','specification/v2/docs/source-import-runtime.md']
def bind(cid,pid,scenario,pol,name,owner,oracle,case=None):
 src=names[name];body=bodies[name]
 command='iteration13-browser' if src==browser else 'iteration13-acquired' if src==acquired else 'iteration13-full' if src==full else 'iteration13-native' if src in [native,repair] else 'iteration13-go'
 pkg='source' if src.startswith('services/api/internal/source/') or src==acquired else 'app';tid='unittest::test_source_browser.'+classes[name]+'.'+name if src==browser else 'tangerine.local/api/internal/'+pkg+'::'+name;tids.append(tid)
 fixture_id='iteration13-'+re.sub(r'\.(POSITIVE|NEGATIVE)$','',cid).replace('.','-');inp=dict(exact_test=name,literal_executable_fixture=body,fixture_source_path=src,fixture_source_sha256=sha(R/src),shared_fixture_library='audit/iteration-13-source-imports-20261021/FIXTURE-LIBRARY.json#'+src)
 expected=dict(independent_literal_assertions=body,oracle=oracle);initial=dict(origin='Exactly labelled native fixture or previously acquired complete public package; as stated in the executable body and fixture library',setup='The exact executable body and shared fixture library define source bytes, prerequisite states and independently expected outcomes.')
 bp=dict(case_id=cid,property_id=pid,polarity=pol,scenario=scenario,fixture_id=fixture_id,test_id=tid,mode='declared_behavior',action='Execute '+name+' through '+owner,initial_state=initial,input=inp,expected=expected,independent_oracle=oracle,observation_state='not_run');plans.append(bp)
 f['case_bindings']=[x for x in f['case_bindings'] if x['case_id']!=cid];f['case_bindings'].append(bp);fixture=next((x for x in f['fixtures'] if x['id']==fixture_id),None)
 if fixture is None:fixture=dict(id=fixture_id,action=bp['action'],initial_state=initial,independent_oracle=oracle,origin=initial['origin']);f['fixtures'].append(fixture)
 fixture['initial_state']=initial;fixture[pol]=dict(input=inp,expected=expected)
 deps=base+[src]
 if src in [native,repair,browser,full]:deps+=['tests/native_source_test.go','tests/native_source_repair_test.go','tests/source-native']
 if src==browser:deps+=['services/web/**','tests/source-browser','tests/source_browser_fixture_test.go','tests/browser_probe.py','tests/browser_playwright.cjs']
 if src in [full,acquired]:deps+=['tests/source-full-native' if src==full else 'tests/source-acquired','specification/v2/docs/sources/**','specification/v2/domain/source-research.v1.json']
 out=case if case is not None else {};out.update(dict(id=cid,property_id=pid,polarity=pol,scenario=scenario,distinct_reason='Literal '+name+' independently scopes '+pid+' scenario '+scenario+' to '+oracle,setup=bp['action']+' '+json.dumps(inp,sort_keys=True),observable=json.dumps(expected,sort_keys=True),red_expectation='Any missing/wrong native observation or forbidden side effect fails.',green_expectation='Every independent literal expected observation passes through the actual owner.',test_id=tid,command_id=command,state='implemented',source_path=src,source_sha256=sha(R/src),invalidation_dependencies=list(dict.fromkeys(deps)),substitution=dict(classification='EXTERNAL_BOUNDARY' if src in [native,repair,browser] else 'NO_TEST_DOUBLE',owner_replaced='Documented remote HTTPS source protocol only; PostgreSQL/MinIO/controllers remain real' if src in [native,repair,browser] else 'none',proof_claims=['Declared source import behavior on labelled inputs'],forbidden_claims=['Unseen private release conformance','All sources acquired','Empirical linguistic gold validity','Paid or hosted provider qualification'],note=oracle),designed_fixture_id=fixture_id,fixture_observation_state='not_run'));out.pop('blocker',None);return out
for rid,title,owner,rule,packets in plan:
 pid=rid+'.P1';pids.append(pid);rr=parsed[cap,rid+' '+title];scenarios=list(rr['scenarios']);oracle='The application SHALL '+rule+' Actual source terms and missing populations remain explicit; constructed cases do not certify unseen private releases or linguistic validity.'
 g['requirements'].append(dict(id=rid,capability=cap,title=rid+' '+title,fingerprint=rr['fingerprint']));g['properties'].append(dict(id=pid,requirement_id=rid,statement=oracle,scenarios=scenarios,owner=owner,oracle=oracle,source_globs=[owner]));inventory.append(dict(id=rid,capability=cap,title=rid+' '+title,statement=oracle,scenarios=scenarios,owner=owner,source='User-authorized iteration13 apply and verification; all original source identities retained.'))
 by={'positive':[],'negative':[]}
 for name in groups[rid]:
  pol='positive' if positive(name) else 'negative';j=len(by[pol])+1;cid=f'{pid}.S{j}.{pol.upper()}';scenario=scenarios[(j-1)%len(scenarios)];case=bind(cid,pid,scenario,pol,name,owner,oracle);case['scenario_fingerprint']=rr['scenario_fingerprints'][scenario];g['cases'].append(case);by[pol].append(cid)
 fixture_id='iteration13-'+re.sub(r'\.(POSITIVE|NEGATIVE)$','',by['positive'][0]).replace('.','-');f['property_bindings'].append(dict(property_id=pid,fixture_id=fixture_id,statement=oracle,independent_oracle=oracle,scenarios=scenarios,observation_state='not_run'));sets['properties'].append(dict(property_id=pid,requirement_id=rid,owner=owner,scenario_names=scenarios,positive_cases=by['positive'],negative_cases=by['negative'],proof_boundary=oracle,runtime_set_observation='not_run',positive_distinct_packets=len(by['positive']),negative_distinct_packets=len(by['negative'])))
# Existing source-import scaffolds keep their immutable identities and scopes.
# Missing source originals are tested as missing, never manufactured acquisition.
aliases={
'COR-01':['TestNativeSourceRightsPositive','TestNativeSourceRightsNegative','TestNativeSourceTransformationPositive','TestNativeSourceReviewTermsNegative'],
'COR-02':['TestNativeSourceArchivePositive','TestNativeSourceArchiveNegative','TestNativeSourceNestedArchivePositive','TestNativeSourceNestedArchiveNegative'],
'SRC-01':['TestNativeSourceIntakePositive','TestNativeSourceIntakeNegative','TestNativeSourceHistoryPositive','TestNativeSourceHistoryNegative'],
'V6-DATA-01':['TestNativeSourceRightsPositive','TestNativeSourceRightsNegative','TestNativeSourceReviewTermsPositive','TestNativeSourceReviewTermsNegative','TestSourceCompletenessNegative'],
'V6-DATA-02':['TestNativeSourceMappingPositive','TestNativeSourceMappingNegative','TestNativeSourceHistoryPositive','TestNativeSourceNativeImportNegative','TestNativeSourceEfcamdatNegative'],
'FULL-01':['TestSourceSourcesPositive','TestSourceSourcesNegative','TestNativeSourceGoldPositive','TestNativeSourceGoldNegative','TestNativeSourceFullScopeNegative'],
'FULL-02':['TestNativeSourceHistoryPositive','TestNativeSourceRightsNegative','TestNativeSourceTransformationPositive','TestNativeSourceCountsNegative','TestNativeSourceIntakeNegative'],
'BUILD-03':['TestNativeSourceMappingPositive','TestNativeSourceMappingNegative','TestNativeSourcePrivateScopePositive','TestNativeSourcePrivateScopeNegative'],
'SPEC-039':['TestNativeSourceIntakePositive','TestNativeSourceIntakeNegative','TestNativeSourceRightsPositive','TestNativeSourceRightsNegative','TestNativeSourceTransformationPositive','TestNativeSourceTransformationNegative','TestNativeSourceCountsPositive','TestNativeSourceCountsNegative'],
'SPEC-040':['TestSourcePublicPositive','TestSourcePublicNegative','TestAcquiredSourceSpeechPositive','TestSourcePhoneCaseNegative','TestSourceSpanPositive','TestSourceSpanNegative','TestSourceJSONPositive','TestSourceJSONNegative'],
}
for rid in ['DATAFULL-'+str(i).zfill(2) for i in range(1,12)]:
 tests=['TestSourceSourcesPositive','TestSourceSourcesNegative','TestNativeSourceSourcesPositive','TestSourceCompletenessNegative']
 if rid=='DATAFULL-01':tests=['TestNativeSourceGoldPositive','TestNativeSourceGoldNegative','TestSourceGoldAdmissionPositive','TestSourceGoldAdmissionNegative']
 elif rid=='DATAFULL-02':tests=['TestAcquiredSourceSpeechPositive','TestSourcePublicNegative','TestSourcePublicPositive','TestSourceCompletenessNegative']
 elif rid=='DATAFULL-03':tests=['TestAcquiredSourceL2Positive','TestSourcePhoneCaseNegative','TestSourcePhoneCasePositive','TestSourceAcousticBoundsNegative']
 elif rid=='DATAFULL-04':tests=['TestNativeSourceFullWIPositive','TestAcquiredSourceNegative','TestAcquiredSourceBEAPositive','TestNativeSourceFullScopeNegative']
 elif rid=='DATAFULL-05':tests=['TestNativeSourceFullFCEPositive','TestNativeSourceNativeImportNegative','TestAcquiredSourceBEAPositive','TestNativeSourceFullScopeNegative']
 elif rid=='DATAFULL-06':tests=['TestNativeSourceEfcamdatPositive','TestNativeSourceEfcamdatNegative','TestNativeSourcePrivateScopePositive','TestNativeSourcePrivateScopeNegative']
 else:tests=['TestNativeSourcePrivateScopePositive','TestNativeSourcePrivateScopeNegative','TestNativeSourceMappingPositive','TestNativeSourceMappingNegative']
 tests.append("TestNativeSourceRightsNegative" if "TestSourceCompletenessNegative" in tests else "TestSourceCompletenessNegative")
 aliases[rid]=tests
for rid,test_names in aliases.items():
 p=next(x for x in g['properties'] if x['requirement_id']==rid);pid=p['id'];pids.append(pid);cases=[c for c in g['cases'] if c['property_id']==pid];assert len(cases)==len(test_names),(rid,len(cases),len(test_names))
 # Preserve existing polarity/scenario order and select genuinely matching literals.
 available={pol:[n for n in test_names if positive(n)==(pol=='positive')] for pol in ['positive','negative']};used=collections.Counter()
 for case in cases:
  pol=case['polarity'];name=available[pol][used[pol]%len(available[pol])];used[pol]+=1;bind(case['id'],pid,case['scenario'],pol,name,p['owner'],p['oracle']+' Actual acquisition remains independently reported and unavailable private originals are not certified.',case)
 for x in f['property_bindings']:
  if x['property_id']==pid:x.update(fixture_id='iteration13-'+re.sub(r'\.(POSITIVE|NEGATIVE)$','',cases[0]['id']).replace('.','-'),observation_state='not_run')
 for x in sets['properties']:
  if x['property_id']==pid:
   x.update(positive_cases=[c['id'] for c in cases if c['polarity']=='positive'],negative_cases=[c['id'] for c in cases if c['polarity']=='negative'],positive_distinct_packets=sum(c['polarity']=='positive' for c in cases),negative_distinct_packets=sum(c['polarity']=='negative' for c in cases),runtime_set_observation='not_run')
env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock');web=load(A/'RUNTIME-BINDINGS.json')['web_image']
g['commands'] += [dict(id='iteration13-go',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestSource','./internal/source','./internal/app'],cwd='.',env=env,timeout_seconds=600,authority='local'),dict(id='iteration13-native',runner='go-test-json',argv=['./tests/source-native','test','-json','-race','-count=1','./internal/app'],cwd='.',env=env,timeout_seconds=1200,authority='local'),dict(id='iteration13-full',runner='go-test-json',argv=['./tests/source-full-native','test','-json','-race','-count=1','-timeout=40m','./internal/app'],cwd='.',env=env,timeout_seconds=2600,authority='local'),dict(id='iteration13-acquired',runner='go-test-json',argv=['./tests/source-acquired','test','-json','-race','-count=1','-timeout=12m','-run','^TestAcquiredSource','./internal/source'],cwd='.',env=env,timeout_seconds=900,authority='local'),dict(id='iteration13-browser',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_source_browser.py','-v'],cwd='.',env={**env,'TANGERINE_INTERPRETATION_TEST_WEB_IMAGE':web},timeout_seconds=900,authority='local')]
# Import-only fallback source-term repair invalidates these two inherited pure
# review projections, not model quality or prompt/context bindings.
for case in g['cases']:
 if case['test_id'].endswith(('::TestReviewSourcePositive','::TestReviewSourceNegative')):case['command_id']='iteration13-dependent-review'
g['commands'].append(dict(id='iteration13-dependent-review',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestReviewSource(Positive|Negative)$','./internal/app'],cwd='.',env=env,timeout_seconds=600,authority='local'))
fresh_go={n for n,p in names.items() if p in extras}|{'TestSourceTextGridPositive','TestSourceTextGridNegative','TestSourceTextGridMultilinePositive','TestSourceParserDispositionPositive','TestSourceParserDispositionNegative'}
fresh_native={n for n,p in names.items() if p==repair}|{'TestNativeSourceFailurePositive','TestNativeSourceFailureNegative','TestNativeSourceResumePositive','TestNativeSourceResumeNegative','TestNativeSourcePrivateScopePositive','TestNativeSourcePrivateScopeNegative'}
fresh_acquired={'TestAcquiredSourceL2Positive'}
for case in g['cases']:
 name=case['test_id'].split('::')[-1]
 if name in fresh_go:case['command_id']='iteration13-repair-go'
 elif name in fresh_native:case['command_id']='iteration13-repair-native'
 elif name in fresh_acquired:case['command_id']='iteration13-repair-acquired'
def expression(names):return '^('+('|'.join(sorted(names)))+')$'
g['commands'] += [dict(id='iteration13-repair-go',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run',expression(fresh_go),'./internal/source','./internal/app'],cwd='.',env=env,timeout_seconds=600,authority='local'),dict(id='iteration13-repair-native',runner='go-test-json',argv=['./tests/source-native','test','-json','-race','-count=1','-run',expression(fresh_native),'./internal/app'],cwd='.',env=env,timeout_seconds=1200,authority='local'),dict(id='iteration13-repair-acquired',runner='go-test-json',argv=['./tests/source-acquired','test','-json','-race','-count=1','-timeout=12m','-run',expression(fresh_acquired),'./internal/source'],cwd='.',env=env,timeout_seconds=900,authority='local')]
# Reconcile only the explicitly edited L2 narrative; all other pins retain their
# original meanings. Source/test fingerprints below describe new materialization.
for r in g['requirements']:
 if r['id']=='DATAFULL-03':r['fingerprint']=parsed[r['capability'],r['title']]['fingerprint']
pending=next(x for x in g['commands'] if x['id']=='pending');pending['expected_markers']=list(dict.fromkeys(c['test_id'] for c in g['cases'] if c['command_id']=='pending'))
discovery['scope']['property_ids']=list(dict.fromkeys(discovery['scope']['property_ids']+pids));discovery['scope']['test_ids']=list(dict.fromkeys(discovery['scope']['test_ids']+tids));discovery['reviews'].append(dict(id='iteration13-source-review-20261021',question='Trace every source-import format, actual data use, retained original scope, rights, remote export, persistence/recovery and local user scenario.',property_ids=pids,test_ids=list(dict.fromkeys(tids)),searches=[dict(kind='exact',status='completed',query='Trace full source native contracts, mapping programs, operations and counts to separated import/persistence/HTTP/UI owners.',outcome='No pre-existing importer. Added deterministic format/mapping owners and separate source-intake/release/binding/staging/mapping/report/rights/connector owners.',results=[dict(path='services/api/internal/source/stream.go',classification='change_candidate',reason='Lossless native record streaming'),dict(path='services/api/internal/app/source_import.go',classification='change_candidate',reason='Foreground orchestration with independent storage and projection owners')]),dict(kind='semantic',status='unavailable',query='Source import native parsers, storage controllers and all eleven source scopes',reason='jbcontext reported no index for this exact checkout 8a1063f47580374215090780ca0caab42953a317e1b838dbfa9b0f6a81836988.',outcome='Read-only context exploration and exact contract/source tracing retained; no semantic-index evidence claimed.',results=[]),dict(kind='jetbrains-index',status='unavailable',query='get_repositories on the exact iteration13 worktree',reason='JetBrains reports this worktree is not an open project. Canonical Tangerine is open but is a different checkout.',outcome='No borrowed canonical IDE/index evidence; exact worktree source and runtime evidence retained.',results=[])],disposition='current_change',rationale='Explicit apply/verify/repair/commit authority. No paid calls, human review, private corpus invention, new remote outreach or full-product acceptance.'))
valid={c['test_id'] for c in g['cases']};old_by_id={c['id']:c for c in load(C/'verification.json')['cases']};new_by_id={c['id']:c for c in g['cases']};rebound={c['test_id']:new_by_id[c['id']]['test_id'] for c in old_by_id.values() if not c['id'].startswith('I13-') and c['id'] in new_by_id and c['test_id']!=new_by_id[c['id']]['test_id']}
for review in discovery['reviews']:review['test_ids']=list(dict.fromkeys(rebound.get(x,x) for x in review['test_ids']))
discovery['scope']['test_ids']=[x for x in discovery['scope']['test_ids'] if x in valid]
for p,d in [(C/'verification.json',g),(C/'property-inventory.json',inventory),(C/'discovery.json',discovery),(V/'domain/verification-fixtures.v1.json',f),(V/'domain/property-test-sets.v1.json',sets),(A/'FIXTURE-LIBRARY.json',library),(A/'CASES.json',dict(properties=pids,requirements=list(groups)+list(aliases),plans=plans))]:save(p,d)
print(json.dumps(dict(properties=len(pids),cases=len(plans),unique_tests=len(set(tids)),polarities=dict(collections.Counter(x['polarity'] for x in plans)))))
