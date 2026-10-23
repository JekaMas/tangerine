"""Authored contrasts, not corpus records or a claim of observed sound.

The literal controls/reasons below are independent of model responses. Keep
expectations out of model inputs. This is a development authoring tool, never a
runtime validator or an automatic linguistic oracle.
"""
import difflib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V = ROOT / 'specification/v2'


def load_taxonomy():
    return json.loads(subprocess.check_output([
        'ruby', '-ryaml', '-rjson', '-e',
        'puts JSON.generate(YAML.load_file(ARGV[0]))',
        str(V / 'domain/error-taxonomy.v1.yaml')], text=True))


# leaf suffix | subtypes (semicolon separated) | permitted context | literal
# correct control | independently authored reason. No frequencies are implied.
GROUPS = {
'grammar': """
determiners.article_omission|singular count;generic bare plural;institutional zero article|Ordinary statement about attending an institution.|The children go to school.|Institutional school needs no article here.
determiners.article_addition|possessive determiner;generic mass;proper name exceptions|General material, not a serving or a specific batch.|Water is essential.|A general mass noun can have zero article.
determiners.article_choice|definiteness;a versus an by SOUND;initialism;silent consonant|Ordinary spoken English; university begins with /j/.|She works at a university.|The following sound, not the written vowel, selects a.
determiners.demonstrative_choice|number;distance;discourse deixis|Several previously introduced books at a distance.|Those books are mine.|Those agrees with plural books.
determiners.possessive_determiner|dependent possessive;independent possessive;double genitive|Ordinary description of one of my sisters.|A sister of mine lives here.|A sister of mine is licensed; a my sister is different.
determiners.quantifier_determiner|countability;scope;few versus a few;less versus fewer context|An amount of measured time.|It took less than five minutes.|Less with an amount of time is permitted; a blanket fewer rule is false.
determiners.other_determiner|another versus other;each versus every;all versus whole|More than one additional chair.|We need other chairs.|Other is licensed with the plural; another is not universally required.
nouns.number|regular;irregular;invariant;plural-only;measurement sense|Two animals of the sheep species.|Two sheep escaped.|Sheep has an invariant plural.
nouns.countability|mass sense;count sense;serving;type;partitive|A café order for two servings.|Two coffees, please.|Coffee is countable for servings.
nouns.possessive|singular possessive;plural possessive;group genitive|A car belonging to my brother.|That is my brother's car.|The possessive is licensed; written apostrophes alone cannot be heard.
nouns.noun_form|malformed noun stem;lexicalized noun;creative coinage|Ordinary money container, not a playful coinage.|I put it in my wallet.|The ordinary noun wallet is valid.
pronouns.subject_object_case|subject;object;predicative complement;isolated answer;who versus whom|Casual response to Who is at the door?|It's me.|Object-form me is normal after be in this context.
pronouns.reference|local antecedent;deixis;animacy;personification|A woman has been introduced explicitly.|Lea arrived; she is waiting outside.|The audible antecedent licenses she.
pronouns.agreement|person;number;singular they;collective reference|Someone of unspecified gender has left property.|Someone left their umbrella.|Singular they/their is licensed.
pronouns.reflexive|local binding;person;number;emphatic intensive;reciprocal distinction|The speaker emphasizes doing the work personally.|I myself fixed the door.|An intensive reflexive need not be an object.
pronouns.relative_pronoun|subject;object;possessive;restrictive that;zero object relative|An integrated restrictive relative about a person.|The person that called is here.|Restrictive that can refer to people.
pronouns.pronoun_omission_addition|required argument;left dislocation;object repetition;ellipsis|Casual left dislocation with a separate topic intonation.|My brother, he works here.|Conversational left dislocation licenses the resumptive pronoun.
verbs.tense|past;present;future reference;historical present;backshift|The speaker explicitly tells a vivid story in the historical present.|So yesterday I walk into the shop, and everyone cheers.|The narrative present is licensed by the stated storytelling mode.
verbs.aspect|progressive;perfect;stative versus dynamic sense;habitual versus temporary|A sports commentator describes live action.|She passes, he shoots, and he scores!|Commentary present is not an aspect error.
verbs.tense_aspect_combination|closed past time;current relevance;perfect progressive;regional alternatives|A permitted American English question with yet.|Did you eat yet?|American past simple with yet can be correct.
verbs.subject_verb_agreement|person;number;collective;notional;existential;mandative subjunctive|British English; team members act separately.|The team are putting on their shirts.|Plural collective agreement is permitted here.
verbs.auxiliary|be;have;auxiliary order;auxiliary omission in conversation|Casual conversation with you and a recoverable auxiliary.|You coming tonight?|Conversational auxiliary ellipsis is licensed.
verbs.do_support|negative;question;emphasis;tense carried by do|An emphatic correction to a denial.|I did pay yesterday.|Emphatic did takes the base form; it is not redundant error.
verbs.modal_choice|obligation;permission;possibility;deduction;prohibition versus non-obligation|Attendance is optional and the speaker is not issuing an indirect criticism.|You don't have to attend, but you may.|Non-obligation does not mean prohibition.
verbs.modal_form|bare infinitive;perfect modal;semi-modal;ought to|Ordinary advice with ought.|You ought to wait.|Ought to does not follow the bare-infinitive pattern of can.
verbs.infinitive_gerund|lexical selection;meaning-changing stop/remember/try;both licensed|The person pauses another activity in order to drink.|She stopped to drink some water.|Stop to drink and stop drinking express different valid meanings.
verbs.participle|perfect;passive;present participle;regional learned/learnt|American English past participle of get.|The weather has gotten colder.|Gotten is a licensed American participle.
verbs.finite_nonfinite_form|finite clause;infinitive;gerund;participial clause;ellipsis|A fragment answering What is she doing?|Working at the bank.|A conversational answer fragment need not be a complete finite sentence.
verbs.passive|be passive;get passive;agentless;intransitive alternation|The window breaks; no agent is asserted.|The window broke.|An intransitive event does not require passive be.
verbs.causative|make;let;have;get;active versus passive make|Passive causative make.|I was made to wait.|Passive made licenses to, unlike active made me wait.
verbs.irregular_form|irregular past;regular alternative;regional past and participle|A permitted standard regular alternative.|She learned the rule.|Learned is valid even where learnt is also used.
prepositions_particles.preposition_choice|time;place;dependent preposition;regional alternative|American English time expression.|We will meet on the weekend.|On the weekend is an acceptable regional choice.
prepositions_particles.preposition_omission|required complement preposition;transitive alternative;stranding|Hear takes a direct object.|Hear the recording first.|Hear does not require the to required by listen.
prepositions_particles.preposition_addition|transitive frame;licensed verb-preposition frame|Talk selects about for a topic.|We talked about the plan.|A preposition valid with talk is not licensed with every synonym.
prepositions_particles.particle_choice|separable verb;pronoun placement;inseparable verb;particle meaning|A separable verb with a full noun object.|Switch off the light.|The full noun can follow the particle.
syntax.word_order|embedded question;adverb order;inversion;focus fronting|A direct information question.|Where is he?|Direct question inversion differs from embedded question order.
syntax.question_formation|yes/no;wh;subject question;tag;echo;embedded question|A direct subject question asking for the person.|Who called you?|Subject wh-questions do not require did.
syntax.negation|scope;negative polarity;negative concord by variety;double negation meaning|A deliberate logical double negation, not negative concord.|It is not impossible.|Two negative elements can express a positive possibility.
syntax.subject_omission_addition|imperative;diary;conversational ellipsis;coordinated subject sharing|An ordinary imperative.|Come here, please.|Imperatives normally omit an explicit subject.
syntax.expletive_subject|existential there;weather it;referential it;cleft it|Identification of an already discussed object.|What is that? It is a book on the desk.|Referential it is not an existential error.
syntax.complementation|argument frame;that clause;recipient;object infinitive;verb-specific alternation|Tell licenses a double-object frame.|She told me the rule.|A frame valid with tell need not be valid with explain.
syntax.clause_structure|fragment;run-on spoken versus written;nonfinite clause;subordinate host|An answer to Why did you leave?|Because I was tired.|A meaningful conversational subordinate answer is acceptable.
syntax.relative_clause|gap;resumptive;restrictive;nonrestrictive;zero object relative|An integrated object relative.|The book I read was excellent.|The object relative pronoun can be omitted.
syntax.conditional|zero;open;remote;past counterfactual;mixed;will as willingness|An open future condition.|If it rains, we will stay inside.|This valid open conditional must not be forced into the remote pattern.
syntax.comparison|comparative;superlative;than clause;correlative;intensifier|A repeated comparative expressing change.|It is getting more and more interesting.|More and more is licensed repetition, not redundant comparison marking.
syntax.coordination|parallel complement selection;shared argument;gapping;different licensed frames|Two clauses share a subject.|She likes swimming and wants to read.|Different heads can license different complement forms.
syntax.subordination|cause;concession;time;purpose;discourse versus clause so|Two independent spoken intonation units.|It was raining. So, we stayed at home.|Discourse so is licensed; punctuation itself is not acoustic evidence.
syntax.agreement_other|attributive measure;determiner concord;predicative measure|A predicative plural measure.|The trip lasted five days.|Plural days is required outside the attributive compound.
morphology.inflection|comparative;superlative;number;tense;irregular suppletion|Ordinary standard superlative.|This is the best option.|Best is the irregular superlative of good.
morphology.derivation|affix productivity;negative prefix;derivative category;creative coinage|An explicitly playful creative writing task.|The dragon is wonderfully undragonlike.|A transparent creative derivative is not automatically an error.
morphology.word_class_form|adjective versus adverb;participial adjective;flat adverb;complement adjective|An ordinary flat adverb modifying drive.|Drive fast, but safely.|Fast is a licensed adverb; -ly is not universally required.
""",
'lexis': """
lexical_choice|sense;near synonym;deixis bring/take;borrow/lend;confusable|The owner is asked to transfer a pen temporarily.|Could you lend me your pen?|Lend is correct from the owner's perspective.
collocation|verb-noun;adjective-noun;adverb-adjective;noun-noun;verb-adverb;lexical preposition;regional alternative|A formal decision statement in a variety permitting take.|The cabinet took a decision.|Take a decision is valid; make is not the only correct collocator.
phraseology_idiom|fixed idiom;semi-fixed frame;literal versus idiomatic;creative variation|An explicitly fictional story about a blue sun.|The planet had a blue sun.|Literal words need not obey an unrelated idiom.
phrasal_verb|idiomatic meaning;literal particle;polysemy;separability|Someone yields after pressure.|She gave in to pressure.|Give in is valid for yielding, not for quitting smoking.
word_formation|derivative meaning;agent versus action;compound;conversion|A person whose occupation is teaching.|She is a teacher.|The conventional agent noun is valid.
false_friend|cross-language sense transfer;English false cognate evidence;actually versus currently|A speaker corrects the presupposition that they live elsewhere.|Actually, I live here.|Actually is valid for correction; the speaker's first language proves nothing.
semantic_precision|hypernym;hyponym;kinship;degree;reference scope|One male sibling of the speaker's father.|My uncle is my father's brother.|The kinship term fits the stated relationship.
selectional_restriction|literal argument type;metaphorical coercion;animacy;semantic role|Explicit personification in a poem.|The thirsty earth drank the rain.|Metaphorical selection is permitted by genre.
redundancy_pleonasm|semantic repetition;emphasis;concise-task requirement|Ordinary emphatic conversation with no concision constraint.|I saw it with my own eyes.|Redundancy can be purposeful emphasis rather than an English error.
lexical_register|formal;casual;technical;regional slang;audience|Casual British conversation.|Someone nicked my bike.|Nicked is permitted in this setting.
""",
'pronunciation.segmental': """
consonant_substitution|phonemic contrast;consonant metathesis/segment order;rhotic/nonrhotic r;tap/flap t-d;yod dropping;accent-specific dental variants|A permitted North American pronunciation, no careful-stop target.|water with intervocalic [ɾ]|A flap is a context-conditioned allophone, not an automatic t-to-d error.
consonant_omission|phoneme loss;unreleased stop;glottal replacement;nonrhotic coda|A permitted unreleased final stop.|coat with final [t̚]|Lack of a release burst does not mean the consonant is absent.
consonant_insertion|extra lexical segment;linking r;intrusive r;hiatus glide|A permitted smooth transition between go and up.|go up with a linking [w] transition|A boundary glide may be normal connected speech rather than an extra lexical consonant.
consonant_voicing|phonemic voicing;contextual partial voicing;flapping|A permitted North American tap between vowels.|ladder with an intervocalic [ɾ]|A tap must not be rejected because it differs from a careful [d].
consonant_devoicing|final partial devoicing;closure cues;preceding vowel cues;lexical contrast|Final bag retains its contrast with back through the available acoustic cues.|bag with a partially devoiced final [ɡ̥]|Partial devoicing alone does not prove loss of the word contrast.
consonant_cluster_simplification|cluster deletion;connected t-d elision;grammatical ending retention|Connected speech in a permitted variety, with no careful-cluster drill; the intended words are next day.|next day realized [neks deɪ], with t elided from the consonant cluster|A licensed cluster simplification is not automatically a wrong word.
consonant_aspiration|stressed onset;post-s position;unstressed onset;contrast task|The p follows s in ordinary English.|spin with unaspirated [p]|Aspiration is not expected in this post-s position.
consonant_place_manner|clear/dark l;dentalized alveolar;approximant/tap r;glottal reinforcement|A variety permitting dark l at the end of a syllable.|full with dark [ɫ]|An allowed allophone is not an incompatible manner error.
vowel_substitution|lexical set;cot-caught merger;trap-bath split;rhotic vowel;accent-conditioned quality|A variety with the cot-caught merger and no contrasting target.|cot and caught share the permitted vowel|A licensed merger is not a lost distinction in that variety.
vowel_length|quality-duration interaction;pre-fortis clipping;rate;context;phonemic contrast|Same word in faster intelligible speech, no exact-duration task.|A shorter but contrast-preserving vowel in sheep|Duration alone cannot establish the wrong lexical vowel.
vowel_reduction|schwa;unstressed full vowel;contrastive full vowel;syllabic consonant|Contrastive emphasis on to.|I said TO him, not FROM him.|The full strong vowel is permitted under emphasis.
diphthong_realization|trajectory;monophthongal regional realization;centering vowel;lexical contrast|A permitted Scottish-style monophthongal FACE vowel, no trajectory drill.|face with a permitted [eː] realization|A licensed monophthong is not intrinsically an incorrect diphthong.
vowel_insertion_epenthesis|extra syllable;transition;syllabic consonant;optional schwa|A permitted realization with a syllabic final consonant.|button with syllabic [n̩]|A syllabic consonant does not itself prove an inserted lexical vowel.
final_segment_realization|plural/past allomorph;release;assimilation;grammatical contrast|The plural allomorph is appropriate after the final sound.|cats with [s], dogs with [z], buses with [ɪz]|Different suffix realizations are licensed by their phonological environments.
""",
'pronunciation.suprasegmental': """
lexical_stress|noun-verb stress;regional alternative;secondary stress;stress shift|The lexical item is the verb record.|Please reCORD the call.|Verb-final stress is correct and must not be judged by the noun pattern.
compound_stress|compound versus phrase;lexical exceptions;contrastive shift|Any bird whose color is black, not the species.|a black BIRD|A phrase may stress bird; compounds do not supply a universal noun-noun rule.
sentence_stress_prominence|new information;contrast;nuclear focus;deaccenting|The question is What did John buy?|John bought a CAR.|Prominence on car fits this question.
rhythm|stress distribution;weak syllable compression;accent/register timing;tempo|Intelligible English in a permitted more syllable-timed variety; no timing drill.|Evenly timed clear syllables preserving the message|No universal equal-stress-interval or syllable-ratio requirement is imposed.
intonation_contour|rise;fall;fall-rise;rise-fall;continuation;tag;alternative question|Ordinary information-seeking wh-question.|Why do you need insurance? with a falling contour|A question mark does not require rising pitch.
intonation_function|confirmation;statement;uptalk;uncertainty;politeness;attitude|An informal confirmation question with declarative word order.|You have insurance? with a final rise|Question function can be conveyed without interrogative syntax.
weak_form|weak versus strong;contrast;clear speech;function word stress|Contrastive correction of the preposition.|I said TO her, not ABOUT her.|Strong to is appropriate under contrastive emphasis.
linking_resyllabification|consonant-vowel;vowel-vowel glide;linking/intrusive r;resyllabification;boundary contrast|Careful but intelligible speech, no linking drill.|turn it off with clear word boundaries|Lack of smooth linking alone is not a general English error.
assimilation|place;voicing;coalescent t+j;coalescent d+j;s+j;optional unassimilated form|Ordinary connected speech in a variety allowing coalescence.|Would you with [wʊdʒə]|Coalescence is permitted; careful [wʊd ju] is also a control.
elision_reduction|t-d elision;vowel deletion/syllable loss;word-internal versus boundary elision;schwa loss;h loss by context;contraction;grammatical cue preservation|Normal connected speech preserving the plural s.|documents with the t elided but plural s retained|Reduction may preserve all required grammatical contrasts.
thought_group_chunking|constituent;vocative;parenthetical;list;scope;prosodic phrasing|An invitation addressed to Grandma.|Let's eat, Grandma, with a vocative boundary|This grouping is licensed; a comma is not a measured pause.
pitch_range|range;register;baseline;speaker physiology;task-specific bound|An intelligible speaker with no specified range exercise.|A naturally narrow pitch range|A narrow range alone is not an error or a clinical diagnosis.
""",
'fluency': """
speech_rate|task-specific WPM;articulation rate;pause-inclusive rate;comprehensibility|No rate constraint; the message is understood.|A clear fast speaker delivering an ordinary greeting|Fast is not automatically erroneous; rate and intelligibility differ.
excessive_pausing|silent interval;planned pause;dramatic pause;task bound|A deliberate dramatic pause in a story.|She opened the door ... and gasped.|A purposeful pause is allowed.
pause_location|word-internal;constituent-internal;phrase boundary;hesitation|A clause boundary with normal planning time.|When the rain stopped, [pause] we left.|A permissible boundary pause is not an intrusive word split.
hesitation_fillers|filler density;placement;discourse function;emergency constraint|Ordinary informal planning, no density ceiling.|Um, I think we should take the bus.|An ordinary planning filler is allowed.
repetition|unintended restart;emphasis;parallelism;quotation|Deliberate emphasis.|It was very, very cold.|Rhetorical repetition is meaningful.
false_start|aborted onset;successful restart;replanning;task constraint|A permitted conversational restart that completes the message.|I wa- I mean, I need the blue form.|A resolved false start is acceptable in this setting.
self_repair|successful correction;unresolved alternatives;retraction;precision|A route speaker explicitly corrects a direction.|Turn left—sorry, right.|The final direction is unambiguous after a successful repair.
breakdown_abandonment|required message missing;recoverable ellipsis;purposeful trailing off|The full familiar expression is mutually established.|When in Rome...|A recoverable conventional ellipsis is permitted.
disfluency_density|event count;overlap;word denominator;task-specific ceiling|One filler among 100 words; task limit is at most two fillers per 100 words.|1 filler / 100 words|This is below the explicit ceiling; no universal clinical norm follows.
""",
'discourse': """
cohesion_reference|cross-turn antecedent;ambiguous pronoun;deixis;bridging|Only one named man is in the supplied discourse.|John came in. He sat down.|The unique antecedent is recoverable.
connector_choice|cause;contrast;concession;addition;contextual expectation|The expected cancellation is avoided despite the rain.|It rained; however, we continued the match.|However expresses a genuine contrast here.
logical_relation|entailment;quantifier scope;invalid converse;presupposition|A valid one-way class inclusion.|All cats are animals; that does not mean all animals are cats.|The invalid converse is explicitly denied.
sequencing|chronology;prerequisite;flashback;explicit temporal marker|The narrator explicitly marks a flashback.|She served the tea. Earlier, she had boiled the water.|Narrative presentation need not match chronological order.
coherence|contradiction;event identity;explicit self-correction;perspective|One arrival is explicitly corrected.|I arrived at nine—sorry, ten.|An explicit repair supersedes the earlier claim rather than contradicting it unrepaired.
topic_management|required topic;transition;licensed digression;return|A friendly conversation explicitly permits a brief digression.|Before we discuss the route, may I ask about your trip?|The transition and setting license the change.
turn_taking|interruption;cooperative overlap;backchannel;floor handoff|Cooperative conversation permits backchannels without masking content.|A listener says mm-hm while the speaker continues clearly.|Cooperative overlap is not automatically disruptive.
response_relevance|direct answer;recoverable indirect answer;honest unknown;question scope|The question asks whether a person can attend tonight.|I am working all evening.|The indirect refusal is recoverable from the question.
information_structure|given/new;contrast;topic;focus;cleft;alternative order|A question asks who bought the car.|It was John who bought the car.|A cleft supplies the requested focus.
clarification_repair|referent disambiguation;hearing repair;paraphrase;repetition|The listener says I did not hear the surname.|Smith. John Smith.|Repetition can repair a hearing problem.
""",
'pragmatics_register': """
formality|whole-turn register;institutional target;informal setting|Friendly conversation between peers who use casual address.|Hi, mate. Can you pass that over?|Casual wording fits the stated relationship.
politeness|relationship;urgency;culture;face threat;explicit preference|An immediate safety hazard requires an urgent warning.|Stop! The wire is live!|Urgent directness is appropriate; indirectness is not always more polite.
directness|emergency clarity;indirect request;hint;stated speech-act objective|A polite ordinary request at a dining table.|Could you pass the salt?|The indirect question conventionally requests an action.
speech_act|apology;request;offer;warning;literal versus irony|A genuine congratulation after a successful exam.|Congratulations on passing your exam!|The speech act matches the event.
sociolinguistic_appropriacy|stated name;title;pronoun;address preference|The addressee explicitly says Please call me Jo.|Hello, Jo.|The actual preference controls; nationality or identity is not an oracle.
audience_context_fit|beginner instruction;technical audience;shared knowledge;gloss|The addressees are engineers familiar with the term.|Check the input impedance.|Established technical knowledge licenses the terminology.
pragmatic_force|promise;hedge;certainty;obligation;permission;mitigation|The speaker genuinely does not know whether attendance is possible.|I might be able to come.|Uncertainty is appropriate when no commitment was made.
naturalness_idiomaticity|conventional speech act;genre;creative phrasing;regional convention|A fictional robot's deliberately literal greeting.|How is your existence proceeding?|Creative genre licenses the unusual greeting; unusual is not ungrammatical.
""",
'acceptable_variant': """
grammar_variant|tense alternative;collective agreement;subjunctive;conditional was/were|A permitted ordinary remote conditional.|If she was in charge, she would change it.|Conversational was may be permitted alongside were.
lexical_variant|synonym;collocation alternative;regional word;sense preservation|Ordinary research activity.|We conducted research into the cause.|Conduct research and do research are both valid.
pronunciation_variant|dictionary variant;regional phoneme;allophone;connected speech|The task permits both common pronunciations of either.|either with /ˈaɪðə/|A permitted dictionary variant is acceptable.
dialect_variant|rhoticity;vowel merger;regional grammar;regional lexicon|A permitted American English time expression.|See you on the weekend.|An attested allowed regional form is not an error.
register_variant|casual reduction;formal equivalent;technical equivalent|Ordinary casual speech, no formal wording restriction.|I wanna go home.|A casual reduction is permitted here.
informal_acceptable|ellipsis;contraction;fragment;left dislocation|A casual invitation.|Want some tea?|Subject/auxiliary ellipsis is acceptable in this context.
stylistic_preference|synonym;active/passive;concision;preposition stranding|Ordinary speech with no special formal restriction.|Who did you speak to?|Stranding is acceptable; a preference for whom does not require a correction.
alternative_standard|emphatic do;regular/irregular alternative;double genitive;regional standard|An emphatic denial of a claim that the person stayed home.|I did go to the meeting.|Emphatic did plus base go is standard.
"""
}

# Replace genuinely ambiguous/abstract illustrations, preserving originals in
# the imported releases and this baseline. Context is supplied to the learner.
REPAIRS = {
'grammar.determiners.article_choice': ('Ordinary spoken English; hour begins with a vowel sound.', 'I waited for an hour.', 'I waited for a hour.'),
'grammar.pronouns.agreement': ('The speaker explicitly refers to both cars together.', 'I saw both cars and photographed them.', 'I saw both cars and photographed it.'),
'grammar.pronouns.reflexive': ('Only the first-person speaker was hurt by their own action.', 'I accidentally hurt myself.', 'I accidentally hurt herself.'),
'grammar.verbs.aspect': ('Ordinary contemporary standard British English; know describes the existing mental state of possessing an answer, not a creative or variety-specific dynamic use.', 'I know the answer.', 'I am knowing the answer.'),
'grammar.verbs.auxiliary': ('A present progressive describing what the speaker is doing now.', 'I am waiting right now.', 'I waiting right now.'),
'grammar.verbs.finite_nonfinite_form': ('An explicit contemporary standard British English full finite-clause exercise, not an auxiliary-omission variety or a conversational fragment.', 'She is working at a bank.', 'She working at a bank.'),
'grammar.verbs.modal_choice': ('The room is closed because of a chemical spill. Absolutely nobody is permitted to enter. The reply must communicate that prohibition, not grant permission.', 'You must not enter the room.', 'You may enter the room.'),
'grammar.morphology.word_class_form': ('A standard attributive adjective modifying solution, no quoted creative wording.', 'We need a clear solution.', 'We need a clearly solution.'),
'grammar.syntax.agreement_other': ('A five-day interval modifies trip in an attributive compound.', 'A five-day trip.', 'A five-days trip.'),
'grammar.syntax.word_order': ('A standard British English grammar practice task for an integrated embedded interrogative, not a variety-specific inverted embedded question or a quoted direct question.', 'Tell me where he is.', 'Tell me where is he.'),
'lexis.selectional_restriction': ('A literal account; this is an ordinary dry stone, not a personified character or a porous absorbent object.', 'The child drank the juice.', 'The stone drank the juice.'),
'lexis.false_friend': ('Literal contemporary standard English: sunlight makes the skin hurt, so the intended property is sensitive, not reasonable or judicious. The generated lexical substitution is a known false-friend pattern; no real speaker L1 is inferred.', 'Sunlight makes my skin hurt. My skin is very sensitive to sunlight.', 'Sunlight makes my skin hurt. My skin is very sensible to sunlight.'),
'discourse.coherence': ('Exactly one event, one simultaneous location and no correction: the speaker asserts both claims as true.', 'At exactly noon, the only key was in Box A and was not in Box B.', 'At exactly noon, the only key was in Box A and was not in Box A.'),
'pronunciation.segmental.consonant_place_manner': ('An explicit target requires alveolar lateral [l] at the onset of leaf.', 'leaf with initial [l]', 'leaf with initial velar stop [k]'),
'pronunciation.segmental.consonant_insertion': ('Across is intended; the authored contrast adds one final /t/ after /s/.', 'across: [əˈkɹɒs]', 'across: [əˈkɹɒst]'),
'pronunciation.segmental.vowel_length': ('Controlled matched-rate target: hold /iː/ in sheep for 200–300 ms; no general lexical-duration norm is claimed.', 'sheep with /iː/ held for 250 ms', 'sheep with /iː/ held for 50 ms'),
'pronunciation.segmental.vowel_reduction': ('An explicit neutral unstressed schwa target for the initial syllable of about.', 'about with initial [ə]', 'about with stressed initial [eɪ]'),
'pronunciation.segmental.diphthong_realization': ('An explicit GOAT /əʊ/ target in boat; BED vowel /ɛ/ changes the intended lexical vowel.', 'boat with target /bəʊt/', 'boat realized /bɛt/'),
'pronunciation.suprasegmental.lexical_stress': ('The noun record refers to a stored document, under the stated noun-stress target.', 'a REcord of the meeting', 'a reCORD of the meeting'),
'pronunciation.suprasegmental.compound_stress': ('A controlled compound/phrase listening task explicitly targets first-element prominence in BLACKbird.', 'BLACKbird under that named target', 'blackBIRD under that named target'),
'pronunciation.suprasegmental.sentence_stress_prominence': ('Who bought the car, John or Mary? John did; the task asks for contrasting those people.', 'JOHN bought the car, with John as the sole nuclear focus', 'John bought the CAR, with car as the sole nuclear focus'),
'pronunciation.suprasegmental.rhythm': ('A controlled rhythm contrast explicitly requires a selected weak syllable interval of 100–150 ms, all other words unchanged.', 'The selected interval is 120 ms', 'The selected interval is 300 ms'),
'pronunciation.suprasegmental.intonation_contour': ('A controlled fall exercise explicitly asks for a final descending contour.', 'A measured final fall from 160 Hz to 110 Hz', 'A measured final rise from 110 Hz to 160 Hz'),
'pronunciation.suprasegmental.intonation_function': ('A listening contrast distinguishes a neutral assertion from a confirmation request; the stipulated interpretation, not punctuation, supplies the observation.', 'You have insurance, heard as the intended neutral assertion', 'You have insurance, heard as a confirmation request instead of the intended assertion'),
'pronunciation.suprasegmental.weak_form': ('A named neutral weak-form drill explicitly targets /tə/ in to be; strong forms remain correct in other tasks.', 'to be with unstressed /tə/', 'to be with strongly stressed /tuː/'),
'pronunciation.suprasegmental.linking_resyllabification': ('The stated phrase is an ice pack; the stipulated heard phrase supplies the lexical boundary contrast.', 'The phrase is heard as an ice pack', 'The phrase is heard as a nice pack'),
'pronunciation.suprasegmental.assimilation': ('Would you under an explicit voiced coalescent /dʒ/ versus voiceless /tʃ/ contrast target.', 'would you with /wʊdʒə/', 'would you with /wʊtʃə/'),
'pronunciation.suprasegmental.elision_reduction': ('The dialogue says several documents, not one document; preserve the plural evidence.', 'documents with the plural /s/ retained', 'documents reduced to singular document with no recoverable plural evidence'),
'pronunciation.suprasegmental.thought_group_chunking': ('An invitation to Grandma; the stipulated listening interpretation is part of this symbolic fixture.', 'Lets eat Grandma, heard as an invitation addressed to Grandma', 'Lets eat Grandma, heard as a proposal to eat Grandma'),
'pronunciation.suprasegmental.pitch_range': ('A controlled exercise specifies a pitch range of 4–8 semitones; no universal human norm is claimed.', 'Measured range is 6 semitones', 'Measured range is 1 semitone'),
'fluency.disfluency_density': ('A task explicitly permits at most 2 filler events per 100 spoken words; the count includes each event once.', '1 filler event in 100 words', '8 filler events in 100 words'),
'fluency.excessive_pausing': ('A controlled demonstration explicitly permits at most 1.5 seconds of internal silence in this phrase; these are stipulated timings, not an observation of our recording.', 'An internal pause of 0.5 seconds between two permitted phrase groups', 'An unplanned internal pause of 4 seconds inside the phrase'),
'fluency.pause_location': ('The lexical word teacher must remain uninterrupted; pauses outside that word are permitted.', 'teacher with no pause inside the word', 'teacher with a 2-second silence between tea and cher'),
'fluency.hesitation_fillers': ('An emergency instruction must tell the listener immediately to pull the red lever; no other action can resolve the emergency.', 'Pull the red lever now.', 'Um, the, um, you know, thing, um...'),
'fluency.false_start': ('The speaker must complete the fixed instruction Press the red button; the turn ends here with no completion.', 'Press the red button.', 'Pre- I wa- where...'),
'fluency.repetition': ('The user explicitly selected a repetition-free delivery drill for this fixed request, excluding unintentional restarts. This local drill does not define correctness in ordinary conversation.', 'I need the form.', 'I I I need the the form.'),
'fluency.breakdown_abandonment': ('A courier asks for the full address, 12 Oak Road; the reply ends without supplying it.', 'The address is 12 Oak Road.', 'The address is... never mind.'),
'discourse.topic_management': ('A route-giving task asks How do I get to the hospital? It requires a route answer with no unrelated digression.', 'Walk straight ahead to the hospital entrance.', 'My football team won three matches last week.'),
'discourse.turn_taking': ('A safety instruction must remain fully audible; this is a stipulated interaction contrast, not an observation of a generated recording.', 'Speaker B waits until the complete safety instruction is audible.', 'Speaker B overlaps Speaker A and completely masks the critical words do not touch.'),
'discourse.clarification_repair': ('Which John do you mean, John Smith or John Brown? The reply must identify one of them.', 'John Smith, not John Brown.', 'He is the one I mean.'),
'discourse.cohesion_reference': ('John and Paul are both present. The listener asks which man put the key on the table.', 'John put the key on the table.', 'He put the key on the table.'),
'discourse.response_relevance': ('The listener asks what time the shop closes.', 'It closes at six.', 'It is a nice shop.'),
'pragmatics_register.formality': ('A stated ceremonial task explicitly requires a formal request to pass the document, excluding casual forms of address.', 'Would you please pass the document?', 'Hey mate, give us that thing.'),
'pragmatics_register.sociolinguistic_appropriacy': ('The addressee explicitly states Please address me as Dr Smith, not Mr Smith.', 'Hello, Dr Smith.', 'Hello, Mr Smith.'),
'pragmatics_register.audience_context_fit': ('A beginner explicitly says I do not know what actuator means; the instruction must say which button to push without unexplained jargon.', 'Push the red button.', 'Depress the red actuator.'),
'pragmatics_register.pragmatic_force': ('The reply must be a firm promise to finish today, not a prediction or a statement of uncertain ability.', 'I promise I will finish it today.', 'I might perhaps finish it today.'),
'discourse.information_structure': ('Which car is selected, the red car or the blue car? This answer must identify one of those two.', 'I choose the blue car.', 'I choose the car.'),
'acceptable_variant.grammar_variant': ('American English permits the simple past with yet in this ordinary question.', 'Did you eat yet?', 'Did you eat yet?'),
'acceptable_variant.lexical_variant': ('Both ordinary collocations preserve the intended research activity.', 'We do research.', 'We conduct research.'),
'acceptable_variant.pronunciation_variant': ('The task explicitly permits both dictionary pronunciations of either.', 'either with /ˈiːðə/', 'either with /ˈaɪðə/'),
'acceptable_variant.dialect_variant': ('The task permits British English collective agreement for members acting separately.', 'The team are putting on their shirts.', 'The team are putting on their shirts.'),
'acceptable_variant.register_variant': ('Casual speech permits the ordinary reduction wanna.', 'I want to go.', 'I wanna go.'),
'acceptable_variant.informal_acceptable': ('A casual invitation with recoverable subject and auxiliary.', 'Do you want some tea?', 'Want some tea?'),
'acceptable_variant.stylistic_preference': ('Both ways of expressing the ordinary request for the addressee are acceptable.', 'To whom did you speak?', 'Who did you speak to?'),
'acceptable_variant.alternative_standard': ('The speaker emphatically denies not attending.', 'I went to the meeting.', 'I did go to the meeting.'),
}


def curated():
    tax = load_taxonomy()
    original = {x['id']: x for x in tax['items']}
    recipes = {x['taxonomy_id']: x for x in json.loads((V/'domain/mutation-recipes.v1.json').read_text())['recipes']}
    rows = []
    for group, table in GROUPS.items():
        for line in table.strip().splitlines():
            suffix, subtypes, context, text, reason = line.split('|')
            tid = group + '.' + suffix
            leaf, recipe = original[tid], recipes[tid]
            ctx, canonical, surface = REPAIRS.get(tid, (recipe['context'], recipe['canonical_example'], recipe['surface_example']))
            source = ('R-CONNECTED' if 'assimilation' in tid or 'linking' in tid or 'elision' in tid else
                      'R-INTONATION' if 'intonation' in tid else
                      'R-PHONOLOGY' if tid.startswith(('pronunciation', 'fluency')) else
                      'R-COLLOCATION' if tid.startswith('lexis') else
                      'R-VARIETIES' if tid.startswith('acceptable_variant') else 'R-GRAMMAR')
            rows.append(dict(taxonomy_id=tid,subtypes=subtypes.split(';'),
                contrast_context=ctx, canonical=canonical, surface=surface,
                surface_status='acceptable' if group=='acceptable_variant' else 'true_error',
                correct_control=dict(context=context,text=text,reason=reason),
                reference_groups=[source],
                modality='stipulated_interaction' if tid=='discourse.turn_taking' else 'stipulated_phonetic_or_timing_description' if tid.startswith(('pronunciation','fluency.speech_rate','fluency.excessive_pausing','fluency.pause_location','fluency.disfluency_density')) else 'written_contextual_language',
                origin='constructed_author_reference_not_corpus_or_observed_audio'))
    assert len(rows)==122 and {x['taxonomy_id'] for x in rows}==set(original)
    return rows


def main():
    rows=curated()
    out=dict(version='1.0.0', scope='finite_122_leaf_specification_contrasts_not_all_English',
        references='docs/linguistic-coverage-and-variants.md', examples=rows)
    (V/'domain/linguistic-contrast-set.v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(categories=len(rows),subtype_mappings=sum(len(x['subtypes']) for x in rows))))


if __name__=='__main__':
    main()
