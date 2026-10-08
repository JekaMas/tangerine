<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: APR-01 Current actual user scope
The team SHALL use the actual user-approved product scope and permit labelled deterministic test examples without per-example or per-property approval. It SHALL never treat model output as actual source/provider observations or a human signature.

#### Scenario: APR-01 Exact scope
- **GIVEN** The owner approves one change with an exact scope.
- **WHEN** The team implements that change inside its scope.
- **THEN** The release links the owner decision and changed artifacts.

#### Scenario: APR-01 Scope expansion
- **GIVEN** A deterministic test example is labelled constructed.
- **WHEN** An implementer proposes another test double or a wider use.
- **THEN** The new deterministic example is permitted within scope and cannot count as real source/provider evidence.

### Requirement: APR-02 No unauthorized substitutes
The default application MUST use real services and genuine stored evidence.
Missing required keys/media MUST stop the affected call; missing optional measurements remain explicit unavailable observations.
The application MUST NOT replace missing results with invented values.

#### Scenario: APR-02 Real evidence
- **GIVEN** A provider returns an authentic response under an active profile.
- **WHEN** The response passes its applicable checks.
- **THEN** The application retains the provider origin and response evidence.

#### Scenario: APR-02 Missing evidence
- **GIVEN** No real provider result exists.
- **WHEN** A caller requests the result.
- **THEN** The application returns the actual unavailable state, not a precomputed success.

### Requirement: APR-03 Protected translation
The translation MUST preserve identifiers, formulas, command syntax, and original language examples.
Changes to behavior MUST remain separate from changes to prose.
An unresolved conflict MUST block the affected implementation decision.

#### Scenario: APR-03 Literal learner text
- **GIVEN** A case contains an intentional grammatical error.
- **WHEN** The surrounding documentation changes to controlled English.
- **THEN** The learner text remains unchanged.

#### Scenario: APR-03 Unsupported new rule
- **GIVEN** The source does not define a scoring tie-break rule.
- **WHEN** The translator finds that ambiguity.
- **THEN** The translator records the gap and does not invent a tie-break rule.
