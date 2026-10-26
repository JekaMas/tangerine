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

The existing accepted Qwen CustomVoice0.6B cache was used in a test-owned
container made from the already installed speech image, with current speech
source mounted read-only, bound to loopback8091. No installation, download,
paid call, deployment or user-service restart occurred. The actual request used
frozen CPU/float32, Ryan/Aiden, the original four-turn car-insurance dialogue
and the original four respellings. Each explicit foreground invocation admits
at most one new piece and remains bounded by270seconds. There are26pieces.
Saved progress is under `data/iteration-25-qwen-20261026/live/`.

The first actual piece hit the client deadline at269.92seconds. Its socket
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

The updated read-failure state was inspected in the actual browser at1280×720,
390×844and320×740. The reference remains loaded and paused, Refresh is enabled,
body type is17px/1.45 with the loaded Source Sans3 font, and no page overflows.
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
selected acoustic confirmation belongs to iteration26. Original failures,
controlled PCM observations and provenance remain retained.
