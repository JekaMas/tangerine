# LLM ownership, controls, development and scoring walkthrough

This describes written behavior. No provider, synthesis, MLflow or application execution was requested or performed.

## Stage routing

| Stage/phase | Model-visible data | Saved semantic output / next owner | Control and exception |
|---|---|---|---|
| case_generation / canonical_text | Expanded topic/speakers/length/optional level, public context and selected optional excerpts | Clean ordered candidate, canonical asset/hash → mutator | No injected units; 90s cap inside generation operation; no hidden corpus prerequisite. |
| case_generation / mutation | Frozen clean candidate, selected actual recipe records, taxonomy/context/family/count constraints | Mutated candidate, independent repair units, typed manifest/key draft → renderer | Preserve canonical sequence and replay exact surface. 150s cap. EXP-003/004/005 need contract repairs. |
| linguistic_audit | Candidate/context/taxonomy, actual available evidence | Advisory findings and missing-input paths | Optional; cannot hear unprovided audio or approve publication. Shared one-repair policy conflicts with its last prompt sentence: EXP-008. |
| blind_claim_extraction | Exact answer and public task information | Clauses/attachments/retractions/source spans → server coverage and mapper | No transcript/key/expected mutations/prior grade. 40s cumulative cap. |
| claim_mapping | Frozen answer/extraction/key/rubric/context and actual evidence | Localized semantic decisions → native scorer | No authoritative numeric grade. 70s cumulative cap. Novel valid repairs allowed; EXP-001/002 still need complete projection. |
| mapping_audit | Same frozen extraction/key/context | Independent mapping diagnostic | Disabled by default. Does not see the first mapping. 70s cap when explicitly enabled/remaining budget permits; disagreement alone does not erase supported score. |
| feedback | Actual native score/findings, key/rationales and selected task context | Grounded explanation and labelled practice recommendations | 40s cap; failure/feedback-only retry preserves numeric result. |
| case_review | Candidate/proposed key plus real modality/evidence | Existing-unit judgments and confirmation basis | Optional, key-aware review; actual exposure prevents a false blind-listening claim. Text-only DeepSeek cannot hear audio. |
| adjudication | Frozen case/answer/extraction/prior decisions, dispute when supplied and actual evidence | Supported mapping correction, key-defect finding or insufficient_evidence | Automatic uncertainty action up to70s remaining; separate review actions up to220s within270s. EXP-002 is the missing semantic producer for a new key. |
| lab.semantic_judge | Candidate output plus separately frozen rubric/reference/actual evidence | supported/unsupported/unknown diagnostic propositions → native Lab statistics | Dedicated judge prompt/input/output. Uses configured linguistic-audit-capable profile; registry explicitly names this surface. Self-consistency is not independent accuracy. |

Nine application bindings are preserved because generation has two phases. The judge policy remains outside the application prompt bundle. Stage roles, semantic surfaces and inference attempts are distinct identities. Local Kokoro, Azure synthesis, Whisper ASR and Azure assessment remain separate configured inference surfaces; exact final audio and actual preprocessing/response provenance matter there.

## Controls that serve the product

Use one configurable default LLM with optional stage overrides. Freeze the actual prompt/context/schema/profile/recipe/input hashes. Keep secrets in local references, rather than prompts/debug copies. One foreground paid action, operation idempotency, cumulative270s deadline, one additional evaluation transport attempt and one adapter repair prevent duplicate work and preserve recoverable input. SDK retries are disabled. Source/user text stays data. Harmless fences/additive fields are normalized locally; the model does not have to implement every JSON Schema keyword.

Preserve actual visible requests/replies, refusal, incomplete output, fallback/repair and cost unknowns separately. Required answer/key/evidence is not silently truncated. Native write fences prevent a late call from replacing a newer result. These are correctness/resource controls, not human approval or LLM-format ceremonies. EXP-006 and EXP-007 identify unnecessary or stale boundaries to remove: permission epochs and lifetime three-attempt limits.

## Exact answer-to-score chain

1. Freeze the heard case/audio and task components; save original answer bytes before a call.
2. Extract real source clauses and attachments without the key. Server derives codepoint coverage; substantive missing interpretation remains explicit.
3. Consolidate same-event compatible claims; retain members. Backward explicit retraction deactivates the referenced claim. Duplicate assertions count once; endorsed contradiction is not solved by choosing the favorable fragment.
4. The mapper selects one target for a resolved group using quote/turn/context/time/description. Repeated ambiguous words cannot create several detections. Wrong category does not cancel correct detection.
5. Determine stance: error on error→TP; acceptable on error→FN without FP; error on control→FP/DF; acceptable on control→DA. A plausible omitted defect is a key issue, not automatically an FP.
6. Supplied repair/explanation comes only from actual answer spans. Native credit is zero for a violated forbidden proposition; otherwise satisfied required/all required. Correct novel wording may satisfy existing constraints. EXP-001/002 are the remaining total-projection gaps.
7. Native code calculates exact42 metrics and composite; requested omissions remain zero, disabled/no-opportunity weights are excluded according to the fixed policy. Detection/classification/correction/explanation weights remain45/15/30/10. Classification uses hierarchical recall; correction uses graded recall. Control-only has no manufactured composite. A genuinely unresolved score-relevant interpretation stays provisional.
8. Feedback explains the saved findings and recommends practice. It never supplies an authoritative grade or rewrites the heard exercise.

`SCORING-PACKETS.json` supplies eight independently derived small arithmetic examples with explicit populations and counterexamples. They are written oracle packets, not scorer executions, semantic benchmarks or evidence that a provider will interpret those answers correctly.

## Development/debug route

MLflow remains suitable for the specified editing, version comparison, native evaluation artifacts and traces. Its documented OTLP/HTTP endpoint accepts native clients at `/v1/traces`, with the experiment header and an SQL/SQLite backend; a separate collector/workspace is unnecessary for this design. [Primary MLflow ingestion documentation](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/ingest). The [pinned3.17.0 release page](https://github.com/mlflow/mlflow/releases/tag/v3.17.0) resolves. These checks establish published interface information, not compatibility observed from an installed pinned build.

Prompt/context edits create immutable versions; export saves exact numeric identities and local bundle bytes; explicit activation affects new operations only. A failed export leaves ordinary native results usable. Explicit sync exports saved artifacts without inference. Ordinary use needs no Lab. Actual AI-affecting development completion requires its selected native/Lab evidence and independent dispatch-to-receipt-to-export join, not a complete corpus/full benchmark or repeated human approval.

For a comparison, hold references and applicable input population fixed. Generation variants create different text; do not present them as fixed-exercise grader comparisons. Pool raw sufficient statistics and recompute F1, retain failures/cancellations/not-run rows, show exclusions and unknown denominators. The22 diagnostic metrics supplement the42 formulas. Secret/private-field redaction has distinct output hashes, actual omitted reasons and controlled-canary test design. A candidate label read by another judge is still self-consistency unless a separate independent reference was obtained.

EXP-010 remains planning work: all affected properties need concrete packets and independent expected outcomes. Registry/index counts, model agreement and “positive/negative” labels cannot substitute for that design or eventual observed behavior.
