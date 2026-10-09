"""Read-only native data audit and authored specification catalogue builder.

Not an application importer, generator, acoustic recognizer or answer evaluator.
No imported code is executed; corpus excerpts are not redistributed here.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
YAML = '/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml'


def yaml_read(path):
    out = subprocess.check_output([
        'node', '-e', 'const fs=require("fs"),y=require(process.argv[1]);process.stdout.write(JSON.stringify(y.parse(fs.readFileSync(process.argv[2],"utf8"))));',
        YAML, str(ROOT / path)], text=True)
    return json.loads(out)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def replacement(canonical, surface):
    start = 0
    while start < min(len(canonical), len(surface)) and canonical[start] == surface[start]:
        start += 1
    tail = 0
    while (tail < len(canonical) - start and tail < len(surface) - start
           and canonical[len(canonical)-1-tail] == surface[len(surface)-1-tail]):
        tail += 1
    ce, se = len(canonical) - tail, len(surface) - tail
    return {'start_cp': start, 'end_cp': ce, 'exact_text': canonical[start:ce],
            'replacement': surface[start:se], 'surface_start_cp': start,
            'surface_end_cp': se, 'kind': 'insert' if ce == start else 'delete' if se == start else 'replace'}


def m2_observation(text):
    """Selected annotator is a reproducible descriptive view, not fused gold."""
    all_tags, selected, presence, pairs, annotators = Counter(), Counter(), Counter(), Counter(), Counter()
    windows = tokens = eligible_events = noops = unresolved = 0
    example_counts = Counter()
    for block in text.strip().split('\n\n'):
        lines = block.splitlines()
        if not lines:
            continue
        assert lines[0].startswith('S ')
        windows += 1
        native = lines[0][2:]
        tokens += len(native.split())
        by_annotator = {}
        for line in lines[1:]:
            assert line.startswith('A ')
            f = line[2:].split('|||')
            assert len(f) == 6
            a, b = map(int, f[0].split())
            tag, correction, annotator = f[1], f[2], int(f[5])
            assert (a, b) == (-1, -1) or 0 <= a <= b <= len(native.split())
            all_tags[tag] += 1
            by_annotator.setdefault(annotator, []).append((tag, a, b, correction))
        if not by_annotator:
            # In M2, a no-A block can mean no change; keep this separately.
            annotators['no_annotation_lines'] += 1
            continue
        chosen = min(by_annotator)
        annotators[str(chosen)] += 1
        local = []
        for tag, a, b, correction in by_annotator[chosen]:
            selected[tag] += 1
            if tag == 'noop':
                assert (a, b) == (-1, -1)
                noops += 1
                continue
            if tag.split(':', 1)[-1] in {'UNK', 'Um'} or tag in {'UNK', 'Um'}:
                unresolved += 1
                continue
            assert (a, b) != (-1, -1)
            local.append(tag)
            eligible_events += 1
            # Count a usable native span/correction, not a taxonomy mapping.
            if correction != '-NONE-':
                example_counts[tag] += 1
        for tag in set(local):
            presence[tag] += 1
        for pair in combinations(sorted(set(local)), 2):
            pairs[' | '.join(pair)] += 1
    stats = []
    for tag, count in sorted(selected.items()):
        uncertain = tag in {'noop', 'UNK', 'Um'} or tag.split(':', 1)[-1] in {'UNK', 'Um'}
        stats.append({'native_tag': tag, 'selected_annotation_count': count,
                      'eligible_corrected_edit_count': 0 if uncertain else count,
                      'window_presence_count': presence[tag],
                      'event_share': None if uncertain or eligible_events == 0 else {'numerator': count, 'denominator': eligible_events},
                      'window_prevalence': None if uncertain else {'numerator': presence[tag], 'denominator': windows},
                      'density_per_1000_native_tokens': None if uncertain or tokens == 0 else {'numerator': 1000*count, 'denominator': tokens},
                      'error_opportunity_rate': None,
                      'opportunity_rate_missing_reason': 'correct_opportunities_not_enumerated',
                      'native_localized_correction_records': example_counts[tag]})
    return {'windows': windows, 'native_tokens': tokens, 'all_annotator_tag_counts': dict(sorted(all_tags.items())),
            'selected_annotator_windows': dict(sorted(annotators.items())), 'selected_tag_counts': dict(sorted(selected.items())),
            'eligible_corrected_edit_count': eligible_events, 'selected_noop_annotations': noops,
            'selected_unresolved_annotations': unresolved, 'statistics': stats,
            'distinct_tag_pair_window_counts': dict(sorted(pairs.items()))}


# Concrete supplemental context repairs preserve every original example.
CONTEXT_PAIRS = {
    'pronunciation.segmental.consonant_insertion': ('Across is intended; the authored contrast adds one final /t/ after /s/.', 'across: [əˈkɹɒs]', 'across: [əˈkɹɒst]'),
    'grammar.verbs.auxiliary': ('A completed simple-past departure, without a progressive meaning.', 'They went home.', 'They were went home.'),
    'discourse.cohesion_reference': ('John and Paul are both present. The listener asks which man put the key on the table.', 'John put the key on the table.', 'He put the key on the table.'),
    'discourse.topic_management': ('The listener requests the route to the hospital; no topic transition is invited.', 'Walk along King Street to the hospital.', 'My football team won yesterday.'),
    'discourse.turn_taking': ('A must finish a safety instruction before B asks an unrelated question. The surface interrupts before the warning is completed.', 'A: Disconnect the power before touching the wire. B: What colour is the box?', 'A: Disconnect the power before— B: What colour is the box?'),
    'discourse.response_relevance': ('The listener asks what time the shop closes.', 'It closes at six.', 'It is a nice shop.'),
    'discourse.information_structure': ('Two routes, the north route and south route, are named. The listener asks which one to take; there is no gesture or other cue.', 'Take the north route.', 'Take that one.'),
    'discourse.clarification_repair': ('Listener: Do you mean John Smith or John Brown?', 'John Smith, not John Brown.', 'I mean him.'),
    'pragmatics_register.sociolinguistic_appropriacy': ('Dr Lee has explicitly requested the address Dr Lee rather than mate, in this meeting.', 'Good morning, Dr Lee.', 'Good morning, mate.'),
    'pragmatics_register.audience_context_fit': ('A beginner unfamiliar with geometry asks how to turn a physical handle to the right.', 'Turn the handle to the right.', 'Rotate the actuator clockwise about its longitudinal axis.'),
    'acceptable_variant.dialect_variant': ('The task explicitly permits ordinary British and American standard vocabulary for the same lift/elevator.', 'Take the lift to the second floor.', 'Take the elevator to the second floor.'),
    'acceptable_variant.stylistic_preference': ('Both statements correctly say where the speaker lives; no particular style is requested.', 'I live here.', 'This is where I live.'),
    'acceptable_variant.grammar_variant': ('A recent-meal question in a context permitting the ordinary present-perfect and American simple-past variants.', 'Have you eaten yet?', 'Did you eat yet?'),
    'acceptable_variant.lexical_variant': ('Both verbs describe carrying out research in this task.', 'We do research.', 'We conduct research.'),
    'acceptable_variant.pronunciation_variant': ('Either option is fine; the task permits both /ˈiːðə/ and /ˈaɪðə/ for either. Only the IPA operation changes, not these words.', 'Either option is fine.', 'Either option is fine.'),
    'acceptable_variant.register_variant': ('Casual conversation explicitly permits wanna as a spoken want to contraction.', 'I want to go.', 'I wanna go.'),
    'acceptable_variant.informal_acceptable': ('A casual offer of food permits an elliptical short question.', 'Do you want some?', 'Want some?'),
    'acceptable_variant.alternative_standard': ('The speaker correctly asserts a past visit; emphasis is permitted.', 'I went.', 'I did go.'),
}

# Leaf-specific instructions; parameter requests are never claimed as observations.
ACOUSTIC = {
    'consonant_substitution': ('phoneme', 'Keep the word three; request /s/ instead of the declared /θ/ in the word-level IPA. Preserve the rest of the phones.', 'Aligned evidence distinguishing the requested initial consonant from the target; intelligibility or explicit target-form context.'),
    'consonant_omission': ('phoneme', 'Keep coat; omit its target final /t/ from the intended IPA.', 'Final interval and audible final-segment contrast, with permitted unreleased/allophonic realizations considered.'),
    'consonant_insertion': ('phoneme', 'Keep across; append /t/ after final /s/ in the authored single-insertion contrast. The original /sts/ illustration remains preserved but is not represented as a one-phone edit.', 'An extra audible consonant in the aligned final cluster, not just a transcript spelling difference.'),
    'consonant_voicing': ('phoneme', 'Keep pair; replace initial /p/ by /b/ for the chosen variety.', 'Actual initial phone/contrast evidence distinguishing pair from bear.'),
    'consonant_devoicing': ('phoneme', 'Keep bag; request final /k/ instead of /g/ as the wrong lexical contrast.', 'Acoustic/perceptual contrast for bag/back including vowel and closure cues; zero voicing alone is insufficient.'),
    'consonant_cluster_simplification': ('phoneme', 'Keep asked in an explicit completed-past context; omit the segment that distinguishes it from ask in intended IPA.', 'Final cluster/past-form contrast; do not flag an allowed connected-speech reduction without loss of the declared contrast.'),
    'consonant_aspiration': ('recorded_contrast', 'Use the matched pin/bin target. IPA p is not an aspiration-duration control; require a recording whose initial release/voicing cues realize the wrong contrast.', 'Aligned initial release/voicing evidence and context-supported interpretation; per-item reference, no universal VOT threshold.'),
    'consonant_place_manner': ('recorded_contrast', 'Declare the target /l/, chosen variety, word and precise incompatible articulation before selecting a source/local recording.', 'Localized actual articulation/phone evidence; label-only /l/ mismatch is not sufficient.'),
    'vowel_substitution': ('phoneme', 'Keep ship; request the vowel /iː/ rather than target /ɪ/ for the chosen contrast.', 'Aligned vowel/lexical contrast for ship/sheep under the permitted variety.'),
    'vowel_length': ('recorded_contrast', 'Use a matched vowel contrast; preserve the declared quality and context, specify reference duration bounds per item. A prosody rate request alone is not vowel duration.', 'Aligned vowel duration in milliseconds plus quality/contrast evidence. No universal long/short cutoff.'),
    'vowel_reduction': ('phoneme', 'Name the unstressed syllable and permitted weak realization; request its corresponding full vowel in intended IPA only for an explicit reduction practice item.', 'Unstressed-syllable vowel evidence against the declared target; an allowed accent is not an error.'),
    'diphthong_realization': ('phoneme', 'Name the face/goat word and canonical trajectory; request a different lexical vowel using supported IPA. A missing trajectory needs actual recording evidence.', 'Aligned vowel identity/trajectory and contextual lexical contrast, with permitted variety realizations retained.'),
    'vowel_insertion_epenthesis': ('phoneme', 'Keep school; request /ɪ/ before /s/ as in the authored contrast.', 'An extra audible vowel/syllable in the aligned word, not a respelled script.'),
    'final_segment_realization': ('phoneme', 'Keep plural cats; omit /s/ from intended IPA in a context requiring plural cats versus singular cat.', 'Recoverability of the actual plural contrast. If it is the same repair obligation as noun number, retain one event with alternative labels.'),
    'lexical_stress': ('phoneme', 'Declare noun record; put the stress marker on the second syllable in intended IPA while keeping text unchanged.', 'Actual syllable prominence/duration/F0 or audio-capable interpretation of the noun/verb contrast.'),
    'compound_stress': ('prosody', 'Declare the species blackbird; scope prominence requests over black and bird to favour the two-word colour-plus-bird reading.', 'Actual prominence and context-supported interpretation; volume/pitch requests alone do not prove compound stress.'),
    'sentence_stress_prominence': ('prosody', 'Context corrects WHO bought the car. Request prominence on car while holding the answer JOHN constant in the words.', 'Actual prominence placement plus the declared information-focus context.'),
    'rhythm': ('prosody', 'Freeze the reading, syllable intervals and per-item reference duration-ratio pattern; request a contrasting scoped rate pattern.', 'Measured syllable/interstress timing under the fixed reference. Accent resemblance is not a target.'),
    'intonation_contour': ('prosody', 'For a task explicitly requesting a fall, submit an increasing contour over the fixed phrase, with per-item positions and pitch values.', 'Final F0 contour over voiced frames under the defined interval; a question need not universally fall.'),
    'intonation_function': ('prosody', 'Use a neutral confirmation context; request a contrasting contour and let an audio-capable LLM judge whether it conveys sarcastic disbelief in context.', 'Modality-labelled contextual inference from actual audio. Historical illustration wording about two reviewers is not a human review prerequisite.'),
    'weak_form': ('phoneme', 'Keep unstressed to in an explicit weak-form practice context; submit the strong /tuː/ instead of the declared weak form.', 'Actual target-word realization and absence of licensed contrastive emphasis.'),
    'linking_resyllabification': ('recorded_contrast', 'Freeze an ice versus a nice context. Select/render separate boundaries only where supported; use an actual recording for the specified wrong boundary cues.', 'Actual segmentation/boundary cues with context; text spacing alone is not the listening contrast.'),
    'assimilation': ('recorded_contrast', 'Specify adjacent words, target boundary phones, permitted assimilation and the contrast being obscured. Use an actually annotated/machine-labelled recording.', 'Actual boundary-phone evidence and lost declared contrast. Ordinary permitted assimilation is a control.'),
    'elision_reduction': ('phoneme', 'Name the tested lexical/grammatical distinction and remove its intended phone in supported IPA without changing the transcript.', 'Actual retained/lost contrast under the permitted variety and speaking context.'),
    'thought_group_chunking': ('pause', 'Keep Let\'s eat, Grandma; place the intended pause before eat rather than at the vocative boundary, preserving exact word order.', 'Measured pause/boundary intervals and context-supported invitation versus object interpretation.'),
    'pitch_range': ('prosody', 'Freeze phrase, reference voiced frames and the per-item semitone interval. Request a wider/narrower contour outside that task interval.', 'Actual final F0 range in semitones under docs/audio-methods.md. Requested pitch offset alone is not pitch range.'),
    'speech_rate': ('prosody', 'For the existing 140 WPM +/-10% task, request a faster rate then measure the fixed spoken-token denominator. Correct range is 126–154 WPM; the illustration requests approximately 200.', 'Actual WPM on the defined final interval. Rate-percent to WPM is not exact without observation.'),
    'excessive_pausing': ('pause', 'Insert an explicit 4000 ms internal pause where the task maximum is 1500 ms; preserve the phrase and intended silence.', 'Actual sample-clock duration/location; other naturally permitted pauses are not errors.'),
    'pause_location': ('pause', 'Split teacher into the explicit planned word pieces with a 2000 ms pause between them, rather than at a permitted word boundary.', 'Actual internal-word discontinuity and duration; synthesis of two fragments may alter phones and needs machine review.'),
    'hesitation_fillers': ('text', 'In a concise emergency instruction context, insert explicit uh/um fillers around the critical instruction; retain all intended words.', 'Audible fillers and context-supported obstruction of the instruction. Ordinary conversational fillers are permitted.'),
    'repetition': ('text', 'Change I need the form to I I I need the the form, with no rhetorical repetition context.', 'Actual repeat locations and distinct event obligations; labels for the same repeat are not extra events.'),
    'false_start': ('text', 'Before the required complete instruction, introduce explicit abandoned fragments I wa- I nee- where... in surface text; preserve fragment/continuation identity.', 'Actual delivered fragments and completion state. Provider reading punctuation does not automatically realize a truncation.'),
    'self_repair': ('text', 'Replace an unambiguous direction with Go left, no right, or left, I don\'t know in the stated route context.', 'Actual unresolved conflicting direction; a successful ordinary self-correction is a control.'),
    'breakdown_abandonment': ('text', 'Replace the required complete address instruction with The address is... never mind, where the address has not been otherwise supplied.', 'Audible abandonment and missing communicative requirement, with the full context retained.'),
    'disfluency_density': ('text', 'Fix the spoken-word denominator, event definitions and per-item density bound. Insert explicitly enumerated fillers/repeats/false starts until the intended count exceeds that bound.', 'Actual event count and actual spoken-token denominator. Do not count one event in several disfluency categories twice.'),
}


def recipe(item):
    key = item['id']
    mode = item['realization_mode']
    e = item['example']
    context, canonical, surface = CONTEXT_PAIRS.get(key, (e['context'], e['accepted_repair'], e['illustrative_target']))
    if mode in {'acoustic_segmental', 'acoustic_suprasegmental', 'temporal_fluency'}:
        operator, procedure, evidence = ACOUSTIC[key.rsplit('.', 1)[-1]]
        edit = None
    else:
        operator = 'control_variant' if mode == 'decoy' else 'contextual_text' if mode in {'discourse_context', 'pragmatic_context'} else 'text'
        procedure = ('Retain a declared permitted realization or substitute the permitted alternative. Keep expected_judgment acceptable and do not request a repair.' if mode == 'decoy' else
                     'Establish the stated canonical/contextual meaning, then apply the recorded codepoint replacement to obtain the stated target. For novel words or turns, use the leaf definition/inclusion/exclusion and preserve this independent repair obligation.')
        evidence = 'Actual rendered wording plus all decisive context and machine-labelled key. Native written labels remain written evidence until final audio exists.'
        edit = replacement(canonical, surface) if mode != 'decoy' or key in CONTEXT_PAIRS else None
    sources = {
        'grammar': ['WILOCNESS-2.1', 'FCE-2.1', 'JFLEG', 'ICNALE', 'EFCAMDAT-R2', 'EFCAMDAT-SHATZ2020', 'EFCAMDAT-OKSUZ2025'],
        'lexis': ['WILOCNESS-2.1', 'FCE-2.1', 'JFLEG', 'ICNALE', 'EFCAMDAT-R2'],
        'pronunciation.segmental': ['L2-ARCTIC', 'SPEECHOCEAN762'],
        'pronunciation.suprasegmental': ['SPEECHOCEAN762', 'L2-ARCTIC', 'EdAcc', 'DRAL', 'ELRD', 'ICNALE'],
        'fluency': ['SPEECHOCEAN762', 'L2-ARCTIC', 'EdAcc', 'DRAL', 'ELRD', 'ICNALE', 'SpeakImprove2025'],
        'discourse': ['ELRD', 'DRAL', 'DiPlomat', 'ICNALE', 'DOUBAO-STUDY-RECORDS'],
        'pragmatics_register': ['DiPlomat', 'ELRD', 'DRAL', 'ICNALE', 'DOUBAO-STUDY-RECORDS'],
        'acceptable_variant': ['WILOCNESS-2.1', 'JFLEG', 'L2-ARCTIC', 'EdAcc', 'DRAL', 'ICNALE'],
    }[item['reporting_domain']]
    return {'taxonomy_id': key, 'reporting_domain': item['reporting_domain'], 'realization_mode': mode,
            'operator': operator, 'procedure': procedure, 'context': context,
            'canonical_example': canonical, 'surface_example': surface, 'codepoint_edit': edit,
            'original_example_preserved_at': 'error-taxonomy.v1.yaml#' + key,
            'example_origin': 'authored_design_illustration_not_external_corpus_or_observed_audio',
            'example_override_reason': 'clarify_canonical_context_or_make_abstract_example_concrete' if key in CONTEXT_PAIRS else None,
            'required_inputs': ['leaf_inclusion_exclusion', 'variety_and_task_context', 'canonical_and_surface_or_acoustic_target', 'localized_utterance_unit_and_edit_scope', 'accepted_repairs_and_required_forbidden_propositions'],
            'required_final_evidence': evidence, 'candidate_sources': sources,
            'candidate_source_claim': 'potential_material_only; no inferred per-leaf coverage',
            'source_mapping_count': None, 'source_mapping_missing_reason': 'localized_122_leaf_crosswalk_not_observed',
            'empirical_leaf_frequency': None, 'frequency_missing_reason': 'no_inspected_project_leaf_population',
            'actual_generated_audio_observed': False, 'recipe_status': 'specified_not_provider_verified',
            'benchmark_target': {'stimuli': 6, 'split_control_counting': 'docs/review-and-gold.md'}}


def main():
    taxonomy = yaml_read('specification/v2/domain/error-taxonomy.v1.yaml')
    items = taxonomy['items']
    recipes = [recipe(i) for i in items]
    ids = [i['id'] for i in items]
    edges = []
    for identifier in ids:
        pieces = identifier.split('.')
        for length in range(1, len(pieces)):
            edge = {'parent': '.'.join(pieces[:length]), 'child': '.'.join(pieces[:length+1]), 'meaning': 'structural_parent_not_empirical_cause'}
            if edge not in edges:
                edges.append(edge)
    overlaps = [
        ('grammar.verbs.irregular_form', 'grammar.verbs.tense'),
        ('grammar.verbs.participle', 'grammar.verbs.passive'),
        ('grammar.verbs.auxiliary', 'grammar.verbs.aspect'),
        ('grammar.verbs.subject_verb_agreement', 'grammar.nouns.number'),
        ('grammar.nouns.number', 'pronunciation.segmental.final_segment_realization'),
        ('grammar.morphology.derivation', 'lexis.word_formation'),
        ('grammar.morphology.word_class_form', 'lexis.lexical_choice'),
        ('lexis.collocation', 'lexis.selectional_restriction'),
        ('lexis.lexical_register', 'pragmatics_register.formality'),
        ('pronunciation.segmental.consonant_omission', 'pronunciation.segmental.final_segment_realization'),
        ('pronunciation.segmental.consonant_omission', 'pronunciation.segmental.consonant_cluster_simplification'),
        ('pronunciation.segmental.vowel_reduction', 'pronunciation.suprasegmental.weak_form'),
        ('pronunciation.suprasegmental.sentence_stress_prominence', 'discourse.information_structure'),
        ('pronunciation.suprasegmental.thought_group_chunking', 'fluency.pause_location'),
        ('fluency.repetition', 'fluency.disfluency_density'),
        ('discourse.response_relevance', 'discourse.topic_management'),
        ('pragmatics_register.politeness', 'pragmatics_register.directness'),
    ]
    catalogue = {'version': '1.0.0', 'authority': 'docs/mistake-data-and-mutations.md',
                 'scope': 'all_122_project_leaves_not_all_possible_English_errors',
                 'observed_source_coverage_claimed': False, 'recipes': recipes,
                 'hierarchy_edges': edges,
                 'candidate_analysis_relationships': [{'a': a, 'b': b, 'meaning': 'possible_alternative_or_related_analysis; use independent_repair_test', 'empirical_frequency': None} for a, b in overlaps],
                 'empirical_leaf_cooccurrence': None, 'observed_mapper_confusion': None,
                 'relationships_missing_reason': 'localized_project_events_and_evaluation_decisions_not_observed'}
    write(ROOT / 'specification/v2/domain/mutation-recipes.v1.json', catalogue)
    matrix = []
    for item, r in zip(items, recipes):
        matrix.append({'taxonomy_id': item['id'], 'domain': item['reporting_domain'],
                       'definition': item['definition'], 'inclusion_criteria': item['inclusion_criteria'],
                       'exclusion_criteria': item['exclusion_criteria'], 'original_example': item['example'],
                       'recipe': r, 'native_source_examples_mapped_to_leaf': None,
                       'leaf_frequency': None, 'observed_benchmark_stimuli_in_this_audit': 0,
                       'data_needed': ['localized_context_supported_source_mapping', 'actual_error_and_control_stimuli_with_split_identity', 'declared_frequency_population_and_counts'] +
                           (['actual_final_acoustic_contrast_and_alignment'] if item['realization_mode'].startswith('acoustic') or item['realization_mode'] == 'temporal_fluency' else [])})
    write(AUDIT / 'all-122-leaf-coverage.json', matrix)
    domains = Counter(i['reporting_domain'] for i in items)
    md = ['# Every project leaf: authored recipe and unmeasured data', '',
          'All entries have definitions and authored examples. Candidate sources do not establish localized leaf coverage. Every source-mapping count and empirical leaf frequency remains unknown, not zero. No benchmark audio was created in this audit. See all-122-leaf-coverage.json for exact definitions, inclusion/exclusion, original examples, and required data.', '',
          '| Exact leaf | Operation | Authored canonical → intended target | Data status |',
          '|---|---|---|---|']
    for r in recipes:
        def esc(s):
            return str(s).replace('|', '\\|').replace('\n', ' ')
        md.append(f"| {r['taxonomy_id']} | {r['operator']} | {esc(r['canonical_example'])} → {esc(r['surface_example'])} | native crosswalk/frequency unmeasured; final audio unverified |")
    (AUDIT / 'ALL-122-LEAVES.md').write_text('\n'.join(md) + '\n')
    observation = {'granularity': 'native_M2_tags_not_122_project_leaves',
                   'method': 'docs/mistake-data-and-mutations.md#frequency-population-and-arithmetic',
                   'source_annotation_preserved': True, 'project_leaf_frequency': None,
                   'opportunity_rates_available': False, 'views': [],
                   'withheld_label_views': [{'source': 'WILOCNESS-2.1', 'partition': 'test', 'windows': 4477, 'error_frequency': None, 'reason': 'public_correction_labels_not_supplied'}]}
    for source, path, prefix in [
        ('WILOCNESS-2.1', 'data/corpora/bea/wi+locness_v2.1.bea19.tar.gz', 'wi+locness/m2/'),
        ('FCE-2.1', 'data/corpora/bea/fce_v2.1.bea19.tar.gz', 'fce/m2/')]:
        with tarfile.open(ROOT / path) as archive:
            for member in sorted(archive.getmembers(), key=lambda m: m.name):
                if member.name.startswith(prefix) and member.name.endswith('.m2'):
                    raw = archive.extractfile(member).read()
                    d = m2_observation(raw.decode('utf-8'))
                    d.update(source=source, archive=path, member=member.name, native_member_sha256=hashlib.sha256(raw).hexdigest(),
                             representation='aggregate_overlaps_components' if '/ABC' in member.name else 'component',
                             count_meaning='native_corrected_edit_annotations_not_project_communicative_events')
                    observation['views'].append(d)
    write(AUDIT / 'bea-native-frequencies-and-cooccurrence.json', observation)
    summary = {'taxonomy_leaves': len(items), 'true_error_leaves': len(items)-domains['acceptable_variant'],
               'control_leaves': domains['acceptable_variant'], 'domain_counts': dict(domains),
               'recipes': len(recipes), 'hierarchy_edges': len(edges), 'candidate_relationships': len(overlaps),
               'all_122_empirical_frequencies': 'not_observed', 'all_122_localized_source_crosswalk': 'not_observed',
               'actual_generated_audio_or_llm_calls_in_audit': 0,
               'native_m2_views_inspected': len(observation['views']),
               'authored_example_context_overrides': list(CONTEXT_PAIRS),
               'proof_boundary': 'full finite taxonomy/static recipe inventory and native writing statistics; no application or empirical all-leaf acceptance'}
    write(AUDIT / 'summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
