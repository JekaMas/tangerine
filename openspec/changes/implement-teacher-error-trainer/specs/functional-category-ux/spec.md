## ADDED Requirements

### Requirement: FX-01 Non-pronunciation mutation path
The application SHALL preserve every existing grammar, vocabulary, fluency,
discourse and style/register category through request selection, mutation,
answer-key projection and scoring. Written contrasts SHALL replay to the exact
authored surface through the native mutation manifest. Timing and interaction
targets SHALL retain their own acoustic evidence limits. Correct contextual
alternatives SHALL remain acceptable, and optional explanations SHALL be scored
separately when supplied.

#### Scenario: All written non-pronunciation contrasts
- **WHEN** each constructed written contrast is admitted as its selected category
- **THEN** the native manifest replays the exact surface and retains the category
- **AND** an unselected category, changed baseline or no-op repair is rejected

### Requirement: FX-02 Effective preparation and saved failure recovery
The application SHALL expose the effective request at narrow and desktop widths,
provide a short default preparation path and retain every optional control.
Saved failures SHALL show a useful reason and explicit recovery action without
automatically restarting generation.

#### Scenario: Advanced override and resumed failure
- **WHEN** advanced settings override simple level/count choices
- **THEN** the visible summary shows the actual overridden values at 320 and 390 px
- **AND** a reopened failed preparation shows its saved reason and Resume action

### Requirement: FX-03 Recognizable saved records
The application SHALL project original exercise titles, saved answer excerpts and
existing creation dates through native list responses and present readable status
and local dates. Legacy missing metadata SHALL have honest fallbacks. Complete
identities SHALL remain available and repeated titles SHALL remain distinct.

#### Scenario: Saved answers and audio
- **WHEN** a user reopens history or stored audio
- **THEN** title, date, state and record links identify the correct saved record
- **AND** missing metadata does not produce an invented topic, date or answer

### Requirement: FX-04 Result hierarchy and finite passage replay
The application SHALL show a completed primary result before the saved answer,
keep explanation results distinct and preserve all detailed findings. Each saved
audio interval SHALL offer explicit finite replay on the existing recording.
Manual seek, pause, full playback or another range SHALL cancel the old range.
Opening results SHALL never autoplay, synthesize or grade.

#### Scenario: Completed result and controlled replay
- **WHEN** a completed answer is reopened and a passage is replayed
- **THEN** the result precedes the collapsed answer and playback pauses at the end
- **AND** switching or manually seeking does not retain an old stop handler

### Requirement: FX-05 Guided optional tools
The application SHALL offer ordinary fields for a labelled constructed report and
an experiment starter using actual configured defaults, retaining advanced JSON
and file import. Saving a starter SHALL make no model call. Cleanup SHALL select
named saved records by complete identity and retain explicit preview/apply.

#### Scenario: Start without JSON or identifiers
- **WHEN** a user chooses a starter or named cleanup record
- **THEN** existing native owners receive a valid definition or exact selected ID
- **AND** invalid input preserves values, with no inference or deletion on selection

### Requirement: FX-06 Functional and visual user journeys
The application SHALL retain its eleven routes, keyboard-operable navigation,
readable Source Sans 3 body text and clear primary actions at desktop and narrow
widths. Important quantitative captions SHALL use at least 13 CSS px. Selected
success, failure, retry and saved states SHALL have actual browser observations.

#### Scenario: Main paths at desktop and narrow widths
- **WHEN** the user navigates, selects practice controls, reopens saved work and results
- **THEN** the controls and content reflow without page overflow or covered focus
- **AND** screenshots, actions and independently expected saved values support the verdict
