# author-review-publication specification

## Purpose

Preserve the observable author review publication requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: AUT-01 Support author preparation

The system SHALL accept topic, speaker count and approximate text length, with optional English level/broad mistake categories, and generate clean text, novel mutations/list/key and real local-or-service audio through the ordinary flow in specification/v2/docs/simple-generation-flow.md. Existing advanced monologue/dialogue/context/voice/rate controls SHALL remain available without being mandatory form inputs.

#### Scenario: AUT-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL prepare an authorized case and retain its real provider output, and SHALL refuse unsupported hard constraints or failed synthesis without a fabricated asset

### Requirement: REV-01 LLM case review

The system SHALL offer optional generated-case review through a configurable LLM with actual modality/evidence and no human peer reviewers, identities or qualification prerequisites. The ordinary exercise SHALL use its saved mutation-list key without requiring this action. When invoked, review SHALL retain blind observations, key comparison, unit correspondence and machine findings.

#### Scenario: REV-01 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL run a machine review and retain its actual receipt/evidence modality, and SHALL never demand a human reviewer or label transcript inference as direct hearing

### Requirement: REV-02 LLM adjudication preserves disagreement

The system SHALL use configurable LLM adjudication for supported case/answer disagreements, retain prior findings and append a resolution or explicit insufficient_evidence.

#### Scenario: REV-02 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL append the supported LLM resolution to retained earlier findings, and SHALL never require a third person or overwrite prior disagreement

### Requirement: PUB-01 Use immutable playable cases

The system SHALL automatically make the ordinary generated exercise available when its actual audio and saved mutation-list key are ready, with explicit quality warnings and no separate case-review action, human approval, native reference audio or full-bank certification. Audio/key changes SHALL create a new immutable version.

#### Scenario: PUB-01 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL use the first real playable case and retain its key/audio identity, and SHALL never invent audio, silently mutate historical keys or gate use on benchmark completion

### Requirement: DSP-01 LLM dispute revisions

The system SHALL give the LLM adjudicator the exact saved answer/key/evidence and append supported mapping/key/result revisions without requiring a human adjudicator.

#### Scenario: DSP-01 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL append a supported corrected result with original available, and SHALL retain original result and failure when adjudication refuses or lacks evidence
