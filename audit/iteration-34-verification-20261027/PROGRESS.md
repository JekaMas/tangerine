# Iteration 34 verification and repair

Entry: committed-clean c6cfd58, implementation 30d4154. Scope is I34 and
demonstrated siblings, plus preparation UI/UX/typography/screenshots/video.
No deployment, installation, model sweep, hosted fallback, paid usage or PBT.

The actual 30 installed-local calls, four native retained-response replays,
109 Go race cases and Go vet have unchanged production inputs and are retained.
No model/prompt/transport/projection changes are currently indicated.

Confirmed finding V1: compare.py checks a claimed correct control using only
realization.surface_text equality. A unit whose actual text span marks the
control, with wider realization wording, incorrectly retains that control as TN.
The zero-error counterexample gives FP1/TN4/accuracy0.8 instead of FP1/TN3/0.75.
Repair belongs to the single comparison oracle, not to runtime generation.
Cover exact/partial/wider spans, repeated occurrences and correct unclaimed
controls. Reassess every retained alternative; preserve old receipts and Lab runs.

Missing evidence V2: this verify request explicitly requires actual preparation
UI error/retry and readable desktop/mobile interaction screenshots and video.
Use isolated HTTP outcomes derived from retained native preparation observations.
Writes must terminate in the test fixture; no forwarding to app3000/providers.
These observations prove presentation/recovery only, separately from native/Lab.

Selection review: only the Qwen9B plain + current scope projection checkpoint
qualifies both fixed requests. Replay is mechanical evidence, not fresh inference
or latency. Repetition of correct wording remains an instruction deviation.
Do not claim an unmeasured global best, model/category population or acoustic flow.

Semantic search returned no index for this exact repository. Known owners were
read directly; no semantic or independent reviewer evidence is claimed.

## Repairs and observations complete

The oracle positive/negative pair is green after four retained negative
counterexamples. All16 retained preparation rows were independently re-assessed;
their scores and the selected system checkpoint are unchanged. Eight review
methods pass. Native/provider/Go/static specification evidence is unchanged and
retained; the current Lab readback assertion also passes after correcting the
actual flat download path. No original Lab run or observation was overwritten.

Actual CUA Chrome UI evidence covers controlled form/generation failure, explicit
keyboard Refresh/Resume, transient and exhausted reads, malformed replies,
retained topic, safe messages, mobile navigation, font/caption sizes and no
horizontal overflow at1280/390/320.19 actual browser frames form a60.959s edited
silent video with explicit cuts/fixture disclosure. No new provider call, user
write, synthesis or installation. Existing source-built I30 UI reuse has the
specific I32 speech-only branch limit recorded in REPORT.md.

Next: stable graph/discovery/strict OpenSpec, inspect final diff and video,
commit implementation/evidence, run the complete16-case I34 selector with
--require-clean once, then record superseding acceptance and finish I34.V1–V3.

## Verified completion

Complete I34 selection passed16/16 cases, both commands exit0, with no skipped,
missing or planned cases at committed-clean `f5f014fda80edd087158a7e87c0c3f00d31436a6`.
Strict OpenSpec1.13.1 and graph/discovery pass. V1–V3 are resolved. Actual
video frames/content and eleven Lab downloads were inspected; no new model or
speech calls occurred. The owned gateway/tab are closed and viewport reset.
Only acceptance/report/progress/task bookkeeping remains for the final commit;
no semantic input to an observed behavior or structural check changes.
