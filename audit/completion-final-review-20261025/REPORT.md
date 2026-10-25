# Final source-report and continuation-spec review

Date: 2026-10-25. Worktree:
`/Users/jekamas/projects/0xatelerix/_worktrees/tangerine_iteration16_20261021`.
Starting revision: `bd5bc18f2d4fb523f44aa73d2e2aad9a630053a0`.

The revised written plan covers both supplied reports completely within their
scope: the same eight UX repairs, the production speech-adapter gap, task and
acceptance reconciliation, main/GitHub delivery, optional provider/acoustic/data
qualifications and preservation of the working interface foundation. It also
preserves the latest exclusion of LLM performance/bulk benchmark execution.
No application implementation or iteration acceptance is claimed here.

## Review method and independence limits

The current agent performed a separate sequential `spec` review using the
repository-pinned verification-design/review guidance and typography rules.
This is self-review, not a separate model or human review. Independence belongs
to the checked requirements and expected outcomes: the user's two source reports,
existing native contracts/formulas, direct source inspection, actual local Git
observations and literal counterexamples, rather than the plan's own green labels
or candidate-generated expectations. No external reviewer/model call occurred.

The review checked both directions: each reported item must have an iteration,
requirement/property, producer/consumer and positive/negative proof; each proposed
repair must serve the user's scope. It challenged plausible incorrect solutions
that could pass the earlier plans. These checks do not certify runtime behavior,
all-English correctness, full accessibility, all provider access or every voice.

## Findings repaired in the specification

| Finding | Why the earlier wording was insufficient | Repair and discriminating evidence |
|---|---|---|
| R01 · History transport | UI wording asked for titles/excerpts/dates, but closed response schemas omitted those projections. A mock card could look correct while native list data could not carry it. | Four optional fields in three canonical schemas; original-heard title, bounded real answer excerpt, actual creation times, legacy absence, duplicate identities and native projection cases. Existing required fields and old properties remain unchanged. |
| R02 · Finite passage replay | The old positive case could pass by setting currentTime while continuing to the end of the recording, or leave an old stop handler active. | Define seek/play/end pause, range replacement/manual cancellation, absent timing and retry on stored media. Add end and interruption counterexamples; seeking alone is insufficient. |
| R03 · Truly guided starters | A button that prefills JSON but still requires manual IDs could satisfy a vague starter-save check while preserving the reported usability problem. | Ordinary labelled fields and named choices need no JSON/hash/ID editing; advanced mode remains. Add normal-form and empty-workspace/recovery cases with zero inference. |
| R04 · Ordinary speech integration | A working standalone dictionary request could be mistaken for main-adapter acceptance; same-word targets inside one turn were underspecified. | Prove ordinary preparation/render/stored playback/answer/native score, preserve first-think/speaker controls, freeze/reuse locator/version, and reject incomplete fresh locator metadata once before dependent synthesis. Controlled semantic inputs retain their proof limits. |
| R05 · Budget-safe negative evidence | Requiring an actual exhausted allowance or repeatedly timing a heavy model can spend quota merely to demonstrate failure. | Use controlled external quota/model/process responses or retained genuine failures for native negative cases. Actual positives remain minimal permitted functional observations. No deliberate exhaustion, performance sweep or bulk judge retry. |
| R06 · Complete dependency routing | Existing CV implementation/evidence was not selected by iteration 26, and final selected-qualification conditions were narrative rather than explicit graph edges. | Include retained CV-01–CV-06 properties in 26; add conditional edges from 23–28 into 29/30 only for selected inputs or confirmed claims. Preserve independent local use and never silently promote unqualified data/providers. |

All six findings are closed **in the written contract/plan**. The associated
application changes remain future work. No new product decision is required for
these repairs; the implementation must materialize and observe their tests.

## Canonical artifacts

- The 25-item `completion-coverage.md` / `coverage_items` map covers every item
  in both reports, including their good-foundation statements and dated snapshot
  limits. It does not count their overlapping UX lists twice.
- `completion-contract-details.md` defines exact history, replay, guided-form
  and ordinary dictionary behavior, interfaces, failure behavior and proof limits.
- `completion-iterations.md` / `.json` retain iterations 17–30, explicit core and
  conditional edges, selected properties and current budget scope.
- `tasks.md` remains the sole task checklist; updated tasks reference the new
  contracts and existing CV evidence without duplicating implementation.
- The local verify adapter still requires actual UI/UX, typography and evidence
  inspection. No report-validation service, automatic aesthetic judge, human
  approval, migration, account system or repeated stored-data audit is added.

The canonical transport edits are `attempt-summary.exercise_title` and
`answer_excerpt`, `preparation-summary.created_at`, and `library-item.created_at`.
They are optional for legacy responses. Shipped embedded schemas, native
projection and UI are updated together during iteration 19; this spec review
does not change application copies or runtime processes.

The continuation DAG retains 19 requirements, 32 properties and 14 future
commands. It now has **118 planned cases**, after eight new cases (four positive/
negative pairs). Existing CV cases keep their own implementation state/receipts;
adding them to selection is not reexecution or blanket audio qualification.

## Structural observations

The stable review snapshot passes graph/discovery validation and native strict
OpenSpec 1.14.3 with zero issues. It includes all 25 FIN/CV requirements, 38
properties, 636 cases and 16 command registrations in this review's dependency
scope. This is structural admission, not execution of those cases. The changed
continuation delta also passes separately. Ten affected iteration selections
were queried without executing commands; unchanged selection identities are
retained and checked against the registry. The final I19 compatibility-boundary
correction is admitted in this stable snapshot.

An earlier whole-working-graph check passed before a new concurrent
`functional-category-ux` delta appeared. The subsequent broad attempt encountered
its six not-yet-registered FX requirements. They were preserved, not silently
registered or overwritten by this review. `review-snapshot-scope.json` records
the FIN/CV qualification boundary; no current whole-dirty-tree or committed-clean
application acceptance is claimed. Iteration 17 reconciles the actual overlapping
FX implementation/receipts before anyone duplicates the UI repairs.

The new FX-01–FX-06 requirement text was inspected: its non-pronunciation,
preparation/history/replay/guided-tool/visual intent is compatible with this
review scope. This is not acceptance of its implementation or registration.
Existing FX/CV tests may satisfy continuation cases after exact mapping; the
plan now explicitly permits rebinding valid tests/receipts instead of creating
duplicate modules or repeating unchanged inference.

Whole-change native strict OpenSpec 1.14.3 still returns non-success with zero
errors and 253 existing warnings. This is not a full strict pass. Version/style
reconciliation remains explicitly assigned to iteration 17; no global tool was
installed, downgraded or silently repinned. Current graph/schema/reference/
routing checks and exact observation boundaries are in `CHECKS.json` and
`OBSERVATIONS.json`; raw outputs are under ignored
`data/completion-final-review-20261025/`.

The final local checker passed 160 coverage/routing/compatibility/literal-oracle
assertions. It reconciles all 25 source/scope items, all 14 iteration selections
and the 636-case FIN/CV selection union. Four unchanged query identity sets were
retained; none of their test commands or model calls was replayed. The 118 new
continuation plans remain unexecuted.

JSON contract inspection checks additive compatibility, preserved required
properties and local reference/field constraints. The future native projection,
browser, media and provider cases remain unexecuted. No general JSON-Schema
runtime acceptance or application pass follows from these structural checks.

## Historical facts and remaining external inputs

The literal baseline still contains 101 unchecked entries, including 53 GAP/SPEC
rows. They are not 101 missing features. I12's report/task mismatch needs exact
later acceptance reconciliation; a generic later demo cannot close every old
failure. Old I16 partial checkpoints remain historical rather than current
release verdicts.

The original baseline release branch was 48 commits ahead of main. A concurrent
commit moved the observed head to `d8a74fe` during review, now 49 commits ahead;
no Git remote name was configured in that observation. Refresh at delivery. Lack
of a local remote does not establish that no external GitHub project exists.
Planning/category work makes the current tree dirty; the old clean/source-
unchanged claims are dated evidence. Canonical unrelated GAPS.md work is preserved.

Future external inputs remain scoped: authorized GitHub destination/publication,
actual selected free provider access/runtime resources, complete selected source
releases/terms, genuine denominators/outcomes and selected acoustic observations.
Their absence does not create a pregenerated-corpus or human-review prerequisite.
It also cannot be called actual acquisition, provider qualification or empirical
confirmation. LLM performance/bulk benchmark campaigns are out of completion
scope, not incomplete prerequisites and not passing observations.

All 122 category/recipe identities, 42 formulas and 11 original source scopes
remain. Concurrent category-realization source/graph/evidence is preserved.
No application test suite, browser, LLM inference, speech synthesis, account,
installation, purchase, provider setting or publication action occurred in this
review. Source inspection is evidence, not execution authority.
