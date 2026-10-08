# recovered-runtime-contract specification

## ADDED Requirements

### Requirement: SYNC-01 Deadline lease and output repair

The system SHALL preserve submitted bytes/idempotency before calls, keep the270s deadline and300s lease, perform calls outside transactions and fence stale results. Stage budgets and one transport retry/one format repair are defined in specification/v2/docs/provider-contracts.md.

#### Scenario: SYNC-01 Complete supported behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL save the answer and normalized repaired result within the current lease

#### Scenario: SYNC-01 Incomplete or forbidden behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never commit stale results, invent missing semantic content or create background retries

### Requirement: SYNC-02 Distinguish lifecycle statuses

The stored attempt state SHALL follow the explicit v2 draft lifecycle in specification/v2/docs/lifecycle.md: started -> saved -> evaluating -> completed, review_required or evaluation_failed. The recovered draft/submitted/complete enums remain historical schemas only. The API SHALL return 200 for completed/review_required, 409 EVALUATION_ACTIVE for an active lease, 502 for refusal/schema failure and 504 for deadline. UI labels ready/needs_review/technical_error SHALL be explicitly derived from those states and never replace contract enums. Quarantine/disputes SHALL preserve immutable saved answers and append result revisions.

#### Scenario: SYNC-02 Complete supported behavior

- **GIVEN** Return resolved, unresolved, refused, active-lease and timed-out evaluations, then read historical results after dispute resolution.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Each response/status/UI label agrees with its immutable stored state and preserved original answer; unresolved aggregates remain null.

#### Scenario: SYNC-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A review result shown as final score, contract enum replaced by UI label, or overwritten historical result is rejected.
