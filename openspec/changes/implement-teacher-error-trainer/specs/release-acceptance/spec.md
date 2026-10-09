# release-acceptance specification

## Purpose

Preserve the observable release acceptance requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: REL-01 Deliver a runnable GitHub source project

The project SHALL supply an Apache-2.0 open-source GitHub source ZIP or clone, with the official LICENSE and third-party notices preserved, containing complete application source, Dockerfiles, working Compose, dependency lock files, migrations, provider-key example and concise README start/stop/restart instructions. The supplied helper SHALL build application images locally and initialize internal services without manual setup. Starting from extracted source SHALL require no Git metadata or workflow submodules. A formal deployment/release manifest, signed bundle, prebuilt application image publication or production deployment platform is not required. Verification SHALL use the documented download-and-run path.

#### Scenario: REL-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL build and start from the complete source ZIP with the documented command and provider keys, and SHALL report missing Docker, build inputs, invalid required settings or build failures without false success

### Requirement: REL-02 Complete local LLM browser cycle

The system SHALL support preparation, real rendering, LLM case review, listening, answer checking, result/retry and LLM dispute flows with saved original data and no human peer reviewers.

#### Scenario: REL-02 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL complete a first playable case and checked answer through the documented UI, and SHALL preserve the answer and actual failure when a provider call fails

### Requirement: REL-03 Verify portability and restore

The system SHALL actually verify amd64 and arm64 builds/runs plus database/media restart and backup restoration with source-bound acceptance reports.

#### Scenario: REL-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL restore and run each architecture with matching hashes and rows, and SHALL block portability or recovery claims for an untested architecture or failed restore
