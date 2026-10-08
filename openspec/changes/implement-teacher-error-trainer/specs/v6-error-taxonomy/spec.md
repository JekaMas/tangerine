<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: TAX-01 Full domain registry
The application MUST retain all 122 existing taxonomy IDs. Every leaf MUST have its definition, inclusion rules, exclusions, correction rules, and evidence requirements. A missing provider capability MUST NOT remove a language domain.

#### Scenario: TAX-01 Permitted behavior
- **GIVEN** A blueprint selects a registered pronunciation category.
- **WHEN** The compiler plans the case.
- **THEN** The pronunciation target remains required throughout generation and review.

#### Scenario: TAX-01 Boundary behavior
- **GIVEN** A generator supplies an unknown category ID.
- **WHEN** The API reads that candidate.
- **THEN** The API rejects the ID rather than extending the registry.

### Requirement: TAX-02 Context and permitted variants
Each judgment MUST use the declared variety, register, task, and context. Accent alone MUST NOT establish an error. A permitted variant MUST NOT count as a true error.

#### Scenario: TAX-02 Permitted behavior
- **GIVEN** The case context permits the observed form.
- **WHEN** The author includes that form as a negative control.
- **THEN** The unit has `acceptable` judgment, not `true_error`.

#### Scenario: TAX-02 Boundary behavior
- **GIVEN** A pronunciation differs from a preferred accent.
- **WHEN** No task-specific defect has supporting evidence.
- **THEN** The reviewer cannot mark the difference as a confirmed error.

### Requirement: TAX-03 Detection units
One detection unit MUST identify one assessable event. Each unit MUST have one primary reporting domain. Additional labels MUST NOT increase the opportunity count.

#### Scenario: TAX-03 Permitted behavior
- **GIVEN** One event has a primary and a secondary category.
- **WHEN** The backend counts true opportunities.
- **THEN** The event contributes one unit to its primary domain.

#### Scenario: TAX-03 Boundary behavior
- **GIVEN** Two labels describe the same target event.
- **WHEN** An author attempts to count both as separate errors.
- **THEN** The overlap review blocks double counting.
