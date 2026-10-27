"""Wire I33 literal cases and the invalidated existing CV comparison closure."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs


def save(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def main():
    graph = json.loads((BASE/'verification.json').read_text())
    spec = parse_delta_specs(BASE)[('iteration-thirty-three-diagnostics','I33 Saved-audio diagnostic and fixture repair')]
    graph['requirements'] = [r for r in graph['requirements'] if r['id']!='I33']
    graph['requirements'].append(dict(id='I33',capability='iteration-thirty-three-diagnostics',
                                    title='I33 Saved-audio diagnostic and fixture repair',fingerprint=spec['fingerprint']))
    graph['properties'] = [p for p in graph['properties'] if p['requirement_id']!='I33']
    graph['cases'] = [c for c in graph['cases'] if not c['id'].startswith('I33.')]
    graph['commands'] = [c for c in graph['commands'] if not c['id'].startswith('iteration33-')]
    scenarios = list(spec['scenario_fingerprints'])
    statements = [
        'Both auditory transports SHALL use the owned projection, retaining actual target/reference context while excluding private key/learner/prior-observation data.',
        'Authored ambiguous expectations SHALL remain uncertain and correct variants SHALL stay acceptable; failed observations and physical change alone cannot confirm an error.',
        'The five selected saved sets SHALL retain original context/audio/replies and separate measured pause/F0 from correctness; future corrected contexts remain unobserved.',
        'The selected iteration SHALL reconcile actual unchanged native observations, original scope and local Lab readback without inference, synthesis or learner key/score changes.',
        'Saved comparison or clip failures SHALL retry locally, retain other playable recordings and enabled human recovery, with observed keyboard/playback/typography/screenshots/video and no provider call.',
    ]
    owners = ['services/speech/diagnostic_models.py','services/speech/category_validation.py',
              'audit/iteration-33-diagnostics-20261027/reconcile.py',
              'audit/iteration-33-diagnostics-20261027/native_cases.py',
              'audit/iteration-26-acoustic-20261026/listening.py']
    deps = owners+['services/speech/diagnostic_context.py','services/speech/diagnostic_audio.py',
                  'services/speech/diagnostic_runtime.py',
                  'audit/iteration-26-acoustic-20261026/selection.json',
                  'audit/iteration-26-acoustic-20261026/observe.py',
                  'audit/iteration-33-diagnostics-20261027/verification_native.py',
                  'audit/iteration-33-diagnostics-20261027/browser_fixture.py',
                  'tests/test_saved_audio_verification.py',
                  'specification/v2/prompts/audio-category-probe-v1.txt',
                  'specification/v2/prompts/audio-judge-v1.txt']
    for i,(scenario,owner) in enumerate(zip(scenarios,owners),1):
        graph['properties'].append(dict(id=f'I33.P{i}',requirement_id='I33',statement=statements[i-1],scenarios=[scenario],owner=owner,oracle='Literal independent context/expectation/transport assertions, original actual saved model bodies/audio and exact PCM arithmetic; native F0 observations remain scoped physical evidence, never pragmatic truth.',source_globs=deps+['tests/test_saved_audio*.py','audit/iteration-33-diagnostics-20261027/**'],iteration=33))
    # Existing CV routes/IDs stay intact. I33's actual typed unittest readers
    # reconcile their newly observed native closure without redispatching it.
    for command in graph['commands']:
        if command['id'] in ['category-realization-native','category-realization-evidence']:
            source = 'test_category_validation.py' if command['id']=='category-realization-native' else 'test_category_evidence.py'
            command['argv'] = ['python3','-B','-m','unittest','discover','-s','tests','-p',source,'-v']
    graph['commands'].append(dict(id='iteration33-evidence',runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_saved_audio_acceptance'],cwd='.',env={},timeout_seconds=120,authority='local'))
    modules = ['tests/test_saved_audio_diagnostics.py','tests/test_saved_audio_acceptance.py',
               'tests/test_saved_audio_verification.py',
               'tests/test_audio_diagnostics.py','tests/test_auditory_protocol.py',
               'tests/test_selected_acoustic.py','tests/test_selected_listening_recovery.py']
    tests = []
    for source in modules:
        text = (ROOT/source).read_text()
        for cls in ast.parse(text).body:
            if not isinstance(cls,ast.ClassDef):continue
            for method in cls.body:
                if isinstance(method,ast.FunctionDef) and method.name.startswith('test_'):
                    tests.append((source,cls.name,method.name,ast.get_source_segment(text,method)))
    source = 'tests/test_completion_i26.py';tree = ast.parse((ROOT/source).read_text())
    for cls in tree.body:
        if not isinstance(cls,ast.ClassDef):continue
        for method in cls.body:
            if isinstance(method,ast.FunctionDef) and method.name in ['test_acoustic_positive','test_acoustic_negative']:
                tests.append((source,cls.name,method.name,ast.get_source_segment((ROOT/source).read_text(),method)))
    all_tests = tests
    ids = []
    for source,cls,name,literal in [r for r in tests if r[1]=='SavedAudioAcceptance']:
        pid = 1 if 'context_native' in name else 2 if ('fixture_native' in name or 'verification_fixture' in name) else 3 if 'saved_physical_native' in name else 5 if 'listening_browser' in name else 4
        scenario = scenarios[pid-1]
        test_id = 'unittest::'+source.removesuffix('.py').replace('/','.')+'.'+cls+'.'+name
        suite = 'evidence'
        graph['cases'].append(dict(id=f'I33.P{pid}.'+cls+'.'+name,property_id=f'I33.P{pid}',polarity='negative' if name.endswith('negative') else 'positive',scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup='Typed unittest reader of exact actual native output on unchanged source inputs, original saved model/WAV contexts and actual local Lab readback. The gate reads exact current or retained native observations; no inference or synthesis is redispatched. '+source+':'+name,observable=literal,red_expectation='The literal independent expected projection, status, original context/audio, arithmetic, failure or readback assertion fails.',green_expectation='All exact independent assertions hold through the named owner with the stated actual or constructed origin.',test_id=test_id,command_id='iteration33-'+suite,state='implemented',source_path=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),invalidation_dependencies=deps+[source,'data/iteration-33-diagnostics-20261027/native/category.*','data/iteration-33-diagnostics-20261027/native/category-evidence.*','data/iteration-33-diagnostics-20261027/native/diagnostic.*','data/iteration-33-verification-20261027/lab-readback.json','data/iteration-33-verification-20261027/native-invalidated.*','data/iteration-33-verification-20261027/directed.json','data/iteration-33-verification-20261027/green-directed.log','data/iteration-33-verification-20261027/browser/**','data/iteration-33-verification-20261027/video-probe.json','data/iteration-33-verification-20261027/browser-server.log'],substitution=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Only explicitly constructed model/transport or file-failure responses. The production serializer/comparison/native diagnostic, actual saved bodies/WAVs and readback owners execute.',allowed_proof='Context exclusion/parity, comparison/fixture logic, exact saved input correspondence, PCM arithmetic, actual scoped saved-listening UI recovery/playback/typography/video and zero-call export. Existing model opinions remain limited to their original inputs.',forbidden_claims=['New hosted/local inference or improved model hearing','Human gold or universal English/accent qualification','Changed context was judged by the old reply','Whole-product acceptance or new ordinary model-flow observation']),distinct_reason='Exact literal assertion; retained original output is replayed only on unchanged source inputs.'))
        ids.append(test_id)
    # Existing aliases of these exact now-observed tests keep their property,
    # polarity and scenarios; refresh only their changed test-source binding.
    observed = {'unittest::'+source.removesuffix('.py').replace('/','.')+'.'+cls+'.'+name
                for source,cls,name,literal in all_tests}
    literals = {'unittest::'+source.removesuffix('.py').replace('/','.')+'.'+cls+'.'+name:literal
                for source,cls,name,literal in all_tests}
    for case in graph['cases']:
        identity = case['test_id'].replace('unittest::test_', 'unittest::tests.test_', 1)
        if identity in observed:
            path = ROOT/case['source_path']
            case.setdefault('distinct_reason','Exact native '+identity+' also proves this existing '+case['property_id']+' assertion; I33 reuses that observation with its original scope rather than dispatching another test or model.')
            if case['scenario'] not in case['distinct_reason']:
                case['distinct_reason'] = case['scenario']+': '+case['distinct_reason']
            previous = case['source_sha256']
            case['source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            case['setup'] = case['setup'].replace(previous,case['source_sha256'])
            if not case['id'].startswith('I33.'):
                # These active aliases point at the exact same newly observed
                # test. Keep their original ID/polarity/scenario; update the
                # literal assertion snapshot when its actual test changed.
                value = case['observable']
                try:packet = json.loads(value)
                except (ValueError,TypeError):packet = None
                if isinstance(packet,dict) and 'independent_literal_assertions' in packet:
                    packet['independent_literal_assertions'] = literals[identity]
                    case['observable'] = json.dumps(packet,ensure_ascii=False)
                elif value.startswith('def test_'):
                    case['observable'] = literals[identity]
    # The active I16 fixture library captures complete constructed source;
    # its old wire carrier omitted required planned_units. Preserve the actual
    # observed assertions while recording the repaired carrier, not a stale hash.
    path = ROOT/'audit/iteration-16-release-20261021/FIXTURE-LIBRARY.json'
    library = json.loads(path.read_text()); entry=library['tests/test_auditory_protocol.py']
    entry['source_sha256'] = hashlib.sha256((ROOT/entry['source_path']).read_bytes()).hexdigest()
    entry['fixture_source'] = (ROOT/entry['source_path']).read_text()
    path.write_text(json.dumps(library,indent=2,ensure_ascii=True)+'\n')
    save(BASE/'verification.json',graph)
    selected = [c for c in graph['cases'] if c['property_id'].startswith('I33.')]
    props = [f'I33.P{i}' for i in range(1,6)]
    coverage = []
    result = json.loads((ROOT/'data/iteration-33-verification-20261027/native-reuse.json').read_text())
    observations = result['observations']
    directed = json.loads((ROOT/'data/iteration-33-verification-20261027/directed.json').read_text())
    observations += [dict(test_id=t,receipt=directed['stdout'],disposition='new_literal_regression') for t in directed['test_ids']]
    for row in observations:
        identity=row['test_id']
        aliases=[c['id'] for c in graph['cases'] if c['test_id'].replace('unittest::test_','unittest::tests.test_',1)==identity]
        proof=[c['id'] for c in selected if identity.removeprefix('unittest::') in c['observable']
               or c['id'].endswith('test_retained_native_cases_positive') and row['disposition']!='new_literal_regression'
               or row['disposition']=='new_literal_regression' and identity.rsplit('.',1)[1] in c['observable']]
        coverage.append(dict(test_id=identity,case_aliases=aliases,acceptance_case_ids=proof,
                             receipt=row['receipt'],origin=row['disposition']))
    save(HERE/'NATIVE-COVERAGE.json',dict(observations=coverage,observation_count=len(coverage)))
    save(HERE/'SELECTION.json',dict(iteration=33,property_ids=props,case_ids=[c['id'] for c in selected],expected_case_count=len(selected),native_observation_count=len(coverage),native_coverage='audit/iteration-33-diagnostics-20261027/NATIVE-COVERAGE.json',scope='Full QUAL-04 repair. Typed acceptance readers reconcile every exact native case in the directly invalidated CV/context/fixture closure without repeating those tests. Reuse all original model/audio observations; zero new inference/synthesis.'))
    path = BASE/'completion-iterations.json';d=json.loads(path.read_text());d['iterations']=[i for i in d['iterations'] if i['iteration']!=33]
    d['iterations'].append(dict(iteration=33,title='Repair saved-audio diagnostics and ambiguous fixtures',source_items=['QUAL-04'],depends_on=[26,31],conditional_dependencies=[],requirement_ids=['I33'],verify_property_ids=props,track='implementation',visual_applicable=True,visual_scope='I33 verify: actual saved-listening page, original twenty role-bound WAVs, controlled comparison/media failures, Refresh/keyboard/playback, desktop/390/320 typography, screenshots and actual 74-second screencast under data/iteration-33-verification-20261027/browser. No ordinary model call or user-app change.',selection='audit/iteration-33-diagnostics-20261027/SELECTION.json',verify_command_ids=['iteration33-evidence']))
    save(path,d)
    path = BASE/'discovery.json';d=json.loads(path.read_text());d['scope']['property_ids']=list(dict.fromkeys(d['scope']['property_ids']+props));d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+ids))
    known = {c['test_id'] for c in graph['cases']}
    d['scope']['test_ids'] = [t for t in d['scope']['test_ids'] if t in known]
    d['reviews']=[r for r in d['reviews'] if r['id']!='iteration33-diagnostics-20261027']
    d['reviews'].append(dict(id='iteration33-diagnostics-20261027',question='Resolve retained weak-form, linking, pause and intonation disagreements by exact context/WAV/physical/model tracing, without a new judge campaign.',disposition='current_change',rationale='Gemini bypassed owned context projection; ambiguous authored labels were forced into an error expectation; failed observations could confirm favorable findings; future intonation context omitted car. Verify repairs additionally isolate all correct-control expectations, count valid candidate false alarms, keep unknown statuses uncertain and prevent saved-comparison shape errors from hiding playable clips; actual Chrome recovery/typography/video is retained. Repairs preserve actual prior replies, strong/connected/accent/question controls and unresolved physical-versus-functional observations.',property_ids=props,test_ids=ids,searches=[dict(kind='exact',status='completed',query='Trace QUAL-04, selected frozen/response/dispatch/comparison, original connected WAV/decoder/F0 receipts, auditory_content/project_audio_intent and make_probe/compare_probe with their native callers and tests.',outcome='One shared projection and existing comparison owner; existing saved fixtures/finalization retained; no renderer defect demonstrated by the model misses.',results=[dict(path=p,classification='interface_dependency',reason='Actual scoped owner, fixture or original evidence inspected.') for p in deps+['data/connected-speech-20261023/output/physical-reconciliation.json']]),dict(kind='semantic',status='unavailable',query='jbcontext search Where does saved audio diagnostic context separate measured silence and pitch direction from whether weak forms, linking and intonation are communicatively incorrect, and where are retained judge disagreement fixtures tested?',reason='The actual exact-worktree CLI returned No index found for repository github.com/jekamas/tangerine. No new index or semantic proof is claimed.',outcome='Continued direct tracing of named source/evidence owners.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Python diagnostic/context/fixture owners; no rename or structural IDE refactor.',reason='Direct source/tests and retained actual inputs answer this scope; no IDE evidence is claimed.',outcome='No PSI operation required.',results=[])]))
    save(path,d)
    print(json.dumps(dict(properties=len(props),cases=len(selected),new_i33_cases=len(ids))))


if __name__=='__main__':main()
