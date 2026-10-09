# local-runtime specification

## Purpose

Preserve the observable local runtime requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: RUN-01 Run the prescribed real services

The system SHALL use Next.js, Go API, PostgreSQL, private MinIO and Python speech in Compose, with only 127.0.0.1:3000 published.

#### Scenario: RUN-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL build the real services and connect the browser through port 3000, and SHALL reject host exposure for API, database, storage or speech

### Requirement: RUN-02 Gate startup on initialization

The system SHALL wait for healthy dependencies and successful migration and private media initialization; it SHALL require no account initialization before web readiness.

#### Scenario: RUN-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL start from empty persistent volumes with successful one-shot initialization, and SHALL keep dependent services unavailable after failed migration or initialization

### Requirement: RUN-03 Keep the exercise bank truthful

The system SHALL read published exercises from PostgreSQL and display an empty library when none exist, without successful placeholder exercises.

#### Scenario: RUN-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL read an actually published exercise from the database, and SHALL show an empty state for zero rows and never synthesize a demonstration

### Requirement: RUN-04 One local workspace without accounts

The system SHALL provide one local workspace without accounts, login, roles, tenant configuration or human reviewer qualification. LLMs SHALL check answers/reviews/disputes.

#### Scenario: RUN-04 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL start locally with operation-dependent keys and no reviewer setup, and SHALL never create a mandatory human identity form

### Requirement: RUN-05 Enforce same-origin access

The system SHALL proxy browser API requests on the same origin and reject cross-origin mutations without exposing provider keys or backend credentials.

#### Scenario: RUN-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL send a same-origin local mutation from the configured local origin, and SHALL reject a cross-origin mutation and keep credentials out of responses

### Requirement: RUN-06 Persist and recover real data

The system SHALL retain PostgreSQL and private media after restart and provide a restorable backup with matching hashes.

#### Scenario: RUN-06 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL restart then restore a backup and read original rows and media hashes, and SHALL detect missing media, incomplete backup or incompatible migration

### Requirement: RUN-07 Report actual readiness

The system SHALL distinguish liveness from dependency readiness and return non-success when database, private media or speech is unavailable.

#### Scenario: RUN-07 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL report ready after real dependencies and migrations are available, and SHALL report unavailable when any required dependency fails

### Requirement: RUN-08 Start from keys and the supplied bundle

The GitHub source project SHALL supply the simple local launcher, operation-dependent provider connection/key setup and default configurable LLM profile in docs/simple-local-product.md. An extracted source ZIP SHALL build and run with Docker without Git metadata, workflow submodules, prebuilt application image distribution or a formal deployment/release manifest. It SHALL initialize internal infrastructure automatically without manual database, storage, API or account setup. Opening the library and playing stored audio SHALL work without provider keys; only dependent cloud operations SHALL request their documented provider authorization/key and permitted source transfer. Eligible ChatGPT-plan sign-in is provider authorization in Settings, not an application login; current included-only defaults and billing constraints follow specification/v2/docs/provider-access.md. Speech keys remain separate when required.

#### Scenario: RUN-08 simple supported startup

- **GIVEN** Docker is running and the GitHub source ZIP has been extracted with all application build inputs.
- **WHEN** the user fills provider keys and starts the supplied launcher.
- **THEN** The local interface becomes available without login or manual infrastructure configuration; a key-free workspace still opens its truthful empty library or plays approved stored audio.

#### Scenario: RUN-08 missing operation key

- **GIVEN** The selected LLM or speech operation has no required key or source-use permission.
- **WHEN** the user invokes that operation.
- **THEN** The interface identifies the missing operation-specific configuration without a provider call, fallback, invented result or blocking unrelated stored playback.

### Requirement: RUN-09 Simple activity views

The system SHALL provide Library, Prepare, machine Review, Results, Sources and Settings with honest pre-submit key disclosure and no human-review ceremony. Imported annotations SHALL remain visible as source data.

#### Scenario: RUN-09 ordinary local activities

- **WHEN** the supported local action completes
- **THEN** it SHALL use all activities in one local installation

#### Scenario: RUN-09 disclosure or false reviewer evidence

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never relabel imported persons as new machine-created humans
