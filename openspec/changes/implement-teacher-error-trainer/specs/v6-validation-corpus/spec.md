<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: GOLD-01 Full category benchmark feature

The project SHALL retain full122-leaf/732-stimulus coverage reports and machine/native label provenance without independent human reviewers or benchmark completion as a local-use gate.

#### Scenario: GOLD-01 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL report actual complete/incomplete per-leaf populations

#### Scenario: GOLD-01 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never claim machine self-agreement as independent human accuracy

### Requirement: GOLD-02 Separate data splits
Development, calibration, and holdout data MUST have disjoint group manifests. The grouping MUST prevent speaker, script, and case-family leakage. Threshold changes MUST preserve the held-out evaluation boundary.

#### Scenario: GOLD-02 Permitted behavior
- **GIVEN** A source contributes related variants.
- **WHEN** The importer assigns a split.
- **THEN** The related variants remain in one permitted group and split.

#### Scenario: GOLD-02 Boundary behavior
- **GIVEN** A holdout script appears in a development prompt.
- **WHEN** The release check finds that link.
- **THEN** The holdout result cannot support the claimed independent evaluation.

### Requirement: GOLD-03 Measured denominators
Each evaluation result MUST report its actual numerator and denominator. Insufficient samples MUST use `insufficient_evidence`. Acceptance thresholds MUST remain policy values, not invented measurements.

#### Scenario: GOLD-03 Permitted behavior
- **GIVEN** A real evaluation satisfies its required sample count.
- **WHEN** The evaluator calculates the metric.
- **THEN** The report includes counts, versions, and applicability.

#### Scenario: GOLD-03 Boundary behavior
- **GIVEN** A domain has fewer eligible observations than its policy requires.
- **WHEN** Its observed percentage exceeds the threshold.
- **THEN** The gate remains insufficient despite that percentage.
