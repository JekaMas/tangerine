"""Register this increment without replacing previous properties or receipts."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs
g=json.loads((C/'verification.json').read_text());d=json.loads((C/'discovery.json').read_text())
for k in ['requirements','properties','cases']:g[k]=[x for x in g[k] if not x['id'].startswith('UX-')]
g['commands']=[x for x in g['commands'] if not x['id'].startswith('ux-')]
specs=parse_delta_specs(C);props=[];tests=[]
owners={'UX-01':'services/web/app/AppShell.js','UX-02':'services/web/app/prepare/CategoryPicker.js','UX-03':'services/api/internal/app/mutation_content.go','UX-04':'services/web/app/prepare/request.js'}
rows=[
('UX-01','test_routes_desktop_positive','positive','browser','All eleven real routes render shared navigation, headings and original actions.'),
('UX-01','test_mobile_navigation_positive','positive','browser','At 390px the menu opens, links work and current route is announced.'),
('UX-01','test_no_horizontal_overflow_negative','negative','browser','No tested page exceeds its 390px viewport; long data stays locally scrollable.'),
('UX-01','test_saved_answer_unchanged_negative','negative','browser','Original saved attempt answer/status and provider policy remain unchanged; UI reads dispatch no inference.'),
('UX-02','TestUXCatalogPositive','positive','native','GET preparation options returns exact shipped leaf IDs/labels and all 122 items without DB/model use.'),
('UX-02','TestUXCatalogControlsNegative','negative','native','The eight acceptable-variant leaves are explicitly controls; no unknown or duplicate category.'),
('UX-02','test_exact_categories_positive','positive','request','Collocation/formality yield only those two category_ids, no broad families and minimum one error each.'),
('UX-02','test_clear_categories_positive','positive','request','Clearing exact selection restores empty targets and automatic families/count.'),
('UX-02','test_category_failure_negative','negative','browser','Failed catalogue read retains topic and selections, offers retry and never claims missing categories loaded.'),
('UX-02','TestUXExactSelectionNegative','negative','native','An unrelated registered category cannot be admitted for a blueprint limited to exact leaves.'),
('UX-02','TestUXCategoryCoveragePositive','positive','coverage','Two independent errors covering both requested leaves are accepted.'),
('UX-02','TestUXCategoryCoverageNegative','negative','coverage','Two repeated-category errors cannot satisfy a request for two different categories.'),
('UX-02','TestUXAcousticSelectionPositive','positive','native','Exact pronunciation IDs retain the controlled local speech route.'),
('UX-02','TestUXAcousticSelectionNegative','negative','native','Text-only exact IDs do not acquire an acoustic route; an unavailable plain adapter cannot accept explicit pronunciation.'),
('UX-02','TestUXCheckpointProjectionPositive','positive','native','Category labels remain frozen request metadata rather than database object references.'),
('UX-02','TestUXCheckpointProjectionNegative','negative','native','The category-label exemption preserves the actual settings asset association.'),
('UX-03','TestUXSeverityPositive','positive','native','Every selected severity is accepted with the unchanged 1/2/3/4 weight.'),
('UX-03','TestUXSeverityRejectedNegative','negative','native','A major true-error output is rejected when only minor/moderate is selected.'),
('UX-03','TestUXSeverityLegacyPositive','positive','native','Absent/empty selection preserves prior admission and request compatibility.'),
('UX-03','TestUXSeverityZeroPositive','positive','native','Explicit zero with selected severity accepts an unchanged text/empty key.'),
('UX-03','test_minor_actual_positive','positive','model','Actual native mutation on the saved clean text satisfies exact category/count/minor request; retain prompt/context/model/output and MLflow.'),
('UX-03','test_zero_actual_negative','negative','model','Actual native zero request adds no errors despite category/severity context; no phantom defect or invented observation.'),
('UX-04','test_presets_positive','positive','request','200 requested words resolve Low=2, Medium=4, High=8; 150 Low=2 and short requests retain minimum one.'),
('UX-04','test_coverage_floor_positive','positive','request','A preset below three distinct required categories visibly resolves to three; overlapping pronunciation families are not double-counted.'),
('UX-04','test_exact_and_zero_positive','positive','request','Exact 3 stays 3, exact 0 stays 0 and Automatic stays null.'),
('UX-04','test_advanced_override_positive','positive','request','Explicit advanced targets/families/count/severity override matching simple controls; topic/other fields remain.'),
('UX-04','test_invalid_count_negative','negative','request','Negative/fractional/blank exact values are rejected without dispatch; no silent rounding of an exact count.'),
('UX-04','test_severity_independent_negative','negative','request','Changing severity never changes the requested amount or category IDs.'),
('UX-01','test_review_selection_positive','positive','browser','Reviews navigation offers actual saved exercises and selecting one loads history without running a review.'),
('UX-01','test_review_selection_failure_negative','negative','browser','A real catalogue outage offers retry; recovery does not dispatch a review.'),
('UX-04','test_advanced_editor_negative','negative','browser','Invalid advanced field types preserve the editor and leave the page usable without a request.'),
('UX-04','test_request_interruption_negative','negative','browser','A real blocked generation transport preserves all selected values and provides clear recovery without inference.'),
('UX-04','test_zero_caption_positive','positive','browser','Exact zero retains selected categories while clearly saying no mistakes are injected.'),
('UX-04','test_saved_request_positive','positive','browser','Real saved blueprint/readback preserves target IDs, severity and resolved count, including existing legacy records.')]
sources={'native':'services/api/internal/app/ux_controls_test.go','coverage':'services/api/internal/app/ux_coverage_test.go','request':'tests/test_ux_request.py','browser':'tests/test_ux_browser.py','model':'tests/test_ux_model_evidence.py'}
dependencies=['services/web/app','services/api/internal/app/preparation_catalog.go','services/api/internal/app/mutation_content.go','services/api/internal/app/domain.go','services/api/internal/app/acoustic_profile.go','specification/v2/contracts/exercise-request.schema.json','specification/v2/prompts/generate-v1.txt']
for rid,owner in owners.items():
 s=next(x for x in specs.values() if x['title'].startswith(rid+' '));pid=rid+'.P1';props.append(pid)
 g['requirements'].append(dict(id=rid,capability=s['capability'],title=s['title'],fingerprint=s['fingerprint']))
 g['properties'].append(dict(id=pid,requirement_id=rid,statement='The application SHALL '+s['title'][6:]+'.',scenarios=s['scenarios'],owner=owner,oracle='Independent literal request/count/severity expectations and actual rendered/readback evidence; preserve unknown provider observations.',source_globs=dependencies))
 for rr,name,pol,kind,oracle in rows:
  if rr!=rid:continue
  source=sources[kind];tid='tangerine.local/api/internal/app::'+name if kind in ('native','coverage') else 'unittest::'+Path(source).stem+'.'+{'request':'UXRequest','browser':'UXBrowser','model':'UXModel'}[kind]+'.'+name
  tests.append(tid);p=R/source
  row=dict(id=pid+'.'+name,property_id=pid,polarity=pol,scenario=s['scenarios'][0],scenario_fingerprint=s['scenario_fingerprints'][s['scenarios'][0]],setup='Authored literal fixtures and real owners; '+oracle,observable=oracle,red_expectation='A missing, changed, silently substituted or unobserved requested value fails.',green_expectation=oracle,test_id=tid,command_id='ux-'+kind,state='implemented' if p.exists() else 'planned',source_path=source,invalidation_dependencies=dependencies+[source],substitution=dict(classification='NO_TEST_DOUBLE',proof_claims=[oracle],forbidden_claims=['Universal linguistic/perceptual accuracy','Paid provider integration','Execution of unselected original release cases']))
  if p.exists():row['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  g['cases'].append(row)
env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',DOCKER_CONFIG=str(R/'data/local-preview/docker-config'))
g['commands'].append(dict(id='ux-native',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestUX(Catalog|ExactSelection|Severity|AcousticSelection|Checkpoint)','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
g['commands'].append(dict(id='ux-coverage',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^TestUXCategoryCoverage','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
for kind in ['request','browser','model']:g['commands'].append(dict(id='ux-'+kind,runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p',Path(sources[kind]).name,'-v'],cwd='.',env=env,timeout_seconds=180,authority='local'))
d['scope']['property_ids']=[x for x in d['scope']['property_ids'] if not x.startswith('UX-')]+props
d['scope']['test_ids']=[x for x in d['scope']['test_ids'] if '::TestUX' not in x and '::test_ux_' not in x]+tests
d['reviews']=[x for x in d['reviews'] if x['id']!='ux-controls-20261023']
d['reviews'].append(dict(id='ux-controls-20261023',question='Whole-service responsive visual refresh and precise category/severity/amount request propagation.',property_ids=props,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Known web/app pages, shared CSS, preparation request, native selected taxonomy and mutation admission.',outcome='Inconsistent chrome, constrained forms, no exact category UI or severity selector; existing exact-count and saved-blueprint owners are reused.',results=[dict(path=p,classification='change_candidate',reason='Actual owner inspected; preserve existing single-admission and local/included-only architecture.') for p in dependencies]),dict(kind='semantic',status='unavailable',query='jbcontext search -p services/web shared layout, CSS and preparation controls',reason='No index exists for this exact checkout.',outcome='No semantic-index evidence claimed; exact known-source tracing continued.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known page, request-projection and native admission owners',reason='No symbol refactor or IDE operation was needed for the inspected owners.',outcome='No IDE-index evidence claimed.',results=[])],disposition='current_change',rationale='Current user directly authorizes interface and control implementation; one canonical task list, no new paid service or runtime audit.'))
for p,x in [(C/'verification.json',g),(C/'discovery.json',d)]:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(dict(properties=len(props),cases=len(rows),planned=sum(x['state']=='planned' for x in g['cases'] if x['id'].startswith('UX-')))))
