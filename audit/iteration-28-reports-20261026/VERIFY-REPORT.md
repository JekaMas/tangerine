# Iteration 28 — verification and repair

Starting revision: `62f0274a5018451e956067af1068340028ea1288`.
Scope: `FIN-EMPIRICAL.P1`, `FIN-VERIFY.I28`; saved-data reports and coverage,
zero new model calls. This is iteration verification, not whole-release acceptance.
**Passed:38/38 cases (18positive,20negative), zero failures/skips**, on committed-clean source `4bbcd5d2fada14a9aa1650663aace9604d9a27bc`. The acceptance record supersedes the original32-case apply acceptance.

## Finding, cause and repair

**P2, repaired: declared annotation scope was presented as observed absence
coverage.** With one category declared and no windows, the actual screen said
“1 of 122 categories inspected for absence”. The same false claim appeared when
a source-annotated window had an unmapped event, leaving zero fully inspected
mapped windows. Native arithmetic already correctly retained unavailable ratios.

`empiricalPresentation.coverageSummary` now names the count `declared`.
`EmpiricalResult` labels declared scope separately and explains the need for
actual inspected windows, including unlisted pairs. It does not recalculate,
rehash, requalify or reject saved data. No new check, approval, gate or user action
is introduced. Population arithmetic/difficulty, admission/storage, experiment
coverage, requests/retries and rendering retain their separate owners.

Both counterexamples were observed through real native PostgreSQL/MinIO and
source-built Next.js in disposable storage. Their original incorrect DOM and
screenshot remain preserved. Fresh literal regressions check the corrected
labels, exact saved identity and unchanged unavailable measurements; the positive
ten-exposure report retains 2/10 → 1/5 and 2000/50 → 40/1 per 1,000 tokens.

## Sibling and error review

- Empty declared population and incompletely mapped source population: repaired
  together by the same presentation owner. Actual source/native counts remain
  distinct; a native annotation does not become a project absence observation.
- Undeclared categories, missing opportunities/tokens, secondary labels, genuine
  versus constructed eligibility, self-pairs, missing/mismatched follow-ups and
  planned/failed coverage: original independent native observations remain valid;
  no related arithmetic or eligibility owner changed.
- Saved selection, obsolete delivery, immutable reopen, malformed definitions,
  missing saved IDs, transient and persistent dependency failures: source and
  original actual browser/request receipts inspected. The common safe read owner
  logs and retries transient reads at most three times. Its persistent failure
  retains the report/fields, displays authored guidance and recovers via Refresh.
  Writes remain explicit and are not blindly replayed. No raw backend response
  becomes a UI message and no extra verification blocks ordinary use.
- Fresh console storage errors were investigated rather than suppressed. Actual
  exception/execution-context observations identify Read on reMarkable's isolated
  extension world; Tangerine runs in the separate default page world. No browser
  extension, permission or account setting was changed.

## UI/UX, typography and evidence

**UI/UX: pass for the selected Reports scope.** Actual Chrome selections show
the exact empty/incomplete/populated report, preserve unavailable measurements
and reload the selected immutable ID. Keyboard focus and horizontal table
scrolling remain visible. Existing unchanged error/recovery observations are
retained with their original finite scopes.

**Typography: pass.** The typography skill and project interaction/review guidance
were applied to actual screenshots, DOM/computed styles and keyboard actions.
1280×720,390×844,320×740 all retain Source Sans3 at17px/24.65px,14px quantitative
captions, left-aligned wrapping metadata, visible3px table focus and no page-level
horizontal overflow. The narrow table scrolls inside its284px region. The current
scope explanation and exact ratios are pictured in
`data/iteration-28-verify-20261026/scope-and-measurements-final.png`.

**Evidence: pass for actual saved-data behavior.** Retained native/JS/browser
observations have independent literal expectations; fresh observations cover the
changed display, both new counterexamples and the owned native fixture's zero
provider receipts. The browser download-event observer remains unavailable, but
the actual expected normal Downloads JSON from the observed button click exists
and equals its native snapshot. The copied file and separate receipt close the
file-delivery gap without browser-internal page/database access. The original
apply's missing observation is not rewritten as an observed event.

This is self-review, not an independent reviewer or linguistic gold. Original I23
HTTP503 and I26 uncertain/not-realized/false-alarm outcomes remain intact. Reading
those native/Lab records neither dispatches calls nor supplies genuine learner
populations, source-wide122-category prevalence or causal effectiveness evidence.
Unknown inputs stay unknown; optional acquisition and bulk/performance campaigns
are not prerequisites to these reports or ordinary exercises.

## Validation and preservation

The three invalidated original display/readout observers and five new review
regressions pass in `focused.log`; the sixth new case confirms actual download
delivery in `download-positive.log`. Eleven production display-helper tests pass.
The new browser fixture passes Go race/native execution with zero provider
receipts. Stable pinned Go vet/gofmt and locked Next.js source build pass.
Strict OpenSpec1.13.1 and complete DAG/discovery validation pass. The complete selected38-case DAG passed with `--require-clean` on `4bbcd5d2fada14a9aa1650663aace9604d9a27bc`. Every exact registered test identity executed; no substitution gap or required skip remains.

Original arithmetic/storage/coverage and bounded read recovery receipts are reused
as detailed in `REUSE.md`; their semantic inputs were not changed. No valid model,
speech or expensive native population test was repeated for a workflow stage.

Protected domain/prompts/source/scoring/contracts/migrations are unchanged.
The122categories/recipes,42formulas and11source identities remain preserved.
The user's one saved report and three planned experiments still match the original
observations. App3000, settings/media, canonical GAPS.md and existing user tabs
are preserved. The owned tab/viewport, proxy, containers and network were cleaned
up. No inference, synthesis, paid credits/overage, installation, acquisition,
deployment, postdeployment, PBT, financial execution or publication occurred.
