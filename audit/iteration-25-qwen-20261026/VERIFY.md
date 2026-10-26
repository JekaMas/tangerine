# Iteration 25 verification and repair

The 2026-10-26 verify request includes repair. Starting revision: `01ecb48`
on `tangerine/iteration-16-release`, in the iteration16 worktree. The selected
properties are `FIN-QWEN.P1` and `FIN-VERIFY.I25`. The earlier clean receipt on
`35ac5b5` contains 26 passes and two skips; it does not accept the iteration.
The canonical checklist remains the change's `tasks.md`.

## Findings and single owners

1. The finite comparison stops at the first transient connection failure.
   `compare.execute` now owns one retry for connection failures and local
   HTTP502/503 responses, within the original shared foreground deadline.
   Cancellation, unavailable capabilities and other terminal responses do not
   retry. Saved responses/pieces are reused. No provider fallback is added.
2. `NativeSpeech` could accept an HTTP error containing an otherwise ordinary
   JSON object. The transport now records the actual status and raises a typed
   failure, so retry classification does not depend on an optional body field.
3. CLI folder/plan setup ran outside its human-readable error handler. The
   command's single outer handler now covers setup as well as execution. It
   reports a useful local-folder action without exposing exceptions or paths.
4. The player could lose its entire page on a failed progress/transcript/media
   read. Its local read owner retries once, logs the error type, and retains
   independently playable saved audio. Persistent media-read failures receive
   authored guidance and recover on Refresh; no synthesis follows a read.
5. A long CPU comparison needs explicit foreground checkpoints. An optional
   one-new-piece step saves progress and returns partial normally. Resume trusts
   saved artifacts. The full reference becomes available as soon as its own
   pieces finish; `result.json` exists only after both complete variants.
6. Missing progress could say no recording was available while a saved
   reference card was present. The same player status owner now derives its
   fallback from available complete recordings, keeping partial versus full
   comparison status truthful.

These are development repairs, not new learner approval or qualification gates.
The native speech process/deadline owner and model generation are unchanged.

## Execution checkpoint

The existing accepted Qwen CustomVoice 0.6B cache was used in a test-owned
container made from the already installed speech image, with current speech
source mounted read-only, bound to loopback 8091. No installation, download,
paid call, deployment or user-service restart occurred. The actual request used
frozen CPU/float32, Ryan/Aiden, the original four-turn car-insurance dialogue
and the original four respellings. Each explicit foreground invocation admits
at most one new piece and remains bounded by 270 seconds. There are 26 pieces.
Saved progress is under `data/iteration-25-qwen-20261026/live/`.

The first actual piece hit the client deadline at 269.92 seconds. Its socket
closed, the native synthesis child was released and no completed piece or
full-pair result was saved. `cpu-timeout-observation.json` retains the actual
request, progress and process observation. Encoded model input/output is unknown
because the child did not return its receipt; no successful model-call count or
acoustic claim is inferred from this attempt. No unchanged heavy retry or model
parameter sweep follows. The existing isolated MPS dependency setup question
remains unanswered; installation is not inferred from silence.

The in-app browser still renders the controlled comparison but does not activate
its native disclosure control. A text request to use installed Chrome for local
interaction verification is pending. No activation or real-pair playback pass
is claimed from rendering alone. The Microsoft handoff and user tabs are kept.

The updated read-failure state was inspected in the actual browser at 1280 × 720,
390 × 844 and 320 × 740. The reference remains loaded and paused, Refresh is enabled,
body type is 17 px/1.45 with the loaded Source Sans 3 font, and no page overflows.
Screenshots and DOM observations are retained in
`data/iteration-25-verify-20261026/read-failure-*`. They use clearly labelled
constructed six-second PCM and prove the rendered recovery state only. They
do not close activation, actual Qwen playback or phonetic realization.

## Verification rules and proof boundary

Changed comparison/player functions and their literal tests invalidate their
own cases. Native model-factory/device/deadline tests remain valid on unchanged
owners until a concrete changed dependency requires re-execution. The complete
selected committed-clean graph must reconcile all required cases before task
acceptance. The earlier two skips remain missing observations until actual
full media, native contexts, Lab readback and browser interaction are retained.

The review uses the OpenSpec verify skill, pinned verification/code-inspection
guidance, the project UI/UX procedure and the typography skill. UI/UX,
typography and evidence receive separate final dispositions. This is self-review
with independent literal expectations, not a second reviewer. No deployment,
postdeployment, PBT, financial execution, benchmark or parameter sweep is in scope.

Qwen respelling is an approximation. Completion of this pair does not certify
that every requested phone/stress deviation is acoustically realized. Exact
selected acoustic confirmation belongs to iteration 26. Original failures,
controlled PCM observations and provenance remain retained.

## Final observed checkpoint

The complete selected DAG ran with `--require-clean` on committed source
`c6cad2f0c13c40cec1fb4749dad6b09ec0ecdc1f`: **37 passed, 2 skipped, 39 selected**.
All four native command owners returned 0. The two required missing observations
remain `FIN-QWEN.P1.qwen_positive` and `FIN-VERIFY.I25.review_positive`.
The run is **incomplete**, and I25.1–I25.3 remain unchecked. Neither negative
timeout evidence nor a passing controlled waveform test substitutes for them.

The source change, literals, constructed filesystem/transport inputs and new
actual observation files invalidate the registered comparison/player cases.
The full selected stable boundary was reobserved, with no learned-model call in
the test runner. Earlier original green receipts are retained, not rewritten.
Strict OpenSpec 1.13.1, DAG/discovery, Python syntax and stable-batch whitespace
checks pass. The JavaScript is unchanged and retains its earlier syntax proof.
Original 122 categories/recipes, 42 formulas, 11 source scopes and migrations remain
unchanged from the selected preservation baseline.

MLflow experiment 16 / run `93d86570ac8244149c1f70c0acfd63c8` contains the actual
failed native request, plan/progress, scoped source, literal checks and new
screenshots. Five selected artifact bodies were downloaded and compared after
export; the run retains 43 files. Export/readback dispatched zero inference.
The actual local piece-request count is 1; successful native/model outputs are 0;
the model-entrypoint count and encoded context are explicitly unknown. The
failed body was not converted into a successful model observation. See
`data/iteration-25-verify-20261026/lab-readback.json`.

- **Code review:** repaired findings and their sibling cases pass through the
  single comparison, transport and file-read owners. The native model and
  foreground-process owners remain unchanged.
- **UI/UX:** rendered empty/partial/success/media-retry states retain their
  original proof boundaries; the new progress-read failure is inspected in the
  actual browser. Full interaction review remains **incomplete** because native
  input activation and actual complete-pair playback are unobserved.
- **Typography:** the inspected collapsed recovery state passes at 1280/390/320,
  with Source Sans 3 at 17 px/1.45, clear hierarchy and no page overflow. Expanded
  details and keyboard focus remain unobserved; no full-state typography claim
  is made from these screenshots.
- **Evidence:** Lab export/readback passes for the retained scope. Actual full
  pair, encoded model result and interactive playback remain **incomplete**.

The test-owned native container, fixture server and tab 29 are removed; the
viewport is reset and the existing Microsoft handoff is preserved. The user app
remains healthy at HTTP 200, and its services, settings, data, audio and canonical
`GAPS.md` edit were not changed. No deployment, postdeployment, PBT, financial
execution, installation, paid credits, overage, benchmark or provider fallback
occurred.

Remaining next actions depend on the existing unanswered isolated-runtime setup
selection and the new browser-selection question. For a changed runtime, retain
the failed CPU checkpoint and create a separately frozen candidate; passing new
CLI flags must not overwrite the stored compute binding. Complete the original
pair through the native owner, retain actual model/Lab observations, exercise
playback and keyboard/click interaction, and reobserve invalidated cases before
issuing any iteration acceptance.
