<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: VER-01 Publication checks
The application MUST apply the applicable gates in `docs/verification-v1.md`. It MUST store `contracts/verification-report.schema.json` output. Structural failures, missing rights, and corrupt audio MUST block publication.

#### Scenario: VER-01 Permitted behavior
- **GIVEN** All applicable gates contain supporting PASS evidence.
- **WHEN** Authorized reviewers approve the case.
- **THEN** The case becomes eligible for publication.

#### Scenario: VER-01 Boundary behavior
- **GIVEN** ASR agrees with the transcript.
- **WHEN** The intended error is absent from the audio.
- **THEN** The case fails its target check despite the ASR agreement.

### Requirement: VER-02 Acoustic evidence
The application MUST distinguish a requested sound from an observed sound. It MUST NOT infer phone identity from a canonical accuracy score. Unsupported automatic measurements MUST remain unavailable until qualified human observation.

#### Scenario: VER-02 Permitted behavior
- **GIVEN** A reviewer hears the target substitution.
- **WHEN** The reviewer records its interval and observed IPA.
- **THEN** The evidence retains the reviewer identity and audio hash.

#### Scenario: VER-02 Boundary behavior
- **GIVEN** A voice lacks supported automatic prosody assessment.
- **WHEN** The adapter evaluates that audio.
- **THEN** The result requires review and contains no invented score.

### Requirement: VER-03 Independent reviews
Two distinct qualified reviewers MUST listen independently before they read the key. They MUST approve each unit and the final audio. A disagreement MUST require a third adjudicator or keep publication blocked.

#### Scenario: VER-03 Permitted behavior
- **GIVEN** Two independent reviewers approve all final units.
- **WHEN** The publisher requests publication.
- **THEN** Both approvals must identify the same final audio hash.

#### Scenario: VER-03 Boundary behavior
- **GIVEN** Reviewers approved an earlier audio version.
- **WHEN** The author changes the audio.
- **THEN** The previous approvals cannot authorize the changed file.
