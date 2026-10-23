"""Append this finite scope; do not rewrite earlier task evidence or receipts."""
import hashlib
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[2]
C=R/'openspec/changes/implement-teacher-error-trainer'
A=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

g=json.loads((C/'verification.json').read_text())
d=json.loads((C/'discovery.json').read_text())
specs=parse_delta_specs(C)
refs=json.loads((R/'specification/v2/domain/linguistic-contrast-set.v1.json').read_text())['examples']
models=json.loads((A/'MODEL-CASES.json').read_text())['cases']
for key in ['requirements','properties','cases']:
    g[key]=[x for x in g[key] if not x['id'].startswith('LF-')]
g['commands']=[x for x in g['commands'] if not x['id'].startswith('linguistic-')]
sources=['services/api/internal/app/generationdata/error-taxonomy.v1.yaml','services/api/internal/app/generationdata/mutation-recipes.v1.json','services/api/internal/app/mutation_selection.go','services/api/internal/app/interpretation_context.go','services/api/internal/scoring/score.go','services/api/internal/scoring/count.go','services/api/internal/lab/builtin.json','specification/v2/domain/linguistic-contrast-set.v1.json']
prop_ids=[];test_ids=[];added=[]


def case(rid,suffix,polarity,test,source,command,fixture,oracle):
    spec=next(v for v in specs.values() if v['title'].startswith(rid+' '))
    scenario=spec['scenarios'][0]
    dependencies=sources+[source,'specification/v2/docs/linguistic-coverage-and-variants.md']
    claim='Real native context/arithmetic on constructed inputs'
    if rid=='LF-04':
        dependencies=[source,'audit/linguistic-fullness-20261023/MODEL-CASES.json','services/api/internal/app/experiment_judge.go','services/api/internal/app/provider_inference.go','services/api/internal/app/linguistic_observation_test.go']
        claim='Actual captured included-plan semantic judgments compared to withheld authored expectations'
    if rid=='LF-05':
        dependencies=[source,'services/speech/acoustic_alignment.py','services/speech/acoustic_plan.py']
        claim='Real native phone-plan compiler on constructed token/vocabulary inputs; zero inference'
    if rid=='LF-06':
        dependencies=[source,'services/api/internal/app/linguistic_flow_observation_test.go','services/api/internal/lab/builtin.json','specification/v2/prompts/canonical-v1.txt','specification/v2/prompts/generate-v1.txt','specification/v2/prompts/map-v1.txt','specification/v2/prompts/audit-map-v1.txt','specification/v2/prompts/case-review-v1.txt','specification/v2/prompts/adjudication-v1.txt']
        claim='Actual native generated exercise, stored local speech, graded answer and optional stage observations with independently inspected literal expectations'
    row=dict(id=rid+'.P1.'+suffix,property_id=rid+'.P1',polarity=polarity,scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup=json.dumps(fixture,ensure_ascii=False),observable=oracle,red_expectation='Wrong or missing selected identity, context, literal arithmetic or actual semantic observation fails the named assertion.',green_expectation='Every independently specified assertion holds within the disclosed proof boundary.',test_id=test,command_id=command,state='implemented',source_path=source,source_sha256=hashlib.sha256((R/source).read_bytes()).hexdigest(),invalidation_dependencies=dependencies,substitution=dict(classification='NO_TEST_DOUBLE',proof_claims=[claim],forbidden_claims=['Universal linguistic coverage','Independently heard IPA or every acoustic realization','Empirical corpus/gold accuracy','All-provider integration or published optional-review revisions']))
    g['cases'].append(row);added.append(row);test_ids.append(test)


for rid,owner,statement in [
('LF-01','services/api/internal/app/mutation_selection.go','Every registered leaf preserves its explicit subtype/exclusion control in the existing selected native context; incompatible family selection remains rejected.'),
('LF-02','services/api/internal/scoring/score.go','A correctly accepted control has no error opportunity/penalty; calling that control wrong gives exactly one false positive and no detection credit.'),
('LF-03','services/api/internal/scoring/score.go','A supported primary answer keeps full credit with omitted or false supplied reasoning; written example edits replay the literal surface in the native scope owner.'),
('LF-04','services/api/internal/app/experiment_judge.go','A finite actual model population has withheld independent labels, literal context, native receipts and explicit unknown acoustic evidence; favorable transport or instructions alone are insufficient.'),
('LF-05','services/speech/acoustic_alignment.py','Actual phone compilation preserves selected consonant order/internal-vowel contrasts, one repair scope, reverse allowed variants and honest unsupported-phone rejection.'),
('LF-06','services/api/internal/app/generation.go','The affected shipped prompts have actual included/local flow and scoped optional-stage evidence, with independent correct/control/false-explanation outcomes and original user data preserved.')]:
    spec=next(v for v in specs.values() if v['title'].startswith(rid+' '))
    g['requirements'].append(dict(id=rid,capability=spec['capability'],title=spec['title'],fingerprint=spec['fingerprint']))
    g['properties'].append(dict(id=rid+'.P1',requirement_id=rid,statement='The application SHALL '+statement,scenarios=spec['scenarios'],owner=owner,oracle='Independently authored literal contrasts and counts; model replies remain observations, not independent perceptual gold.',source_globs=sources))
    prop_ids.append(rid+'.P1')

for ref in refs:
    tid=ref['taxonomy_id']
    fixture=dict(reference=ref,origin='authored',numeric_expectations='Acceptable control: G=TP=FN=FP=0,D=1. False accusation: FP=DF=1,TP=FN=0,precision=0/1. Matched true error: TP=1,FN=FP=0,correction=1; explanation omitted=N/A or false=0 independently.')
    for rid,method,pol in [
        ('LF-01','TestLinguisticContextPositive','positive'),
        ('LF-01','TestLinguisticSelectionNegative','negative'),
        ('LF-02','TestLinguisticControlPositive','positive'),
        ('LF-02','TestLinguisticControlNegative','negative'),
        ('LF-03','TestLinguisticRecipePositive','positive')]:
        case(rid,method+'.'+tid,pol,'tangerine.local/api/internal/app::'+method+'/'+tid,'services/api/internal/app/linguistic_coverage_test.go','linguistic-native',fixture,'Actual selection/mapper context, exact rational scoring or declared codepoint replay. The native owners do not judge linguistic truth.')
    if ref['surface_status']=='true_error':
        for method,pol in [('TestLinguisticPrimaryPositive','positive'),('TestLinguisticExplanationNegative','negative')]:
            case('LF-03',method+'.'+tid,pol,'tangerine.local/api/internal/app::'+method+'/'+tid,'services/api/internal/app/linguistic_coverage_test.go','linguistic-native',fixture,'Existing native answer-components-v2 scoring with exact independently stated counts/fractions; assumed semantic decisions are constructed, not LLM outputs.')

for x in models:
    pol='positive' if x['expected']=='supported' else 'negative'
    tid='unittest::test_linguistic_model_evidence.LinguisticObservedCases.test_'+x['id']+'_'+pol
    case('LF-04',x['id'],pol,tid,'tests/test_linguistic_model_evidence.py','linguistic-observations',x,'Actual retained model verdict must equal the independently authored label. Input must equal the frozen blind context. Receipts/context and native readback must exist. Unknown requires missing evidence; no inference occurs during readback.')

for method,pol in [('TestLinguisticAliasesPositive','positive'),('TestLinguisticAliasesNegative','negative')]:
    case('LF-01',method,pol,'tangerine.local/api/internal/app::'+method,'services/api/internal/app/linguistic_coverage_test.go','linguistic-native',dict(input='Authored consonant-metathesis alias versus absent category wording',expected='Existing consonant-substitution ID; no category context for empty category text.'),'Real mapper alias selection on the shipped English registry; no new taxonomy/scoring identity or invented category wording.')
for method,pol in [('test_metathesis_target_positive','positive'),('test_allowed_metathesis_control_negative','negative'),('test_internal_vowel_elision_positive','positive'),('test_spelling_does_not_force_syllables_negative','negative'),('test_missing_model_phone_negative','negative'),('test_one_repair_unit_positive','positive')]:
    case('LF-05',method,pol,'unittest::test_linguistic_injection.LinguisticInjection.'+method,'tests/test_linguistic_injection.py','linguistic-injection',dict(fixture='Ask me: æsk/æks; Camera me: kæməɹə/kæmɹə; missing k vocabulary; one-word unit.'),'Literal native compiled phone strings and unchanged surface text match the stated contrasts; one unit/scope remains one repair, and an unavailable phone fails. This does not establish Kokoro perception or arbitrary IPA support.')
for method,pol in [('test_generated_preparation_positive','positive'),('test_correct_repair_false_claims_negative','negative'),('test_optional_case_review_positive','positive'),('test_optional_reconsideration_negative','negative')]:
    case('LF-06',method,pol,'unittest::test_linguistic_flow_evidence.LinguisticFlowEvidence.'+method,'tests/test_linguistic_flow_evidence.py','linguistic-flow-observations',dict(fixture='Actual new train-trip exercise; two ticket -> two tickets; Shall I book is acceptable; all plurals take -s and shall never makes British offers are false.',expected=dict(tp=1,fp=1,fn=0,correction='1/1',explanation='0/1',precision='1/2')),'Actual generated clean/mutated text, nonempty stored WAV, native exact score/comments and actual optional stage receipts satisfy the authored independent expectations. Optional stage experiments publish no review/result revisions.')

env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock',DOCKER_CONFIG=str(R/'data/local-preview/docker-config'))
g['commands'].append(dict(id='linguistic-native',runner='go-test-json',argv=['./tests/go-docker','test','-json','-count=1','-run','^TestLinguistic(Context|Selection|Control|Primary|Explanation|Recipe|Aliases)','./internal/app'],cwd='.',env=env,timeout_seconds=300,authority='local'))
g['commands'].append(dict(id='linguistic-observations',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_linguistic_model_evidence.py','-v'],cwd='.',env={},timeout_seconds=90,authority='local'))
g['commands'].append(dict(id='linguistic-flow-observations',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_linguistic_flow_evidence.py','-v'],cwd='.',env={},timeout_seconds=90,authority='local'))
g['commands'].append(dict(id='linguistic-injection',runner='python-unittest',argv=['./tests/speech-python','-m','unittest','discover','-s','tests','-p','test_linguistic_injection.py','-v'],cwd='.',env={**env,'TANGERINE_SPEECH_TEST_RUNTIME_IMAGE':'sha256:e60ccf1b355001517bf95d3e5f135414b05740d08ca677cb74c1a19e714cb2df'},timeout_seconds=90,authority='local'))
d['scope']['property_ids']=[x for x in d['scope']['property_ids'] if not x.startswith('LF-')]+prop_ids
d['scope']['test_ids']=[x for x in d['scope']['test_ids'] if not ('::TestLinguistic' in x or any('::'+name+'.' in x for name in ['test_linguistic_model_evidence','test_linguistic_flow_evidence','test_linguistic_injection']))]+test_ids
d['reviews']=[x for x in d['reviews'] if x['id']!='linguistic-fullness-20261023']
d['reviews'].append(dict(id='linguistic-fullness-20261023',question='Full 122-leaf linguistic scope, missing subtypes, acceptable varieties/grammar/usage/collocations and false-positive evidence attacks.',property_ids=prop_ids,test_ids=test_ids,searches=[dict(kind='exact',status='completed',query='Known taxonomy, recipe, native selection/mapper, score and actual quality judge sources; primary linguistic research',outcome='Active ambiguous illustrations/stale review language and implicit subtype/variant coverage repaired; no new category ID is needed.',results=[dict(path=p,classification='change_candidate' if 'generationdata' in p or 'builtin' in p else 'reusable_unchanged',reason='Existing owner and context data inspected; preserve single-admission architecture and exact native arithmetic.') for p in sources]),dict(kind='semantic',status='not_applicable',query='Known owner trace from the preceding connected-speech iteration',reason='Exact known sources answered this scope; no unknown owner discovery was required.',outcome='No semantic-index claim.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Registry/specification and direct native owner tests',reason='No semantic refactor or IDE setup is needed for this change.',outcome='No IDE-index claim.',results=[])],disposition='current_change',rationale='Preserve all original IDs/formulas/sources. Reuse unaffected audio/physics observations and record actual linguistic-semantic limitations. No runtime gate or human review.'))
for path,obj in [(C/'verification.json',g),(C/'discovery.json',d),(A/'CASES.json',dict(properties=prop_ids,canonical_details='../../openspec/changes/implement-teacher-error-trainer/verification.json',cases=[{k:v for k,v in row.items() if k in ['id','property_id','polarity','test_id','source_path']} for row in added]))]:
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(properties=len(prop_ids),cases=len(added),model_cases=len(models),native_cases=sum(x['command_id']=='linguistic-native' for x in added),phone_compiler_cases=6,actual_flow_cases=4)))
