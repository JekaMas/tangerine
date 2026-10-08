# recovered-runtime-contract specification

## ADDED Requirements

### Requirement: SYNC-01 Preserve deadline lease and request identity

Attempts SHALL persist original UTF-8/hash and idempotency atomically before providers, permit empty answers, and reject over 20,000 Unicode codepoints. Same key/different payload SHALL return 409. Revision/token compare-and-swap SHALL enforce a 300-second lease; stale returns cannot commit and network calls cannot hold a DB transaction. A single propagated 270-second attempt deadline SHALL cover extraction 40, mapping 70, audit 70, feedback 40 and at least five seconds for persistence. API write/proxy/browser timeouts SHALL be 285/300/310 seconds. At most one transport retry per request budget is permitted, with no JSON repair loop or background recovery.

#### Scenario: SYNC-01 Complete supported behavior

- **GIVEN** Use empty/max/oversize answers, same/different idempotency payloads, overlapping requests, expired lease and late-stage provider returns with controlled time boundaries.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** A saved answer survives failure/disconnection; eligible explicit retry uses the same attempt and only the current lease can commit within the shared deadline.

#### Scenario: SYNC-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A stale result, renewed per-stage global deadline, DB transaction spanning network, oversized Unicode input or favorable JSON retry is rejected.

### Requirement: SYNC-02 Distinguish lifecycle statuses

The stored attempt state SHALL follow the recovered lifecycle: draft -> submitted -> evaluating -> complete, review_required or evaluation_failed. The API SHALL return 200 for complete/review_required, 409 EVALUATION_IN_PROGRESS for an active lease, 502 for refusal/schema failure and 504 for deadline. UI labels ready/needs_review/technical_error SHALL be explicitly derived from those states and never replace contract enums. Quarantine/disputes SHALL preserve immutable saved answers and append result revisions.

#### Scenario: SYNC-02 Complete supported behavior

- **GIVEN** Return resolved, unresolved, refused, active-lease and timed-out evaluations, then read historical results after dispute resolution.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Each response/status/UI label agrees with its immutable stored state and preserved original answer; unresolved aggregates remain null.

#### Scenario: SYNC-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A review result shown as final score, contract enum replaced by UI label, or overwritten historical result is rejected.
