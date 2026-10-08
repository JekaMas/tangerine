<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: PROV-01 Named providers
The application MUST use an explicitly selected active profile from `domain/providers.v1.yaml` or the versioned configurable registry described in `docs/llm-configuration.md`. The profile MUST name the service, model, role, and request format. A missing key or unavailable profile MUST stop that operation.

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

### Requirement: PROV-03 Profile changes
A provider change MUST require a new profile version and explicit owner approval. It MUST also require evaluation against the applicable gold data. The application MUST NOT silently change models, voices, or thresholds.

#### Scenario: PROV-03 Permitted behavior
- **GIVEN** An owner approves one exact profile change.
- **WHEN** The team obtains the required evaluation evidence.
- **THEN** The release records the approval and measured results.

#### Scenario: PROV-03 Boundary behavior
- **GIVEN** A new profile has no held-out evaluation.
- **WHEN** A publisher requests release.
- **THEN** The profile remains blocked despite a valid JSON response.
