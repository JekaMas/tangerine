## ADDED Requirements

### Requirement: GEN-01 Candidate output
The compiler MUST use the blueprint, canonical script, error opportunities, and typed mutations. Its output MUST obey `contracts/case-candidate.schema.json`. The LLM MUST NOT create observed evidence, human approvals, or publication status.

#### Scenario: GEN-01 Permitted behavior
- **GIVEN** A candidate obeys all typed counts and span rules.
- **WHEN** The compiler accepts its structure.
- **THEN** The candidate can enter audio generation, but cannot enter publication.

#### Scenario: GEN-01 Boundary behavior
- **GIVEN** The generator has no recorded human approval.
- **WHEN** Its output asserts a reviewer decision or observed IPA.
- **THEN** The API rejects the unsupported output.

### Requirement: GEN-02 Origin and linguistic review
The compiler MUST retain canonical text, surface text, source permissions, and mutation IDs. It MUST retain prompt and provider versions. A separate linguistic audit MUST remain advisory until human review.

#### Scenario: GEN-02 Permitted behavior
- **GIVEN** A source permits the proposed use.
- **WHEN** The compiler uses a source-derived pattern.
- **THEN** The candidate links the source record and transformation.

#### Scenario: GEN-02 Boundary behavior
- **GIVEN** A reviewer finds an unlisted error.
- **WHEN** The error changes the declared budget.
- **THEN** The case remains unpublished until revision and review.

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
