"""Register only I34; planned literals become implemented only with real tests."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0, str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

def save(p, v):
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n')

def main():
    spec = parse_delta_specs(BASE)[('iteration-thirty-four-local-generation','I34 Installed-local generation repair')]
    graph = json.loads((BASE/'verification.json').read_text())
    for key in ['requirements','properties','cases','commands']:
        graph[key] = [r for r in graph[key] if not (r.get('id','').startswith('I34') or r.get('id','').startswith('iteration34-'))]
    graph['requirements'].append(dict(id='I34',capability='iteration-thirty-four-local-generation',title='I34 Installed-local generation repair',fingerprint=spec['fingerprint']))
    source = 'tests/test_local_generation_acceptance.py'
    tests = {}
    if (ROOT/source).exists():
        raw = (ROOT/source).read_text()
        for cls in ast.parse(raw).body:
            if isinstance(cls,ast.ClassDef):
                for method in cls.body:
                    if isinstance(method,ast.FunctionDef) and method.name.startswith('test_'):
                        tests[method.name] = (cls.name, ast.get_source_segment(raw,method))
    scenarios = list(spec['scenario_fingerprints'])
    names = [
        ('test_local_generation_positive','test_zero_error_negative'),
        ('test_failure_retention_positive','test_failure_containment_negative'),
        ('test_comparison_positive','test_quality_counterexamples_negative'),
        ('test_native_lab_positive','test_no_fallback_negative'),
    ]
    owners = ['services/api/internal/app/mutation.go','services/api/internal/provider/execute.go',
              'audit/iteration-34-local-generation-20261027/compare.py','services/api/internal/app/provider_inference.go']
    deps = ['services/api/internal/app/preparation.go','services/api/internal/app/provider_context.go',
            'services/api/internal/app/mutation*.go','services/api/internal/provider/*.go',
            'specification/v2/prompts/canonical-v1.txt','specification/v2/prompts/generate-v1.txt',
            'services/api/internal/lab/builtin.json','services/api/internal/app/mutation_shape.go',
            'services/api/internal/app/mutation_local_projection_test.go',
            'tests/native_local_generation_test.go','tests/native_local_generation_failures_test.go',
            'tests/native_local_generation_replay_test.go',
            'services/api/internal/app/mutation_correction_projection.go',
            'specification/v2/docs/generation-contract-details.md',
            'audit/iteration-34-local-generation-20261027/PLAN.json',
            'audit/iteration-34-local-generation-20261027/REPAIR-PLAN.json',
            'audit/iteration-34-local-generation-20261027/FINAL-PLAN.json',
            'audit/iteration-34-local-generation-20261027/REPAIRED-PLAN.json',
            'audit/iteration-34-local-generation-20261027/DEADLINE-PROFILE-PLAN.json',
            'audit/iteration-34-local-generation-20261027/QWEN-REPAIRED-PLAN.json',
            'audit/iteration-34-local-generation-20261027/compare.py']
    for i, scenario in enumerate(scenarios,1):
        pid = f'I34.P{i}'
        graph['properties'].append(dict(id=pid,requirement_id='I34',statement=spec['scenarios'][i-1] if isinstance(spec.get('scenarios'),list) else scenario,scenarios=[scenario],owner=owners[i-1],oracle='Frozen independent literal targets, actual local native owner/dispatch/assets and Lab readback; finite functional population only.',source_globs=deps+[source,'audit/iteration-34-local-generation-20261027/**'],iteration=34))
        for name in names[i-1]:
            implemented = name in tests
            cls,literal = tests.get(name,('LocalGenerationAcceptance','Frozen PLAN.json defines exact target phrases, categories, corrections, valid controls, limits and denominators before inference.'))
            graph['cases'].append(dict(id=pid+'.'+name,property_id=pid,polarity='negative' if name.endswith('negative') else 'positive',scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup='PLAN.json fixed common requests; actual installed-local native preparation and failed witnesses, independently expected targets and arithmetic. Actual30 source calls are unsubstituted; current mechanical projection/finalization additionally uses four labelled retained-response replays with identity rebound only.',observable=literal,red_expectation='The literal linguistic, persisted-state, native-wire, failure, arithmetic or Lab assertion differs or is missing.',green_expectation='Exact selected positive/negative assertions hold within the stated finite functional proof boundary.',test_id=('unittest::tests.test_local_generation_acceptance.'+cls+'.'+name) if implemented else 'planned::I34::'+name,command_id='iteration34-evidence' if implemented else 'pending',state='implemented' if implemented else 'planned',source_path=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest() if implemented else None,invalidation_dependencies=deps+[source,'data/iteration-34-local-generation-20261027/comparison.json','data/iteration-34-local-generation-20261027/lab-readback.json','data/iteration-34-local-generation-20261027/go-final.jsonl','data/iteration-34-local-generation-20261027/controlled/native.jsonl','data/iteration-34-local-generation-20261027/controlled-deadline/native.jsonl','data/iteration-34-local-generation-20261027/*/dispatches.json','data/iteration-34-local-generation-20261027/documents.json','data/iteration-34-local-generation-20261027/*/documents.json','data/iteration-34-local-generation-20261027/assets/*.json','data/iteration-34-local-generation-20261027/*/assets/*.json','data/iteration-34-local-generation-20261027/*/*asset_id.json','data/iteration-34-local-generation-20261027/*/*-preparation.json'],substitution=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Only deterministic failures and explicitly labelled retained actual reply replay with blueprint identity rebound. Actual30 installed-local calls are unsubstituted; replay makes no inference.',allowed_proof='Finite generation/key/recovery contract, exact saved/native/Lab evidence and selected repair comparison.',forbidden_claims=['Universal category/model quality','New speech or arbitrary answer-checking qualification','Population statistics','Hosted entitlement or paid use','A retained reply replay is fresh inference or generation latency']),distinct_reason=scenario+': '+name))
    if tests:
        graph['commands'].append(dict(id='iteration34-evidence',runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_local_generation_acceptance'],cwd='.',env={},timeout_seconds=120,authority='local'))
    pending=next(c for c in graph['commands'] if c['id']=='pending')
    pending['expected_markers']=[t for t in pending['expected_markers'] if not t.startswith('planned::I34::')]+[c['test_id'] for c in graph['cases'] if c['id'].startswith('I34.') and c['state']=='planned']
    save(BASE/'verification.json',graph)
    props=[f'I34.P{i}' for i in range(1,5)]
    selected=[c for c in graph['cases'] if c['property_id'] in props]
    save(HERE/'SELECTION.json',dict(iteration=34,property_ids=props,case_ids=[c['id'] for c in selected],expected_case_count=len(selected)))
    p=BASE/'completion-iterations.json';v=json.loads(p.read_text());v['iterations']=[r for r in v['iterations'] if r['iteration']!=34];v['iterations'].append(dict(iteration=34,title='Repair generation with installed local LLMs',source_items=['QUAL-05'],depends_on=[31],conditional_dependencies=[],requirement_ids=['I34'],verify_property_ids=props,track='implementation',visual_applicable=False,visual_scope='Provider/preparation/prompt/profile and evidence scope; no web presentation or interaction changes.',selection=str(HERE.relative_to(ROOT)/'SELECTION.json'),verify_command_ids=['iteration34-evidence']));save(p,v)
    p=BASE/'discovery.json';v=json.loads(p.read_text());v['scope']['property_ids']=list(dict.fromkeys(v['scope']['property_ids']+props));ids=[c['test_id'] for c in selected];v['scope']['test_ids']=[i for i in v['scope']['test_ids'] if 'I34::' not in i and 'test_local_generation_acceptance' not in i]+ids
    v['reviews']=[r for r in v['reviews'] if r['id']!='iteration34-local-generation']
    v['reviews'].append(dict(id='iteration34-local-generation',question='Trace retained local invalid-mutation/runner/deadline failures and bounded repair alternatives through actual owners.',disposition='current_change',rationale='Retained outputs distinguish an MLX kernel panic, invalid quote/false linguistic claims and two canonical deadlines. Current normalization/admission already reject these; no hypothetical extra gate is authorized. Compare existing explicit profile and decoding choices with literal semantic oracles.',property_ids=props,test_ids=ids,searches=[dict(kind='exact',status='completed',query='QUAL-05, I29 local preparations/dispatches/assets, PrepareCanonical/invokeMutation/InvokeLLM/Execute/normalization/admission/finalization and installed Ollama metadata.',outcome='Named production owners and exact retained failed wires identified before implementation.',results=[dict(path=o,classification='interface_dependency',reason='Actual owner inspected.') for o in owners]),dict(kind='semantic',status='unavailable',query='Context-explorer: local generation failures, transport timeout and mutation owner chain.',reason='Exact-worktree jbcontext returned no index for github.com/jekamas/tangerine.',outcome='Used direct reads of known owners; no semantic proof claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Go generation/provider owners; no symbol refactor or IDE diagnostic needed.',reason='Exact source and native functional boundary answer this scope.',outcome='No PSI evidence claimed.',results=[])]));save(p,v)
    print(json.dumps(dict(cases=len(selected),implemented=sum(c['state']=='implemented' for c in selected))))

if __name__=='__main__':main()
