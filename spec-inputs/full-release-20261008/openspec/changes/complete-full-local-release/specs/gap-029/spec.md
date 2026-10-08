## ADDED Requirements

### Requirement: SPEC-029 Complete role input and configuration binding schemas

Every model stage MUST receive its complete allowed input under a hashed provider, prompt, schema, policy, and permission binding.

The normative artifacts are:

- `contracts/effective-binding.schema.json`.
- `contracts/provider-receipt.schema.json`.
- `contracts/stage-cache.schema.json`.
- `contracts/taxonomy-context.schema.json`.
- `prompts/manifest.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-029`.
- **THEN** The server supplies actual taxonomy definitions and authorized excerpts rather than inaccessible version IDs alone. The stage receipt records that exact payload.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-029`.
- **THEN** Blind extraction receives the key, an unknown configuration field enters a stage, or a cache entry belongs to other inputs. The operation is rejected.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
