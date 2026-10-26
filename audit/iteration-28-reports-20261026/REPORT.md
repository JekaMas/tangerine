# Iteration 28 — saved-data empirical reports and coverage

Implementation and self-review are complete; committed-clean acceptance is
pending. The selected properties are `FIN-EMPIRICAL.P1` and `FIN-VERIFY.I28`.
`SELECTION.json` registers 32 literal cases. No model call, speech synthesis,
provider change, purchase, installation, acquisition, deployment or publication
occurred. This is the I28 report capability, not whole-product release acceptance.

## Implemented behavior and ownership

Reports now show the complete selected population, exact reduced fractions and
their unreduced numerator/denominator, annotation/window/token/category coverage,
native versus mapped labels, distinct-event relationships and confusion.
Constructed/model origins, uninspected categories and unavailable denominators
remain explicit. Token-density labels explain the 1,000 multiplier.

Learner outcomes are separate from source frequencies. The screen explains the
eligible first-answer denominator, optional Wilson interval, unrated reason and
excluded observations. Paired change stays descriptive; it does not establish
that recommendations caused improvement. No human review or population-collection
gate is added to ordinary exercises.

| Finding | Root cause and repair | Owner / proof |
|---|---|---|
| Self-referential follow-up | A record could count itself as a before/after pair. Require two distinct observation identities when selecting a pair; otherwise retain the unavailable paired result. The report still saves. | `internal/empirical.DifficultyReport`; original red, supported/self pair and four origin/participant/missing/outcome sibling cases. |
| Hidden report scope and counts | The old compact view hid most provenance, original denominators, difficulty missingness and relationships behind JSON. Render the existing saved native results with readable explanations. | `EmpiricalResult` renders; `empiricalPresentation` owns display labels only. Arithmetic/storage and the unchanged download handler retain their owners. |
| Saved selection/reopen | An asynchronous report could arrive after its URL fragment, and a newly selected/saved report could leave the previous ID in the URL. Read the explicit report query once, update the URL with the delivered report ID, then focus/scroll an explicitly requested fragment after delivery. | `useReports` owns selected read/URL continuity; the result component owns anchor focus/scroll. Actual selection→reload identity and visible landing are observed. |
| Metadata alignment | Global definition-list styling right-aligned the new metadata. Scope left alignment to the population view. | Reports CSS; inspected 1280/390/320 screens, no document overflow, body 17 px/24.65 px and numeric captions 14 px. |
| Evidence-reader assumptions | Initial observers assumed TAP and all-success Gemini records. Actual Node output uses its named-test reporter; the retained six-wire Gemini record contains five HTTP 200 responses and one HTTP 503. Parse the real reporter and preserve the failure. | Three focused repaired observer cases; the original failed 32-case receipt remains retained. No replacement model call. |

Native report admission/save/readback remains in `app/empirical_reports`; existing
`empirical_report`/private assets retain the input/report association. Existing
`qualityCoverage` calculates frozen dataset polarity/completed-row coverage.
Request retries and selection delivery remain in the existing request/session
owners. No API, migration, queue, schema-byte archive, repeated stored-data audit,
provider fallback, prompt change or new approval boundary is introduced.

## Actual observations

- Ten constructed annotated exposures contain two mistakes and eight correct
  controls. The report retains 2/10 and exact 1/5 for prevalence/opportunity rate,
 2/2 event share, and 2000/50 → 40/1 per 1,000 tokens. Only one category is inspected;
  all 122 remain visible with their actual unknown/known meanings.
- Four constructed windows produce A/B support 1/4, conditional 1/2, lift 1/1 in
  both directions, plus reference/prediction proportions 2/3 and 1/3. Secondary
  labels do not invent additional independent events or relationships.
- Constructed participant-shaped eligibility fixtures test two declared first
  answers and one follow-up. They are not real learners. The result remains
  unrated below 100 observations; the paired 1/1 change has no causal claim.
- Missing/zero denominators, unmapped annotations, model/constructed attempts,
  invalid self-pairs and unobserved polarity coverage stay unknown/excluded.
- The current user's saved constructed two-sentence report reproduces identically
  in disposable native storage. The three saved generation datasets remain
  constructed and planned: zero completed rows across 122 coverage entries.
- Real Chrome selection, named population reproduction, exact rendered values,
  all-category/unknown views, malformed definition retention, keyboard selection,
  table focus/horizontal scrolling and selected report reload are observed.
  Transient reads yield 503, 503, 200; persistent reads stop after three HTTP 503 responses
  with authored guidance and retained report/fields, then recover through Refresh.
  A missing saved report recovers through another named selection.
- The disposable browser fixture saves five report snapshots and finishes with
  **zero provider receipts**. Every browser POST was report creation; no model,
  experiment Run, speech or other execution route was dispatched.

## UI/UX, typography and evidence review

`REVIEW.json` records separate **pass** dispositions for the selected UI/UX,
typography and evidence scope. The typography skill and project review guidance
were applied to actual screenshots, loaded/computed styles, visible text and
actions. Metadata stays left-aligned; long values wrap, tables retain named
keyboard scrolling and 3 px focus, and saved-link landing clears the mobile header.
The scope is Reports; the eleven-route full-flow/video review remains I29.

This is self-review using independent literal expectations, not another agent,
human reviewer or candidate-generated linguistic gold. I23/I26 native/Lab files
were inspected without re-execution. Their actual failures, false alarms and
uncertainty remain, as described in `REUSE.md`.

The download control activated, but the browser download-event observer timed
out; browser file delivery is **not claimed**. Native immutable report JSON and
readback were verified, and the existing download serialization handler was not
changed. An attempted browser-internal Downloads page was blocked by policy;
no workaround or browser permission change occurred. This extra tooling limit
does not certify or invalidate an unchanged file-transport implementation.

The first fixture setup and generic viewport-control failures are retained and
classified as harness/tool limits. An ordinary test-owned loopback network and
documented tab-scoped CUA emulation supplied the actual observations; all temporary
overrides were cleared. Retained console warnings identify an installed browser
extension; unrelated browser settings were preserved.

## Data and validation boundaries

No genuine learner cohort, corpus-wide 122-category frequency table, recommendation
effectiveness estimate or new model-performance population is claimed. Those
inputs remain unknown until actually collected/imported. I27 restricted owner
releases are not selected as available populations here. No product decision or
new model campaign is needed to implement/test this report capability.

The original 122 categories/recipes, 42 learner scoring formulas and 11 source scopes,
source adapters, prompts, contracts and migrations are unchanged, verified by
the baseline diff in `PRESERVATION.json`. The running user's one saved report,
three planned experiments, app3000 and canonical `GAPS.md` remain unchanged.
Only the owned disposable test stack, proxy and Chrome tab were removed.

Stable Go 1.26.5 race/native and meaningful follow-up checks, Go vet/gofmt, locked
Next.js source build, OpenSpec 1.13.1 strict validation and evidence DAG/discovery
checks are retained. `REUSE.md` identifies fresh/retained scopes and original
failures; no valid heavy test or provider run was repeated merely for a new
workflow stage. Raw receipts/screenshots/input/output are under the ignored
`data/iteration-28-reports-20261026/` directory.
