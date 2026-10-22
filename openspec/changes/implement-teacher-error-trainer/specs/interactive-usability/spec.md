# Ordinary exercise controls and visible checking

## ADDED Requirements

### Requirement: USE-01 Ordinary exercise controls

The Prepare form SHALL expose topic, speaker count, approximate word length, optional A1–C2 level, selectable broad mistake families and optional exact mistake count without requiring JSON. Empty families and blank count mean automatic selection; zero count means a control-only exercise. All eight existing family selections, including broad pronunciation and its two subdomains, SHALL remain available. The request SHALL retain these values through the existing blueprint expansion and frozen preparation. Advanced blueprint overrides SHALL retain their documented precedence and remain accessible. Failed requests SHALL retain the form values; invalid local JSON or numeric input SHALL not launch generation. The saved preparation display SHALL show its requested settings without exposing the answer key.

#### Scenario: USE-01 Selected, automatic and rejected controls

- **WHEN** a user selects B2, two speakers, 180 approximate words, grammar and lexis, and three mistakes, or selects automatic/zero alternatives
- **THEN** the real blueprint owner saves exactly those request values and all requested speaker levels; blank count is null, zero remains zero, and a failed generation retains the controls
- **AND** malformed advanced JSON, a negative/fractional count or unsupported level/family never becomes an accepted generation request

### Requirement: USE-02 Visible foreground checking

The listening page SHALL acknowledge the saved immutable answer while its synchronous submit/check request is still active, show elapsed checking time and the current stage derived from durable checkpoints, and display saved findings and the native score before optional comments complete. Reading progress SHALL invoke no model, regrade, or replacement submission. No queue, background evaluation, fabricated percentage or automatic retry SHALL be introduced. Completed, failed and historical result views SHALL preserve existing numeric/semantic content.

#### Scenario: USE-02 Saved answer and score during checking

- **WHEN** the extraction, matching or feedback response is held at the test-owned external model boundary
- **THEN** the browser shows saved-answer acknowledgement and the corresponding stage from read-only state; the score appears during held feedback and comments are shown as in progress
- **AND** repeated reads do not increase model-call counts or expose private native/provider fields

### Requirement: USE-03 Checking failure and lifecycle

Foreground progress reads SHALL be sequential and stop when the action completes or the page unmounts. A progress-read failure SHALL not cancel the active submission or overwrite the local answer. An interrupted submit SHALL reconcile durable saved state before claiming that saving failed. Feedback failure SHALL preserve the score and offer the existing explicit feedback-only retry; no extraction or mapping is repeated by that retry.

#### Scenario: USE-03 Read failure, completion and explicit retry

- **WHEN** a progress read fails during checking, comments fail, or the caller leaves the page
- **THEN** supported saved work remains visible/recoverable, completed or abandoned observers stop, and only an explicitly requested retry performs further evaluation
- **AND** the retry preserves the saved answer and exact score and reuses extraction/mapping checkpoints
