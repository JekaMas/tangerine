# Simple authored listening exercise flow

## ADDED Requirements

### Requirement: FLOW-01 Minimal request with optional level and broad categories

The system SHALL accept topic, speaker count and approximate word length through exercise-request.schema.json, with English level and broad mistake categories optional. It SHALL expand the request into the existing blueprint and retain advanced controls. No leaf-ID, corpus, reviewer or API configuration selection SHALL be required in the ordinary preparation form.

#### Scenario: FLOW-01 Three inputs suffice

- **GIVEN** a topic, two speakers and 150 words with no level/categories/source records
- **WHEN** Generate exercise is selected
- **THEN** the request expands to a two-role dialogue with automatic concrete mutation choices and no hidden CEFR constraint

#### Scenario: FLOW-01 Explicit user choices are preserved

- **GIVEN** a B2 request selecting grammar and lexis
- **WHEN** preparation expands defaults
- **THEN** the level/families remain saved and no prompt asks the user to choose every exact leaf or silently changes the speaker count

### Requirement: FLOW-02 Clean text precedes novel mutations and their key

The system SHALL save the canonical_text phase before the mutation phase, using generation-input.schema.json and the existing case_generation role. Mutation output SHALL retain that exact canonical script and produce surface text, typed edits and planned_units as the complete mutation list/key. Novel/OOD instances SHALL use the declared novelty basis without claiming access to the LLM's hidden training distribution.

#### Scenario: FLOW-02 Fixed canonical text receives localized novel edits

- **GIVEN** a saved clean dialogue and broad grammar family
- **WHEN** the mutation phase chooses context-supported concrete leaves
- **THEN** canonical text stays fixed, the changed script and complete mutation list/repairs are saved and recipe illustrations need not be copied

#### Scenario: FLOW-02 A mutation failure preserves the baseline

- **GIVEN** the clean text was saved but mutation output is incomplete or rewrites canonical text
- **WHEN** the phase fails its semantic projection
- **THEN** the clean text survives for retry and no successful key, OOD verification or corpus quotation is fabricated

### Requirement: FLOW-03 Local or service audio is generated and stored

The system SHALL synthesize the mutated render input through the selected local or external service adapter and store actual final audio with its text/key/version. Local Kokoro and the original Azure service/voices SHALL remain configured options. Replay SHALL use stored bytes. The app SHALL preserve deliberate text/acoustic operations and actual provider provenance without requiring native example audio or empirical calibration data before ordinary synthesis.

#### Scenario: FLOW-03 Local synthesis requires model assets rather than a speech key

- **GIVEN** the configured local model/voices are available and the request uses supported text/turn/pause operations
- **WHEN** the speech worker synthesizes the mutated turns
- **THEN** actual assembled audio is stored and replayed without a speech-service API key or new inference on each playback

#### Scenario: FLOW-03 Audio failure retains text and key

- **GIVEN** the selected local/service synthesizer fails or produces no playable bytes
- **WHEN** generation returns its result
- **THEN** saved text/mutations remain available for retry and no playable placeholder or silent backend substitution is used

### Requirement: FLOW-04 Ordinary use does not wait for reference corpora or review

The system SHALL make an authored exercise usable once its actual audio and generated mutation-list key are saved. Reference audio, all 11 full corpora, acoustic diagnostics, a separate LLM case review and the 732-stimulus benchmark SHALL be optional enrichment/evaluation features rather than prerequisites. All original scope SHALL remain preserved. GENERATED-EXERCISE provenance SHALL not imply benchmark or external-corpus acquisition.

#### Scenario: FLOW-04 Empty corpus collection can generate the first exercise

- **GIVEN** a fresh local workspace has no imported corpus or reference recordings and has configured generation/synthesis resources
- **WHEN** the first ordinary authored exercise completes
- **THEN** it can be listened to and scored against its mutation list without a separate review or benchmark action

#### Scenario: FLOW-04 Optional data stays optional and honestly accounted

- **GIVEN** native acoustic examples or full Cambridge releases remain missing
- **WHEN** the independently generated exercise is used
- **THEN** missing-source reports remain accurate but do not block that flow or mark generated examples as those acquired sources

### Requirement: FLOW-05 Free text is compared with the saved mutation list

The LLM SHALL compare the saved listener answer with the exact exercise mutation-list key/context, accepting localized semantic descriptions, category synonyms and valid alternative repairs. It SHALL preserve duplicate/retraction/ambiguity/key-defect behavior and all existing exact arithmetic. The checking LLM SHALL not need to hear audio again for this text/key comparison; known acoustic disputes can use optional actual evidence.

#### Scenario: FLOW-05 A paraphrase finds a recorded mutation

- **GIVEN** a saved agreement mutation and a listener describing the missing verb ending in the correct turn
- **WHEN** answer mapping uses the frozen mutation list
- **THEN** the supported detection/repair earns the applicable unchanged credit without exact answer-string matching

#### Scenario: FLOW-05 Hidden keys and duplicate claims do not inflate results

- **GIVEN** a listener has not submitted or repeats one mutation claim several times
- **WHEN** the app displays the listening task or grades the saved answer
- **THEN** the pre-submit key/transcript stays hidden and repeated compatible claims count once

### Requirement: FLOW-06 Scores and actionable LLM recommendations complete the flow

Native code SHALL retain all 42 existing formulas and calculate applicable exercise metrics/composite from the LLM's supported semantic decisions. Metrics requiring other observed populations SHALL remain N/A with a reason until those inputs exist. The feedback LLM SHALL explain found/missed/false-positive/control findings and recommend targeted practice, including labelled new practice examples and supported paraphrases without human approval or exact-copy restrictions. Recommendation failure SHALL preserve the score and answer.

#### Scenario: FLOW-06 Grounded new practice advice is allowed

- **GIVEN** the listener missed an article mutation
- **WHEN** the feedback LLM explains the finding and proposes a new article-listening practice example
- **THEN** it may return llm_grounded/practice_recommendation content linked to the actual finding without a human signature

#### Scenario: FLOW-06 Recommendations cannot fabricate heard defects or grades

- **GIVEN** a new practice example or failed feedback call
- **WHEN** results are displayed
- **THEN** the example is not counted as a recording defect and backend scores/saved answers remain unchanged without fabricated recommendations
