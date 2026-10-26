# Iteration 23 — Gemini Free text qualification

Starting revision: `8ae0901`; worktree `tangerine_iteration16_20261021`.
Selection: `FIN-GEMINI.P1`, `FIN-VERIFY.I23`; task GEN.R4 depends on actual
unchanged-request success. Initial graph validation passes. Six existing
literal cases were planned before implementation; initial execution was not claimed.

The actual AI Studio account shows the existing key/project as Free tier and
No billing account. The ignored key matches that visible key. No billing or
quota controls are changed. Current allowance remains to be inspected before
functional calls. External failures will not be substituted with another model.

## Production anchors before editing

- Provider: `internal/provider/gemini.go` serializeGemini, geminiContent,
  geminiError; `transport.go` Included/Exchange; `execute.go` Execute.
- Dispatch/admission/context: `internal/app/provider_configuration.go` and
  the existing InvokeLLM owner; frozen preparation configuration and Lab bundle.
- Pipeline: PrepareCanonical → PrepareMutation → RenderPreparation → stored
  listening case → StartAttempt/answer write → InterpretAttempt/native scoring
  and feedback. Final state is the persisted result envelope, not a model reply.
- Durable lineage: preparation/operation IDs, frozen configuration/bundle,
  provider receipt and context snapshot IDs, private input/output assets,
  case/key/audio/attempt/result IDs. Preserve errors and repair attempts.
- Evidence: independently observed HTTP dispatch wire/response, native documents
  and assets, local MLflow artifact readback; controlled packets stay labelled.

## Stable implementation checkpoint

Actual garden request produced 90 canonical / 89 mutated words, four turns,
two local voices and 28.875s saved audio. Initial answer recognition was supported
but unresolved attribution made the score uncertain. Extractor instruction now
keeps the lead-in with its claim. A new same-case attempt exposed a native
recorder panic: it decoded Gemini's string input as an OpenAI message array.
Provider Execute now supplies the constructed RepairMessage directly; retries
retain it. Existing output admission/repair bounds and score arithmetic stay.

Explicit Resume on the same second attempt now yields 100/100,1TP,0FN,0FP and
100%optional explanation with actual Gemini comments/recommendation. Seven
candidate dispatches match seven native receipts/snapshots. Twelve hosted calls
total include five failed-baseline observations; one pre-fix response has no
completed receipt/snapshot. That baseline remains incomplete. All retained
candidate observations and baseline limits are exported/read back in local Lab
experiment13/run b83631af099449d1baed0ca39881a0f6 (176artifacts), zero export calls.

Controlled native quota/denial/missing-credentials/outage/recovery pass; native
repair+transport retry context,19provider cases and14source/sibling cases pass.
Actual UI/UX/typography inspected at1280/390/320, keyboard/mobile navigation,
playback/settings/reopen. No frontend change or provider substitution. Historical
I17 replay is bound to its actual accepted task/graph snapshot, allowing later
current GEN.R4 completion without rewriting its dated classification.

Final: source `33c2d29` passes --require-clean for all 14 selected cases (8 I23,
6 affected historical replay cases). Strict OpenSpec1.13.1, 388 static assertions,
graph/discovery, focused native/race tests and Go vet pass; unchanged builds
are retained. ACCEPTANCE.json records the observed exact closure. I23.1–.3,
I23.R1–.R2 and GEN.R4 are complete. Later iterations remain open. All owned
runtime fixtures are removed; app3000 is healthy and canonical GAPS.md remains
user-dirty/untouched. No remaining I23 action or new inference is required.
