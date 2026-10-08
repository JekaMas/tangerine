## ADDED Requirements

### Requirement: BP-01 Typed targets
A blueprint MUST define its format, speaker profiles, duration limits, and error targets. Each target MUST refer to the taxonomy registry. The compiler MUST reject conflicting constraints rather than silently change them.

#### Scenario: BP-01 Permitted behavior
- **GIVEN** A blueprint contains supported and consistent constraints.
- **WHEN** The author submits it.
- **THEN** The API stores its version without publishing a case.

#### Scenario: BP-01 Boundary behavior
- **GIVEN** The structured CEFR level conflicts with a persona description.
- **WHEN** The compiler examines the blueprint.
- **THEN** The conflict requires a correction, not a guessed precedence.

### Requirement: BP-02 Public context
A blueprint MUST separate public task context from private targets. Public context MUST state the variety and task information necessary for fair judgment. It MUST NOT reveal the answer key.

#### Scenario: BP-02 Permitted behavior
- **GIVEN** Register affects whether a form is permitted.
- **WHEN** The teacher opens the exercise.
- **THEN** The public context states that register without identifying the target form.

#### Scenario: BP-02 Boundary behavior
- **GIVEN** A public field contains hidden error counts.
- **WHEN** The server prepares a teacher response.
- **THEN** The response fails its disclosure check.

### Requirement: BP-03 Requested answer components
The case MUST define detection, classification, correction, and explanation requirements before answer entry. Unrequested components MUST not reduce the composite. Missing requested components MUST contribute zero coverage when opportunities exist.

#### Scenario: BP-03 Permitted behavior
- **GIVEN** The exercise requests corrections.
- **WHEN** The teacher finds an error but gives no correction.
- **THEN** Detection remains credited and correction coverage is zero.

#### Scenario: BP-03 Boundary behavior
- **GIVEN** The exercise does not request explanations.
- **WHEN** The backend calculates the composite.
- **THEN** The explanation component is not applicable and cannot reduce the score.
