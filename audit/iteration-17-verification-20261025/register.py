"""Register the final repaired I17 selection; no product/provider execution."""
import ast
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'openspec/changes/implement-teacher-error-trainer'
path=BASE/'verification.json'; graph=json.loads(path.read_text())
fps=json.loads((ROOT/'data/iteration-17-verification-20261025/spec-fingerprints.json').read_text())['specifications']
req=fps['completion-and-verification::FIN-RECOVERY Unobstructed local error recovery']
graph['requirements'].append(dict(id='FIN-RECOVERY',capability='completion-and-verification',title='FIN-RECOVERY Unobstructed local error recovery',fingerprint=req['fingerprint']))
scenario='FIN-RECOVERY Observable recovery and counterexamples'
source=['services/web/app/clientRequest.js','services/web/app/requestError.js','services/web/app/RefreshButton.js','services/web/app/**/*.js','services/web/app/styles/base.css']
graph['properties'].append(dict(id='FIN-RECOVERY.P1',requirement_id='FIN-RECOVERY',statement='Actual browser recovery retries safe reads, shows authored inline guidance, retains inputs and keyboard focus, and keeps writes singly owned without automatic replay or new UX gates.',scenarios=[scenario],owner='services/web/app/clientRequest.js',oracle='Literal call counts/status/delays, exact safe messages, retained field/score values, actual CUA focus and controlled write observations; expected results authored independently of production output.',source_globs=source+['tests/test_client_recovery.py','tests/test_i17_recovery_browser.py'],iteration=17))
for prop in graph['properties']:
 if prop['id'] in ['FIN-LEDGER.P1','FIN-VERIFY.I17']:
  prop['source_globs']=[p.replace('audit/iteration-17-reconciliation-20261025/REVIEW.json','audit/iteration-17-verification-20261025/REVIEW.json') for p in prop['source_globs']]
 if prop['id']=='FIN-VERIFY.I17':
  prop['statement']='Iteration 17 records actual ledger/evidence review plus the explicitly authorized whole-service recovery, UI/UX and typography repairs. Inspect affected real source-built views/actions with independent literal expectations. Exclude deployment, postdeployment, PBT, financial execution and new inference/synthesis; do not accept later iterations or universal product/provider quality.'

def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
for c in graph['cases']:
 if c['property_id'] in ['FIN-LEDGER.P1','FIN-VERIFY.I17']:
  c['source_sha256']=digest(c['source_path'])
  c['invalidation_dependencies']=[p.replace('audit/iteration-17-reconciliation-20261025/REVIEW.json','audit/iteration-17-verification-20261025/REVIEW.json') for p in c['invalidation_dependencies']]
  if c['property_id']=='FIN-VERIFY.I17':
   c['substitution']['proof_claims']=['Review packet correctness against independently authored evidence rules. Actual visual/action observations are separately registered under FIN-RECOVERY.P1.']
 for group in ['request_error']:
  if c['source_path']=='tests/test_request_error.py':
   c['source_sha256']=digest(c['source_path'])
   c['setup']='Exercise the actual shared presentation owner with network/programmer exceptions and explicitly authored user guidance.'
   c['observable']=c['green_expectation']='Unknown technical errors use safe fallback; explicitly authored guidance survives; uncertain write outcomes do not claim deletion or saving.'
   c['substitution']['proof_claims']=[c['green_expectation']]

oracles={
 'test_deadline_stops_retry_negative':'TimeoutError dispatches once; it is never retried.',
 'test_retry_after_date_respected_negative':'Future HTTP-date Retry-After dispatches once and returns503.',
 'test_failed_experiment_row_negative':'Controlled failed experiment row displays exact human guidance without raw error code or page overflow.',
 'test_transient_read_recovers_positive':'503 then 200: exactly two calls and one 160ms wait.',
 'test_network_read_recovers_positive':'Network TypeError then 200: exactly two calls.',
 'test_exhaustion_is_bounded_negative':'Persistent 503: exactly three calls; waits [160,480]; return 503.',
 'test_no_permission_or_quota_probe_negative':'403 and Retry-After 60s each dispatch once.',
 'test_no_write_replay_negative':'POST network failure and PUT 503 each dispatch once.',
 'test_cancel_never_dispatches_negative':'Pre-aborted signal dispatches zero calls.',
 'test_write_identity_preserved_positive':'PUT retains identical options object, body and Idempotency-Key same.',
 'test_technical_errors_not_displayed_negative':'Raw SQL/secret/Traceback absent from displayed exception and saved failure guidance.',
 'test_authored_recovery_positive':'Exact authored message: Your answer is saved. Refresh to continue.',
 'test_invalid_json_has_field_guidance_negative':'Invalid JSON names Mapping program and retained input, without raw content.',
 'test_diagnostic_log_redacted_negative':'Logged path/status excludes hidden query, private answer and password.',
 'test_routes_readable_positive':'All eleven named headings at mobile390x844 and desktop1280x720; Source Sans 3 body17px, no horizontal overflow.',
 'test_all_read_failures_negative':'All eleven routes under controlled503 retain a visible human error and enabled recovery action without raw marker/overflow.',
 'test_transient_read_positive':'Actual source route recovers silently with populated records and enabled Refresh.',
 'test_source_recovery_positive':'Source outage then Refresh retains review-input-retained and restores the source list.',
 'test_generation_failure_negative':'Failed initial blueprint shows choices retained, topic retained, Generate enabled; never claims saved exercise.',
 'test_report_failure_negative':'Controlled report write failure retains Recovery review report title and Calculate action with exact human guidance.',
 'test_keyboard_refresh_positive':'Enter leaves BUTTON Refresh focused with 3px outline, retained title and no alert after successful read.',
 'test_refresh_during_write_negative':'During delayed write Calculate remains disabled, Refresh enabled; Calculate re-enables after failure.',
 'test_saved_result_positive':'Existing saved result stays primary60/100, optional explanation100%,1of2found,1miss,0false positives; answer read-only/audio paused.',
 'test_controlled_write_not_replayed_negative':'One controlled POST and two GET report reads during Refresh; no automatic write replay.'}
for module,klass,command in [('test_client_recovery','ClientRecovery','i17-client-recovery'),('test_i17_recovery_browser','RecoveryBrowser','i17-recovery-browser')]:
 file=f'tests/{module}.py'
 graph['commands'].append(dict(id=command,runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.'+module],cwd='.',env={},timeout_seconds=60,authority='local'))
 cls=next(x for x in ast.parse((ROOT/file).read_text()).body if isinstance(x,ast.ClassDef))
 for method in [x.name for x in cls.body if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')]:
  oracle=oracles[method]
  graph['cases'].append(dict(id='FIN-RECOVERY.P1.'+method,property_id='FIN-RECOVERY.P1',polarity='positive' if method.endswith('positive') else 'negative',scenario=scenario,scenario_fingerprint=req['scenario_fingerprints'][scenario],setup='Exercise the actual JS owner with controlled responses.' if module=='test_client_recovery' else 'Read retained actual CUA actions from the isolated source-built frontend; all writes are controlled, only saved-record reads reach local backend.',observable=oracle,red_expectation='The independently expected outcome is absent or contradicted: '+oracle,green_expectation=oracle,test_id=f'unittest::tests.{module}.{klass}.{method}',command_id=command,state='implemented',source_path=file,source_sha256=digest(file),invalidation_dependencies=source+[file],substitution=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='HTTP/network outcomes' if module=='test_client_recovery' else 'HTTP failure/write outcomes supplied by a test-owned gateway; saved records are read only',allowed_proof=oracle,proof_claims=[oracle],forbidden_claims=['Hosted model/speech operation or quality','New end-to-end generation/grading','Deployment or financial execution','An independent reviewer or universal product correctness'])))

# Retain the old property/test identities; run only three genuinely invalidated
# failure helpers, not unrelated already green replay/starter helpers.
helpers=['test_failure_reasons_positive','test_failure_empty_message_negative','test_completed_stale_failure_negative']
graph['commands'].append(dict(id='i17-affected-failure-helpers',runner='python-unittest',argv=['python3','-B','-m','unittest','-v']+['test_final_functional_helpers.FinalFunctionalHelpers.'+x for x in helpers],cwd='.',env={'PYTHONPATH':'tests'},timeout_seconds=60,authority='local'))
dependent=[]
for c in graph['cases']:
 if c['source_path']=='tests/test_final_functional_helpers.py' and c['test_id'].rsplit('.',1)[-1] in helpers:
  c['command_id']='i17-affected-failure-helpers';dependent.append(c['id'])
 elif c['source_path'] in ['tests/test_request_error.py','tests/test_ux_request.py']:dependent.append(c['id'])
path.write_text(json.dumps(graph,indent=2)+'\n')
iteration=BASE/'completion-iterations.json'; packet=json.loads(iteration.read_text());item=next(x for x in packet['iterations'] if x['iteration']==17)
item['requirement_ids'].append('FIN-RECOVERY');item['verify_property_ids'].append('FIN-RECOVERY.P1');item['dependent_case_ids']=dependent;item['visual_applicable']=True;item['visual_scope']='User-authorized verification repair: all eleven route recovery states, shared guidance/Refresh/focus and affected keyboard/narrow-width actions; no deployment or new provider calls.'
iteration.write_text(json.dumps(packet,indent=2)+'\n')
selection=dict(properties=item['verify_property_ids'],dependent_case_ids=dependent,expected_case_count=46,excluded=['deployment','postdeployment','PBT','financial execution','inference','synthesis'],invalidation='Ledger helper/test assertions, shared request/presentation/Refresh owners, affected literal request/failure helpers and new controlled browser actions changed. Unrelated native/provider/media and unchanged replay/starter assertions retain their original greens.')
(ROOT/'audit/iteration-17-verification-20261025/SELECTION.json').write_text(json.dumps(selection,indent=2)+'\n')
ledger_path=BASE/'discovery.json';ledger=json.loads(ledger_path.read_text());props=item['verify_property_ids'];test_ids=[c['test_id'] for c in graph['cases'] if c['property_id'] in props or c['id'] in dependent]
ledger['scope']['property_ids'].append('FIN-RECOVERY.P1')
ledger['scope']['test_ids']=list(dict.fromkeys(ledger['scope']['test_ids']+test_ids))
ledger['reviews'].append(dict(id='iteration17-verification-recovery-20261026',question='Review the exact ledger helper, shared client failure owners and all sibling routes; repair observed errors without new UX gates or provider operations.',disposition='current_change',rationale='Current user authorizes I17 verification and generalized sibling UI recovery repair without deployment, PBT, financial execution or provider calls.',property_ids=props,test_ids=test_ids,searches=[dict(kind='exact',status='completed',query='Read named requestError/usePreparation/useListening/route owners, original101ledger and admitted receipts; inspect all sibling fetch/error/Refresh sites.',outcome='Receipt-identity weakness, raw technical projections, absent safe read retries, Refresh focus/state ownership and Recovery missing presentation import repaired. Controlled all-route failures and retained-field/score/focus observations recorded.',results=[dict(path=p,classification='interface_dependency',reason='Exact named production/review/test owner inspected.') for p in ['services/web/app/requestError.js','services/web/app/clientRequest.js','services/web/app/RefreshButton.js','services/web/app/listen/useListening.js','services/web/app/reports/page.js','services/web/app/recovery/page.js','audit/iteration-17-reconciliation-20261025/verify.py']]),dict(kind='semantic',status='not_applicable',query='Known exact error/request and I17 audit owners.',reason='The entry-point files and owner functions were already identified; direct sibling source tracing answered this verification question. No semantic search evidence is claimed.',outcome='Known source reads plus actual browser and literal owner tests.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known JS modules and document records.',reason='No IDE refactor or unknown symbol ownership was needed; no IDE/index evidence is claimed.',outcome='Known source reads only.',results=[])]))
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps(dict(new_cases=24,dependent_cases=len(dependent),total=46)))
