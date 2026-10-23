# Linguistic coverage and correct variants

The finite inventory is the existing 122 leaves. The companion
`domain/linguistic-contrast-set.v1.json` explicitly maps their subtypes and gives
literal contextual error/correct controls. Subtypes refine selection within a
leaf; they are not extra scoring opportunities. One independently repairable
event has one primary category; compatible overlapping labels are secondary.
No finite list covers every possible English utterance or every English variety.

## What counts as a mistake

Use the audible meaning, public task, permitted variety and register. Separate:

1. A grammatical, lexical or meaning-changing defect in that context.
2. Failure of an **explicit, learner-visible practice target**, such as a named
   falling contour or a matched-duration exercise. Explain it as a target
   mismatch; do not claim the realization is wrong in all English.
3. A valid alternative. It remains acceptable even when another form is more
   common, formal, familiar to the judge or closer to one synthesizer's voice.
4. Insufficient evidence. Unknown hearing, unresolved sense or absent context
   is not a confirmed error or a reason to invent a correction.

Selecting a broad family or CEFR level does not silently impose a narrow accent,
rhythmic ratio, social convention, dictionary pronunciation or formal register.
The learner must have the decisive context before answering. Ordinary generated
dialogue stays self-contained; never score private generator intentions. A
language variety is not inferred from ethnicity, nationality, L1 or a provider's
voice label. A list of permitted varieties is not a list of required stereotypes.

Do not invent a new narrow drill restriction solely to make an otherwise valid
variant wrong. A user-requested practice target can be scored as that target;
ordinary broad generation chooses an unambiguous meaning/form contrast or
communicative defect instead. The ms/range/density examples in the contrast set
are explicitly stipulated controlled tasks, not default English norms.

## Pronunciation: correct alternatives and corresponding traps

| Feature | Acceptable under the stated variety/context | Reject the false inference |
| --- | --- | --- |
| Rhoticity | Pronounced or absent non-prevocalic /r/ where licensed | Absent coda /r/ always means consonant omission |
| Stops | Released, unreleased or permitted glottalized /t/ | No burst means no stop; every glottal closure is intrusive |
| Flapping | Intervocalic North American /t,d/ realized as [ɾ] in its environment | A flap in “water” is automatically a voicing error |
| Aspiration | Context-dependent aspiration; post-/s/ /p/ in “spin” normally lacks aspiration | Every /p/ must have the same VOT |
| Voicing | Partial final devoicing with other contrast cues preserved | A voicing percentage alone determines “bag” versus “back” |
| Place/manner | Permitted clear/dark /l/, dentalized alveolars, rhotic allophones | A narrow transcription must equal one preferred allophone |
| Vowel systems | Licensed mergers, splits, rhotic qualities and monophthongal regional forms | “cot/caught” must differ in every variety; GOAT must always glide |
| Duration | Rate/context/quality-dependent duration preserving the word | A short vowel is always the wrong phoneme; one universal ms norm |
| Unstressed vowels | Schwa, permitted full vowels and syllabic consonants | Every unstressed syllable must become schwa |
| Endings | /s,z,ɪz/ and /t,d,ɪd/ in their environments, including licensed reductions | Every plural/past ending has the same phones; spelling proves sound |
| Lexical stress | Dictionary/variety alternatives, noun/verb patterns, secondary stress and contextual shift | One stress pattern applies to every sense or derivative |
| Compound stress | Lexical and contextual compound/phrase patterns | All noun-noun combinations require first-word stress |
| Sentence focus | Different nuclear focus answering different questions | One fixed stressed word fits every dialogue |
| Rhythm | Intelligible variety/register/rate differences; weak syllable compression where appropriate | All English has mathematically equal stress intervals or one vowel ratio |
| Weak/strong forms | Neutral weak forms, emphatic strong forms and acceptable clear speech | Strong “to” is inherently wrong; reduction is mandatory in every setting |
| Linking | Smooth consonant-vowel linking, resyllabification, boundary glides and licensed /r/ | A linking glide is an inserted lexical segment; clear separation is always wrong |
| Assimilation | Place changes and contextual coalescence, or careful unassimilated speech | “would you” [dʒ] is wrong; every “did you” must coalesce |
| Elision | Licensed /t,d/ or schwa reduction preserving the task's contrast | Any absent phone is an error; any elision preserves meaning |
| Metathesis/syllable count | Attested regional consonant order, dictionary syllable reductions such as two-syllable “camera” | Every segment transposition or missing written vowel is wrong |
| Intonation | Rise, fall, fall-rise, rise-fall and continuation patterns in context | `?` requires a rise; `.` requires a fall; one contour proves sarcasm |
| Questions | Falling ordinary wh-questions; context-appropriate confirmation, echo, tag and alternative-question patterns | Word order/punctuation alone determines intended function |
| Chunking | Vocative, list, parenthetical and clause boundaries appropriate to meaning | Every comma is a fixed silence; every hesitation is an error |
| Pitch range | Individual and contextual range differences | Monotone delivery diagnoses pathology or always fails English |

Each actual acoustic key distinguishes requested controls from heard/measured
realization. Symbolic IPA or stipulated timing examples test a linguistic
contract, not actual hearing. Actual WAV evidence, source interval, preprocessing
and uncertainty are required for a claim about generated sound. An ASR transcript,
successful API reply, requested phoneme or model opinion alone cannot establish
all these distinctions. Existing acoustic controllers remain the owners; no new
runtime audit or mandatory review is added.

Consonant order/metathesis uses the existing consonant-substitution leaf and
whole-phrase/word phone pair as one independently repairable event. Inappropriate
vowel deletion/syllable loss uses the existing elision/reduction leaf; ordinary
reductions remain controls. Neither requires another score or new category ID.
The regional “ask” [æks] form is documented in
[university linguistic research](https://alic.sites.unlv.edu/chapter-11-8-assimilation/?print=print);
[Cambridge camera](https://dictionary.cambridge.org/pronunciation/english/camera)
provides the two-syllable control. Provider realization of these newly explicit
subtypes remains a separate actual-audio observation, never inferred from IPA.

## Grammar, words and collocations

The per-leaf subtype inventory covers determiners including sound-conditioned
`a/an`, count and mass senses, pronoun case/binding/reference, tense/aspect,
agreement, auxiliaries, modal meaning/form, complement patterns, passive and
causative frames, prepositions/particles, clause construction, coordination,
conditionals, comparison, inflection, derivation and word class. Direct, embedded,
subject, echo and tag questions are different constructions. A sound-conditioned
article error is grammatical even when pronunciation reveals its trigger.

Correct controls include institutional zero article, serving/type count nouns,
singular *they*, British collective agreement, conversational ellipsis and left
dislocation, historical present, American past with *yet*, *gotten*, permitted
regular/irregular alternatives, passive *made to*, emphatic *did*, flat adverbs,
preposition stranding and an explicitly resolved self-correction. A form may be
acceptable in one sense or register and unacceptable in another. For example,
*stop to drink* and *stop drinking* express different meanings; a synonym cannot
automatically inherit another verb's argument frame. Written punctuation,
apostrophe and spelling mistakes are outside an audio-only finding unless they
change an audible realization. Their spoken grammatical effects remain covered.

Explicit variety scope matters even for familiar classroom grammar. Embedded
question inversion is attested in Irish and other English varieties. Preserve a
correct allowed-variety control; a mainstream standard embedded-order drill
must state its narrower target instead of labelling all such speakers wrong.
See [Yale's embedded-question research](https://ygdp.yale.edu/phenomena/inversion-embedded-questions).
Likewise a false-friend example must actually retain the wrong meaning-bearing
word; a source sentence that explicitly paraphrases and repairs its meaning
cannot serve as an unrepaired-error reference.
The same distinction applies to auxiliary/copula absence in a permitted variety;
see [Yale's null-copula research](https://ygdp.yale.edu/phenomena/null-copula).
An accent/locale tag alone neither excludes nor proves that grammatical system.

Lexical subtypes include near-synonym/confusable sense, deixis, semantic role,
polysemy, lexicalized derivation, fixed/semi-fixed idioms, phrasal-verb meaning,
false-friend transfer supported by actual meaning (never L1 alone), semantic
precision, literal/metaphorical selection, register and purposeful redundancy.
Collocations cover verb-noun, adjective-noun, adverb-adjective, noun-noun,
verb-adverb and lexical preposition patterns. Do not convert low frequency into
ungrammaticality. *Make/take/reach a decision* and *do/conduct research* demonstrate
why alternatives must be checked in their sense, variety and register. Do not
reject every creative metaphor or productive coinage by dictionary absence.

Fluency, discourse and pragmatic categories retain their full scope. Natural
fillers, successful self-repair, rhetorical repetition, backchannels, cooperative
overlap, indirect answers, marked flashbacks, cultural politeness differences and
explicit participant preferences are controls. A numerical timing/density bound
is a local practice objective with a defined denominator, never a universal
clinical or accent norm. A turn that explicitly replaces “nine” with “ten” is a
repair, not an unrepaired contradiction.

## Generation and answer checking

Use the existing clean-text and mutation phases. The mutation phase selects a
concrete subtype, ensures the canonical text is acceptable and changes the
surface/audio so the intended defect actually exists. It preserves every valid
alternative and decisive context in the saved key. Original illustrations are
historical inputs, not unquestionable linguistic truth or text to copy. The
active recipe errata replace ambiguous illustrations; original bytes remain in
`spec-inputs/` and Git history.

The existing taxonomy inclusion/exclusion projection carries concrete correct
controls into generation and interpretation. No new endpoint, service, external
dictionary dependency, per-read check or human approval is required. New saved
preparations use the updated frozen registries; existing assets/results retain
their recorded bindings and bytes.

When a listener calls a permitted control wrong, apply the existing false-positive
semantics. A valid alternative repair receives the same primary credit as the
preferred repair. An unnecessary stylistic rewrite is not discovery of an error.
Assess explanations separately: omitting one has no penalty; supplying “all
questions rise” or “all adverbs end in -ly” requires rejection/feedback even when
the proposed correction itself is valid. A credible defect in the key remains
unresolved and can use the existing optional reconsideration/key-repair route;
do not force a linguistically false result solely to agree with a saved label.

## Research and finite evidence

Reference groups in the contrast file resolve as follows. These references
explain linguistic distinctions; they do not validate generated audio or provide
empirical coverage of all 122 leaves.

- **R-PHONOLOGY:** [Council of Europe phonological competence](https://www.coe.int/en/web/common-european-framework-reference-languages/phonological-competence),
  [CEFR revision report](https://rm.coe.int/phonological-scale-revision-process-report-cefr/168073fff9),
  [open university phonetics: glottalization](https://opentextbooks.rug.nl/americanenglishphonetics2/chapter/9-3-glottal-reinforcement-glottalization-and-glottal-stopping-glottaling/),
  [Essentials of Linguistics](https://ecampusontario.pressbooks.pub/essentialsoflinguistics2/open/download?type=pdf).
- **R-CONNECTED:** [British Council connected speech](https://www.teachingenglish.org.uk/professional-development/teachers/teaching-knowledge-database/c/connected-speech),
  [assimilation lesson](https://www.britishcouncil.org.br/sites/default/files/lesson_plan_-_eng.pdf),
  [rhythm](https://www.teachingenglish.org.uk/professional-development/teachers/knowing-subject/rhythm),
  [World Englishes rhythm research](https://onlinelibrary.wiley.com/doi/10.1002/9781119518297.eowe00334).
- **R-INTONATION:** [Cambridge intonation](https://dictionary.cambridge.org/grammar/british-grammar/intonation).
- **R-GRAMMAR:** [Cambridge articles](https://dictionary.cambridge.org/grammar/british-grammar/articles),
  [countability](https://dictionary.cambridge.org/uk/grammar/british-grammar/countable-and-uncountable-nouns),
  [personal pronouns](https://dictionary.cambridge.org/uk/grammar/british-grammar/personal-pronouns),
  [singular they](https://dictionary.cambridge.org/us/grammar/british-grammar/someone-somebody-something-somewhere),
  [who/whom](https://dictionary.cambridge.org/us/grammar/british-grammar/who-whom),
  [must and non-obligation](https://dictionary.cambridge.org/grammar/british-grammar/must),
  [British Council ellipsis](https://learnenglish.britishcouncil.org/free-resources/grammar/c1/ellipsis),
  [conditionals](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/conditionals-zero-first-second).
- **R-VARIETIES:** [Cambridge British/American differences](https://dictionary.cambridge.org/grammar/british-grammar/british-and-american-),
  [Yale embedded-question inversion](https://ygdp.yale.edu/phenomena/inversion-embedded-questions).
- **R-COLLOCATION:** [Cambridge collocation](https://dictionary.cambridge.org/us/grammar/british-grammar/collocation_2),
  [do/make](https://dictionary.cambridge.org/grammar/british-grammar/collocation-do-or-make),
  [Canadian government decision usage](https://our-languages.canada.ca/en/writing-tips-plus/decision-make-a-decision-take-a-decision).

The tracked audit at `audit/linguistic-fullness-20261023/REPORT.md` records every
selected literal test, native projection/arithmetic result, actual model/Lab
observation and failed attack. The contrast population is authored reference
data. It is not the separate 732-stimulus benchmark, external corpus frequency,
independent empirical gold or qualification of every provider/voice/accent.
