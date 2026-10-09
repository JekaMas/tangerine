# Primary generated-exercise flow — specification update

The actual user flow supersedes any earlier claim that a complete empirical mistake corpus or native audio examples are required for ordinary generated exercises. The current owning contract is specification/v2/docs/simple-generation-flow.md, linked from the active README, authority record and single OpenSpec change.

## Product flow

1. Enter topic, speaker count and approximate text length in words. English level and broad mistake families are optional. Existing advanced controls remain available.
2. The configured LLM generates clean text. Save this exact canonical text before mutation.
3. Choose contextual, novel mutations; save the changed text, localized edits, valid repairs and full mutation list as the answer key. Ordinary generation needs no acquired source record.
4. Generate speech with the configured local backend or generative service, retain intentional changes and store actual final audio with the text/key/version. Playback uses stored bytes.
5. A listener plays the exercise and submits a free-text description of heard mistakes. Hide the transcript/key before submission.
6. The LLM compares the saved answer with the frozen mutation list and context, allowing semantic paraphrases and valid alternative corrections. Existing duplicate, uncertainty, key-reconsideration and immutable-revision behavior remains.
7. Native code calculates the applicable exact scores. The feedback LLM explains the findings and gives grounded practice recommendations, including clearly labelled new examples. Other population-dependent metrics remain N/A until their inputs exist.

Reference recordings, corpus frequencies, imports, the complete benchmark and separate LLM case review are optional enrichment/evaluation features. No human peer review is required. The eleven original full-source scopes remain separately preserved; missing native data remains accurately missing without blocking this authored flow.

## Concrete contract changes

The new exercise-request schema accepts three required form fields. blueprint-write supports this simple input or the existing advanced body; the local server expands the simple form. Optional level/duration constraints can remain null rather than invent a CEFR rating or exact measured duration. Broad pronunciation expands to the two original pronunciation domains.

Generation uses two phases of the existing case_generation role, with separate canonical/mutation prompts and saved input/output identities. Failed mutation preserves clean text; failed rendering preserves the text/key. The ordinary generated origin is GENERATED-EXERCISE, separate from external corpora and TET-GOLD-1. Actual audio and the generated key suffice for local use; a separate review is optional.

The existing speech worker/render contracts support the specified local Kokoro-82M option and original Azure service. Basic local capability is text, ordered turns and silence assembly. Arbitrary precise IPA, pitch or learner-accent realization is not inferred from ordinary TTS. Exact acoustic targets remain preserved and use an actually capable configured adapter or the separate recording/import route. No native audio example is required for every new exercise. Local assets have an explicit future model-setup action; service synthesis uses its selected credentials. No model setup or inference occurred here.

Workspace speech_profile and case_review_enabled settings are explicit; ordinary extra review defaults false. Feedback allows supported LLM paraphrases and practice recommendations without human signatures or exact-copy wording. Practice examples are not counted as defects in the recording, and feedback failure does not change the score.

OOD means novel lexical/contextual instances and combinations relative to explicit recipe illustrations, selected optional references and prior exercises. It is not a statistical claim about an undisclosed LLM training distribution. Saved actual outputs, rather than a seed alone, own replay.

## Preservation and validation

All 122 original taxonomy records/examples, all 122 authored recipes and all 42 original equations are byte-identical to baseline b654e64. All eleven original source entries and their full-release components are structurally identical. The original Azure profile/voices remain identical. Original operations and data fields remain; no application source, fixtures, immutable supplied archives or acquired corpus bytes changed.

The current active namespace has 195 files, 124 schemas and 2,490 indexed field occurrences. Mechanical checks parsed all 129 JSON and 21 YAML files, resolved 85 local schema references, and reconciled every schema/field/prompt/request-ownership/vector entry. This is not formal full-schema compilation or a runtime migration proof.

The static suite passed 187 checks, including constructed positive/negative contract slices for preparation, generation, novelty, synthesis configuration, ordinary usability, semantic answer matching and recommendations. A final metadata-order correction preserved baseline ordering to avoid unrelated churn: 185 observations retain their original valid receipt, and the two affected field-index/vector checks passed a focused validation. See validation-results-initial.json, metadata-order-focused-validation.json and validation-results.json.

Strict OpenSpec validation passed. The graph/discovery check passed with 349 requirements, 364 properties and 1,456 case edges. Six existing properties were reconciled; six new flow properties add 24 positive/negative planned edges. Every new behavior edge remains blocked and has no executed-test hash. No historical application receipt was refreshed or relabelled. The graph initially rejected missing discovery outcome text, then exposed previously uncovered mistake-data discovery scope; both failures and the corrected passing observation are retained. Static harness fixture failures are also retained and described in invalidation.md.

No application tests were rerun, because application bytes/fixtures/assertions were unchanged. No implementation, LLM call, audio synthesis, model installation, corpus acquisition or publication occurred. The prior implementation foundation does not establish this new flow's behavior.

## Decisions and remaining work

No additional product-owner decision is required for this update. Defaults and the meaning of word length/OOD are explicit above. Actual implementation, generation/synthesis fidelity, semantic answer matching and positive/negative provider behavior remain future work under separate authorization. Corpus-access and empirical completeness questions remain in their original ledgers as optional research/import dependencies for this primary flow.
