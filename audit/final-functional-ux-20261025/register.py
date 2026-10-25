"""Add only FX properties/cases to the existing evidence DAG."""
from pathlib import Path
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

def main():
 graph=json.loads((CHANGE/'verification.json').read_text());discovery=json.loads((CHANGE/'discovery.json').read_text());specs=parse_delta_specs(CHANGE)
 for field in ('requirements','properties','cases'):graph[field]=[x for x in graph[field] if not x['id'].startswith('FX-')]
 graph['commands']=[x for x in graph['commands'] if not x['id'].startswith('final-functional-')]
 properties=[];cases=[];tests=[]
 owners={'01':'services/api/internal/app/mutation_content.go::mutationContent','02':'services/web/app/prepare/RequestPreview.js::RequestPreview','03':'services/api/internal/app/history_summary.go::attemptHistorySummary','04':'services/web/app/listen/passageReplay.js::createPassageReplay','05':'services/web/app/reports/starters.js::experimentStarter','06':'services/web/app/layout.js::RootLayout'}
 deps={
 '01':['services/api/internal/app/mutation_content.go','services/api/internal/app/mutation_manifest.go','services/api/internal/app/mutation_selection.go','services/api/internal/app/functional_category_test.go','services/api/internal/app/testdata/linguistic-contrasts.json'],
 '02':['services/web/app/prepare/Controls.js','services/web/app/prepare/RequestPreview.js','services/web/app/prepare/page.js','services/web/app/prepare/failureMessage.js','services/web/app/prepare/usePreparation.js','services/web/app/styles/prepare.css'],
 '03':['services/api/internal/app/attempt_history.go','services/api/internal/app/history_summary.go','services/api/internal/app/speech_http.go','services/web/app/savedRecord.js','services/web/app/attempts/page.js','services/web/app/audio/page.js'],
 '04':['services/web/app/listen/page.js','services/web/app/listen/Results.js','services/web/app/listen/passageReplay.js','services/web/app/styles/base.css'],
 '05':['services/web/app/reports/page.js','services/web/app/reports/StarterForms.js','services/web/app/reports/starters.js','services/web/app/cleanup/page.js','services/web/app/cleanup/RecordPicker.js'],
 '06':['services/web/app/**/*.js','services/web/app/styles/base.css','services/web/app/styles/prepare.css']}
 for num in owners:
  rid='FX-'+num;s=next(v for v in specs.values() if v['title'].startswith(rid+' '));pid=rid+'.P1';properties.append(pid)
  graph['requirements'].append(dict(id=rid,capability=s['capability'],title=s['title'],fingerprint=s['fingerprint']))
  graph['properties'].append(dict(id=pid,requirement_id=rid,statement='The application SHALL satisfy '+s['title']+' with positive and negative observed behavior.',scenarios=s['scenarios'],owner=owners[num],oracle='Independent authored contrasts/arithmetic and literal browser/action expectations; no universal model/hearing claim.',source_globs=deps[num]))
 def add(num,test,source,polarity,expectation,command,double=None):
  rid='FX-'+num;s=next(v for v in specs.values() if v['title'].startswith(rid+' '));tests.append(test)
  sub=dict(classification='NO_TEST_DOUBLE',proof_claims=[expectation],forbidden_claims=['Universal linguistic or auditory quality','Unperformed hosted integration','Independent human gold'])
  if double:sub=dict(classification='EXTERNAL_BOUNDARY',owner_replaced=double,allowed_proof=expectation,forbidden_claims=['Uncontrolled live provider behavior','Actual listening from a constructed response'])
  row=dict(id=rid+'.P1.'+test.split('::')[-1],property_id=rid+'.P1',polarity=polarity,scenario=s['scenarios'][0],scenario_fingerprint=s['scenario_fingerprints'][s['scenarios'][0]],setup=expectation,observable=expectation,red_expectation='The literal expected state/value/action is absent or wrong.',green_expectation=expectation,test_id=test,command_id=command,state='implemented',source_path=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),invalidation_dependencies=list(dict.fromkeys(deps[num]+[source])),substitution=sub)
  cases.append(row);graph['cases'].append(row)
 refs=json.loads((ROOT/'specification/v2/domain/linguistic-contrast-set.v1.json').read_text())['examples']
 for ref in refs:
  if ref['taxonomy_id'].startswith(('pronunciation.','acceptable_variant.')) or ref['modality']!='written_contextual_language':continue
  for polarity,name in [('positive','TestFXWrittenMutationPositive'),('negative','TestFXWrittenMutationNegative')]:
   add('01','tangerine.local/api/internal/app::'+name+'/'+ref['taxonomy_id'],'services/api/internal/app/functional_category_test.go',polarity,'Category '+ref['taxonomy_id']+': '+('admit authored mutation, replay exact independent surface and retain correction' if polarity=='positive' else 'reject unselected leaf, no-op repair and rewritten canonical checkpoint'),'final-functional-go')
 for name in ['TestFXHistorySummaryPositive','TestFXHistorySummaryUnicodePositive','TestFXHistoryLegacyNegative','TestFXPreparationDatePositive']:
  add('03','tangerine.local/api/internal/app::'+name,'services/api/internal/app/functional_category_test.go','negative' if name.endswith('Negative') else 'positive','Literal saved title/date/excerpt, Unicode truncation, original identity and honest missing metadata: '+name,'final-functional-go')
 source='tests/test_final_functional_helpers.py'
 for node in ast.walk(ast.parse((ROOT/source).read_text())):
  if not isinstance(node,ast.FunctionDef) or not node.name.startswith('test_'):continue
  n=node.name;num='04' if any(v in n for v in ['passage','autoplay','seek','range','playback','dispose','media']) else '05' if any(v in n for v in ['report','experiment','asset','semantic','invalid_fields']) else '02' if 'failure' in n else '03'
  add(num,'unittest::test_final_functional_helpers.FinalFunctionalHelpers.'+n,source,'negative' if n.endswith('negative') else 'positive','Native JS owner with independently literal expectations in '+source+'::'+n,'final-functional-helpers','Browser media event source' if num=='04' else None)
 source='tests/test_final_functional_browser.py'
 if (ROOT/source).exists():
  for node in ast.walk(ast.parse((ROOT/source).read_text())):
   if not isinstance(node,ast.FunctionDef) or not node.name.startswith('test_'):continue
   num=next((n for word,n in [('category','01'),('audio_limits','01'),('prepare','02'),('failure','02'),('history','03'),('result','04'),('replay','04'),('starter','05'),('cleanup','05')] if word in node.name),'06')
   add(num,'unittest::test_final_functional_browser.FinalFunctionalBrowser.'+node.name,source,'negative' if node.name.endswith('negative') else 'positive','Literal real CUA browser/action and saved HTTP observation: '+node.name,'final-functional-browser')
 source='tests/test_request_error.py'
 for node in ast.walk(ast.parse((ROOT/source).read_text())):
  if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'):
   add('06','unittest::test_request_error.RequestError.'+node.name,source,'negative' if node.name.endswith('negative') else 'positive','Transport formatting retains specific native errors and uncertain write outcomes: '+node.name,'final-functional-errors')
 graph['commands'].append(dict(id='final-functional-errors',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_request_error.py','-v'],cwd='.',env={},timeout_seconds=30,authority='local'))
 env={'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(ROOT/'data/local-preview/docker-config')}
 graph['commands'].append(dict(id='final-functional-go',runner='go-test-json',argv=['./tests/go-docker','test','-json','-count=1','-run','^TestFX','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
 for name in ('helpers','browser'):
  if name=='browser' and not (ROOT/'tests/test_final_functional_browser.py').exists():continue
  graph['commands'].append(dict(id='final-functional-'+name,runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_final_functional_'+name+'.py','-v'],cwd='.',env={},timeout_seconds=90,authority='local'))
 discovery['scope']['property_ids']=[v for v in discovery['scope']['property_ids'] if not v.startswith('FX-')]+properties
 discovery['scope']['test_ids']=[v for v in discovery['scope']['test_ids'] if not ('::TestFX' in v or '::test_final_functional_' in v or '::test_request_error.' in v)]+tests
 discovery['reviews']=[x for x in discovery['reviews'] if x['id']!='final-functional-ux-20261025']
 discovery['reviews'].append(dict(id='final-functional-ux-20261025',question='Verify all non-pronunciation categories and complete functional/UI/UX/typography user paths; repair observed gaps.',property_ids=properties,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Known catalogue, mutation admission/manifest/scoring, saved history and eleven UI routes',outcome='88 non-pronunciation leaves; add 83 written native replay/admission contrasts and repair UX01–08.',results=[dict(path=p.split('::')[0],classification='change_candidate',reason='Actual selected production owner') for p in owners.values()]),dict(kind='semantic',status='completed',query='Tangerine preparation mutation category selection, answer interpretation and scoring owners for grammar lexis discourse pragmatic register and fluency categories',outcome='CLI reports no semantic index for this checkout; no semantic code evidence obtained.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known exact owners; no symbol refactor',reason='No IDE index operation required.',outcome='No index claim.',results=[])],disposition='current_change',rationale='User authorizes functional repairs, real UI review and scoped commit. No performance campaign, paid use, new service or human review.'))
 for path,obj in [(CHANGE/'verification.json',graph),(CHANGE/'discovery.json',discovery),(HERE/'CASES.json',{'properties':properties,'canonical_details':'../../openspec/changes/implement-teacher-error-trainer/verification.json','cases':[{k:r[k] for k in ('id','property_id','polarity','test_id','source_path')} for r in cases]})]:path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'properties':len(properties),'cases':len(cases)}))
if __name__=='__main__':main()
