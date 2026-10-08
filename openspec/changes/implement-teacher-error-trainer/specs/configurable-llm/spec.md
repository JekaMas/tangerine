# configurable-llm specification

## ADDED Requirements

### Requirement: CFG-01 Select versioned LLM profiles

The application SHALL configure provider, model, API base URL, wire format, reasoning mode, supported sampling settings, secret environment reference and role-to-profile bindings through operator-controlled versioned profiles. docs/llm-configuration.md SHALL define the DeepSeek 4.1 fast development profile requested by the user while preserving the original OpenAI baseline. No client-provided endpoint, silent fallback or automatic Codex configuration mutation is permitted.

#### Scenario: CFG-01 Complete supported behavior

- **GIVEN** Select DeepSeek fast for development extraction/mapping/audit/generation/feedback; separately select the original OpenAI baseline.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The explicitly selected role sends the documented endpoint/model/settings and retains the selected profile version.

#### Scenario: CFG-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** Unknown role, client endpoint, missing key, unsupported setting or unavailable selected model stops the affected operation without fallback.

### Requirement: CFG-02 Tolerant semantic output projection

The system SHALL normalize harmless reply fences/prefixes/additive fields, project supported wire schemas and allow one same-profile JSON fallback/output repair under the deadline. Canonical semantic references and quote content SHALL remain valid.

#### Scenario: CFG-02 Complete supported behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL accept a uniquely valid projected semantic object despite harmless wrapping

#### Scenario: CFG-02 Incomplete or forbidden behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL preserve failure for conflicting valid objects or fabricated source content after repair

### Requirement: CFG-03 Record provider provenance and usable cache

The system SHALL freeze actual effective profile, request/returned model and input versions and reuse only matching completed semantic stages. Changed profiles SHALL work without mandatory canary or holdout qualification; diagnostics retain actual versions.

#### Scenario: CFG-03 Complete supported behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL run the explicitly changed profile and record its actual receipts

#### Scenario: CFG-03 Incomplete or forbidden behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never silently switch provider or reuse another input binding

### Requirement: CFG-04 Keep credentials server private

LLM secrets SHALL resolve from a server-only environment reference. Codex configuration is read-only discovery evidence, not application runtime configuration. Secret values/full config/auth stores SHALL NOT be copied into the repository, image, browser, prompt or logs. Cloud disclosure acknowledgment and source-use permission SHALL precede external transfer; identity/consent material SHALL not be sent to the model.

#### Scenario: CFG-04 Complete supported behavior

- **GIVEN** Use a server secret reference and inspect request/browser/image/log boundaries; remove the referenced key in the negative case.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Authorized requests use the server reference and secret-safe receipts; browser assets and request prompts contain no credential or identity/consent record.

#### Scenario: CFG-04 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** Missing credentials or upload permission fail before a call, and a secret-containing browser/log/image artifact blocks acceptance.
