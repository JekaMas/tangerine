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

Implementation checkpoint committed at3bde1fb. Verify found one missing native
assertion: stored HTTP range playback was stated but only the full response
was checked. Native overlap tests now assert206 and exact selected mixed bytes,
Content-Range and416 for an impossible range. This invalidates only the native
cohort's changed test input; production and138+59 retained observations are
unchanged. Check sibling advisory quality failure/warning/malformed/measured
paths through the now changed assembly dependency. Frontend source is identical
to downloaded release4558af1; the existing source-built isolated web is reusable.

Fresh verify: native6/6 passed (two overlap scenes with206/exact bytes/416,
four advisory quality siblings), actual session72879 exit0. New recordings0;
latest native WAVs equal the originally recognized audio exactly. Ordinary
unchanged Next Listen/results inspected through a read-only controlled fixture
transport using those native WAV/key/score records. This does not fabricate a
new durable learner attempt or LLM feedback observation. Keyboard replay and
refresh, mobile menu,320/390/1280 layouts,503→503→200 transparent recovery,
persistent3-read failure and authored guidance observed. Saved answer/score/audio
remain; no backend canary displayed and no write except labelled playback ack.
No production repair emerged from these observations.

Final recovery trace exposed a real sibling UX defect: fixed clipping or absent
word timing on frozen recordings was persisted retryable=true, and immediate/
Prepare/Audio guidance offered ineffective Resume. Repaired speechRetryable at
the speech outcome owner, shared fixedSpeechFailure/failureMessage UI projection
and both action lists; immediate generation response now agrees with saved state.
No new numerical/data audit. Native missing-timing negative retains both actual
source recordings with retryable=false; interrupted source reuse stays true.
New narrow policy/response/helper/browser tests plus existing directly dependent
recovery siblings are selected. Speech outcome/response production changes
invalidate the former Go/native source-bound cohorts; contract/Lab59 remains
unchanged. Existing Listen replay/screens/video retain their unchanged owners.

Final stable repair inputs: speechRetryable/speechPublicFailure, immediate
generation response, shared frontend fixed-failure projection and Prepare/Audio
actions. Go144/native7 passed after those changes; contract/Lab59 valid greens
reused with corrected explicit package dependency scope. JS helper/sibling52
passed. Actual final frontend build and six fixed/transient responsive views
with two keyboard continuation observations are retained. Model calls during
verify remain0.39 DAG cases registered across all five properties.
Final390 structural assertions pass after one required vector refresh; strict
1.13.1 and graph/discovery pass. Remaining: final lint/metadata readback, commit
stable code/evidence, execute selected --require-clean, record acceptance and
check canonical tasks, acceptance-only commit and final clean readback.

ACCEPTED: selected --require-clean run passed39/39 at clean
e05d673acfe260a2854974c52c28dcd8dab915c1, actual session36499 exit0,
no missing/skipped/failed/substitution gaps. All four verify findings closed.
Canonical I32.1–5, I32.V1–V3 and ALL-AUDIT.2 now complete. ACCEPTANCE.json
retains the original tested revision and immutable receipt. Final stable language
checks pass. Lab runfed5e5bee645468aa393857e60e67410 FINISHED,87files and
12 exact download readbacks; export inference0. Test-owned browser tab, two web
containers/images and loopback comparison/gateway stopped; existing local/I30
services and user workspace preserved. Acceptance bookkeeping accompanies this final note. Final readback confirms
all39 accepted results, the unchanged manifest/receipt, preserved GAPS and
clean worktree. No remaining I32 work; no behavioral rerun is required for
bookkeeping.
