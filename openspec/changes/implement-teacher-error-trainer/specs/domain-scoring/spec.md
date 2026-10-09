# domain-scoring specification

## Purpose

Preserve the observable domain scoring requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.

## ADDED Requirements

### Requirement: DOM-01 Retain the full taxonomy

The system SHALL retain all 122 original category IDs, key versions, protected illustrations, variety, register and intended-context constraints.

#### Scenario: DOM-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL accept an original category valid in the declared context, and SHALL reject unknown categories and context-incompatible error labels

### Requirement: DOM-02 Scope evidence ownership

The system SHALL bind evidence to the exact exercise, unit, revision and audio SHA-256 and authorize the reader, rather than accepting global ID membership.

#### Scenario: DOM-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL accept evidence owned by the selected exercise revision and audio, and SHALL reject existing evidence borrowed from another exercise, unit, revision or audio

### Requirement: DOM-03 Preserve exact Unicode claims

The system SHALL extract quoted claims with half-open Unicode codepoint offsets in the original answer, preserving repeated text, normalization and retractions.

#### Scenario: DOM-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL resolve a quoted repeated Unicode span to its exact occurrence, and SHALL reject byte/UTF-16 offsets, normalized-text drift and an untraceable quote

### Requirement: DOM-04 Separate distinct claim outcomes

The system SHALL deduplicate repeated assertions, preserve explicit retractions, scope contradictions to their actual component and keep unresolved classification/explanation separate from detection and correction under answer-components-v2.

#### Scenario: DOM-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL score resolved distinct assertions with retracted claims excluded as specified, and SHALL route unresolved primary groups to LLM reconsideration while retaining independent primary ratios for explanation-only issues

### Requirement: DOM-05 Represent exact ratios and N/A

The system SHALL store exact numerator and denominator, use null with no_opportunities or no_assertions for zero denominators, and round displayed percentages half-up to one decimal.

#### Scenario: DOM-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL produce an exact ratio and independently expected display percentage, and SHALL return N/A for zero denominators and reject invalid or negative counters

### Requirement: DOM-06 Aggregate from raw decisions

The system SHALL pool raw counters for aggregate metrics, provide domain breakdowns and never average percentages or publish a primary composite for unresolved primary claims. Optional explanation is separately scored over supplied eligible reasons, with no omission penalty.

#### Scenario: DOM-06 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL recalculate pooled counters across differently sized exercises, and SHALL reject percentage averaging and final primary metrics for unresolved primary evidence; optional rationale uncertainty affects only dependent explanation metrics

### Requirement: DOM-07 Preserve auxiliary and unobserved metrics

The system SHALL retain all 15 auxiliary formulas and keep teacher talk time, spoken pronunciation, classroom management and real engagement null in this listening-only mode.

#### Scenario: DOM-07 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL report an auxiliary value with observed counts and method provenance, and SHALL keep unobserved teacher behavior null and refuse unsupported acoustic comparisons

### Requirement: MET-01 Preserve detection.precision

The system SHALL calculate detection.precision using the exact retained formula `TP/(TP+FP)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for detection.precision, and SHALL reject invalid counters and return N/A for the zero denominator of detection.precision

### Requirement: MET-02 Preserve detection.recall

The system SHALL calculate detection.recall using the exact retained formula `TP/G` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for detection.recall, and SHALL reject invalid counters and return N/A for the zero denominator of detection.recall

### Requirement: MET-03 Preserve detection.f1

The system SHALL calculate detection.f1 using the exact retained formula `2*TP/(2*TP+FP+FN)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for detection.f1, and SHALL reject invalid counters and return N/A for the zero denominator of detection.f1

### Requirement: MET-04 Preserve detection.miss_rate

The system SHALL calculate detection.miss_rate using the exact retained formula `FN/G` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for detection.miss_rate, and SHALL reject invalid counters and return N/A for the zero denominator of detection.miss_rate

### Requirement: MET-05 Preserve detection.false_discovery_rate

The system SHALL calculate detection.false_discovery_rate using the exact retained formula `FP/(TP+FP)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for detection.false_discovery_rate, and SHALL reject invalid counters and return N/A for the zero denominator of detection.false_discovery_rate

### Requirement: MET-06 Preserve classification.coverage

The system SHALL calculate classification.coverage using the exact retained formula `LC/TP` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-06 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for classification.coverage, and SHALL reject invalid counters and return N/A for the zero denominator of classification.coverage

### Requirement: MET-07 Preserve classification.family_accuracy

The system SHALL calculate classification.family_accuracy using the exact retained formula `LF/LC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-07 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for classification.family_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of classification.family_accuracy

### Requirement: MET-08 Preserve classification.exact_accuracy

The system SHALL calculate classification.exact_accuracy using the exact retained formula `LE/LC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-08 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for classification.exact_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of classification.exact_accuracy

### Requirement: MET-09 Preserve classification.hierarchical_accuracy

The system SHALL calculate classification.hierarchical_accuracy using the exact retained formula `H/LC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-09 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for classification.hierarchical_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of classification.hierarchical_accuracy

### Requirement: MET-10 Preserve classification.hierarchical_recall

The system SHALL calculate classification.hierarchical_recall using the exact retained formula `H/G` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-10 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for classification.hierarchical_recall, and SHALL reject invalid counters and return N/A for the zero denominator of classification.hierarchical_recall

### Requirement: MET-11 Preserve correction.attempt_rate

The system SHALL calculate correction.attempt_rate using the exact retained formula `CA/TC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-11 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.attempt_rate, and SHALL reject invalid counters and return N/A for the zero denominator of correction.attempt_rate

### Requirement: MET-12 Preserve correction.strict_accuracy

The system SHALL calculate correction.strict_accuracy using the exact retained formula `CK/CA` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-12 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.strict_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of correction.strict_accuracy

### Requirement: MET-13 Preserve correction.graded_accuracy

The system SHALL calculate correction.graded_accuracy using the exact retained formula `CQ/CA` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-13 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.graded_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of correction.graded_accuracy

### Requirement: MET-14 Preserve correction.strict_recall

The system SHALL calculate correction.strict_recall using the exact retained formula `CK/GC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-14 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.strict_recall, and SHALL reject invalid counters and return N/A for the zero denominator of correction.strict_recall

### Requirement: MET-15 Preserve correction.graded_recall

The system SHALL calculate correction.graded_recall using the exact retained formula `CQ/GC` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-15 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.graded_recall, and SHALL reject invalid counters and return N/A for the zero denominator of correction.graded_recall

### Requirement: MET-16 Preserve correction.assertion_precision

The system SHALL calculate correction.assertion_precision using the exact retained formula `CK/(CA+FC)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-16 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for correction.assertion_precision, and SHALL reject invalid counters and return N/A for the zero denominator of correction.assertion_precision

### Requirement: MET-17 Preserve explanation.coverage

The system SHALL calculate explanation.coverage using the exact retained formula `EA/TE` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-17 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for explanation.coverage, and SHALL reject invalid counters and return N/A for the zero denominator of explanation.coverage

### Requirement: MET-18 Preserve explanation.strict_accuracy

The system SHALL calculate explanation.strict_accuracy using the exact retained formula `EK/EA` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-18 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for explanation.strict_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of explanation.strict_accuracy

### Requirement: MET-19 Preserve explanation.graded_accuracy

The system SHALL calculate explanation.graded_accuracy using the exact retained formula `EQ/EA` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-19 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for explanation.graded_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of explanation.graded_accuracy

### Requirement: MET-20 Preserve explanation.graded_recall

The system SHALL calculate explanation.graded_recall using the exact retained formula `EQ/GE` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-20 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for explanation.graded_recall, and SHALL reject invalid counters and return N/A for the zero denominator of explanation.graded_recall

### Requirement: MET-21 Preserve decoy.overcorrection_rate

The system SHALL calculate decoy.overcorrection_rate using the exact retained formula `DF/D` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-21 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for decoy.overcorrection_rate, and SHALL reject invalid counters and return N/A for the zero denominator of decoy.overcorrection_rate

### Requirement: MET-22 Preserve decoy.unflagged_rate

The system SHALL calculate decoy.unflagged_rate using the exact retained formula `(D-DF)/D` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-22 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for decoy.unflagged_rate, and SHALL reject invalid counters and return N/A for the zero denominator of decoy.unflagged_rate

### Requirement: MET-23 Preserve decoy.explicit_acceptability_accuracy

The system SHALL calculate decoy.explicit_acceptability_accuracy using the exact retained formula `DA/(DA+DF)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-23 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for decoy.explicit_acceptability_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of decoy.explicit_acceptability_accuracy

### Requirement: MET-24 Preserve acceptability.explicit_accuracy

The system SHALL calculate acceptability.explicit_accuracy using the exact retained formula `SA/SN` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-24 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for acceptability.explicit_accuracy, and SHALL reject invalid counters and return N/A for the zero denominator of acceptability.explicit_accuracy

### Requirement: MET-25 Preserve weighted.precision

The system SHALL calculate weighted.precision using the exact retained formula `WTP/(WTP+WFP)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-25 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for weighted.precision, and SHALL reject invalid counters and return N/A for the zero denominator of weighted.precision

### Requirement: MET-26 Preserve weighted.recall

The system SHALL calculate weighted.recall using the exact retained formula `WTP/(WTP+WFN)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-26 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for weighted.recall, and SHALL reject invalid counters and return N/A for the zero denominator of weighted.recall

### Requirement: MET-27 Preserve weighted.f1

The system SHALL calculate weighted.f1 using the exact retained formula `2*WTP/(2*WTP+WFP+WFN)` from domain/metrics.v1.yaml, with exact counters and N/A behavior.

#### Scenario: MET-27 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate an independently specified exact arithmetic case for weighted.f1, and SHALL reject invalid counters and return N/A for the zero denominator of weighted.f1

### Requirement: AUX-01 Preserve annotation.agreement

The system SHALL retain the auxiliary formula `agreements/N` for annotation.agreement with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-01 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate annotation.agreement from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for annotation.agreement

### Requirement: AUX-02 Preserve annotation.cohen_kappa

The system SHALL retain the auxiliary formula `(Po-Pe)/(1-Pe); Pe=sum_label(p_rater1(label)*p_rater2(label))` for annotation.cohen_kappa with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-02 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate annotation.cohen_kappa from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for annotation.cohen_kappa

### Requirement: AUX-03 Preserve verification.wer

The system SHALL retain the auxiliary formula `(substitutions+deletions+insertions)/reference_word_count` for verification.wer with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-03 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate verification.wer from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for verification.wer

### Requirement: AUX-04 Preserve audio.speech_rate_wpm

The system SHALL retain the auxiliary formula `60*spoken_token_count/elapsed_speech_span_seconds` for audio.speech_rate_wpm with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-04 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate audio.speech_rate_wpm from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for audio.speech_rate_wpm

### Requirement: AUX-05 Preserve audio.articulation_rate_wpm

The system SHALL retain the auxiliary formula `60*spoken_token_count/active_speech_seconds` for audio.articulation_rate_wpm with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-05 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate audio.articulation_rate_wpm from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for audio.articulation_rate_wpm

### Requirement: AUX-06 Preserve audio.pause_ratio

The system SHALL retain the auxiliary formula `internal_silent_seconds/elapsed_speech_span_seconds` for audio.pause_ratio with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-06 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate audio.pause_ratio from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for audio.pause_ratio

### Requirement: AUX-07 Preserve audio.disfluency_density

The system SHALL retain the auxiliary formula `100*reviewed_disfluency_events/spoken_token_count` for audio.disfluency_density with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-07 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate audio.disfluency_density from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for audio.disfluency_density

### Requirement: AUX-08 Preserve evaluation.coverage

The system SHALL retain the auxiliary formula `resolved_decisions/eligible_decisions` for evaluation.coverage with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-08 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate evaluation.coverage from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for evaluation.coverage

### Requirement: AUX-09 Preserve evaluation.exact_mapping_agreement

The system SHALL retain the auxiliary formula `identical_claim_to_unit_decisions/eligible_gold_decisions` for evaluation.exact_mapping_agreement with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-09 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate evaluation.exact_mapping_agreement from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for evaluation.exact_mapping_agreement

### Requirement: AUX-10 Preserve telemetry.elapsed_seconds

The system SHALL retain the auxiliary formula `submitted_at-started_at` for telemetry.elapsed_seconds with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-10 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate telemetry.elapsed_seconds from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for telemetry.elapsed_seconds

### Requirement: AUX-11 Preserve telemetry.replay_count

The system SHALL retain the auxiliary formula `count(validated_play_events)` for telemetry.replay_count with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-11 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate telemetry.replay_count from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for telemetry.replay_count

### Requirement: AUX-12 Preserve teacher.talk_time

The system SHALL retain the auxiliary formula `null` for teacher.talk_time with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-12 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate teacher.talk_time from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for teacher.talk_time

### Requirement: AUX-13 Preserve teacher.pronunciation

The system SHALL retain the auxiliary formula `null` for teacher.pronunciation with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-13 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate teacher.pronunciation from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for teacher.pronunciation

### Requirement: AUX-14 Preserve teacher.classroom_management

The system SHALL retain the auxiliary formula `null` for teacher.classroom_management with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-14 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate teacher.classroom_management from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for teacher.classroom_management

### Requirement: AUX-15 Preserve teacher.engagement

The system SHALL retain the auxiliary formula `null` for teacher.engagement with its declared observation/method limits; unavailable observations remain null.

#### Scenario: AUX-15 supported and rejected inputs

- **WHEN** the authorized operation receives supported inputs or a violating input
- **THEN** it SHALL calculate teacher.engagement from actual permitted observations using the approved method, or preserve its specified null value, and SHALL reject an invented observation or unsupported measurement for teacher.engagement
