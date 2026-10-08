# Provider contracts

`domain/providers.v1.yaml` names the retained v5 baseline. It does not claim that the baseline is the best current model.
No live account or quality result exists in this package. The baseline must pass the real corpus gates before release.
An unavailable model, voice, or region produces `CONFIG_UNAVAILABLE`. Do not select a similar service automatically.

## OpenAI language stages

Use the HTTPS Responses API with `gpt-4.1-2025-04-14`.
Use temperature zero, `stream:false`, `store:false`, and no tools.
Use the closed schema for the stage through `text.format` with strict JSON Schema output.
The exact fields appear in the provider registry. [SRC-GPT41, SRC-STRUCTURED]

Keep trusted instructions separate from the JSON-encoded untrusted payload.
Do not put a teacher answer inside a system instruction.
`store:false` does not prove zero provider retention. The source permission must cover external processing.
Temperature zero does not guarantee identical or true outputs.

Record the profile, prompt, schema, input, and output hashes. Record the returned request ID, usage, and outcome.
Do not put API keys in those records, browser code, prompts, or logs.

Extraction receives the frozen teacher text, public task instructions, and interface language.
Extraction receives no transcript, taxonomy shortlist, or answer key.
The backend assigns claim IDs after it checks exact source spans.
Mapping receives the checked claims, reviewed key, and permitted identifiers.

The audit is a separate request to the same registered model. It is a consistency check, not independent scientific evidence.
The audit request must not receive the first mapper result before its own decision.
Compare claim IDs, stance, target, and proposition sets. A relevant difference requires review.
Do not retry until both outputs agree. Unparsed substantive text also requires review.

No language stage calculates a numerical score. The backend is the only score authority.
A new correction alternative requires review. Absence from the key is not proof that the alternative is wrong.
A suspected additional error requires review of the recording and key.

## Azure synthesis

Use the named REST SSML profile and a registered voice for the locale.
During preflight, obtain the voice inventory from the selected region. Require the exact voice IDs in the configuration.
Record the inventory date and hash. Do not substitute another voice.

Compile SSML from the typed render operations. Escape text and attributes before the request.
Do not accept arbitrary XML, custom namespaces, remote audio URLs, or voice cloning.
The active package permits no human-recording fallback. Such a change requires a separate owner approval.

The existing master format is 24 kHz, mono, 16-bit PCM WAV.
If the delivery format changes, measure and review the final encoded file.
Keep the turn offsets and final hashes. Requested rate, pitch, pause, and IPA remain intended values.

A voice ID does not identify an immutable cloud engine.
A provider change requires real canary evidence before new publication.
Reuse historical published audio bytes. Do not synthesize a historical case again under the same version.

A failed target permits at most the existing three total render attempts.
After that limit, block the candidate. Do not remove its target or silently replace its source.
SSML phonemes are synthesis controls, not observed phoneme evidence. [SRC-AZURE-IPA, SRC-AZURE-VOICES]

## Audio evidence

Use `whisper-1` with `verbose_json` and word timestamps.
Do not send the answer key as a recognition prompt. Save the independent ASR hypothesis before alignment.
Its timestamps are proposals, not forced-alignment proof. Reviewed intervals remain authoritative. [SRC-ASR]

Use the Azure short-audio REST profile for its documented advisory fields.
Send 16 kHz mono PCM chunks of no more than 25 seconds.
Encode the registry's pronunciation-assessment header as base64 JSON. Preserve the actual response and profile hash.

The registered prosody profile applies to `en-US` only.
For an unsupported locale or absent field, return `advisory_unavailable`.
Do not create a zero score in place of a missing value. [SRC-AZURE-REST, SRC-AZURE-PA]
A phoneme accuracy score is not observed IPA.
Observed IPA requires a qualified transcription or an explicitly validated observed-phone method.

## Preflight and release

Before a real request, make sure that keys, approved profiles, and source permissions exist.
Before a release, exercise every required adapter with real permitted inputs.
Use an owner-approved diagnostic case, not an invented success response.
Save actual output bytes and the resulting decision. A failed or unperformed check cannot pass.

The package has no Groq, Anthropic, or ElevenLabs fallback. Competitor providers do not become project requirements.
Any new provider requires a separate approval, a versioned contract, and fresh measured evidence.
Do not bypass provider access restrictions.
