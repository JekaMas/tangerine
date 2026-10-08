<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: PLAT-01 Local provenance and audit
The application MUST use one local workspace without tenant or access-role authorization. State-changing operations MUST commit their audit and exact case/version/source evidence together. Human-review records MUST identify genuine people and qualifications without requiring accounts. Model output MUST NOT satisfy a human-review guard or create an approval. docs/simple-local-product.md defines the current scope.

#### Scenario: PLAT-01 Permitted behavior
- **GIVEN** The operator records a genuine qualified reviewer decision.
- **WHEN** The API commits the review.
- **THEN** The audit links the recorded reviewer evidence to the case version.

#### Scenario: PLAT-01 Boundary behavior
- **GIVEN** A review references another case version or presents a model response as a human decision.
- **WHEN** The application validates evidence ownership and review guards.
- **THEN** The application rejects the mutation and preserves the case and audit history.

### Requirement: PLAT-02 Costs and failures
The platform MUST limit requests and record provider usage. Provider failures MUST preserve saved attempts. Quotas MUST NOT prevent playback of an existing published local case.

#### Scenario: PLAT-02 Permitted behavior
- **GIVEN** The local generation budget is exhausted.
- **WHEN** A teacher opens an existing published exercise.
- **THEN** The teacher can still play its stored audio.

#### Scenario: PLAT-02 Boundary behavior
- **GIVEN** A provider request reaches its deadline.
- **WHEN** The adapter receives no valid result.
- **THEN** The attempt remains recoverable without invented output.

### Requirement: PLAT-03 Truthful release records
A release record MUST separate proposed behavior from measured results. Unperformed checks MUST use `not_run` or `blocked`. An unmet evidence requirement MUST NOT receive PASS.

#### Scenario: PLAT-03 Permitted behavior
- **GIVEN** A checker examines actual contract files.
- **WHEN** The checker completes its work.
- **THEN** Its result identifies the examined files and supported check scope.

#### Scenario: PLAT-03 Boundary behavior
- **GIVEN** No real provider evaluation exists.
- **WHEN** A publisher prepares release evidence.
- **THEN** The provider gate remains blocked.
