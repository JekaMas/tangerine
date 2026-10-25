"""Register scoped paired properties before production changes."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs
g=json.loads((C/'verification.json').read_text());d=json.loads((C/'discovery.json').read_text());specs=parse_delta_specs(C)
for key in ['requirements','properties','cases']:g[key]=[v for v in g[key] if not v['id'].startswith('FOS-')]
g['commands']=[v for v in g['commands'] if not v['id'].startswith('recurring-')]
rows=[
('04','TestRecurringSavedProjectionObservation','projection','positive','Actual saved synthetic key and positive/negative score summaries pass the complete evaluation and feedback DTO admissions; no inference or storage mutation.'),
('01','test_profiles_positive','request','positive','Enabled roles submit exact number, target85 and optional instruction; disabled roles are absent.'),
('01','test_retention_positive','request','positive','Count2→1→2 retains hidden settings but submits only current active profiles.'),
('01','test_legacy_negative','request','negative','Absent/disabled recurrence omits the field and preserves ordinary mistake counts.'),
('01','test_override_positive','request','positive','Advanced recurring_errors override the simple fields.'),
('01','test_count_negative','request','negative','An exact positive count below enabled-speaker count is explained; zero remains supported.'),
('01','TestRecurringProfilesPositive','native','positive','Complete blueprint expansion freezes two explicit profile settings without changing voice/default policies.'),
('01','TestRecurringProfilesNegative','native','negative','Repeated/out-of-range speaker and impossible exact count fail one input admission; zero preserves settings.'),
('02','TestRecurringQuotaPositive','native','positive','Literal20-opportunity cases at70/85/95 yield14/17/19;7at85 yields6;4at85 yields3.'),
('02','TestRecurringQuotaNegative','native','negative','Sixteen of20 marked mutations cannot satisfy85%; no invented denominator or percent.'),
('02','TestRecurringSpeakerNegative','native','negative','A different speaker’s otherwise identical words do not enter this profile’s opportunities.'),
('02','TestRecurringScopeNegative','native','negative','Duplicate/mislocated or unkeyed opportunities do not count as distinct occurrences.'),
('02','TestRecurringCorrectNegative','native','negative','A supposedly correct exception cannot have changed wording or a scoped acoustic operation.'),
('02','TestRecurringGroupPositive','native','positive','One valid recurring unit with several actual changes passes the existing full mutation admission.'),
('03','TestRecurringPersistencePositive','native','positive','The actual manifest/key projection retains every eligible context, rule and profile through schema admission.'),
('03','TestRecurringSpeechPlanPositive','native','positive','A recurring group with repeated edits is forwarded once per turn for shared variant rendering, without losing any actual operations.'),
('03','TestRecurringSpeechPlanNegative','native','negative','Ordinary speech plans do not acquire a recurring-variant directive.'),
('03','TestRecurringScorePositive','native','positive','One general detected/corrected group gives one TP, supported primary score and the actual M/N result reference.'),
('03','TestRecurringControlNegative','native','negative','Absent profiles cannot introduce an unsolicited recurring group; explicit zero needs no group.'),
('03','TestRecurringReasonNegative','native','negative','A false supplied explanation keeps supported primary credit and scores the optional reason separately.'),
('04','test_controls_positive','evidence','positive','Actual browser changes per-role rule/rate and saved effective request retains those settings.'),
('04','test_controls_negative','evidence','negative','Disabled/hidden roles and transport failure retain unsaved topic/voices/recurrence without new inference.'),
('04','test_acoustic_positive','evidence','positive','Real local synthesis retains one shared same-unit phone variant, three distinct scopes and the saved mutations.'),
('04','test_correct_exception_negative','evidence','negative','The third of four phonetic opportunities has no edit and its waveform correspondence is retained unchanged.'),
('04','test_group_positive','acoustic','positive','Declared recurring scopes compile to one combined variant with exact literal phones and shifted phone intervals; correct third occurrence remains unchanged.'),
('04','test_independent_negative','acoustic','negative','Ordinary independent same-unit scopes retain their three separate variants and existing semantics.'),
('04','test_generation_positive','evidence','positive','Actual included-plan generation persists one group, exact independently observed eligible subset and audio.'),
('04','test_answer_positive','evidence','positive','A real common-rule answer maps once to the group, with actual scoring and comments.'),
('04','test_correct_answer_negative','evidence','negative','A real assertion against the saved correct exception is false-positive rather than a group detection.'),
('04','test_preservation_negative','evidence','negative','Original attempt/configuration match baseline and selected resources exclude paid dispatch/fallback.')]
sources={'request':'tests/test_recurring_request.py','native':'services/api/internal/app/recurring_errors_test.go','evidence':'tests/test_recurring_evidence.py','acoustic':'tests/test_recurring_acoustic.py','projection':'services/api/internal/app/recurring_observation_test.go'}
owners={'01':'services/web/app/prepare/RecurringErrors.js','02':'services/api/internal/app/recurring_errors.go','03':'services/api/internal/app/scoring_projection.go','04':'audit/recurring-errors-20261025/REPORT.md'}
deps=['services/api/internal/app/recurring_errors.go','services/api/internal/app/preparation_content.go','services/api/internal/app/mutation_content.go','services/api/internal/app/scoring_projection.go','services/api/internal/app/speech_plan.go','services/api/internal/app/review_input.go','services/api/internal/app/review_key.go','services/speech/melo_english.py','services/speech/acoustic_alignment.py','services/web/app/prepare','services/web/app/listen/Results.js','specification/v2/contracts/recurring-error.schema.json','specification/v2/contracts/exercise-request.schema.json','specification/v2/contracts/evaluation-key.schema.json','specification/v2/contracts/feedback-score.schema.json','specification/v2/contracts/teacher-key.schema.json','specification/v2/prompts']
props=[];tests=[]
for number,owner in owners.items():
 rid='FOS-'+number;pid=rid+'.P1';props.append(pid);spec=next(v for v in specs.values() if v['title'].startswith(rid+' '))
 g['requirements'].append(dict(id=rid,capability=spec['capability'],title=spec['title'],fingerprint=spec['fingerprint']))
 g['properties'].append(dict(id=pid,requirement_id=rid,statement=spec['title'][7:],scenarios=spec['scenarios'],owner=owner,oracle='Independent literal opportunities/quotas and actual saved native/browser/model observations with explicit scope.',source_globs=deps))
 for num,name,kind,polarity,expected in rows:
  if num!=number:continue
  source=sources[kind];path=R/source;tid='tangerine.local/api/internal/app::'+name if kind in ['native','projection'] else 'unittest::'+Path(source).stem+'.'+{'request':'RecurringRequest','evidence':'RecurringEvidence','acoustic':'RecurringAcoustic'}[kind]+'.'+name;tests.append(tid)
  case=dict(id=pid+'.'+name,property_id=pid,polarity=polarity,scenario=spec['scenarios'][0],scenario_fingerprint=spec['scenario_fingerprints'][spec['scenarios'][0]],setup=expected,observable=expected,red_expectation='A missing, substituted or changed required outcome fails.',green_expectation=expected,test_id=tid,command_id='recurring-'+kind,state='implemented' if path.exists() else 'planned',source_path=source,invalidation_dependencies=deps+[source]+(['audit/recurring-errors-20261025/run_projection.sh'] if kind=='projection' else []),substitution=dict(classification='NO_TEST_DOUBLE',proof_claims=[expected],forbidden_claims=['Universal linguistic opportunity completeness','Real-person fossilization diagnosis','Unselected/full-release/provider qualification']))
  if name=='test_controls_negative':case['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Test-owned browser transport block to local metadata; removed before live generation.',allowed_proof='Actual UI retains settings and recovers without inference.',forbidden_claims=['Actual API/storage outage','Substituted ordinary generation response'])
  if path.exists():case['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  g['cases'].append(case)
env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',DOCKER_CONFIG=str(R/'data/local-preview/docker-config'))
g['commands'].append(dict(id='recurring-native',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestRecurring','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
g['commands'].append(dict(id='recurring-projection',runner='go-test-json',argv=['./audit/recurring-errors-20261025/run_projection.sh','test','-json','-race','-count=1','-run','^TestRecurringSavedProjectionObservation$','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
for kind in ['request','evidence','acoustic']:g['commands'].append(dict(id='recurring-'+kind,runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p',Path(sources[kind]).name,'-v'],cwd='.',env=env,timeout_seconds=180,authority='local'))
d['scope']['property_ids']=[v for v in d['scope']['property_ids'] if not v.startswith('FOS-')]+props
d['scope']['test_ids']=[v for v in d['scope']['test_ids'] if '::TestRecurring' not in v and '::test_recurring_' not in v]+tests
d['reviews']=[v for v in d['reviews'] if v['id']!='recurring-errors-20261025']
d['reviews'].append(dict(id='recurring-errors-20261025',question='Research/implement speaker-specific recurring rules, opportunity frequency and accurate grouped feedback.',property_ids=props,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Known generation/mutation/key/score owners and primary fossilization literature; trace unit metadata and acoustic scope keys.',outcome='Use one optional grouped unit ledger and existing prompt/admission/render/score owners; extend per-role controls.',results=[dict(path=p,classification='change_candidate',reason='Direct owner of current requested behavior.') for p in deps]),dict(kind='semantic',status='not_applicable',query='Known generation and speaker owners; jbcontext discovery attempted.',reason='Concrete owners are already identified; no semantic-index evidence is claimed.',outcome='Exact source tracing supplies the implementation context.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known native owners and plain schema/prompt changes',reason='No symbol/IDE operation is needed.',outcome='No IDE-index claim.',results=[])],disposition='current_change',rationale='Current user explicitly asks for research and implementation; preserve ordinary behavior and original data.'))
for p,v in [(C/'verification.json',g),(C/'discovery.json',d)]:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'properties':4,'cases':len(rows),'planned':sum(v['id'].startswith('FOS-') and v['state']=='planned' for v in g['cases'])}))
