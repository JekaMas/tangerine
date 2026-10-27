# Iteration 32 progress

Entry revision: 60bb692, clean. Existing I31 acceptance remains frozen to its tested revision.

Production anchors before edits:
- Hook: renderSpeech -> assembleSpeech, after every source piece is complete.
- Single numeric owner: new speech_composition.go in the Go application package. Worker supplies accepted source recordings/native timing; it will not gain another mixer.
- Admission: mutationContent checks fresh overlap intent alongside its unit/turn references, then the existing frozen candidate/manifest/render-plan owns it.
- Lineage: preparation id -> render_plan_asset_id -> render_progress_asset_id pieces/source assets, native timing, resolved composition and final sample_map_asset_id -> assembled asset/key id. Existing operation/CAS owns resume.
- Finalizer: saveSpeechKey followed by RenderPreparation checkpoint render=complete.
- Evidence: exact piece IDs/source SHA/source sample intervals, final sample starts/gains, unit IDs/masked ranges, native receipts and actual WAVs. No new evidence DB, provider or runtime audit.

Preimplementation graph structurally validated. Semantic query returned no index for github.com/jekamas/tangerine; exact source tracing used. Original composer appends PCM; no actual overlap.

Next: implement typed intent/resolved schedule, mixer/key wiring; exact native tests and local recordings.

Two duplicate broad changed-path DAG queries were terminated after several minutes of CPU work without a result. Their output is not acceptance. A bounded explicit-property selection and direct source dependency inventory will replace that exploratory query; no shared runner/workflow changes.

Implementation complete through typed intent/manifest/render binding, one PCM
composer, persisted schedule, concurrent key/sample clocks and advisory quality.
First directed cohort passes; native actual synthesis produced four local clips.
Both native scenes passed. A test-owned cancellation after schedule persistence
then a fresh server resumed with no synthesis. The repaired score fixture and
render-progress/schema agreement passed with the same retained source recordings.
Independent local Whisper source/mixed observations: source safety warning is
recognized; obstructive mix replaces it with B's competing floor-taking turn;
cooperative source/mix both retain the museum message. These are finite machine
observations, not human/perceptual gold or universal voice qualification.

Current stable regressions and native cohort execute against the finalized
shipped prompt/schema bundle and refactored source-word owner. No new synthesis
is permitted in the stable native command; missing cached clips fail explicitly.
Next: finish evidence/Lab export, final graph/discovery registration, stable
language/static checks, informational selection, commit, selected clean gate.

Stable boundary: Go199 exact observations, language check,20 current DAG
evidence assertions,390 specification assertions, pinned1.13.1 strict and graph/
discovery are green. Four local TTS/four local ASR calls only; stable native and
all metadata/DAG checks add no inference. Original CV/other iterations remain
scoped. Final Lab run740d39aee892441a94b94e5cf9a6adf2 has actual readback.

Remaining: commit this complete increment, execute the same20-case selection
with --require-clean, record acceptance/check canonical I32 and ALL-AUDIT.2,
then commit acceptance. No application or test repair remains known.

Verification request renewed: inspect and repair the full I32 production/UX
closure, sibling error/recovery cases and actual media evidence; add ordinary
stored playback screenshots and a video. No deployment, PBT, financial or
provider execution. Existing valid native/Go/ASR observations remain retained;
only changed semantic inputs invalidate their dependent checks.
