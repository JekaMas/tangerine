"""Bind the eight implemented I23 cases to native/Free/CUA/Lab observations."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
AUDIT=ROOT/'audit/iteration-23-gemini-20261026';PREFIX='data/iteration-23-gemini-20261026/'
PROPS=['FIN-GEMINI.P1','FIN-VERIFY.I23'];SOURCE='tests/test_completion_i23.py'
OWNERS=['services/api/internal/provider/execute.go','services/api/internal/app/provider_inference.go','services/api/internal/lab/builtin.json','specification/v2/prompts/extract-v1.txt']
HELPERS=['tests/native_gemini_test.go','services/api/internal/app/extraction_attribution_test.go','services/api/internal/provider/repair_context_test.go','audit/iteration-23-gemini-20261026/review.py','audit/iteration-23-gemini-20261026/observe.py','tests/test_completion_i17.py','audit/iteration-17-reconciliation-20261025/verify.py']
PROOF=[PREFIX+x for x in ['account-api-keys.txt','account-billing.txt','answer-expectation.json','native-relationship.json','observations.json','layouts.json','reopened.json','playback.json','requests.jsonl','native-write-responses.jsonl','REVIEW.json','candidate-reconciliation.json','lab-readback.json','extraction-siblings.jsonl','repair-protocol.jsonl','historical-ledger.log','live/preparation.json','live/fixture.json','live/key.json','live/result.json','live/dispatches.json','live/exercise.wav','live/assets/','resume/fixture.json','resume/attempt.json','resume/result.json','resume/dispatches.json','resume/documents.json','resume/assets/','resume/native.jsonl','resume/exit-code','repair/native.jsonl','repair/exit-code','controlled/native.jsonl','controlled/recovery.json','context/native.jsonl','context/repair-context.json']]
PROOF += [PREFIX+'controlled/error-'+name+'.json' for name in ['quota','denied','credentials','unavailable']]

def main():
 p=CHANGE/'verification.json';v=json.loads(p.read_text());old=[c for c in v['cases'] if c['property_id'] in PROPS];oldids={c['test_id'] for c in old};by={'test_'+c['id'].rsplit('.',1)[1]:c for c in old}
 methods=sorted(n.name for n in ast.walk(ast.parse((ROOT/SOURCE).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
 extra={
  'test_attribution_positive':('positive','Actual same-case Gemini extraction retains the attributed claim and supplied repair/reason; native repaired result is100/100. The shared recorder preserves semantic-repair metadata and a subsequent transport retry across native and provider wire owners.'),
  'test_unparsed_negative':('negative','Keep the actual original attribution uncertainty and the pre-fix recorder panic as failed baseline evidence. Genuine unparsed substantive text is not erased to obtain a score; the repaired current candidate passes without relabeling those failures.')}
 sha=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
 for method in methods:
  c=by.get(method)
  if c is None:
   c=copy.deepcopy(old[0]);polarity,oracle=extra[method];c.update(id='FIN-GEMINI.P1.'+method.removeprefix('test_'),property_id='FIN-GEMINI.P1',polarity=polarity,setup='Use the actual selected native/Free observations and literal sibling packets in '+SOURCE+':'+method,observable=oracle,green_expectation=oracle,red_expectation='Actual output contradicts: '+oracle);v['cases'].append(c)
  substitution=dict(classification='NO_TEST_DOUBLE',proof_claims=['The inspected finite native/provider/media/browser/development evidence only.'],forbidden_claims=['Universal model/linguistic correctness','An incomplete failed baseline counted as successful candidate','New inference or full source acquisition from evidence readback'])
  if method in ['test_gemini_negative','test_attribution_positive']:
   substitution=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Constructed Gemini quota/denial/unavailable/repair HTTP replies for controlled native cases; actual hosted candidate observations are separate.',allowed_proof='Actual native checkpoint preservation, finite retry/repair/context behavior plus the explicitly retained live selected-flow observations.',forbidden_claims=['Hosted entitlement or quality from a controlled reply','Intentional quota exhaustion','A replay substituted for an actual candidate call'])
  c.update(test_id='unittest::tests.test_completion_i23.CompletionI23.'+method,command_id='completion-i23',state='implemented',source_path=SOURCE,source_sha256=sha,invalidation_dependencies=list(dict.fromkeys(c['invalidation_dependencies']+OWNERS+HELPERS+PROOF+[SOURCE])),substitution=substitution);c.pop('blocker',None)
 for prop in v['properties']:
  if prop['id'] in PROPS:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+OWNERS+HELPERS+PROOF+[SOURCE]))
 # The historical replay source changed meaningfully. Its six literal cases
 # are selected again alongside I23; old receipts are not disguised as current.
 historical=[];historical_sha=hashlib.sha256((ROOT/'tests/test_completion_i17.py').read_bytes()).hexdigest()
 for case in v['cases']:
  if case.get('source_path')=='tests/test_completion_i17.py':
   case['source_sha256']=historical_sha;historical.append(case['id'])
 p.write_text(json.dumps(v,indent=2)+'\n')
 selected=[c for c in v['cases'] if c['property_id'] in PROPS];assert len(selected)==len(methods)==8
 (AUDIT/'SELECTION.json').write_text(json.dumps(dict(iteration=23,primary_properties=PROPS,properties=PROPS+['FIN-LEDGER.P1','FIN-VERIFY.I17'],expected_primary_case_count=8,expected_case_count=8+len(historical),case_ids=[c['id'] for c in selected]+historical,scope='Eight I23 finite oracles plus six directly affected historical replay cases. Actual hosted/media/CUA/Lab observations retained without redispatch. Failed baseline and controlled replies stay explicit.'),indent=2)+'\n')
 p=CHANGE/'discovery.json';d=json.loads(p.read_text());ids=[c['test_id'] for c in selected]
 d['scope']['test_ids']=list(dict.fromkeys([x for x in d['scope']['test_ids'] if x not in oldids]+ids))
 for r in d['reviews']:
  if any(x in oldids for x in r.get('test_ids',[])):r['test_ids']=list(dict.fromkeys([x for x in r['test_ids'] if x not in oldids]+ids))
 d['reviews']=[r for r in d['reviews'] if r['id']!='iteration23-gemini-free-20261026']
 d['reviews'].append(dict(id='iteration23-gemini-free-20261026',question='Qualify actual explicitly selected Gemini Free text generation/mutation/checking/feedback through native persistence, local audio, exact scores and Lab; fix causes/siblings without paid fallback or repeated runtime checks.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Known native adapter/InvokeLLM/extraction owners traced directly. Actual attribution uncertainty and Gemini semantic-repair recorder panic repaired through shared ownership. Historical I17 replay reads its accepted snapshot; present GEN.R4 status is reconciled separately.',searches=[dict(kind='exact',status='completed',query='Trace Gemini serialize/Exchange/Execute, InvokeLLM repair/context snapshots, extraction source coverage/relations, frozen preparation and listening case/attempt/result owners plus retained historical/provider observations.',outcome='Actual wire, native rows, local audio, browser views and Lab artifacts inspected. Controlled replies and one pre-fix baseline missing receipt remain explicit.',results=[dict(path=x,classification='interface_dependency',reason='Actual named owner, directly traced caller or literal regression dependency.') for x in OWNERS+HELPERS]),dict(kind='semantic',status='not_applicable',query='Named Gemini adapter/InvokeLLM and exact panic/source anchors are known.',reason='No unknown implementation ownership; direct source/stack/request tracing resolves the change.',outcome='No semantic-index evidence claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Go/prompt sources, no symbol rename or index-sensitive refactor.',reason='No PSI operation is needed for the selected adapter metadata/prompt repair.',outcome='No IDE/index claim.',results=[])]))
 p.write_text(json.dumps(d,indent=2)+'\n');print('Registered8 implemented I23 cases')
if __name__=='__main__':main()
