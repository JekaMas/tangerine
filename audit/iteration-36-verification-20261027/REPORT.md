# I36 verification and repair

Entry: clean `0d5ba2f` in the iteration16 worktree. Verify the complete selected
JFLEG supplement, repair findings and related source-consumer issues. This report
supersedes the earlier conclusion for the affected UI paths; their old observations
remain retained. Native corpus acquisition, parsing/projection, resume and local
reference membership are unchanged and keep their precise evidence boundaries.

## Findings, repairs and related cases

| Finding | Owner and repair | Discriminator / related coverage |
|---|---|---|
| P2: an obsolete More response appends after Refresh | `correctionSession.js` owns example read order. Every new read supersedes the previous result, error and loading completion. The JSX only renders state and triggers downloads. | Actual Chrome red40 versus expected20; repaired20, followed by an intentional current40. Pure cases also cover older errors, old completions while a new read is pending, pagination, recovery and disposal after leaving an import. |
| P2: issue-history Refresh has the same race | The existing `sourceSession.js` history owner now separates its current read from superseded requests. | Two literal tests fail before repair: old page replaces fresh history, and old failure produces an error after success. Both pass. Source rows already use import-generation ownership; its related stale-page case passes without an additional product change. |
| P2: a completed refresh clears an active export's shared busy state | The correction view owns reads and explicit exports independently. Refresh remains available; export progress and download errors remain owned by the active export. | Actual Chrome holds the real development dataset response, finishes Refresh, observes export progress and disabled duplicate-export controls, then saves754examples. Controlled test download503s retain20visible examples; retry downloads747. All1501originals/6004reference positions are independently checked again in these actual downloads. |
| P3: partial-data caption promises four references unconditionally | Render all available references, accurately explain the complete versus partial release and use a singular label for one supplied reference. | Two real constructed originals with one reference each; exact trailing spaces and text survive. A separate ref-only import shows0examples and usable controls. These are labelled fixtures, not acquired corpus or linguistic gold. |
| Missing evidence: empty/partial source UI and export failure states | Native storage owners create and commit two small test releases in the existing owned stack. Current Chrome exercises the actual source controls. | Empty/partial, export loading/failure/recovery, keyboard and1280/390/320layouts are observed. Successful source responses and the DOM are real. Only delayed response order and labelled HTTP failures are controlled. |

No new source-admission, saved-data consistency, approval, human-review or learner
qualification gate was added. Refresh stays reachable during reads. The existing
request owner logs diagnostics and retries transient GETs before authored recovery
guidance. Failed reads/exports retain data and enable recovery; raw backend canaries
do not reach the user. No automatic generation, inference, grading or write follows
from these controls.

The source domain still owns native roles, exact coarse Unicode transforms and
reference membership; app owners own storage/projection/readback/evaluation assets;
the web view's session owns asynchronous read state. The history repair stays in
its existing owner. There is no new framework, service, schema, migration or queue.

## Full-scope review and retained evidence

The seven original I36 properties remain selected. Review covered native core
file recognition, exact same-directory/partition/line joins, every reference
position, spellcheck separation, source/tool/experimental origins, coarse replay,
invalid M2 metadata, completeness, staged/accepted resume, tuple cursor readback,
partial/missing references, dataset terms, local Lab input/report retention and
exact reference-membership semantics. Fresh portable Lab input is admitted once;
saved memory/DB data are trusted. Outside-reference corrections remain semantically
unjudged; there is no invented grade or semantic-gold claim.

The acquired owner release remains29files plus its original archive,1501originals,
6004reference positions,1501spellchecked lines,1501M2sentences,22549M2annotations
and1733experimental CSV records:34789native rows,1501primary families. The19invalid
tool edits and five affected sentence rows stay non-authoritative metadata. No
archive is downloaded or re-audited; no full corpus import is replayed. Original
native/import/consumer receipts are indexed in the prior NATIVE-EVIDENCE.json.

Changed dependencies are confined to the correction UI session/rendering and
issue-history ordering. They invalidate the earlier affected UI observations,
so the full current browser regression and new counterexamples were observed.
All34existing source-session JavaScript assertions were also rerun, together
with12new cases. The backend import, source-derived mappings and local evaluator
production owners did not change; their33unique Go race observations are retained.
Two new native cases exercise the small UI fixtures and commit their existing IDs.
The previous first fixture pass remains valid: the later added commit test changes
no earlier fixture assertion, helper or production code.

The regression initially assumed the latest source card still described the full
release. Its input now includes newer partial fixtures. The corrected test checks
the latest partial status and the selected full import's actual complete report
separately. The original failure is retained as a harness/oracle repair, not a new
product defect. The two fixture imports are explicitly committed through the
production owner; their native rows/IDs remain available in the owned stack.

The first expanded reconciliation exposed a receipt-reader defect: six new
assertions compared a shell-written exit-code file to a string without its line
terminator. Parse the exit code as an integer. All six directly affected assertions
then pass against the unchanged native/JS/browser observations. The original
failed reconciliation remains retained. This does not change a product oracle,
weaken an expected outcome or require another corpus/browser/provider run.

## UI/UX — pass

Used OpenSpec verify and the project's pinned UI/UX/typography procedure, with
installed Chrome through its existing Playwright test adapter. The affected scope
is Sources, written examples, dataset downloads and related issue-history reads.
It is not another eleven-route or generated-exercise acceptance campaign.

Current actual Chrome observes20→40pagination, the old-page/Refresh counterexample
and repair, read loading with retained data,503→200automatic recovery, exhausted
read retries with retained examples and usable Refresh, correct download progress,
exhausted export retries and explicit successful retry, and reopening the same
compact138byte saved locator. Original text, all four references, separate
spellcheck and provenance are visible. Partial and empty states use real saved
fixtures and working controls. Keyboard Enter/Tab, visible focus, mobile navigation
and desktop/narrow layouts pass; current functional sessions report no page errors.
Application browser calls are GET only. No user data or live workspace was used.

## Typography — pass

Applied the available typography skill with the project baseline. Source Sans3
is actually loaded, body text17px with24.65px line height, control text16px and
44.8px control height, visible3px keyboard focus and readable bounded paragraph
measure.1280×720,390×844and320×740reflow without page overflow. Inspected original
and all-reference screenshots, partial original/one reference, empty result,
download-progress and recovery screens. No fonts were shrunk or features hidden.
Exact source spelling, whitespace and grammar remain unedited.

One initial narrow capture placed the empty message below the controls and showed
an unsettled viewport/compositor artifact. Focused captures frame the actual
empty result after layout settles, with one measured navigation header. Both raw
captures remain retained; no CSS or DOM was altered for the screenshots.

## Evidence — pass within the written-source scope

Private retained evidence is `data/iteration-36-verification-20261027/`:

- `browser-red/` and `history-red.tap`: original decisive product failures.
- `sessions-green.tap`:46actual passing JavaScript assertions.
- `native*.jsonl`, `verify-ui-fixtures.json`, `verify-fixtures-commit.json`: two
  actual Go race cases, exact labelled partial/empty source inputs and durable IDs.
- `browser-green/`: new actual ordering/export/partial/empty actions and downloads.
- `browser-regression-fixed/`: current complete source UI regression; the earlier
  `browser-regression/` retains the latest-source fixture mismatch.
- `browser-visual/` and `browser-states/`: current full references, controls and
  focused partial/empty result pictures across all three widths.
- `jfleg-verification.mp4`:4.44seconds, silent, uncut actual Chrome with fast
  automated actions; visibly labelled controlled delays/failures and constructed
  partial/empty sources. Original WebM sessions are retained. Decoded frame content
  was inspected alongside the actual screenshots and native record associations.

The clip shows browsing/refresh/download/partial-source work against already saved
data. It does not show the preceding corpus import, a generated exercise or audio
qualification. Audio is not applicable to this written-correction increment.

The DAG adds8literal cases to the same seven properties (22total), with exact
source bindings and independent counterexamples. Its command reconciles retained
native observations and fresh directly invalidated UI/session observations; it
does not replay corpus import or inference. Final committed-clean acceptance is
recorded separately in ACCEPTANCE.json after the stable boundary.

All122categories/recipes,42formulas, provider/quality registries and11original
source scopes are preserved. No user-stack restart, installation, provider/model
call, purchase/overage, deployment/postdeployment, PBT, financial execution, source
script execution or publication is included. This is self-review; no independent
reviewer, semantic-index or IDE evidence is claimed. No product decision remains
for these repairs. Other supplements and model/acoustic claims keep their existing
scope and evidence limits.
