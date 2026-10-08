# full-validation-policy specification

## ADDED Requirements

### Requirement: VALFULL-01 Preserve every validation gate

Release SHALL satisfy every recovered VAL-STRUCT/MAP/COVER/REPAIR/REPEAT/AUDIO/SCORE/ISOLATION gate in domain/validation-policy.yaml for fixed versions. Precision SHALL be >=0.98 overall and >=0.95 per observable domain with >=100 human-labelled eligible mappings/domain; coverage >=0.90 overall and per domain; correction agreement >=0.95 on >=100 attempts/domain with every critical counterexample correct; repeat mapping agreement >=0.99 over three identical fixed holdout runs. All 122 leaves/control types and exact rational metrics SHALL remain in scope. Thresholds/weights remain inherited policy candidates under DEC-008, with no sample-deficient PASS.

#### Scenario: VALFULL-01 Complete supported behavior

- **GIVEN** Use fixed approved versions, untouched grouped holdout and real per-domain human labels; compare against all exact gate denominators.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Each gate includes actual numerator/denominator, abstentions, version hashes, applicability, approvals and sufficient samples.

#### Scenario: VALFULL-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** High aggregate performance, omitted domain, small denominator, tuned/reused holdout or unapproved numerical policy cannot qualify release.
