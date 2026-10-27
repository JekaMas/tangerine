# Iteration 34 verification — local generation repair

**Verification passed:16/16 selected cases on committed-clean `f5f014fda80edd087158a7e87c0c3f00d31436a6`.**

Entry revision: `c6cfd58`; original implementation: `30d4154`. This verdict
supersedes the original eight-case apply acceptance for I34. The original receipt
remains intact; [ACCEPTANCE.json](ACCEPTANCE.json) records the expanded cohort.

## Findings and repairs

| Finding | Actual counterexample or missing observation | Resolution |
|---|---|---|
| V1: inflated correct-control accounting | A true-error unit marks “help with the event” through its text span but supplies wider realization wording. The evaluator returned FP1/TN4/accuracy0.8 instead of FP1/TN3/0.75. | One owner, `compare.control_claimed`, now follows overlapping heard spans in the correct turn. Exact, partial, wider and repeated occurrences are covered; neighboring spans, other turns and acceptable variants remain distinct. Four original failures and repaired passes are retained. |
| V2: actual preparation UI evidence missing for this verify request | Apply had native failure/recovery receipts but no new browser interaction, screenshot or video observations. | Actual Chrome form, keyboard, error/read-retry/resume and 1280/390/320 observations. No new product check, gate or rendering change was indicated. All API writes terminate in an isolated fixture. |
| V3: comparison/selection needed independent rechecking | Admission alone, aggregate resident memory or replay duration could be mistaken for model quality, resource requirements or live speed. | Reassessed all16 original rows with the repaired evaluator: no original score or winner changed. Recorded model-specific resident allocations and a narrow decision matrix. No latency/quality population claim or new inference. |

The production owners are unchanged: canonical preparation/freezing, provider
execution/retry, shape/locator/correction projection, mutation admission,
manifest generation and persistence keep separate responsibilities. The repair
changes the development evaluator, not learner admission or stored accepted data.
No new code defect was demonstrated in the I34 production projections.

## Why the selected alternative remains the best supported here

The frozen rule requires both common requests to complete and the exact
independent target/repair expectations to hold. Only Qwen9B plain with the current
native correction projection meets that rule among the observed checkpoints.

| Observed alternative | Admission | Exact target/repair precision and recall | Decision |
|---|---:|---:|---|
| Qwen9B, plain, repaired prompts, raw output | 2/2 | 50% /50% | One preferred correction is too wide for its quoted span. |
| Qwen9B, same retained replies through current projection | 2/2 | 100% /100% | Selected system checkpoint: TP2/FP0/FN0/TN6, matching-event accuracy100%. |
| Qwen9B, complete decoder schema | 0/2 mutation completion | Unavailable | Conservative final-wire budget rejects the mutation dispatch. This does not establish schema-decoder linguistic quality. |
| GPT-OSS20B, latest observed checkpoint | 2/2 | 50% /50% | Wrong requested placement/correction despite protocol admission. |
| Original27B, thinking off | 1/2 | Complete-population rates unavailable | Positive canonical call reaches its90s deadline; the zero-error request takes191.6s. |

These are two authored requests, not a blind or general benchmark. Precision and
recall include the exact canonical preferred repair defined by the fixed fixture;
they do not estimate general linguistic accuracy or reject valid alternative
corrections in the product. The existing production regression preserves valid
“take a” as an alternative. Matching-event accuracy counts an incorrectly keyed
prediction as FP and its missed expected repair as FN; it is not ordinary
classification accuracy over a population. Repeated correct wording remains a
separate once-only construction deviation, rather than a learner error.

All choices use local API charge$0; electricity/hardware cost is unmeasured.
The source Qwen requests took140.4s and61.2s and returned32,200 input/2,788 output
tokens over five actual calls, including retry. The final projection replay made
zero inference calls; its1.83/1.76s cannot be treated as generation speed.
Model-specific observed resident peaks were9.39GB for the selected Qwen source
run,13.10GB for GPT-OSS and19.68GB for27B. Other resident models are excluded from
those per-model figures. They are observations, not minimum RAM requirements or
isolated hardware measurements. See `data/iteration-34-verification-20261027/decision.json`.

The selected profile is documented in [local setup](../../docs/local-llm-generation.md).
It is an explicit configuration for new preparations. The running user service
was neither reconfigured nor restarted. No broader best-model claim is justified.

The current [Ollama compatibility documentation](https://docs.ollama.com/api/openai-compatibility)
describes local stateless Responses use; its
[structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs)
describes schema-constrained output. These interface capabilities alone do not
prove this application's full-schema budget, linguistic correctness or installed
runner stability. The actual retained native wires and failures decide those.

## UI, UX, typography and evidence

Used the typography skill and the pinned verification-design interaction/review
guidance. Actual Chrome observations show:

- Topic, speaker count, B1 level, exact two mistakes, Grammar/Vocabulary and Minor
  severity reach the constructed HTTP request unchanged. Busy generation disables
  the native fieldset and primary action; completion/failure re-enables them.
- Failure retains the form, saved clean-text status and explicit Resume. Keyboard
  Refresh and Resume work. A constructed UI-only success removes obsolete errors.
- Transient reads recover after503→200. Exhausted reads stop after three503s,
  preserve input and keep generation available. Explicit category/Refresh retry
  recovers with no write or implicit model dispatch.
- Unreadable responses display authored guidance. Backend canary, SQL/password
  strings and private traces never reach visible content. Writes occur once per
  explicit action with distinct idempotency keys; none is forwarded to a real API.
- Loaded Source Sans3 body text is17px/24.65px. All nine amount/severity captions
  are14px and fit their containers. No page overflow at1280,390 or320px. Mobile
  navigation works through keyboard activation; Refresh shows a3px focus outline.

The existing I30 source-built frontend supplies the unchanged generation/read
recovery paths. Its source correspondence was inspected against the current
checkout: later I32 changes concern the fixed **speech** failure action and saved
helper wording, outside these selected generation failure paths. This review
does not requalify that separate speech branch or claim a fresh frontend build.
An offline rebuild missed its dependency layer and was cancelled at `npm ci`;
no completed new dependency installation or image is claimed.

Screenshots and observations are in
`data/iteration-34-verification-20261027/browser/`. Inspect viewport frames for
fixed navigation positions: full-page screenshots place fixed elements at the
captured scroll offset. The60.959s silent video, `preparation-recovery.mp4`, is an
edited sequence of19 actual Chrome frames with cuts and compressed waits. Its
on-screen disclosure identifies controlled HTTP and zero new generation/audio.
It is not a continuous recording or evidence of fresh inference, audio completion
or native persistence. The fixture's completed-audio response is UI-only; native
I34 recovery remains mutation-only and is separately proved by retained receipts.

## Native, Lab, preservation and remaining observations

All109 Go race cases, Go1.26.5 vet,390 static specification assertions,30 actual
local calls and four native projection/persistence replays retain their original
receipts: no production owner, model-visible input, fixture or language dependency
changed. The expanded I34 selection contains16 actual methods, including eight
added review cases. Graph/discovery and selected strict OpenSpec results are
recorded with the final acceptance; structural success alone is not behavior.

Local MLflow experiment23 has an appended zero-inference review run, with11
artifact downloads/readback, including the repaired evaluator, re-assessment,
decision, actual browser observations and video. See [Lab readback](LAB.json).
The eight original model/replay runs remain intact. A temporary assertion used a
nested download path although MLflow downloaded single files by basename; the
assertion was corrected against the actual readback and then passed.

All122 categories/recipes,42 formulas and11 source scopes remain unchanged.
Canonical GAPS.md, app3000, settings, records, media and existing tabs are
preserved. The owned tab and gateway are closed after observation. See
[preservation](PRESERVATION.json).

Known external/model observations stay explicit: the installed MLX engine can
still panic on cache offsets (existing same-profile retry recovered the observed
case); the27B positive timed out; exact once-only wording and arbitrary-topic/
all-category generation quality remain unproven. This review does not label those
engine/model facts repaired. They do not add a user approval or qualification gate.
No new inference, synthesis, model download, paid usage, hosted fallback,
deployment/postdeployment, PBT, financial execution, push or publication occurred.
This is self-review against independent requirements and literals, not a second
reviewer or a model/human gold-standard assessment.
