<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: GEN-01 Candidate output
The compiler MUST use the simple topic/speaker/word-length request or advanced blueprint, save a clean canonical_text phase, then apply a separate mutation phase to that fixed script using broad/exact category choices and typed mutations. Both outputs MUST obey `specification/v2/contracts/case-candidate.schema.json`; the first has identical canonical/surface text and no planned units, and the second supplies the mutation list/key. Corpus excerpts and example audio are optional. The LLM MUST NOT create observed evidence, human approvals, or publication status. The owning flow is specification/v2/docs/simple-generation-flow.md.

#### Scenario: GEN-01 Permitted behavior
- **GIVEN** A candidate obeys all typed counts and span rules.
- **WHEN** The compiler accepts its structure.
- **THEN** The candidate can enter audio generation, but cannot enter publication.

#### Scenario: GEN-01 Boundary behavior
- **GIVEN** The generator has no recorded human approval.
- **WHEN** Its output asserts a reviewer decision or observed IPA.
- **THEN** The API rejects the unsupported output.

### Requirement: GEN-02 Origin and LLM linguistic review

The compiler SHALL retain original/surface text, source notices, mutation IDs and actual prompt/provider versions. Linguistic audit SHALL remain an optional machine diagnostic with no subsequent human review prerequisite; generation and use SHALL not require a separate audit.

#### Scenario: GEN-02 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL retain machine findings with generation provenance

#### Scenario: GEN-02 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never invent source data, reviewer identity or actual observed sound

### Requirement: GEN-03 Generation limits
A candidate MUST have at most three compilation attempts and three audio-generation attempts. Each attempt MUST record its cause and cost. A later attempt MUST require an explicit request after the current request ends.

#### Scenario: GEN-03 Permitted behavior
- **GIVEN** A transport failure occurs inside the request budget.
- **WHEN** The configured transport retry remains available.
- **THEN** The adapter can make one recorded retry within that budget.

#### Scenario: GEN-03 Boundary behavior
- **GIVEN** The candidate reaches an attempt limit.
- **WHEN** Its constraints remain unsatisfied.
- **THEN** The API returns `constraint_unsatisfied` and retains the failed evidence.
