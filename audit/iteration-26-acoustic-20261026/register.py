"""Wire the selected I26 cases; preserve all historical CV case bindings."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
PROPS=['FIN-ACOUSTIC.P1','FIN-VERIFY.I26']
DEPS=['audit/iteration-26-acoustic-20261026/observe.py',
      'audit/iteration-26-acoustic-20261026/listening.py',
      'audit/iteration-26-acoustic-20261026/selection.json',
      'audit/iteration-25-qwen-20261026/player.py',
      'tests/test_selected_acoustic.py','tests/test_completion_i26.py',
      'data/iteration-26-acoustic-20261026/selected/',
      'data/iteration-26-acoustic-20261026/browser-observations.json']


def main():
    path=CHANGE/'verification.json';graph=json.loads(path.read_text())
    templates={prop:copy.deepcopy(next(c for c in graph['cases'] if c['property_id']==prop)) for prop in PROPS}
    graph['cases']=[c for c in graph['cases'] if c['id'].split('.contract_')[0] not in PROPS]
    command='completion-i26-contracts'
    graph['commands']=[c for c in graph['commands'] if c['id']!=command]+[
        dict(id=command,runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_selected_acoustic'],cwd='.',env={},timeout_seconds=120,authority='local')]
    source='tests/test_selected_acoustic.py';text=(ROOT/source).read_text()
    for cls in ast.parse(text).body:
        if not isinstance(cls,ast.ClassDef):continue
        for node in cls.body:
            if not isinstance(node,ast.FunctionDef) or not node.name.startswith('test_'):continue
            prop='FIN-VERIFY.I26' if cls.name=='SelectedListening' else 'FIN-ACOUSTIC.P1'
            case=copy.deepcopy(templates[prop]);literal=ast.get_source_segment(text,node)
            case.update(id=prop+'.contract_'+node.name.removeprefix('test_'),property_id=prop,
                        polarity='negative' if node.name.endswith('negative') else 'positive',
                        setup='Literal selected native projection/persistence or read-only media fixture in '+source+':'+node.name,
                        observable=literal,red_expectation='The independently specified context, role, receipt, saved-response or media-route expectation fails.',
                        green_expectation='The literal independent assertions hold through the named owner within the recorded controlled boundary.',
                        test_id='unittest::tests.test_selected_acoustic.'+cls.name+'.'+node.name,
                        command_id=command,source_path=source,state='implemented')
            case['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Only the auditory response or test-owned HTTP failure is constructed. Native blind projection, saved-response finalization and actual saved-file HTTP reader are real.',allowed_proof='Finite selection, correct-variant controls, no-redispatch recovery and file-read behavior. Browser activation is a separate actual case.',forbidden_claims=['Constructed judgments are actual hearing','Every pronunciation, voice or accent is confirmed','Rendered HTML proves user activation'])
            graph['cases'].append(case)
    selected=[c for c in graph['cases'] if c['property_id'] in PROPS]
    for case in selected:
        case['state']='implemented';case.pop('blocker',None)
        case['source_sha256']=hashlib.sha256((ROOT/case['source_path']).read_bytes()).hexdigest()
        case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+DEPS))
        if case['id']=='FIN-VERIFY.I26.review_positive':
            case['blocker']='The authorized in-app browser loads all20 actual clips but native/locator keyboard and screenshot-grounded Play actions do not activate playback. Existing Chrome-selection question remains unanswered. This actual interaction case skips, not passes.'
    for prop in graph['properties']:
        if prop['id'] in PROPS:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+DEPS))
    path.write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
    path=CHANGE/'discovery.json';discovery=json.loads(path.read_text());ids=[c['test_id'] for c in selected]
    discovery['scope']['test_ids']=list(dict.fromkeys(discovery['scope']['test_ids']+ids))
    discovery['reviews']=[r for r in discovery['reviews'] if r['id']!='iteration26-acoustic-20261026']
    discovery['reviews'].append(dict(id='iteration26-acoustic-20261026',question='Reconcile existing CV proof and make only necessary selected saved-audio observations with actual correct contextual controls.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Retain the518 historical CV identities and unchanged122-row matrix. Repair weak-form and rising-question acceptable controls and align the thought-group public context with the saved600ms boundary. Four finite existing-free-provider requests are saved once; one confirms assimilation, three retain unconfirmed/conflicting outcomes. Actual browser activation remains unobserved; no universal qualification or learner gate is introduced.',searches=[dict(kind='exact',status='completed',query='Trace category_validation blind_input/compare_probe, diagnostic HTTP/model owners, original CV exact receipts, connected-speech native pause/F0 provenance and saved-media recovery owner.',outcome='Known native owner, retained measurements/audio and exact original test identities located. Original twelve parent fingerprints match current code and518 exact observations retain their proof boundary.',results=[dict(path=p,classification='interface_dependency',reason='Known owner or literal selected test dependency.') for p in DEPS if not p.startswith('data/')]),dict(kind='semantic',status='unavailable',query='Locate the CV-01 through CV-06 category acoustic realization verification, retained evidence receipts, target-control comparisons and allowed pronunciation variants used to confirm generated speech mistakes.',reason='jbcontext reports no index for repository fffb5cc5644365f06373a66ac2d3932f0d4b510a4a6f7f5df5c8ffd285d35165. No index creation or semantic proof is claimed.',outcome='Direct exact owner/artifact tracing completed; original native mechanisms are reused.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Python verification/media files; no symbol rename or refactor.',reason='Direct source, native literal tests and actual retained media answer this scoped iteration; no IDE operation is needed.',outcome='No PSI/index proof claimed.',results=[])]))
    path.write_text(json.dumps(discovery,indent=2,ensure_ascii=False)+'\n')
    print('Registered',len(selected),'selected I26 cases; original518 CV edges unchanged, actual browser activation remains blocked.')


if __name__=='__main__':main()
