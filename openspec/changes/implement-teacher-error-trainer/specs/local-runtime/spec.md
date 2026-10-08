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

The system SHALL wait for healthy dependencies and successful migration, private media initialization and account initialization before web readiness.

#### Scenario: RUN-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL start from empty persistent volumes with successful one-shot initialization, and SHALL keep dependent services unavailable after failed migration or initialization

### Requirement: RUN-03 Keep the exercise bank truthful

The system SHALL read published exercises from PostgreSQL and display an empty library when none exist, without successful placeholder exercises.

#### Scenario: RUN-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL read an actually published exercise from the database, and SHALL show an empty state for zero rows and never synthesize a demonstration

### Requirement: RUN-04 Authenticate local accounts

The system SHALL initialize the local owner idempotently, hash passwords, persist expiring sessions, revoke on logout and require authentication for protected data.

#### Scenario: RUN-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL log in with a configured account and read its session, and SHALL reject wrong passwords, expired/revoked sessions and unauthorized requests

### Requirement: RUN-05 Enforce same-origin access

The system SHALL proxy browser API requests on the same origin and reject cross-origin mutations without exposing provider keys or backend credentials.

#### Scenario: RUN-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL send an authenticated mutation from the configured local origin, and SHALL reject a cross-origin mutation and keep credentials out of responses

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
