# release-acceptance specification

## Purpose

Preserve the observable release acceptance requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: REL-01 Deliver fixed build artifacts

The system SHALL deliver source, Dockerfiles, working Compose, fixed dependencies, inspected image references/digests, migrations and exact startup instructions.

#### Scenario: REL-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL build and inspect the actual images used by the documented command, and SHALL block release for missing builds, moving image tags or invented digests

### Requirement: REL-02 Prove the complete browser cycle

The system SHALL demonstrate real author, independent reviewers and teacher flows with real providers, persistent answers, no early key leakage and no browser secrets.

#### Scenario: REL-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL complete one real published case end to end through the browser, and SHALL demonstrate that provider failure preserves the answer without a fake result

### Requirement: REL-03 Verify portability and restore

The system SHALL actually verify amd64 and arm64 builds/runs plus database/media restart and backup restoration with source-bound acceptance reports.

#### Scenario: REL-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL restore and run each architecture with matching hashes and rows, and SHALL block portability or recovery claims for an untested architecture or failed restore
