# provider-integration specification

## Purpose

Preserve the observable provider integration requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: PRV-01 Use the retained real profiles

The system SHALL preserve gpt-4.1-2025-04-14 as the original LLM baseline and permit the explicitly configured, versioned DeepSeek fast development profile in docs/llm-configuration.md. Azure registered voices, whisper-1 and Azure Pronunciation Assessment remain the speech baseline. The selected operation SHALL never silently fall back to another profile.

#### Scenario: PRV-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL call the configured profile and retain its exact returned metadata, and SHALL fail the affected call on missing credentials or unavailable profile without substitution

### Requirement: PRV-02 Retain real call receipts

The system SHALL record profile, prompt/schema versions, input hash, output/error, duration and usage for each real call without leaking credentials.

#### Scenario: PRV-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL reconcile a real call with its versioned secret-safe receipt, and SHALL reject a receipt missing versions, hashes or real provenance

### Requirement: PRV-03 Verify acoustic realization

The system SHALL verify that intended grammar, phonetic substitutions, voice differences and tempo occur in the actual audio, not merely the request parameters.

#### Scenario: PRV-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL retain real audio and qualified listening evidence for each required target, and SHALL fail an unrealized acoustic target and preserve its category in scope

### Requirement: PRV-04 Bound advisory speech assessment

The system SHALL treat ASR timing and Azure scores as advisory, use prosody assessment only for supported en-US, and never infer an observed replacement phone from a low score.

#### Scenario: PRV-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL retain supported advisory output with its declared scope, and SHALL refuse phoneme-gold or non-en-US prosody claims from the advisory profile
