## ADDED Requirements

### Requirement: GOLD-01 Full category coverage
The release MUST satisfy the category coverage rule in `domain/validation-policy.yaml`. Cases MUST have real audio and independent reviews. An unresolved counting rule MUST block the coverage claim.

#### Scenario: GOLD-01 Permitted behavior
- **GIVEN** A corpus manifest lists reviewed cases for every required category.
- **WHEN** The publisher calculates coverage under an approved counting rule.
- **THEN** The report names the actual records and missing coverage.

#### Scenario: GOLD-01 Boundary behavior
- **GIVEN** An empty manifest declares 732 planned stimuli.
- **WHEN** A publisher requests a complete-corpus claim.
- **THEN** The claim fails because a plan is not acquired evidence.

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
