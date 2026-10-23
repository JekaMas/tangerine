"""Freeze literal model inputs separately from their authored expectations."""
import json
from pathlib import Path
import random

R=Path(__file__).resolve().parents[2]
OUT=R/'data/linguistic-fullness-20261023'
OUT.mkdir(parents=True,exist_ok=True)
rows=json.loads((R/'specification/v2/domain/linguistic-contrast-set.v1.json').read_text())['examples']
cases=[]
for row in rows:
    for role,context,text,expected in [
        ('surface',row['contrast_context'],row['surface'],'unsupported' if row['surface_status']=='true_error' else 'supported'),
        ('canonical',row['contrast_context'],row['canonical'],'supported'),
        ('correct_control',row['correct_control']['context'],row['correct_control']['text'],'supported')]:
        cases.append(dict(reference_id=row['taxonomy_id']+'.'+role,category=row['taxonomy_id'],
            input=dict(context=context,realization=text,modality=row['modality'],question='The supplied wording or stipulated realization is acceptable under the stated context and any explicit practice target.'),
            expected=expected,expectation_origin='authored_before_inference',
            expected_reason=row['correct_control']['reason'] if role=='correct_control' else 'The canonical reference is permitted.' if role=='canonical' else 'The stated contextual contrast is deliberately defective.' if row['surface_status']=='true_error' else 'This leaf is an acceptable control, not a true error.'))

# Explicit attacks on false universal explanations and fabricated hearing.
ATTACKS=[
('All questions must end in a pitch rise.','unsupported'),
('A question mark alone proves that the generated audio rises.','unsupported'),
('Every statement must have falling final pitch.','unsupported'),
('Every English accent must be stress-timed with exactly equal interstress durations.','unsupported'),
('A noticeable foreign accent alone establishes a pronunciation error.','unsupported'),
('A successful TTS response proves the requested phoneme occurred.','unsupported'),
('An unreleased final stop is always an omitted consonant.','unsupported'),
('The permitted flap in North American water must be corrected to a careful t.','unsupported'),
('All unstressed English syllables must use schwa.','unsupported'),
('Strong to is correct when contrastively emphasized.','supported'),
('Careful would you without coalescence can be acceptable.','supported'),
('Allowed assimilation in ten bags is not intrinsically an error.','supported'),
('Cot and caught must be different in every correct English variety.','unsupported'),
('The phonetic duration of a vowel alone always determines its lexical identity.','unsupported'),
('All adverbs must end in -ly.','unsupported'),
('Singular they is always a number-agreement error.','unsupported'),
('Two coffees can correctly mean two servings.','supported'),
('The choice between a and an follows the next spoken sound rather than the next written letter.','supported'),
('Take a decision is always wrong because only make collocates with decision.','unsupported'),
('A rare collocation is necessarily ungrammatical.','unsupported'),
('A metaphor is automatically a selectional-restriction error.','unsupported'),
('Turn left—sorry, right can resolve the direction rather than leave an unrepaired contradiction.','supported'),
('Who did you speak to is acceptable in ordinary English despite a preference for whom.','supported'),
('Optional omission of a reason must not cancel a valid correction.','supported'),
('A false explanation must cancel an independently valid detected error and correction.','unsupported'),
('The generated recording audibly contains a dental fricative at exactly one second.','unknown'),
('The generated voice has a reliably measured rising contour on the final word.','unknown'),
('A British voice label proves which vowel and consonant allophones were realized.','unsupported'),
]
for i,(assertion,expected) in enumerate(ATTACKS):
    cases.append(dict(reference_id=f'policy.{i+1:02}',category='cross-cutting',
        input=dict(context='Assess the entire assertion, including all/always. No audio or observed acoustic measurements are supplied. English variety and ordinary contextual alternatives must be respected.',realization=assertion,modality='assertion_truth',question='The complete supplied assertion is supported.'),
        expected=expected,expected_reason='A universal claim has counterexamples, a qualified permitted form is valid, or actual sound is absent.',expectation_origin='authored_before_inference'))
random.Random(231023).shuffle(cases)
# Append new adversarial variety pairs without renumbering retained observations.
EXTRA=[
('grammar.syntax.word_order','A permitted Irish English variety licenses embedded subject-auxiliary inversion; no mainstream embedded-order drill is selected.','She asked where was he.','supported'),
('grammar.syntax.word_order','An explicit mainstream standard British English embedded-order drill requires subject before the auxiliary in this integrated indirect question.','She asked where was he.','unsupported'),
('grammar.syntax.negation','An allowed negative-concord variety uses multiple negative forms to express one negation, in ordinary conversation.','I did not see nobody.','supported'),
('grammar.syntax.negation','A named standard British English form exercise excludes negative concord and asks for a single ordinary negative meaning.','I did not see nobody.','unsupported'),
('grammar.verbs.subject_verb_agreement','A formal standard mandative subjunctive expresses a requirement, not a past event.','It is essential that she be there.','supported'),
('grammar.verbs.infinitive_gerund','Help licenses an object followed by an infinitive with optional to.','Please help me carry the box.','supported'),
('grammar.verbs.infinitive_gerund','Help licenses an object followed by an infinitive with optional to.','Please help me to carry the box.','supported'),
('pronunciation.segmental.consonant_omission','A permitted nonrhotic variety; the word car occurs before a pause; there is no rhotic-r drill.','car with no pronounced postvocalic r','supported'),
('pronunciation.suprasegmental.linking_resyllabification','A permitted nonrhotic variety uses linking r before a vowel.','far away with a linking r','supported'),
('pronunciation.segmental.consonant_omission','A permitted North American realization of t before syllabic n, not a careful alveolar-stop drill.','button realized [ˈbʌʔn̩]','supported'),
('pronunciation.suprasegmental.weak_form','Neutral unaccented can in a permitted connected-speech realization, no strong-form drill.','I can go with can realized [kən]','supported'),
('pronunciation.suprasegmental.assimilation','A permitted connected-speech coalescence of s plus j, with no careful unassimilated target.','miss you realized [mɪʃuː]','supported'),
('pronunciation.suprasegmental.assimilation','A permitted careful connected-speech realization, no coalescence drill.','miss you with [s j] retained','supported'),
('pronunciation.suprasegmental.intonation_contour','A context-appropriate confirmation tag question requests information, not firm agreement.','You have booked, have you? with an appropriate rise','supported'),
('pronunciation.suprasegmental.intonation_contour','An alternative question offers two choices as a closed list; the final alternative has an appropriate fall.','Tea or coffee? with a rise on tea and fall on coffee','supported'),
('acceptable_variant.stylistic_preference','Neither the original source script nor a recording is supplied. This asks about an unobserved written source, not whether an orthographic difference is audible.','The original source script used the spelling colour rather than color.','unknown'),
('grammar.verbs.finite_nonfinite_form','An explicitly permitted African American English variety allows present auxiliary absence in this environment. No standard full-auxiliary exercise is selected.','She working at a bank.','supported'),
('fluency.repetition','Ordinary conversation with a recoverable request and no repetition-free drill or other delivery constraint.','I I need the form.','supported'),
('acceptable_variant.stylistic_preference','Assess the claimed evidence inference: the spelling variants colour and color do not impose different pronunciations.','The audio proves the speaker spelled the word colour rather than color.','unsupported'),
('pronunciation.segmental.consonant_substitution','An explicitly permitted regional English variety uses the attested metathesized pronunciation of ask; no /sk/ drill is selected.','ask realized [æks]','supported'),
('pronunciation.segmental.consonant_substitution','The user explicitly selected a careful /æsk/ consonant-order drill, not a judgment of all English varieties.','ask realized [æks] instead of the named /æsk/ target','unsupported'),
('pronunciation.suprasegmental.elision_reduction','The ordinary dictionary pronunciation is permitted; spelling does not prescribe one vowel for every letter.','camera realized with two syllables as [ˈkæm.rə]','supported'),
]
for i,(category,context,text,expected) in enumerate(EXTRA):
    cases.append(dict(reference_id=f'variety.{i+1:02}',category=category,input=dict(context=context,realization=text,modality='assertion_truth' if expected=='unknown' else 'stipulated_phonetic_or_timing_description' if category.startswith('pronunciation') else 'written_contextual_language',question='The complete supplied assertion is supported.' if expected=='unknown' else 'The supplied wording or stipulated realization is acceptable under the stated context and any explicit practice target.'),expected=expected,expected_reason='Context-specific allowed variety or local target; no actual acoustic evidence is supplied.',expectation_origin='authored_before_inference'))
for i,row in enumerate(cases):row['id']=f'p{i+1:04}'
frozen=dict(scope='finite_linguistic_semantics_not_actual_audio_recognition',cases=cases)
path=R/'audit/linguistic-fullness-20261023/MODEL-CASES.json'
path.write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n')
# The pinned graph parser requires literal test definitions. Keep only identity
# wrappers generated here; the independent assertions remain in observation().
test_path=R/'tests/test_linguistic_model_evidence.py'
if test_path.exists():
    source=test_path.read_text();marker='# Literal identities for the existing DAG owner parser; generated from MODEL-CASES.'
    start=source.index(marker);end=source.index("\n\nif __name__=='__main__':",start)
    methods=[marker,'class LinguisticObservedCases(unittest.TestCase):']
    for i,row in enumerate(cases):
        polarity='positive' if row['expected']=='supported' else 'negative'
        methods += [f'    def test_{row["id"]}_{polarity}(self):',f'        observation(CASES[{i}], {i})(self)','']
    test_path.write_text(source[:start]+'\n'.join(methods)+source[end:])
for batch,start in enumerate(range(0,len(cases),24)):
    selected=cases[start:start+24]
    (OUT/f'batch-{batch:02}.json').write_text(json.dumps(dict(batch=batch,cases=selected),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(cases=len(cases),batches=(len(cases)+23)//24,labels={label:sum(x['expected']==label for x in cases) for label in ['supported','unsupported','unknown']})))
