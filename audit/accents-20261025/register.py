"""Register the scoped accent increment without replacing earlier requirements."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs
g=json.loads((C/'verification.json').read_text());d=json.loads((C/'discovery.json').read_text());specs=parse_delta_specs(C)
for k in ['requirements','properties','cases']:g[k]=[x for x in g[k] if not x['id'].startswith('ACC-')]
g['commands']=[x for x in g['commands'] if not x['id'].startswith('accent-')]
rows=[
('01','test_speaker_choices_positive','request','positive','Two roles selecting Australian/Indian submit [melo_en_au,melo_en_in] in order.'),
('01','test_speaker_restore_positive','request','positive','Count 2→1→2 retains the first two chosen roles; growth defaults only new roles.'),
('01','test_advanced_speakers_positive','request','positive','Explicit advanced speakers and effective speaker_count override matching simple controls.'),
('01','test_auto_negative','request','negative','All Automatic omits speaker_voice_ids and never forces the local profile.'),
('01','test_active_count_negative','request','negative','A one-speaker request excludes retained hidden second-speaker choices.'),
('01','test_controls_positive','evidence','positive','Actual browser selects Australian and Indian independently and plays the exact stored previews.'),
('01','test_voice_failure_negative','evidence','negative','Catalogue/preview failure retains topic and role selections without LLM dispatch.'),
('02','TestAccentBlueprintPositive','native','positive','Exact native blueprint expansion maps ordered AU/IN to melo_en_au/melo_en_in and persists speaker descriptions.'),
('02','TestAccentDefaultsNegative','native','negative','Absent/all-null choices preserve Kokoro defaults and existing settings; no global configuration mutation.'),
('02','TestAccentProfilePositive','native','positive','A mixed six-voice local profile routes AU/IN locales per actual speaker rather than text variety.'),
('02','TestAccentUnknownNegative','native','negative','Unknown voice and wrong choice count fail admission; no substitution.'),
('02','TestAccentCheckpointPositive','native','positive','speaker_voice_ids are frozen registry metadata rather than database IDs.'),
('02','TestAccentFrozenProfilePositive','native','positive','Resume retains the admitted saved profile and speed rather than replacing them with the current built-in catalogue.'),
('02','TestAccentAdvancedSpeakersPositive','native','positive','Explicit complete advanced speakers override stale simple choices even when changing the effective role count.'),
('02','TestAccentCheckpointNegative','native','negative','The metadata exemption preserves required settings association validation.'),
('03','test_ipa_positive','speech','positive','Literal theta→s, ship→sheep and stress inputs yield independently expected model phone/tone sequences.'),
('03','test_unknown_phone_negative','speech','negative','An unsupported IPA symbol is rejected; no dropped segment or other-voice fallback.'),
('03','test_routing_positive','speech','positive','AU maps to native speaker3, IN to2; US/UK retain Kokoro with unchanged voice IDs.'),
('03','test_missing_model_negative','speech','negative','An empty actual model directory yields MODEL_SETUP_REQUIRED before inference.'),
('03','test_australian_positive','evidence','positive','Actual local AU WAV and native call bind model speaker3 and en-AU with inspectable inputs.'),
('03','test_indian_positive','evidence','positive','Actual local IN WAV and native call bind model speaker2 and en-IN with inspectable inputs.'),
('03','test_acoustic_pair_positive','evidence','positive','Actual AU/IN reference versus mutated phone inputs and produced waveforms retain model-derived timing.'),
('03','test_preview_replay_negative','evidence','negative','Two actual preview plays read the same stored WAV and trigger zero synthesis/LLM requests.'),
('04','test_actual_demo_positive','evidence','positive','Real video and persisted exercise/attempt/result show generation, listening, submitted answer, native score and LLM comments.'),
('04','test_preserved_work_negative','evidence','negative','Original attempt/configuration match baseline and demo has no simulated network/model results or paid fallback.')]
sources={'request':'tests/test_accents.py','native':'services/api/internal/app/accents_test.go','speech':'tests/test_accent_speech.py','evidence':'tests/test_accent_evidence.py'}
owners={'01':'services/web/app/prepare/SpeakerVoices.js','02':'services/api/internal/app/local_voices.go','03':'services/speech/melo_english.py','04':'audit/accents-20261025/REPORT.md'}
deps=['services/web/app/prepare','services/api/internal/app/local_voices.go','services/api/internal/app/preparation_content.go','services/api/internal/app/preparation_catalog.go','services/api/internal/app/acoustic_profile.go','services/api/internal/app/speech_plan.go','services/api/internal/app/domain.go','services/speech','specification/v2/contracts/exercise-request.schema.json']
props=[];tests=[]
audio_cases={'test_australian_positive','test_indian_positive','test_acoustic_pair_positive'}
statements={'01':'Each role independently selects a previewable registered accent/voice, retaining choices across count changes, failures and advanced overrides.','02':'An explicitly selected local speaker binding persists through preparation and resume without changing workspace defaults or substituting unavailable voices.','03':'Actual local AU/IN speech and controlled phone edits retain native input/output/timing; preview replay dispatches no synthesis.','04':'The real recorded generation/listening/answer/result flow preserves original work and uses admitted included/local resources with labelled edits.'}
for num,owner in owners.items():
 rid='ACC-'+num;pid=rid+'.P1';props.append(pid);s=next(x for x in specs.values() if x['title'].startswith(rid+' '))
 g['requirements'].append(dict(id=rid,capability=s['capability'],title=s['title'],fingerprint=s['fingerprint']))
 g['properties'].append(dict(id=pid,requirement_id=rid,statement=statements[num],scenarios=s['scenarios'],owner=owner,oracle='Independent literal expectations and actual native/browser/model artifacts with explicit limits.',source_globs=deps))
 for n,name,kind,pol,oracle in rows:
  if n!=num:continue
  source=sources[kind];module=('tests.' if kind=='request' or kind=='evidence' and name not in audio_cases else '')+Path(source).stem;tid='tangerine.local/api/internal/app::'+name if kind=='native' else 'unittest::'+module+'.'+{'request':'AccentRequest','speech':'AccentSpeech','evidence':'AccentEvidence'}[kind]+'.'+name;tests.append(tid);p=R/source
  case=dict(id=pid+'.'+name,property_id=pid,polarity=pol,scenario=s['scenarios'][0],scenario_fingerprint=s['scenario_fingerprints'][s['scenarios'][0]],setup=oracle,observable=oracle,red_expectation='Any missing, changed, unobserved or silently substituted requested outcome fails.',green_expectation=oracle,test_id=tid,command_id='accent-audio' if name in audio_cases else 'accent-'+kind,state='implemented' if p.exists() else 'planned',source_path=source,invalidation_dependencies=deps+[source],substitution=dict(classification='NO_TEST_DOUBLE',proof_claims=[oracle],forbidden_claims=['Universal accent/perceptual correctness','Unselected provider qualification','Reexecution of retained earlier checks']))
  if name=='test_voice_failure_negative':case['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Browser transport to the catalogue/preview URLs is blocked explicitly by the test through native CDP, then restored.',allowed_proof='Actual UI displays transport failure and retains inputs/voice choices, then recovers without LLM dispatch.',forbidden_claims=['An actual API/storage outage occurred','Real generation used substituted responses'])
  if p.exists():case['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  g['cases'].append(case)
env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',DOCKER_CONFIG=str(R/'data/local-preview/docker-config'))
g['commands'].append(dict(id='accent-native',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestAccent','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
g['commands'].append(dict(id='accent-request',runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_accents'],cwd='.',env=env,timeout_seconds=180,authority='local'))
for group,audio in [('accent-evidence',False),('accent-audio',True)]:
 names=[('test_accent_evidence' if audio else 'tests.test_accent_evidence')+'.AccentEvidence.'+name for _,name,kind,_,_ in rows if kind=='evidence' and (name in audio_cases)==audio]
 g['commands'].append(dict(id=group,runner='python-unittest',argv=['python3','-B','-m','unittest','-v',*names],cwd='tests' if audio else '.',env=env,timeout_seconds=180,authority='local'))
g['commands'].append(dict(id='accent-speech',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_accent_speech.py','-v'],cwd='.',env=env,timeout_seconds=180,authority='local'))
d['scope']['property_ids']=[x for x in d['scope']['property_ids'] if not x.startswith('ACC-')]+props
d['scope']['test_ids']=[x for x in d['scope']['test_ids'] if '::TestAccent' not in x and '::test_accent' not in x]+tests
d['reviews']=[x for x in d['reviews'] if x['id']!='accents-20261025']
d['reviews'].append(dict(id='accents-20261025',question='Selectable local Australian/Indian voices and real full-flow demo.',property_ids=props,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Known preparation/voice/render/model/acoustic owners and existing native tests; primary Melo upstream code/config.',outcome='Reuse existing checkpoint, speaker and foreground speech owners; add explicit local voices and English adapter.',results=[dict(path=p,classification='change_candidate',reason='Scoped actual owner; preserve existing data and single admission.') for p in deps]),dict(kind='semantic',status='not_applicable',query='Known owners from preceding speaker/locale inspection',reason='No unknown-owner lookup is needed; no semantic-index claim.',outcome='Exact source tracing only.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known component and pure adapter implementation',reason='No IDE symbol operation is needed.',outcome='No IDE-index claim.',results=[])],disposition='current_change',rationale='Actual user requests accents and chooses Australian/Indian; keep the earlier real demo request in scope.'))
for p,v in [(C/'verification.json',g),(C/'discovery.json',d)]:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'properties':4,'cases':len(rows),'planned':sum(x['id'].startswith('ACC-') and x['state']=='planned' for x in g['cases'])}))
