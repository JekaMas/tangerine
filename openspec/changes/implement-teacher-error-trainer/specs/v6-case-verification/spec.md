<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: VER-01 Playable audio and quality report

The application SHALL require actual playable audio and a machine-produced/imported key; quality thresholds and capability checks SHALL be reports/warnings rather than human or full-release gates.

#### Scenario: VER-01 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL use a real playable case with explicit quality warnings

#### Scenario: VER-01 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never fabricate a playable asset for corrupt or missing bytes

### Requirement: VER-02 Actual acoustic evidence

The application SHALL distinguish requested, measured, native-annotated and model-inferred sound. Missing acoustic observations SHALL remain unknown without requiring humans.

#### Scenario: VER-02 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL retain method/modality and actual requested-versus-observed fields

#### Scenario: VER-02 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never derive precise heard phone from canonical score or text-only model

### Requirement: VER-03 LLM review without peers

The application SHALL offer optional machine case review and dispute adjudication through configurable stages and retain original findings, with no distinct-person, competence or two-approval requirement. Ordinary authored use SHALL require its actual audio and generated mutation-list key, not a separate case-review pass.

#### Scenario: VER-03 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** an explicitly requested case review SHALL retain its actual LLM findings; ordinary use SHALL proceed without requesting it

#### Scenario: VER-03 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never block ordinary use on human approvals
