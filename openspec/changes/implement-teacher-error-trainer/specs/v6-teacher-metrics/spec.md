<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: MET-01 Named metric formulas
The backend MUST implement all 27 core metrics and their sufficient statistics.
It MUST use the exact formulas and null rules in `specification/v2/domain/metrics.v1.yaml`.
Its domain results MUST obey `specification/v2/docs/scoring-v1.md` and the reference arithmetic.

#### Scenario: MET-01 Resolved results
- **GIVEN** Every claim has a resolved decision under the frozen policy.
- **WHEN** The backend calculates the score.
- **THEN** It returns named metrics with exact fractions and raw statistics.

#### Scenario: MET-01 Zero denominator
- **GIVEN** A metric has no applicable denominator.
- **WHEN** The backend calculates that metric.
- **THEN** It returns null and the correct applicability reason, not a guessed zero or perfect score.

### Requirement: MET-02 Separate components
Detection, classification, correction, and explanation MUST remain separate.
Missing requested work MUST NOT remove its composite weight.
Partial credit and hierarchical category credit MUST use the fixed formulas.

#### Scenario: MET-02 Wrong correction
- **GIVEN** A teacher correctly finds a true error.
- **WHEN** The teacher supplies a wrong correction.
- **THEN** Detection receives credit, but the correction does not receive full credit.

#### Scenario: MET-02 Omitted explanation
- **GIVEN** The exercise requests an explanation and contains explanation opportunities.
- **WHEN** The teacher supplies no explanation.
- **THEN** Explanation coverage is zero and its requested composite weight remains active.

### Requirement: MET-03 Negative controls
Designated permitted controls MUST have explicit denominators.
Silence about a control MUST NOT count as proven conscious recognition or general specificity.
Unresolved claims MUST prevent final aggregate scores.

#### Scenario: MET-03 Unmentioned control
- **GIVEN** A case includes a designated permitted form.
- **WHEN** The teacher makes no assertion about that form.
- **THEN** The form contributes to the unflagged rate, but not to explicit recognition credit.

#### Scenario: MET-03 Unresolved control judgment
- **GIVEN** The teacher supplies contradictory judgments about one control.
- **WHEN** No explicit retraction resolves the contradiction.
- **THEN** The score remains in review instead of selecting the more favorable judgment.

### Requirement: MET-04 Observable scope
The backend MUST report evidence counts and pooled micro metrics.
Absent opportunities MUST remain distinct from zero performance.
It MUST NOT infer teacher speech, engagement, or classroom management from a written listening response.

#### Scenario: MET-04 Absent domain
- **GIVEN** A case contains no pronunciation opportunities.
- **WHEN** The interface shows the domain results.
- **THEN** Pronunciation is not applicable, rather than a score of zero.

#### Scenario: MET-04 Unobserved teaching behavior
- **GIVEN** The teacher only listens and submits text.
- **WHEN** The interface requests a teacher talk-time value.
- **THEN** The value is null with `not_observable_in_this_mode`.
