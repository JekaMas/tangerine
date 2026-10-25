# UI, UX, typography and evidence during verify

This is Tangerine’s project review procedure. `openspec-verify-change` reaches it
through `.agents/workflow-project.json` → `REVIEW_AND_VALIDATION.md`. Use it for
every selected iteration, including a backend-only iteration whose UI and
typography dimensions have justified not-applicable dispositions. It is a
development check, not a new step for a learner or a human peer-review gate.

Load the available `typography` skill when inspecting formatted output. Use the
pinned shared workflow’s verification and review guidance for interaction and
evidence inspection. No additional UI/UX package, visual judge, agent, provider
call or tool installation is automatically authorized by this procedure. State
which skill and guidance were actually used.

## Select the real scope

Read the selected iteration in the canonical change’s `tasks.md` and, for
iterations 17–30, its `completion-iterations.json` entry. Select every listed
behavior property plus its `FIN-VERIFY.I<n>` property. Extend the selection when
an actual dependency changed; do not treat the small review selection as a
substitute for the iteration’s complete affected behavior closure.

For each required case, reconcile an exact observation or an unchanged valid
receipt. Keep pass, fail, skipped, blocked, missing and not_run distinct. New
planned cases must first become executable tests through their named production
owners with independent expectations. Merely registering a command, writing a
test plan, checking a task box or passing structural validation proves no UI,
provider, linguistic or acoustic behavior.

## Stay within included limits

LLM performance benchmarks are excluded from apply/verify completion. Do not
start load/concurrency/latency/throughput/cost tests, model/parameter sweeps,
repeated judge campaigns or the bulk 732-case LLM benchmark. Keep functional
positive/negative and selected real-flow checks. Reuse valid native/Lab/media
receipts and deterministic fixtures; use only necessary authorized functional
calls within actual remaining included/free/local limits. Visual review,
report arithmetic, evidence inspection and export must not dispatch extra model
calls. No purchased credits, overage or silent provider fallback is permitted.

Excluded performance populations are out of scope, not release blockers and not
passing observations. Available functional-call timing/usage fields may be
reported descriptively; missing performance metrics remain unknown. This follows
the current execution scope in `specification/v2/docs/ai-development.md`.

For the continuation repair scope, also read
`specification/v2/docs/completion-contract-details.md` and the canonical change’s
`completion-coverage.md`. A seek alone cannot prove finite replay; a JSON editor
cannot prove a guided form; a standalone speech comparison cannot prove the
ordinary adapter path. History metadata must be observed through native list
responses and UI, with honest legacy fallbacks.

## UI and UX

Inspect the affected screens in a real browser, perform the selected actions and
read their results. Cover the meaningful empty, populated, loading, success,
error and explicit retry/recovery states for the change. Use test-owned records
and dependencies for destructive or failure fixtures; preserve the user’s
workspace, answers, provider settings and media.

- Inspect desktop at 1280 × 720 and narrow layout at 390 × 844. Add 320 × 740
  where a changed control, navigation, text or reflow can be affected. Use other
  specific breakpoints when the finding demands them, such as 960 or 1100 px.
- Check the primary action, understandable labels and status, request precedence,
  retained input, recovery guidance and the absence of unintended dispatches.
  Closing a disclosure, viewing an error or reloading saved work must not
  silently generate, grade, delete or switch providers.
- Exercise keyboard navigation and activation, visible focus, relevant labels,
  validation focus and the mobile menu. Watch for covered fields, focus traps,
  accidental autoplay, lost draft text and page-level horizontal overflow.
- Verify that title, date, status, answer, score and media refer to the correct
  saved record. Review completed results separately from editable drafts and
  checking progress. Optional explanation scoring remains distinct.

At iteration 29, reconcile all eleven routes: Library `/`, Prepare `/prepare`,
Saved attempts `/attempts`, Saved audio `/audio`, Listen/results `/listen`,
Optional LLM review `/reviews`, Reports/experiments `/reports`, Sources
`/sources`, Settings `/settings`, Recovery `/recovery` and Cleanup `/cleanup`.
Use representative actual/controlled states appropriate to each route; do not
call every provider or repeat every invalidated-independent functional case
just to obtain a screenshot. Earlier route observations may be retained where
their actual rendering and interaction dependencies are unchanged.

## Typography and visual hierarchy

Inspect loaded fonts, computed styles and actual rendered text together. A font
name or a web build cannot establish readability. Preserve the existing Source
Sans 3 body baseline of 17 px and 1.45 line height unless a justified change
keeps the same readability. The typography skill’s body-size, spacing and
45–90-character line-length guidance is contextual: a 320 px screen cannot be
required to fit a 45-character minimum.

Check primary score/action prominence, heading hierarchy, contrast, selected and
focused states, line wrapping, paragraph measure and spacing. Quantitative
amount captions and actionable severity descriptions use at least 13 CSS px,
preferably 14 px, rather than the observed 10–11 px shrinkage. This is a product
readability decision; do not present it as a WCAG minimum-font-size rule. Large
intentional titles are not defects merely because they exceed body-text advice.

Retain readable labels at desktop and narrow widths, with long content and the
actual selected/error states. Do not fix dense layouts by hiding the effective
request, shrinking important text or removing advanced functionality. Do not
apply typography prose conventions to machine identifiers, code or exact quotes.

## Evidence content and proof limits

Inspect evidence contents and their relation to the selected behavior. A file’s
existence, byte count, screenshot count, green summary or candidate’s own label
is insufficient. Use the existing operation IDs, record IDs, native receipts,
test results and source bindings; do not add schema-byte archives, repeated
stored-data revalidation or a new evidence database.

- Pictures show the actual route, relevant state and desktop/narrow layout.
  Inspect text and interaction as well as the image. Screenshots alone cannot
  prove audio realization, model interpretation, saved data or exact arithmetic.
- The final demo shows actual preparation, generated clean text and mutation
  key, stored speech, listening, a saved answer, checking, score/comments,
  recommendations and reopening. Label constructed developer answers. Disclose
  cuts, compressed waits, omitted stages and separately synchronized saved audio;
  retain the original observations. An edited demo may be useful without proving
  an uninterrupted real-time run.
- Audio is the actual selected saved recording and target/control set. Preserve
  speaker/accent assignment and intended versus observed pronunciation. An IPA
  request, provider instruction or symbolic transform never establishes that a
  listener can hear the requested deviation. Correct contextual/accent variants
  and mixed or unavailable observations remain explicit.
- Scores use independently expected arithmetic for the actual saved key and
  answer. The fixed 60/100 results fixture is not an assumed outcome for a newly
  generated random exercise. Missing explanations are optional; if supplied,
  their correctness and feedback are evaluated separately as specified.
- For AI-affecting development, apply `AI_DEVELOPMENT.md`: retain actual
  prompt/context/model/input/output/native and Lab evidence. A controlled
  transport proves its native boundary only. No additional paid inference or
  automatic judge follows from verification; the no-paid-credit rule still
  requires individual personal approval for any exception.

Reject these counterexamples: a screenshot from attempt A paired with attempt
B’s score/audio; a partial voice preview called a complete dialogue; a build or
file count called a UX pass; a planned/skipped/blocked case called executed; or
candidate-generated expectations called independent gold. Report the exact
unsupported claim and required observation. Do not discard original failures.

Mechanical tests can check observable interaction/layout and artifact relations.
They cannot automatically certify aesthetics or replace the agent’s actual
visual review. Assertions that a report says “passed” are not acceptance tests.

## Record the verdict and repair only within authority

In the selected iteration’s existing review/audit record, give **UI/UX**,
**typography** and **evidence** separate dispositions: **pass**, **finding**,
**incomplete**, or **not applicable with a concrete scope reason**. Cite the
inspected cases/artifacts, observations, retained receipts and limitations.
Backend-only work may justify no affected UI/style review; omission of the
dimension is not that justification. Use ordinary Markdown; no extra signature,
approval document or report schema is required.

Verify-only remains read-only. When the current request includes repair, address
in-scope findings, add the literal regression and reobserve the invalidated
cases. Reuse valid greens. Reconcile the complete selected iteration at the
stable committed boundary using retained valid evidence plus required new
observations; do not blindly replay the full suite. Perform stable-batch lint
and final evidence-manifest updates once where required. A new commit or a
planning/progress edit alone does not invalidate unrelated behavior receipts.

Missing optional provider/data observations remain visible for their selected
feature claims without blocking independent local exercises. This review never
adds human peer review, corpus acquisition, benchmarking or Lab as a learner’s
prerequisite.
