"""One stable I18 repair registration; no runtime, inference or schema gates."""
import ast, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'openspec/changes/implement-teacher-error-trainer'
p=base/'verification.json';v=json.loads(p.read_text())
props=['FIN-UI-01.P1','FIN-UI-06.P1','FIN-UI-07.P1','FIN-VERIFY.I18']
sha=lambda name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
data='data/iteration-18-verification-20261026/'
audit='audit/iteration-18-verification-20261026/'
ui=['services/web/app/prepare/'+n for n in ['RequestPreview.js','summaryVoices.js','Controls.js','AmountControl.js','CategoryPicker.js','SpeakerVoices.js','RecurringErrors.js','request.js','recurringRequest.js','usePreparation.js','response.js','page.js']]+['services/web/app/styles/prepare.css','services/web/app/styles/base.css','services/web/app/styles/shell.css','services/web/app/clientRequest.js','services/web/app/requestError.js']
evidence=[data+n for n in ['observations.json','repair-observations.json','requests.jsonl','frontend-source.json']]+[audit+'REVIEW.json','audit/iteration-18-preparation-20261026/review.py','data/iteration-18-preparation-20261026/observations.json','data/iteration-18-preparation-20261026/requests.jsonl']
for command in v['commands']:
 if command['id']=='completion-i18':command['env']={'TANGERINE_I18_DATA':data.rstrip('/'),'TANGERINE_I18_REVIEW':audit+'REVIEW.json'}
for prop in v['properties']:
 if prop['id'] in props:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+ui+evidence+['tests/test_preparation_recovery.py','tests/test_preparation_browser_repair.py']))
for case in v['cases']:
 if case['property_id'] in props and case['command_id']=='completion-i18':
  case.pop('blocker',None)
  case['source_sha256']=sha(case['source_path']);case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+ui+evidence))
modules=[('i18-preparation-recovery','tests.test_preparation_recovery','PreparationRecovery'),('i18-browser-repair','tests.test_preparation_browser_repair','PreparationBrowserRepair')]
oracles={
 'test_advanced_count_positive':('FIN-UI-01.P1','Blank simple Exact count is overridden by explicit advanced zero or null.'),
 'test_effective_voice_count_positive':('FIN-UI-01.P1','Advanced1/3 speakers submit vectors [British] / [British,Australian,null]; only active recurring speakers remain.'),
 'test_effective_density_positive':('FIN-UI-01.P1','Low400words gives4; three selected categories give3; cleared recurring profiles in20words give1.'),
 'test_ordinary_invalid_negative':('FIN-UI-01.P1','Without an override blank Exact is still invalid and malformed authored JSON has field-specific guidance.'),
 'test_success_response_positive':('FIN-UI-06.P1','A valid201/200 response retains its payload without an invented provider/storage result.'),
 'test_unreadable_response_negative':('FIN-UI-06.P1','HTML502, empty503 and broken200 bodies produce unreadable-service guidance, never an advanced-user-JSON error.'),
 'test_backend_details_negative':('FIN-UI-06.P1','Unknown/null failure payloads retain local guidance and never display SQL/password/backend strings.'),
 'test_actionable_response_positive':('FIN-UI-06.P1','MODEL_SETUP_REQUIRED and LEASE_ACTIVE preserve exact local setup/wait guidance.'),
 'test_malformed_summary_negative':('FIN-UI-01.P1','Null and object recurring/speaker/category/severity overrides retain Topic/editor and safe summary text without a global page failure.'),
 'test_advanced_native_positive':('FIN-UI-01.P1','With blank simple native controls, an advanced90word/C1/two/zero request submits once with the exact effective body.'),
 'test_clear_restores_validation_negative':('FIN-UI-01.P1','Clearing overrides restores retained blank editable controls and native Topic validation, with no second POST.'),
 'test_transient_read_positive':('FIN-UI-06.P1','Each initial503 read recovers on attempt2 with working options, no technical text and zero POST.'),
 'test_bounded_read_failure_negative':('FIN-UI-06.P1','Persistent read503s stop after3 each, show Retry/Refresh, retain input and keep Generate usable; no POST.'),
 'test_explicit_read_recovery_positive':('FIN-UI-06.P1','Explicit Retry and Refresh restore options while retaining the exact Topic and dispatching no generation.'),
 'test_service_response_negative':('FIN-UI-06.P1','HTML failure leaves Topic and a human service message, never raw technical or incorrect user-JSON text; only one POST.'),
 'test_primary_error_preserved_negative':('FIN-UI-06.P1','Model setup guidance survives a separate3-attempt saved-list failure and the action is never replayed.'),
 'test_write_lifecycle_positive':('FIN-UI-06.P1','Busy disables editing/actions; controlled success and Stop retain input; each blueprint/generation write is dispatched exactly once.'),
 'test_feedback_visible_positive':('FIN-UI-06.P1','Error/loading/success feedback is adjacent to Generate before optional controls, visible in desktop/mobile views and readable16px.'),
 'test_effective_amount_help_positive':('FIN-UI-06.P1','Advanced Low400word request and cleared recurring profiles show4 in both summary and amount help, without a POST.'),
 'test_current_typography_positive':('FIN-UI-07.P1','Loaded17px/24.65px Source Sans3 and all nine14px captions wrap within320px with no clipping.'),
}
for command,module,cls in modules:
 assert not any(c['id']==command for c in v['commands'])
 v['commands'].append({'id':command,'runner':'python-unittest','argv':['python3','-B','-m','unittest','-v',module],'cwd':'.','env':{},'timeout_seconds':60,'authority':'local'})
 source=module.replace('.','/')+'.py'
 methods=[n.name for n in ast.walk(ast.parse((ROOT/source).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
 for method in methods:
  prop,oracle=oracles[method];template=next(c for c in v['cases'] if c['property_id']==prop)
  boundary={'classification':'EXTERNAL_BOUNDARY','owner_replaced':'Constructed HTTP responses and a write-intercepting test gateway; all frontend/parser/projection owners are production code.','allowed_proof':'Actual source-built CUA states or literal pure-owner request/response outputs, as explicitly asserted by this exact test.','forbidden_claims':['New provider/model/speech operation or quality','Actual generated or saved fixture exercise','Deployment, PBT or financial execution','All-product linguistic or acoustic qualification']}
  v['cases'].append({'id':prop+'.'+method,'property_id':prop,'polarity':'negative' if method.endswith('negative') else 'positive','scenario':template['scenario'],'scenario_fingerprint':template['scenario_fingerprint'],'setup':'Use the literal inputs/actions in '+source+' and actual retained data/iteration-18-verification-20261026 observations. '+oracle,'observable':oracle,'red_expectation':'The independently specified observable is contradicted: '+oracle,'green_expectation':oracle,'test_id':'unittest::'+module+'.'+cls+'.'+method,'command_id':command,'state':'implemented','source_path':source,'source_sha256':sha(source),'invalidation_dependencies':ui+evidence+[source],'substitution':boundary})
p.write_text(json.dumps(v,indent=2)+'\n')
plans=json.loads((base/'completion-iterations.json').read_text());i=next(i for i in plans['iterations'] if i['iteration']==18)
dependents=[c for c in v['cases'] if c['source_path'] in ['tests/test_ux_request.py','tests/test_recurring_request.py']]
i['dependent_case_ids']=[c['id'] for c in dependents]
i['visual_scope']='Prepare basic/advanced and retained controls; malformed structured input, safe transient/terminal error/retry, action-adjacent feedback and readable typography. No new native/provider/financial execution.'
(base/'completion-iterations.json').write_text(json.dumps(plans,indent=2)+'\n')
selected=[c for c in v['cases'] if c['property_id'] in props or c['id'] in i['dependent_case_ids']]
selection={'iteration':18,'properties':props,'dependent_case_ids':i['dependent_case_ids'],'case_ids':[c['id'] for c in selected],'expected_case_count':len(selected),'command_ids':list(dict.fromkeys(c['command_id'] for c in selected)),'original_acceptance':'audit/iteration-18-preparation-20261026/ACCEPTANCE.json','proof_boundary':'Exact UI/projection/transport observations and retained unaffected facts; zero new inference, synthesis, native writes or deployment.'}
(ROOT/audit/'SELECTION.json').write_text(json.dumps(selection,indent=2)+'\n')
p=base/'discovery.json';d=json.loads(p.read_text());ids=[c['test_id'] for c in selected];d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+ids))
d['reviews'].append({'id':'iteration18-verification-repair-20261026','question':'Verify full I18 and repair nonblocking summary, effective precedence, error classification and action feedback siblings.','property_ids':props,'test_ids':ids,'disposition':'current_change','rationale':'Actual user authorizes repair and local verification/commits. Original receipts are preserved. No deployment, provider or financial action.','searches':[{'kind':'exact','status':'completed','query':'Trace all named preparation components, request/recurrence projection, usePreparation, shared clientRequest/requestError and API expansion/caller tests. Compare code, source-built CUA counterexamples and original receipt boundaries.','outcome':'Four confirmed finding groups repaired through cohesive presentation/projection/transport/action owners. Existing bounded safe-read/no-write-replay owner preserved. Eight native,12actual UI regressions plus13existing dependent projection cases extend20original cases.','results':[{'path':name,'classification':'interface_dependency','reason':'Known production owner inspected for direct/sibling behavior or preserved shared dependency.'} for name in ui]},{'kind':'semantic','status':'not_applicable','query':'Known explicit I18 preparation/error owners and prior map.','reason':'No unfamiliar ownership question; direct named source/caller tracing and actual browser counterexamples suffice. No semantic index evidence claimed.','outcome':'Exact source evidence only.','results':[]},{'kind':'jetbrains-index','status':'not_applicable','query':'Known JavaScript/CSS presentation and Python assertion paths.','reason':'No symbol refactor or index-dependent investigation was needed.','outcome':'No IDE/index evidence claimed.','results':[]}]})
p.write_text(json.dumps(d,indent=2)+'\n')
print('Registered full I18 repair selection:',len(selected),'cases; commands',selection['command_ids'])
