# full-validation-policy specification

## ADDED Requirements

### Requirement: VALFULL-01 Preserve full validation reports

The system SHALL provide all VAL-STRUCT/MAP/COVER/REPAIR/REPEAT/AUDIO/SCORE/ISOLATION reports using the approved thresholds/populations in specification/v2/domain/validation-policy.yaml. These SHALL not block startup or ordinary use. Repair applies only to correction-eligible domains; all122leaves/all42equations remain.

#### Scenario: VALFULL-01 Complete supported behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL report actual denominators, label origin and insufficient_data separately

#### Scenario: VALFULL-01 Incomplete or forbidden behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never count a nonexistent acceptable-variant repair population or report an insufficient sample as a pass
