"""Bind the complete implemented I22 selection to literal native/CUA/protocol oracles."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
AUDIT=ROOT/'audit/iteration-22-elevenlabs-20261026';PREFIX='data/iteration-22-elevenlabs-20261026/'
PROPS=['FIN-SP-01.P1','FIN-VERIFY.I22'];SOURCE='tests/test_completion_i22.py'
OWNERS=['services/speech/backends.py','services/speech/elevenlabs_dictionary.py','services/speech/acoustic_runtime.py','services/api/internal/app/acoustic_profile.go','services/web/app/listen/useListening.js']
HELPERS=['tests/test_elevenlabs.py','tests/native_elevenlabs_test.go','services/api/internal/app/elevenlabs_profile_test.go','audit/iteration-22-elevenlabs-20261026/review.py']
PROOF=[PREFIX+x for x in ['observations.json','requests.jsonl','REVIEW.json','lab-readback.json','live/native-fixture.json','live/native-final.json','live/native.jsonl','live/exit-code','live/frozen-plan.json','live/failed-progress.json','live/progress.json','live/preparation.json','live/failed-preparation.json','live/key.json','live/result.json','live/exercise.wav','live/constructed-wires.json','live/native-documents.json','live/subscription-before.json','live/subscription-after.json','live/auditory-response.json','live/resolved-after-label-repair.json']]
PROOF+=[PREFIX+'live/assets/']
BOUNDARY=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Clean-text/mutation/semantic replies and deliberate HTTP quota/malformed metadata/read failures are constructed. Native compiler/transport/storage/acoustic finalization/interpreter/scorer and CUA are real. Five actual ElevenLabs Free TTS calls and one existing Gemini Free paired listening opinion are retained.',allowed_proof='Exact target/control/model/voice/dictionary bindings, saved progress/resume, native100 arithmetic, current actual browser failure/recovery and typography. Completion executes local negative protocol cases and concrete retained-data oracles without repeating hosted calls.',forbidden_claims=['Hosted text-semantic accuracy from constructed replies','Independent human or linguistic gold from one model listening opinion','Universal pronunciation/model qualification or new native/provider execution from a receipt oracle','PBT, deployment, financial execution or performance campaigns'])

def main():
 p=CHANGE/'verification.json';v=json.loads(p.read_text());old=[c for c in v['cases'] if c['property_id'] in PROPS];oldids={c['test_id'] for c in old};by={'test_'+c['id'].rsplit('.',1)[1]:c for c in old}
 methods=sorted(n.name for n in ast.walk(ast.parse((ROOT/SOURCE).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
 sha=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
 extras={'test_safe_recovery_positive':'Three transient read failures retain answer/actions and show only authored recovery, no stale success; explicit recovery submits the same answer. Keyboard/mobile navigation remains usable.',
 'test_native_interval_positive':'Actual whole-piece timing is labelled as generated piece interval, keeps native decoder provenance when present, and projects the independently calculated saved sample interval; finite replay pauses with ordinary browser-event granularity.',
 'test_limits_negative':'Unsupported partial-word/internal-phone timing and metered access fail without hosted dispatch, provider/model fallback or hidden text substitution.'}
 for method in methods:
  c=by.get(method)
  if c is None:
   c=copy.deepcopy(old[0]);oracle=extras[method]
   c.update(id='FIN-SP-01.P1.'+method.removeprefix('test_'),property_id='FIN-SP-01.P1',polarity='negative' if method.endswith('negative') else 'positive',setup='Use literal owner inputs and the actual selected native/CUA observations in '+SOURCE+':'+method,observable=oracle,green_expectation=oracle,red_expectation='Actual output contradicts: '+oracle)
   v['cases'].append(c)
  c.update(test_id='unittest::tests.test_completion_i22.CompletionI22.'+method,command_id='completion-i22',state='implemented',source_path=SOURCE,source_sha256=sha,invalidation_dependencies=list(dict.fromkeys(c['invalidation_dependencies']+OWNERS+HELPERS+PROOF+[SOURCE])),substitution=BOUNDARY)
  c.pop('blocker',None)
 for prop in v['properties']:
  if prop['id'] in PROPS:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+OWNERS+HELPERS+PROOF+[SOURCE]))
 p.write_text(json.dumps(v,indent=2)+'\n')
 selected=[c for c in v['cases'] if c['property_id'] in PROPS];assert len(selected)==len(methods)==13
 (AUDIT/'SELECTION.json').write_text(json.dumps(dict(iteration=22,properties=PROPS,expected_case_count=13,case_ids=[c['id'] for c in selected],scope='13 exact executable oracles; retained native and hosted observations remain bounded. Local protocol counterexamples execute with zero hosted calls.'),indent=2)+'\n')
 p=CHANGE/'discovery.json';d=json.loads(p.read_text());ids=[c['test_id'] for c in selected]
 d['scope']['test_ids']=list(dict.fromkeys([x for x in d['scope']['test_ids'] if x not in oldids]+ids))
 for r in d['reviews']:
  if any(x in oldids for x in r.get('test_ids',[])):r['test_ids']=list(dict.fromkeys([x for x in r['test_ids'] if x not in oldids]+ids))
 d['reviews']=[r for r in d['reviews'] if r['id']!='iteration22-native-dictionaries-20261026']
 d['reviews'].append(dict(id='iteration22-native-dictionaries-20261026',question='Implement and verify scoped production ElevenLabs dictionaries through ordinary preparation, saved speech, answer/scoring and recovery.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Missing production dictionary owner is implemented; inspect native/profile/storage, target scope and siblings. Repair stale refresh notice and false hosted decoder label without a new service/gate or repeated stored-data checks.',searches=[dict(kind='exact',status='completed',query='Trace selected dictionary/plan/render/acoustic/profile/assembly/key/answer and UI refresh owners from exact canonical contracts, prior comparison and named sources.',outcome='Actual selected owners and current native/CUA/provider artifacts are inspected; unsupported models/timing and source/model proof limits remain explicit.',results=[dict(path=x,classification='interface_dependency',reason='Actual selected owner/caller or directly inspected test dependency.') for x in OWNERS+HELPERS]),dict(kind='semantic',status='not_applicable',query='Exact named adapters and DAG owners are known.',reason='No unknown implementation ownership or semantic lookup is needed.',outcome='No semantic index claim.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Python/Go/JS owners; no index-sensitive refactor.',reason='No PSI operation needed for selected changes.',outcome='No IDE index evidence claimed.',results=[])]))
 p.write_text(json.dumps(d,indent=2)+'\n');print('Registered13 implemented I22 cases')
if __name__=='__main__':main()
