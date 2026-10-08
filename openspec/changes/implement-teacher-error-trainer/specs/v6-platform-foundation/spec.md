<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: PLAT-01 Local data provenance

The application SHALL commit content/state references atomically in one workspace. LLM review records SHALL name actual receipts; person/qualification/approval records SHALL be imported metadata rather than required new human workflow.

#### Scenario: PLAT-01 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL save actual machine review with no person identity

#### Scenario: PLAT-01 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never manufacture source annotations or human approval

### Requirement: PLAT-02 Optional budgets and saved failures

The platform SHALL record usage/cost or explicit unknown, with one paid foreground operation and optional disabled-by-default daily/monthly caps. All paid flows SHALL use the same policy.

#### Scenario: PLAT-02 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL allow unknown-price local calls when caps are disabled and retain usage

#### Scenario: PLAT-02 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never require per-call budget approval or block stored playback on cloud quota

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
