# Mistake data and mutations

## ADDED Requirements

### Requirement: MDC-01 Every finite taxonomy leaf has a data and recipe ledger

The system SHALL retain all122project leaves, their original definitions/examples and the exact authored recipe entries in specification/v2/domain/mutation-recipes.v1.json. It SHALL report actual localized source mappings, final stimuli, controls, split identities and missingness per leaf separately from written definitions. The finite project taxonomy SHALL NOT be represented as every possible English mistake or as empirically complete merely because its catalogue has122entries.

#### Scenario: MDC-01 Full finite catalogue with explicit missing data

- **GIVEN** every original leaf has an authored recipe but no observed project-leaf frequency population
- **WHEN** completeness is reported
- **THEN** all122IDs and their examples remain present and empirical frequencies remain null with a missing-data reason

#### Scenario: MDC-01 Authored examples cannot manufacture coverage

- **GIVEN** one authored pair and an acquired source with only broad native labels
- **WHEN** leaf-level source or benchmark coverage is requested
- **THEN** neither fills an unobserved localized source mapping or final-stimulus denominator

### Requirement: MDC-02 Relationship meanings and independent events remain separate

The system SHALL distinguish structural parent edges, alternative analyses of one event, measured co-occurrence and observed mapper confusion under specification/v2/docs/mistake-data-and-mutations.md. Secondary labels SHALL NOT multiply opportunities. Candidate analysis relationships SHALL retain nonempirical provenance; unknown co-occurrence/confusion SHALL remain unavailable.

#### Scenario: MDC-02 One event may have multiple analyses

- **GIVEN** a single lost plural contrast has noun-number and final-segment analyses
- **WHEN** the frozen contextual key describes one independent repair obligation
- **THEN** the alternative labels remain available and detection counts one event

#### Scenario: MDC-02 A hierarchy is not a measured causal graph

- **GIVEN** two taxonomy leaves share a parent and no observed event-pair population exists
- **WHEN** their relationship is reported
- **THEN** no co-occurrence frequency, mapper confusion or causal claim is invented

### Requirement: MDC-03 Frequencies name their actual population and denominator

The system SHALL use the descriptive arithmetic/population rules in specification/v2/docs/mistake-data-and-mutations.md. It SHALL retain native labels and annotators separately, avoid overlapping-view double counts, separate written/inferred/acoustic populations and distinguish event share, window prevalence, token density and opportunity rate. All42grading equations SHALL remain unchanged.

#### Scenario: MDC-03 Native frequency stays native

- **GIVEN** a fully inspected M2 partition with native correction tags and no122leaf contextual mapping
- **WHEN** its tag counts and sentence co-occurrences are reported
- **THEN** source/split/annotator/window, exact numerators and denominators remain explicit and project-leaf frequencies remain unmeasured

#### Scenario: MDC-03 Unknown opportunity or test labels stay unavailable

- **GIVEN** correct opportunities are not enumerated or public W&I test labels are withheld
- **WHEN** frequency is requested
- **THEN** opportunity rate or test error frequency remains unavailable rather than zero or an inferred global learner probability

### Requirement: MDC-04 Text mutation is an explicit contextual transformation

The generator SHALL use the selected leaf recipes in trusted instructions and record canonical/surface text, exact codepoint edit provenance and independent repair obligations through existing type=mutation evidence. It SHALL compose compatible edits against the same immutable canonical version and retain decisive context. Source-derived reverse corrections SHALL use one compatible native annotator view; acceptable controls SHALL remain nonerrors.

#### Scenario: MDC-04 Explicit edit and valid alternative repair

- **GIVEN** present-context canonical She works here and the corresponding subject-verb-agreement recipe
- **WHEN** surface She work here is generated
- **THEN** the saved transformation locates the changed verb, preserves outside text and supports context-valid alternative teacher repairs

#### Scenario: MDC-04 Stale or ambiguous edit does not invent a transformation

- **GIVEN** overlapping edits without an explicit composition or a native pair with ambiguous reconstruction
- **WHEN** an injectible mutation is requested
- **THEN** the original annotations remain retained and no arbitrarily reconstructed pair is represented as a verified mutation

### Requirement: MDC-05 Acoustic requests remain distinct from final realization

The generator SHALL preserve every acoustic/fluency leaf, use its exact declared contrast/scope and existing typed render operations, and retain actual final-audio evidence. A suitable annotated source/local recording SHALL remain supported through the separate import lifecycle. IPA, SSML, transcript-only DeepSeek inference or an accent label SHALL NOT by itself establish an observed phone, prosodic contrast or successful accent synthesis. Existing playable-audio warnings and hard-target failure semantics SHALL remain; no human review or full-provider qualification gate is added.

#### Scenario: MDC-05 Intended pause and actual measurement remain separate

- **GIVEN** a4000ms internal pause is requested for a task whose maximum internal pause is1500ms
- **WHEN** actual final audio is measured and machine checked
- **THEN** requested and observed duration/location remain distinct and the intended silence is retained in playback

#### Scenario: MDC-05 An unsupported acoustic claim stays unknown

- **GIVEN** only a phoneme request or text transcript exists and the configured checker cannot hear audio
- **WHEN** acoustic realization is assessed
- **THEN** no observed pronunciation is fabricated and uncertainty or an unsatisfied hard target remains explicit without deleting the category

### Requirement: MDC-06 Answer claims match contextual frozen events

The configured LLM SHALL interpret original answer spans against actual frozen case/audio/context/key events and their required/forbidden propositions. Semantic synonyms and valid novel repairs SHALL be supported. Duplicate claims, alternative labels, repeated words, contradictions, genuine key defects and provisional outcomes SHALL follow specification/v2/docs/math-and-judgments.md. Native code SHALL calculate all authoritative grades; no human peer review is required.

#### Scenario: MDC-06 Two phrasings can correct the same event

- **GIVEN** a present-context She work here event with a frozen works repair obligation
- **WHEN** the answer says The verb after she needs s or Change work to works in the first sentence
- **THEN** the LLM can recognize the same localized detection/repair under the existing semantic propositions

#### Scenario: MDC-06 One ambiguous repeated quote does not fan out

- **GIVEN** the same erroneous words occur in two turns and the answer does not identify either occurrence
- **WHEN** answer matching is performed
- **THEN** it does not arbitrarily select the first occurrence or credit both and uses the existing LLM reconsideration/provisional behavior

### Requirement: MDC-07 Every data source has a preserved use and limit

The system SHALL preserve all eleven complete original source identities and lossless native data, and keep supplements separate. The exact acquired/native/normalized/eligible/missing distinctions and data uses in specification/v2/docs/mistake-data-and-mutations.md and its acquisition audit SHALL remain explicit. Full source acquisition, original illustration examples and broad source scores SHALL NOT establish all-leaf listening gold, a trained accent model, actual teacher difficulty or executed provider behavior. Ordinary local use SHALL not wait for the complete source collection.

#### Scenario: MDC-07 Acquired supplemental corrections add useful alternatives

- **GIVEN** the complete JFLEG release has four repair references per sentence
- **WHEN** reference data are prepared for contextual answer checking
- **THEN** every alternative is retained under source terms as a reference and no original corpus is replaced

#### Scenario: MDC-07 Missing private sources and speech media remain missing

- **GIVEN** complete Cambridge/private originals or separately linked ICNALE audio/video have not been acquired
- **WHEN** dataset completeness is reported
- **THEN** the exact missing bytes/dictionaries/context/terms remain listed and texts, metadata or outreach are not represented as complete speech/data releases
