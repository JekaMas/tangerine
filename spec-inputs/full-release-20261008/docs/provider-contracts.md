# Provider contracts

The profile registry names the exact endpoints, models, voices, formats, and key variables.
The default LLM profile is `deepseek-flash-low-v1`. The OpenAI snapshot remains an explicitly selectable alternative.
This selection preserves the supplied report's configurable DeepSeek development scope.
Neither profile has live qualification evidence in this package.

## Role inputs

The prompt manifest binds every stage to one exact input and output schema.
Generation receives a blueprint and only rights-cleared selected source excerpts. It never receives fabricated corpus records.
The linguistic audit receives the exact candidate, public context, and correction definitions. It produces advisory findings only.
Extraction receives the exact teacher answer, requested components, and language. It receives no transcript or key.
Mapping and mapping audit receive the same frozen extraction, permitted evaluation key, actual alias entries, and scoped evidence.
The audit does not receive the mapper result.
Feedback receives accepted item decisions, original teacher claims, approved rationale text, issues, and an optional complete score.
No role receives reviewer identity documents, consent documents, storage credentials, or provider keys in its text input.

## OpenAI Responses

Send POST to `https://api.openai.com/v1/responses` with Bearer authentication.
Set `model` to `gpt-4.1-2025-04-14` for the baseline profile.
Put the exact trusted prompt in `instructions`.
Put the canonical input JSON in one user input message. Do not interpolate it into trusted instructions.
Set `text.format` to the projected JSON schema with `type=json_schema`, a stable name, and `strict=true`.
Set `stream=false`, `store=false`, `tools=[]`, and the fixed stage output cap.
Use temperature zero for this non-reasoning snapshot. Do not send an unsupported reasoning control.

Require HTTP success and top-level response status `completed`.
Read only assistant message content blocks of type `output_text`, in documented output order.
A refusal block, tool-call block, incomplete status, failed status, or missing visible text is a failure.
Concatenate only consecutive output_text blocks from that one assistant message.
Require exactly one complete JSON object with no trailing non-whitespace text.
Do not concatenate different assistant messages or reasoning text into a plausible object.
Preserve raw response bytes before decoding. Apply full local schema and semantic checks after parsing.

## DeepSeek Responses

Send POST to `https://api.deepseek.com/responses` with Bearer authentication.
Set the requested model to `deepseek-flash` and reasoning effort to `low`.
This identifier is a provider alias, not an immutable snapshot.
Use top-level `instructions` for trusted stage instructions.
DeepSeek treats an input `developer` message as user input. Do not use it as the trusted boundary.
Send the canonical stage DTO as untrusted user content.
Use `text.format` JSON schema, `stream=false`, and the declared output cap.
Do not rely on ignored parameters such as metadata, truncation, background processing, conversation state, or prompt-cache keys.
Do not set temperature as a promised control in this reasoning profile.
Read only the completed visible assistant output under the same single-object rule.
Never use reasoning content as output JSON, repair material, evidence, or teacher feedback.
Record returned model identity and input/output/reasoning token fields when present. Missing usage remains unknown.

## Schema projection

The full application schema remains authoritative after every provider response.
The projection registry records a disposition for every keyword that the source schema uses.
Copy type, properties, required, enum, and closed additionalProperties directly.
Replace const with a one-value enum.
Resolve local references from the exact hashed bundle. Retain reusable definitions to prevent uncontrolled size expansion.
Copy supported anyOf branches. For a discriminated oneOf, send anyOf and enforce exclusive branch selection locally.
Remove only annotation keywords such as title, description, examples, and schema ID when the provider does not accept them.
Check length, range, format, pattern, uniqueness, conditional, and cross-reference constraints locally even if the wire schema also carries them.
If a provider rejects a structural keyword required for an unambiguous output shape, mark the binding incompatible.
Do not drop that keyword silently or replace the stage with free text.
Do not send self-recursive raw source trees to a model. Generation uses bounded authorized excerpts instead.
A wire-schema success does not prove complete application conformance or semantic correctness.

## Results and cache

The API assigns receipt IDs, input digests, and operation metadata. Models cannot invent these fields.
A parsed payload enters the completed cache only after schema, scope, conditional, and domain checks pass.
A cache entry is private and bound to exact answer, case, audio, prompt, schemas, adapter, profile, and permission epoch.
Changing any binding invalidates reuse but preserves prior evidence.
The request-wide retry budget and deadline apply to both adapters. Their SDKs cannot retry independently.

## Speech profiles

Azure synthesis accepts only compiler-produced SSML from the typed render plan.
The four baseline voices are Jenny and Guy for en-US, and Sonia and Ryan for en-GB.
An arbitrary national accent label is not a verified capability of those voices.
The complete first release needs observed qualification for each required target combination.
A failed capability remains a release blocker. No human-recording substitute is enabled.

Whisper supplies an independent textual hypothesis and proposed word times, without a reference prompt.
Azure pronunciation assessment receives the reviewed surface text, not the correct canonical replacement.
Its scores are reference-conditioned advisory measurements. Low accuracy is not a phonetic transcription.
Only a genuine observation can populate observed IPA.
