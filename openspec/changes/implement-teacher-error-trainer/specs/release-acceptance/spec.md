# release-acceptance specification

## Purpose

Preserve the observable release acceptance requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: REL-01 Deliver a runnable GitHub source project

The project SHALL supply an open-source GitHub source ZIP or clone with complete application source, Dockerfiles, working Compose, dependency lock files, migrations, provider-key example and concise README start/stop/restart instructions. The supplied helper SHALL build application images locally and initialize internal services without manual setup. Starting from extracted source SHALL require no Git metadata or workflow submodules. A formal deployment/release manifest, signed bundle, prebuilt application image publication or production deployment platform is not required. Verification SHALL use the documented download-and-run path.

#### Scenario: REL-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL build and start from the complete source ZIP with the documented command and provider keys, and SHALL report missing Docker, build inputs, invalid required settings or build failures without false success

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
