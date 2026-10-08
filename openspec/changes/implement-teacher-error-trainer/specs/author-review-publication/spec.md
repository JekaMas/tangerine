# author-review-publication specification

## Purpose

Preserve the observable author review publication requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: AUT-01 Support author preparation

The system SHALL let authors prepare monologues/dialogues with context, voices, rate and planned errors, then obtain source text, key and real synthetic audio.

#### Scenario: AUT-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL prepare an authorized case and retain its real provider output, and SHALL refuse unsupported hard constraints or failed synthesis without a fabricated asset

### Requirement: REV-01 Require independent blind review

The system SHALL require two distinct qualified humans to listen without the planned key before comparing their own annotations with the key; require verified phonetics competence for acoustic cases.

#### Scenario: REV-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL retain two independent blind annotations and qualifying competence, and SHALL reject one person using two accounts, early key disclosure or missing acoustic qualification

### Requirement: REV-02 Resolve disagreement without erasure

The system SHALL retain initial disagreement and use a third qualified adjudicator or leave the recording unpublished.

#### Scenario: REV-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL retain initial labels and a separate adjudication decision, and SHALL refuse publication with unresolved disagreement or overwritten initial labels

### Requirement: PUB-01 Publish immutable reviewed versions

The system SHALL publish only after every required gate and create a new unapproved version whenever audio or key changes.

#### Scenario: PUB-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL publish a qualifying reviewed revision with immutable key/audio hashes, and SHALL reject approval reuse after key/audio mutation and edits to published revisions

### Requirement: DSP-01 Version disputed results

The system SHALL show original teacher answer and evidence during disputes and append adjudicated result versions without deleting earlier results.

#### Scenario: DSP-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL append a reviewed result linked to the preserved original, and SHALL reject unauthorized adjudication or replacement/deletion of result history
