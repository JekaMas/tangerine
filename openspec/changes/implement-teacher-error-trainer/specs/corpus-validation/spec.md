# corpus-validation specification

## Purpose

Preserve the observable corpus validation requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: COR-01 Protect source permissions

The system SHALL acquire exact corpus releases only with scope-specific permission, preserve raw hashes in quarantine and keep corpora out of normal startup and public images.

#### Scenario: COR-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL import a permitted immutable release with actual legal/source receipts, and SHALL deny unapproved uses, guessed mirrors or startup corpus downloads

### Requirement: COR-02 Normalize safely and transparently

The system SHALL reject traversal, external links, executable content, unbounded decompression and command execution; preserve original tokens, annotators, source scales and transformations with invalid rows quarantined.

#### Scenario: COR-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL import a bounded archive and retain accepted/rejected provenance, and SHALL quarantine unsafe archives, invalid offsets or unknown scales rather than guess

### Requirement: COR-03 Cover every category honestly

The system SHALL cover all 122 leaves and required controls using independently reviewed real synthesis, and keep the inherited 732 floor pending DEC-002 rather than treating it as a resolved counting rule.

#### Scenario: COR-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL reconcile per-leaf assets, observations and controls under approved counting, and SHALL refuse coverage when a variant becomes an error or counts have no approved unit

### Requirement: COR-04 Collect real teacher answers

The system SHALL retain real answers and independent pre-model labels for correct, partial, vague, repeated, contradictory, false, alternative and off-key observations.

#### Scenario: COR-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL retain permitted real answers and independently adjudicated claims, and SHALL leave missing classes missing instead of filling them with invented real answers

### Requirement: COR-05 Keep splits and thresholds frozen

The system SHALL group related learners/speakers/scripts/derivatives into one development, calibration or holdout split, prohibit holdout prompt tuning and fix approved thresholds before seeing results.

#### Scenario: COR-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL evaluate untouched holdout with real denominators and fixed policy, and SHALL block fresh-independent claims after overlap, holdout reuse or post-result threshold tuning

### Requirement: COR-06 Measure semantic performance

The system SHALL measure mapping precision, decision coverage, correction agreement and repeatability with real denominators, preserved initial disagreement and the fixed approved policy.

#### Scenario: COR-06 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL publish measured results with authentic populations and denominators, and SHALL reject zero-selected, missing-class or invented performance receipts
