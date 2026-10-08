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

### Requirement: CFG-02 Qualify strict output and failures

A configured LLM SHALL qualify each full original closed schema and prompt contract before use. JSON syntax alone is insufficient. Unsupported schema keywords or transport formats SHALL fail qualification without deleting constraints; extra fields, fabricated spans, wrong-subject references, truncation, refusal and malformed output SHALL fail server checks or become the specified review/failure state. LLM output SHALL never create numerical grades, observed acoustics or human approvals.

#### Scenario: CFG-02 Complete supported behavior

- **GIVEN** Exercise each real configured role with its full schema and approved accepted/rejected boundary input after implementation authorization.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Schema support, server invariants and named positive/negative real-provider receipts are recorded for every role, including DEC-001 only after its exact contract decision.

#### Scenario: CFG-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A schema-valid unsupported semantic claim, numeric grade, repaired JSON retry or stripped constraint cannot qualify the profile.

### Requirement: CFG-03 Freeze provider provenance and caches

Attempts SHALL freeze profile/model/requested and returned model metadata, endpoint, prompt and schema hashes, reasoning/supported settings, input/case/answer hashes and versions. Exact matching stage results alone are reusable. Profile changes or moving-alias drift SHALL invalidate affected calibration/cache evidence and require qualification and applicable held-out evaluation before production acceptance. Development-profile selection is authorized by the current user; it does not prove empirical equivalence or approve speech-provider substitutions.

#### Scenario: CFG-03 Complete supported behavior

- **GIVEN** Retry the same saved answer with unchanged profile, then explicitly select a new profile or observe returned-model alias drift.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Only identical frozen-stage inputs reuse receipts; changed configuration starts a separately recorded evaluation/profile version.

#### Scenario: CFG-03 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** Old provider results or gold measurements cannot qualify a changed model, settings, schema, prompt or profile.

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
