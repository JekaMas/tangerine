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

### Requirement: RUN-04 Open one local workspace without accounts

The system SHALL open one installation-owned local workspace without accounts, passwords, login, logout, session cookies, access roles or tenant configuration. Teaching, preparation and review are activities available to the local operator. docs/simple-local-product.md governs the trust boundary; lifecycle and genuine review guards remain mandatory.

#### Scenario: RUN-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL open the library and saved local data without a login or session, and SHALL reject configuration that enables unsupported remote exposure rather than introducing account or tenant setup

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

The release SHALL supply the simple local launcher, key-only setup and default configurable LLM profile in docs/simple-local-product.md. It SHALL initialize internal infrastructure automatically without manual database, storage, API or account setup. Opening the library and playing stored audio SHALL work without provider keys; only dependent cloud operations SHALL request their keys and permitted source transfer. Speech keys remain separate when required.

#### Scenario: RUN-08 simple supported startup

- **GIVEN** Docker is running and the supplied local bundle is available.
- **WHEN** the user fills provider keys and starts the supplied launcher.
- **THEN** The local interface becomes available without login or manual infrastructure configuration; a key-free workspace still opens its truthful empty library or plays approved stored audio.

#### Scenario: RUN-08 missing operation key

- **GIVEN** The selected LLM or speech operation has no required key or source-use permission.
- **WHEN** the user invokes that operation.
- **THEN** The interface identifies the missing operation-specific configuration without a provider call, fallback, invented result or blocking unrelated stored playback.

### Requirement: RUN-09 Use activity views with honest disclosure boundaries

The interface SHALL offer Library, Prepare, Review and Results in one local workspace, without an admin console, role switcher or public API setup. Teacher and blind-review projections SHALL withhold keys at their specified stages; the local operator can access authoring separately, so no adversarial role isolation is claimed. Review decisions SHALL retain actual person/qualification/independence evidence without reviewer accounts.

#### Scenario: RUN-09 ordinary local activities

- **GIVEN** A local operator and genuine independently supplied reviewer observations.
- **WHEN** the operator prepares, reviews and opens an eligible published exercise.
- **THEN** The activities require no account or role assignment and preserve distinct reviewer evidence, final hashes and teacher-view key omission.

#### Scenario: RUN-09 disclosure or false reviewer evidence

- **GIVEN** A teacher payload includes a pre-submit key or publication uses duplicate-person or fabricated approval evidence.
- **WHEN** projection and publication guards are checked.
- **THEN** The key-bearing teacher payload fails validation and the invalid review cannot publish; local naming alone cannot prove external independence.
