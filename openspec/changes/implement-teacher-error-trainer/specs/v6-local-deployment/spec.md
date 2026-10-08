<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: LOCAL-01 Local containers
The application MUST start from the open-source GitHub source ZIP or clone through the supplied local helper and Docker Compose with real provider configuration. The downloaded source MUST include all application build inputs and MUST NOT depend on Git metadata, workflow submodules or host language runtimes. Application images MUST build locally on first start; prebuilt application image distribution and a formal release manifest are not required. Missing inputs or a failed local build MUST produce a clear startup error.

#### Scenario: LOCAL-01 Permitted behavior
- **GIVEN** The user extracts the GitHub source ZIP with complete build inputs and provides keys for the intended provider operations.
- **WHEN** The user invokes the supplied local start helper.
- **THEN** The teacher interface uses the local web origin.

#### Scenario: LOCAL-01 Boundary behavior
- **GIVEN** A required source build input is absent or the local build fails.
- **WHEN** The operator attempts startup.
- **THEN** Startup reports the actual build/input error without a substitute application or fake success response. Absence of a prebuilt application image alone is normal on first start.

### Requirement: LOCAL-02 Limited access
Only the web port MUST bind to host loopback and MUST reject non-loopback exposure configuration. Each container MUST receive only the secrets for its service. Provider keys MUST NOT enter browser assets or image layers.

#### Scenario: LOCAL-02 Permitted behavior
- **GIVEN** The operator uses the default local topology.
- **WHEN** The containers start.
- **THEN** Database and storage ports remain inside the container network.

#### Scenario: LOCAL-02 Boundary behavior
- **GIVEN** The deployment configures a non-loopback web binding or exposes an internal service port.
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
