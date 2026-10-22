"""Register only this increment's exact tests; preserve all older fingerprints."""
from pathlib import Path
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

change=ROOT/'openspec/changes/implement-teacher-error-trainer'
p=change/'verification.json';graph=json.loads(p.read_text())
graph['cases']=[x for x in graph['cases'] if not x['id'].startswith('USE-')]
pending=next(x for x in graph['commands'] if x['id']=='pending')
pending['expected_markers']=[x for x in pending['expected_markers'] if not x.startswith('planned::USE-')]
commands=[
 {'id':'usability-go','runner':'go-test-json','argv':['./tests/go-docker','test','-json','-race','-count=1','-run','^Test(PreparationOrdinary|PreparationSummary|PreparationLegacySummary|Checking)','./internal/app'],'cwd':'.','env':{},'timeout_seconds':300,'authority':'local'},
 {'id':'usability-browser','runner':'python-unittest','argv':['python3','-B','-m','unittest','discover','-s','tests','-p','test_usability_browser.py','-v'],'cwd':'.','env':{'TANGERINE_USABILITY_WEB_IMAGE':'tangerine-usability-web:local'},'timeout_seconds':660,'authority':'local'},
]
for command in commands:
 graph['commands']=[x for x in graph['commands'] if x['id']!=command['id']]+[command]
specs=parse_delta_specs(change)
browser_path='tests/test_usability_browser.py';browser_source=(ROOT/browser_path).read_text()
methods={n.name:ast.get_source_segment(browser_source,n) for n in ast.walk(ast.parse(browser_source)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
groups={
 'USE-01':[x for x in methods if any(word in x for word in ['controls','levels','families','automatic','zero','advanced','invalid','request_failure','saved_summary'])],
 'USE-02':['test_extraction_progress_positive','test_matching_progress_positive','test_score_before_comments_positive','test_reads_no_dispatch_negative','test_privacy_negative'],
 'USE-03':['test_read_failure_negative','test_feedback_failure_negative','test_feedback_retry_positive','test_observer_stop_positive','test_unmount_negative'],
}
go_groups={'USE-01':['TestPreparationOrdinaryChoicesPositive','TestPreparationOrdinaryInvalidNegative','TestPreparationSummaryChoicesPositive','TestPreparationLegacySummaryNegative'],'USE-02':['TestCheckingStagesPositive','TestCheckingIncompleteNegative']}
for (cap,title),spec in specs.items():
 if cap!='interactive-usability':continue
 rid=title.split()[0];pid=rid+'.P1';scenario=spec['scenarios'][0]
 for name in groups[rid]+go_groups.get(rid,[]):
  browser=name.startswith('test_')
  source=browser_path if browser else 'services/api/internal/app/usability_test.go'
  test_id=('unittest::test_usability_browser.UsabilityBrowser.'+name) if browser else 'tangerine.local/api/internal/app::'+name
  literal=(methods[name] if browser else (ROOT/source).read_text()).strip()
  dependencies=['services/web/app/prepare','services/api/internal/app/preparation.go','services/api/internal/app/speech_http.go'] if rid=='USE-01' else ['services/web/app/listen','services/api/internal/app/interpretation_view.go']
  graph['cases'].append({'id':pid+'.'+name,'property_id':pid,'polarity':'negative' if name.lower().endswith('negative') else 'positive','scenario':scenario,'scenario_fingerprint':spec['scenario_fingerprints'][scenario],
   'setup':json.dumps({'origin':'Real application/storage/browser with constructed external model replies and held response timing; form generation stops after real blueprint save. Native initial preparation is seeded through the actual freeze/checkpoint owner.','fixture':'tests/usability-browser and tests/usability_fixture_test.go','literal_test':literal}),
   'observable':literal,'red_expectation':'A changed request/score/answer, missing stage/control, extra inference/submission, private leak or live observer after completion fails the exact assertions.','green_expectation':'Each independently specified literal input/state/count/display equals the actual selected native/browser output.',
   'test_id':test_id,'command_id':'usability-browser' if browser else 'usability-go','state':'implemented','source_path':source,'source_sha256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),
   'invalidation_dependencies':[source]+dependencies+(['tests/usability-browser','tests/usability_fixture_test.go','tests/native_listening_test.go','tests/native_interpretation_test.go','tests/native_scoring_test.go'] if browser else []),
   'substitution':{'classification':'EXTERNAL_BOUNDARY' if browser else 'NO_TEST_DOUBLE',**({'owner_replaced':'External model output/timing and post-blueprint generation only.','proof_claims':['Actual UI/HTTP/admission/checkpoint/storage behavior and exact state/call-count/score projection.'],'forbidden_claims':['Live provider linguistic quality, CEFR certification or synthesis quality.','Complete generation from the deliberately paused form test.']} if browser else {})},
   'distinct_reason':scenario+': '+name+' qualifies the specific selected request/progress/lifecycle obligation with independent literal expectations.'})
p.write_text(json.dumps(graph,indent=2)+'\n')
p=change/'discovery.json';discovery=json.loads(p.read_text());discovery['reviews']=[x for x in discovery['reviews'] if x['id']!='interactive-usability-20261022']
discovery['scope']['property_ids']=list(dict.fromkeys(discovery['scope']['property_ids']+[r+'.P1' for r in groups]))
discovery['scope']['test_ids']=list(dict.fromkeys(discovery['scope']['test_ids']+[x['test_id'] for x in graph['cases'] if x['id'].startswith('USE-')]))
discovery['reviews'].append({'id':'interactive-usability-20261022','question':'Why did submit take30seconds, and are ordinary request controls and foreground progress complete?','property_ids':[r+'.P1' for r in groups],'test_ids':sorted({x['test_id'] for x in graph['cases'] if x['id'].startswith('USE-')}),
 'searches':[{'kind':'exact','status':'completed','query':'Actual attempt operation timing and exact preparation/interpretation/listening/score owners and tests','outcome':'Answer save took0.013s; extraction/mapping/feedback took9.163/9.709/10.432s. Count existed only in advanced JSON and categories were free text; score already checkpoints before comments.','results':[{'path':path,'classification':'change_candidate','reason':'Expose accepted inputs or read-only durable checking progress through the existing owner.'} for path in ['services/web/app/prepare/page.js','services/web/app/listen/useListening.js','services/api/internal/app/interpretation_view.go','services/api/internal/app/preparation.go']]},
 {'kind':'semantic','status':'unavailable','query':'jbcontext search for submit latency and preparation controls in the exact checkout','reason':'No index found for repository fffb5cc5644365f06373a66ac2d3932f0d4b510a4a6f7f5df5c8ffd285d35165.','outcome':'Used exact source/runtime tracing; no semantic-index evidence claimed.','results':[]},
 {'kind':'jetbrains-index','status':'not_applicable','query':'Exact runtime and known owner inspection','reason':'The actual native records and exact owners resolved the selected behavior; no index/refactor operation was required.','outcome':'No IDE-index evidence claimed.','results':[]}],
 'disposition':'current_change','rationale':'Repair ordinary UI/property gaps without changing grading stages, prompts, models, formulas, paid access or foreground ownership.'})
p.write_text(json.dumps(discovery,indent=2)+'\n')
p=change/'property-inventory.json';inventory=json.loads(p.read_text());inventory=[x for x in inventory if x['id'] not in groups]
for requirement in graph['requirements']:
 if requirement['id'] in groups:
  prop=next(x for x in graph['properties'] if x['requirement_id']==requirement['id'])
  inventory.append({'id':requirement['id'],'capability':requirement['capability'],'title':requirement['title'],'statement':prop['statement'],'scenarios':prop['scenarios'],'owner':prop['owner'],'source':'Actual user submit-latency and ordinary request-control repair; interactive-usability/spec.md.'})
p.write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps({'mapped_cases':sum(x['id'].startswith('USE-') for x in graph['cases']),'physical_tests':len({x['test_id'] for x in graph['cases'] if x['id'].startswith('USE-')})}))
