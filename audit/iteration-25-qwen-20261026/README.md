# Iteration 25 — complete local Qwen dialogue pair

Apply starts at clean `4c1a5569d6b7b82795b3cbb150a38ee820541d7c`.
The selected properties are `FIN-QWEN.P1` and `FIN-VERIFY.I25`; the canonical
checklist remains `openspec/changes/implement-teacher-error-trainer/tasks.md`.

The source is preparation `9dbf8c95-51a3-4c0f-9395-b3a77a824d22`, opening four
turns, preserved in `../iteration-24-azure-20261026/material.json`. The four
targets remain choices, companies, another and Collision. Ryan/Aiden are the
selected synthetic voices. Qwen CustomVoice 0.6B uses phonetic respelling as an
approximation; it does not supply an exact IPA control or guaranteed accent.

## Owners and completion boundary

`services/speech/backends.py:qwen/plan/render` owns local synthesis, accepted
model reuse, literal/encoded inputs and native output receipts.
`services/speech/server.py:Handler.do_POST` owns each foreground child, its
deadline and disconnect cleanup. The finite comparison client uses that HTTP
owner, retains each accepted piece and assembles only complete variants. A
270-second foreground invocation may resume its saved plan/pieces explicitly;
there is no detached model queue, enlarged deadline or automatic fallback.
The local comparison player only reads saved recordings; viewing, refreshing
and playing never dispatch synthesis. A full pair requires all planned pieces
and both complete variants; the old 5.6-second preview cannot satisfy it.

The native plan binds `qwen_runtime` per piece. The original CLI selection is
frozen and remains the consumed selection after a native server environment change; direct
legacy pieces without that binding keep the explicit environment/default route.
Loaded model/codec placement is recorded separately from requested placement.
The `--device` and `--dtype` flags select a new plan; they do not rewrite a saved
one on resume. Use a new output folder for a changed compute candidate, preserving
the old plan and recordings.

Native inputs, outputs, calls, actual runtime and failures belong in ignored
`data/iteration-25-qwen-20261026/`. The existing local MLflow Lab receives these
same artifacts, with zero additional inference for export or verification.
Actual browser observations are separate from deterministic lifecycle fixtures.
No paid service, purchase, overage or provider switch is allowed.

The CLI defaults to `--max-pieces 1`: each explicit invocation admits at most
one new piece, reuses saved responses/audio and prints its effective frozen
compute selection. Repeat the same command/output directory to resume. A
partial step is ordinary saved progress; it is not a full-pair result. The
reference WAV becomes playable once its own pieces finish. A temporary local
connection or HTTP502/503 failure retries once within the original 270 seconds;
cancellation, deadline and terminal configuration failures do not retry.
The local player retries failed file reads once, keeps independent recordings
available and gives authored recovery guidance without exposing backend errors.

## Runtime investigation

The installed Docker speech image has the accepted pinned model
`Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` at revision
`85e237c12c027371202489a0ec509ded67b5e4b5`. The historical CPU timeout and
cancelled int8 experiment remain in `../speech-comparison-20261022/REPORT.md`.
This Mac is an Apple M1 Max with 64 GiB RAM. Its existing Python 3.12/PyTorch
2.5.0 reports MPS built and available, but Qwen/Transformers/audio dependencies
are absent. An isolated dependency setup is requested; no installation has
occurred at this checkpoint. An unavailable GPU must not silently select CPU.

Verify 2026-10-26 exercised the installed CPU image through a test-owned native
server. The first piece timed out at the unchanged client deadline; the native
child was released and no completed audio was admitted. Requested inputs and
the failure are retained; actual encoded model context is unavailable because
the child was terminated before returning its receipt. This is a failed real
qualification, not a benchmark or proof that every CPU configuration is unusable.
See `VERIFY.md` for repairs, sibling cases and the remaining observation limits.

The initial structural DAG/discovery proof is retained from
`data/iteration-24-verify-20261026/graph.json`: the starting manifest has not
changed. Planned I25 cases are not executed evidence. New/changed source,
fixtures and assertions will invalidate only their selected dependencies.

The user's running app, Docker services, settings, saved media, browser tabs and
canonical `GAPS.md` edit are protected. Iteration 24's external Azure blockers
remain separate. No deployment, PBT, hosted benchmark or publication is in scope.
