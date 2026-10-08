# Configurable LLM contract

This is a specification, not a configured application adapter. The user explicitly requested configurable LLM support and DeepSeek 4.1 fast for testing on 2026-10-08. That request authorizes this development profile plan; it is not evidence of a live call, approved test gold or production calibration. The original four profiles and five prompt hashes remain unchanged in domain/providers.v1.yaml and prompts/manifest.yaml.

## Roles and profiles

An operator selects a versioned role binding for case_generation, blind_claim_extraction, claim_mapping, mapping_audit and feedback. linguistic_audit is also configurable but remains blocked on DEC-001's exact prompt/schema. Every role retains its original disclosure and schema contract. Models only propose bounded semantic decisions; code derives all scores. TTS/ASR/PA are separate speech profiles and are unaffected by LLM selection.

The proposed development registry is domain/providers.configurable.v1.yaml. Effective profile lookup combines the unchanged baseline registry with explicitly enabled versioned overlays; duplicate IDs or unknown role bindings fail startup. The default for future development testing is deepseek-v41-flash-local-test-v1. Production activation is an explicit operator action and requires applicable real held-out evaluation. A missing/unavailable selected provider stops that operation. No automatic provider, model, reasoning, voice or threshold fallback is permitted.

## Discovered local access

A secret-safe read of /Users/jekamas/.codex/config.toml found model_providers.deepseek with base_url https://api.deepseek.com/, wire_api responses, and env_key DEEPSEEK_API_KEY. The current process has that variable present; neither its value nor full Codex/auth configuration was copied. The configured model catalog includes deepseek-flash and low/high/max reasoning levels. Codex's existing default model and all configuration remain unchanged. Presence of a credential reference is not a successful authentication or quota check. Future service execution must inject the environment secret into its server process explicitly; it must not mount the Codex config or credential store.

DeepSeek's [official update log](https://api-docs.deepseek.com/updates/) identifies DeepSeek-V4.1-Flash with API model ID deepseek-flash. Its [Codex integration guide](https://api-docs.deepseek.com/quick_start/agent_integrations/codex/) documents the Responses transport and base URL. Use low reasoning for the requested fast development mode. A moving alias is not an immutable model snapshot: retain requested model, returned model metadata and provider release/date observations, and requalify detected changes.

The [Responses API guide](https://api-docs.deepseek.com/guides/responses_api/) documents Responses calls to model deepseek-flash at https://api.deepseek.com. Full strict-schema support for every supplied schema, exact supported settings and real latency remain unqualified. Do not treat JSON-object mode as equivalent to strict JSON Schema or copy OpenAI-only sampling fields blindly. No inference request was made in this review.

## Operator configuration and receipts

Configuration includes profile ID/version/environment, provider, model, HTTPS base URL, wire format, roles, reasoning mode, supported sampling/output limits, stream=false, tool policy, storage/retention settings and secret environment reference. The exact request payload uses only qualified supported settings. Endpoint configuration is server/operator controlled; browser input cannot select an arbitrary URL. Explicit local development endpoints require a separately identified profile and cannot inherit remote-provider calibration.

Freeze these values and the exact role prompt, schema, input, original-answer and case hashes before a stage. Receipts contain requested/returned model metadata, duration/usage, output or refusal/error, and real provenance without credentials. Stage reuse requires every frozen identity to match. A profile/model/prompt/schema/settings change starts a new configuration version, invalidates affected stage reuse and requires applicable provider qualification/calibration; it never rewrites historical results.

The original prompt manifest names the OpenAI baseline. A profile binding must explicitly name the same prompt bytes and their hash plus the selected DeepSeek profile; it must not rewrite the immutable manifest or imply old OpenAI evidence qualifies DeepSeek. Audit uses a separate request under its selected role binding, but shared-model consistency is not independent scientific truth.

## Future qualification cases

Before using a live role, test a supported real closed-schema result and its rejection boundaries: extra/unknown fields, wrong types/enums/IDs, unsupported schema keywords, malformed JSON, truncation, refusal, fabricated answer quotes, UTF-8/UTF-16 versus codepoint offsets, wrong case/unit/audio evidence, invented numeric grades and role disclosure leakage. Server semantic checks remain mandatory after structural parsing. No JSON repair loop, favourable-output retry or stripped schema constraint may turn a failed response into acceptance.

All such positive and negative cases are planned in CFG-01–CFG-04 and the recovered role requirements. No tests or adapters were implemented in this spec-only turn. Real calibration still requires approved inputs, genuine independently labelled teacher answers and untouched grouped holdout data. Existing cloud disclosure acknowledgment and source-specific upload permission precede transfer; source personal identity and consent artifacts stay outside prompts.
