<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: PLAT-01 Authorization and audit
The API MUST enforce tenant, role, and resource permissions. It MUST record privileged changes with the actor and source evidence. Model output MUST NOT authorize access or create an approval.

#### Scenario: PLAT-01 Permitted behavior
- **GIVEN** An authorized reviewer records a decision.
- **WHEN** The API commits the review.
- **THEN** The audit links that authenticated reviewer to the case version.

#### Scenario: PLAT-01 Boundary behavior
- **GIVEN** A user requests another tenant resource.
- **WHEN** The API resolves authorization.
- **THEN** The API denies access without protected content.

### Requirement: PLAT-02 Costs and failures
The platform MUST limit requests and record provider usage. Provider failures MUST preserve saved attempts. Quotas MUST NOT prevent playback of an existing authorized case.

#### Scenario: PLAT-02 Permitted behavior
- **GIVEN** A tenant exhausts its generation budget.
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
