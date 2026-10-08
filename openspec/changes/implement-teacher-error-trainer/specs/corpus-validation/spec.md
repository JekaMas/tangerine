# corpus-validation specification

## Purpose

Preserve the observable corpus validation requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: COR-01 Keep source notices and actual provenance

The system SHALL support complete operator-supplied full releases, preserve actual source notices/agreements and provenance, and exclude corpus acquisition from startup. No human legal-review or per-transfer signature service SHALL be required.

#### Scenario: COR-01 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL ingest a complete supplied release and report actual source-use metadata, and SHALL never infer a third-party license from a key or claim missing data acquired

### Requirement: COR-02 Lossless inert source intake

The system SHALL preserve every supplied file including ancillary scripts as inert bytes, never execute source content, reject unsafe extraction paths and account all native fields/records without truncation.

#### Scenario: COR-02 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL retain scripts/docs/raw unknown fields with exact file dispositions, and SHALL never execute wav.scp pipelines/macros or omit members to claim full intake

### Requirement: COR-03 Report complete category coverage

The system SHALL retain122-leaf/full-source coverage and the732-stimulus benchmark target with LLM/native label provenance. Coverage SHALL be a report rather than a prerequisite for local use.

#### Scenario: COR-03 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL report true per-leaf coverage and missing benchmark populations, and SHALL never claim absent observations complete or require human gold before an exercise is usable

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
