# Product-scoped data dependencies

## ADDED Requirements

### Requirement: DREL-01 Generated flow requires its own artifacts

The generated exercise flow SHALL use the preserved taxonomy/recipes, configured LLM/speech resources, saved canonical text/mutations/key/audio and submitted answer. Missing external corpora, empirical frequencies, academic identity, participant cohorts and full benchmarks SHALL NOT prevent independent generation, answer checking, native scoring or recommendations. Owning definitions are specification/v2/docs/product-data-relevance.md and domain/product-data-relevance.v1.json.

#### Scenario: DREL-01 Independent generated exercise

- **GIVEN** No external source is acquired and empirical difficulty is unrated
- **WHEN** the generated exercise is prepared, listened to and checked
- **THEN** the selected actual LLM/speech owners use the saved artifacts and return native scores and category-targeted advice without external acquisition

#### Scenario: DREL-01 Unavailable selected enrichment source

- **GIVEN** An operator explicitly selects an unacquired source as generation context
- **WHEN** that selected source context is requested
- **THEN** the action reports that source unavailable, offers an explicit independent/available-source choice and does not silently replace it or block unrelated independent generation

### Requirement: DREL-02 Scope optional data to the consuming action

All eleven original full-source identities and complete member/native-field scopes SHALL remain. Missing private exports, dictionaries, instruments or remote interfaces SHALL affect only the selected source action, normalized semantics or named completeness claim. Supported local intake SHALL NOT require a private API; unbound study/pedagogy scales SHALL remain raw source data without adopting them as Tangerine grades. Official-equivalence explanations and duplicate high-resolution downloads SHALL NOT gate valid pinned-source use. Owning definitions are specification/v2/docs/product-data-relevance.md and domain/product-data-relevance.v1.json.

#### Scenario: DREL-02 Scoped local source intake

- **GIVEN** An actual permitted archive has complete observed raw members and some native instrument fields are unbound
- **WHEN** local intake or an independent source representation is used
- **THEN** raw fields/members survive, unbound semantics remain raw_only, no private API or study UI is required and actual source/representation/count provenance is retained

#### Scenario: DREL-02 Unsupported completeness or source substitution

- **GIVEN** A source is partial, a URL replaces media bytes or mirror counts differ from published expectations
- **WHEN** a named full/normalized/official-equivalence report is requested
- **THEN** the report exposes its missing/unknown/discrepant scope without calling it complete, dropping fields or substituting another release; unrelated generated use continues

### Requirement: DREL-03 Keep necessary selected behavior evidence

Actual selected main-flow builds, stored audio, mutation realization and semantic answer-checking acceptance SHALL remain future engineering obligations. Selected AI-affecting development SHALL retain mandatory Lab/native prompt/context/call evidence and meaningful affected positive/negative cases. Full732stimuli, all sources, universal accent/provider/platform qualification and genuine participant populations SHALL be required only for their explicitly claimed full or empirical scope, never every increment. Owning definitions are specification/v2/docs/product-data-relevance.md and domain/product-data-relevance.v1.json.

#### Scenario: DREL-03 Focused development experiment

- **GIVEN** An authorized AI increment selects meaningful constructed or permitted references for a concrete LLM/speech binding
- **WHEN** the changed property and affected pipeline are exercised
- **THEN** actual Lab/native observations cover the selected positive/negative cases, failures and circular-reference limits; no732population or participant recruitment is required

#### Scenario: DREL-03 Claim exceeds selected observed evidence

- **GIVEN** Only fixture/static or selected-binding evidence exists and other categories/voices/populations are unobserved
- **WHEN** implementation, precise acoustic or full empirical coverage is claimed
- **THEN** the claim remains limited or incomplete; no artifact fixture, intended sound or small selected population is represented as actual full-scope behavior
