<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: LOCAL-01 Local containers
The application MUST start locally through Docker Compose with real provider configuration. It MUST require no host language runtime or external database. Missing application images MUST remain a release blocker.

#### Scenario: LOCAL-01 Permitted behavior
- **GIVEN** The release supplies real images and credentials.
- **WHEN** The operator starts the Compose deployment.
- **THEN** The teacher interface uses the local web origin.

#### Scenario: LOCAL-01 Boundary behavior
- **GIVEN** The application image does not exist.
- **WHEN** The operator attempts startup.
- **THEN** Startup fails without a substitute application or fake success response.

### Requirement: LOCAL-02 Limited access
Only the web port MUST bind to host loopback by default. Each container MUST receive only the secrets for its role. Provider keys MUST NOT enter browser assets or image layers.

#### Scenario: LOCAL-02 Permitted behavior
- **GIVEN** The operator uses the default local topology.
- **WHEN** The containers start.
- **THEN** Database and storage ports remain inside the container network.

#### Scenario: LOCAL-02 Boundary behavior
- **GIVEN** The deployment selects development authentication outside local mode.
- **WHEN** The API starts.
- **THEN** The API refuses that configuration.

### Requirement: LOCAL-03 Persistent startup
Startup MUST wait for database, migration, and private-storage readiness. Persistent volumes MUST retain attempts and media after a normal restart. Initialization MUST NOT create invented exercises, reviews, or scores.

#### Scenario: LOCAL-03 Permitted behavior
- **GIVEN** The operator stops and restarts containers without volume deletion.
- **WHEN** The services become ready.
- **THEN** Existing case and attempt records remain available.

#### Scenario: LOCAL-03 Boundary behavior
- **GIVEN** A fresh installation has no reviewed media.
- **WHEN** Initialization finishes.
- **THEN** The library stays empty instead of receiving a fake seed case.
