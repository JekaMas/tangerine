# teacher-workflow specification

## Purpose

Preserve the observable teacher workflow requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: TCH-01 Save original submissions first

The system SHALL save original English/Russian answer bytes/hash before calls and use the sole active specification/v2 attempt schema/lifecycle in one local workspace.

#### Scenario: TCH-01 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL read back exact saved original before LLM processing, and SHALL never decode an old local1.1 record as active by dropping fields

### Requirement: TCH-02 LLM checking and native arithmetic

The system SHALL extract without the key, map with the key through the configurable LLM, calculate authoritative numbers in code and generate feedback. Mapping audit SHALL remain optional.

#### Scenario: TCH-02 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL complete answer checking without a human or repeat audit, and SHALL never let LLM prose replace exact equations or invent teacher correction content

### Requirement: TCH-03 Persist actual processing outcomes

The system SHALL display completed, review_required and evaluation_failed outcomes from the active lifecycle, where review_required means provisional LLM reconsideration rather than a human queue.

#### Scenario: TCH-03 supported and rejected inputs

- **WHEN** the local action receives the supported or failing input
- **THEN** it SHALL show saved metrics and clearly unresolved interpretations, and SHALL never treat an optional audit failure or harmless reply wrapper as missing human approval

### Requirement: TCH-04 Keep synchronous bounded processing

The system SHALL use a common 270-second overall bound across API/proxy/browser with cancellation, no queue or WebSocket, and explicit user-triggered retries using the same saved answer.

#### Scenario: TCH-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL complete synchronously within the overall deadline and explicitly retry saved content, and SHALL cancel on the overall deadline and prevent automatic retry/background execution
