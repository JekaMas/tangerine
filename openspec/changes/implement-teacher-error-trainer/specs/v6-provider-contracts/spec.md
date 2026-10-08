<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: PROV-01 Named providers
The application MUST use an explicitly selected active profile from `specification/v2/domain/providers.v1.yaml` or the versioned configurable registry described in `specification/v2/docs/llm-configuration.md`. The profile MUST name the service, model, role, and request format. A missing key or unavailable profile MUST stop that operation.

#### Scenario: PROV-01 Permitted behavior
- **GIVEN** An active profile has real credentials.
- **WHEN** The adapter sends a request.
- **THEN** The request uses the named endpoint and model.

#### Scenario: PROV-01 Boundary behavior
- **GIVEN** A configured model is unavailable.
- **WHEN** The adapter receives that failure.
- **THEN** The adapter does not use a mock or a different model.

### Requirement: PROV-02 Provider limits
The adapter MUST obey each profile capability and limitation. Requested IPA MUST NOT count as observed IPA. Schema-conforming text MUST NOT count as independently proven meaning.

#### Scenario: PROV-02 Permitted behavior
- **GIVEN** A service returns a pronunciation score.
- **WHEN** The application stores that result.
- **THEN** The evidence identifies the service and its advisory scope.

#### Scenario: PROV-02 Boundary behavior
- **GIVEN** A requested constraint exceeds the profile capability.
- **WHEN** The operator starts generation.
- **THEN** The operation stops with the unsupported constraint.

### Requirement: PROV-03 Configured profile changes

A changed provider profile SHALL be versioned and explicitly selected in settings. No additional owner signature, canary or heldout certification SHALL be required before local use.

#### Scenario: PROV-03 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL run the selected changed profile and record actual metadata

#### Scenario: PROV-03 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never silently substitute a different provider/model
