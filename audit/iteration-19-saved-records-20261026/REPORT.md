# Iteration 19 — Persistent guidance and recognizable saved work

Scope: UX-02/UX-03, FIN-UI-02.P1, FIN-UI-03.P1, FIN-VERIFY.I19.
Started clean at bb88023 in tangerine/iteration-16-release. Acceptance is scoped
to these25 executable cases; no later iteration or all-product claim follows.

## Delivered behavior

| Finding or retained owner | Result |
|---|---|
| Native title/excerpt/date fields already exist | Retained their existing storage/projection owners and byte-identical canonical/embedded response schemas. No migration or duplicate metadata store. Real PostgreSQL/MinIO fixtures show original heard Picnic after catalogue renaming,160-character answer excerpt plus ellipsis, exact saved answer, original timestamps, full IDs and stable pagination. |
| Identical visible record names/dates | Shared savedRecord/RecordIdentity presentation shows full identities when title/date collide. Records sharing the first8ID bytes remain distinguishable in Prepare, Attempts, Audio and review choices. Ordinary records keep title/date/state/answer prominence. |
| Legacy failed phases without failure details | Shared failureMessage now uses saved failed/interrupted phase as well as actual failure metadata. Unknown/empty reasons have plain-English fallback and useful action. Canonical MISSING_CREDENTIALS has Settings guidance. Raw backend/provider messages are never display text. |
| Review chooser hid retained rows after a read error | Error guidance and retained choices render independently. Refresh and explicit Retry keep the same full-ID choices available. Empty/loading/initial-error views remain distinct. Selection is read-only. |
| Recovery and stale failure | Actual explicit resume reuses the original first audio asset, requests only the missing second piece from a controlled local endpoint, persists completion and clears the saved failure. Reload shows complete state; another failed row does not contaminate it. |
| Restart fixture copied a server lock | The sibling test now uses NewServer. Its exact native race case and Go vet pass. Production API/storage/speech owners are unchanged. |

No new preflight, consistency audit, approval, schema round-trip or user-facing
verification gate was introduced. Existing bounded GET recovery still logs and
tries three times before locally authored guidance. Viewing failure, refreshing
or selecting a record never dispatches a write/LLM/synthesis. Explicit resume
retains its existing action/idempotency/persistence owner.

## Evidence and proof boundaries

SELECTION.json lists14 materialized literal continuation cases plus11 shared-owner
and sibling regressions. The25-case selected command executes the actual pure JS
owners and independent oracles over retained native/CUA interactions. It does not
replay browser/provider actions merely to obtain a new commit hash.

Native execution uses real typed storage, publication, attempt answer writes,
list routes and resume finalization in test-owned PostgreSQL/MinIO. Clean-text,
mutation and local speech endpoint responses are constructed transport packets;
the few PCM samples are synthetic fixtures. Display-only failed/completed records
and fixed historical dates are explicitly seeded. They do not represent genuine
learner outcomes, acoustic mistakes, accents or provider qualification.

The original interactive Go server hit its default10minute harness deadline
AFTER the useful browser observations. Its projection/pagination subtests passed,
but that root is retained as a failed run. A native persisted readback separately
passed against the exact original IDs/assets. The tracked tests/history-browser
launcher now supplies -timeout=70m and the explicit done-file lifecycle. It was
executed on fresh owned storage: actual UI resume completed, then the full native
root and both subtests passed before cleanup. This repaired run is separate from
the original screenshots/IDs; test_recovery_positive checks both sequences. No
failed run was relabelled green, and unaffected UI suites were not replayed.

The original helper observer also exposed a harmless expectation-parser mistake:
rendered paragraphs contain blank lines. The test now extracts the first nonblank
state line and still requires the independently specified Draft/Completed/Draft
and exact IDs. The directly affected records case passed before the full selection.

Native receipts: original projection/pagination, exact persisted readback,
TestNativeSpeechRestartPositive and corrected interactive root under
`data/iteration-19-saved-records-20261026/`. The corrected root's receipt and before/
after/UI records are under `harness-fixed/`. requests.jsonl retains actual method,
path, query, attempt number and scenario; no private credential headers are logged.

The shared Go fixture file changed only TestNativeSpeechRestartPositive. The36
structural source pins are reconciled in PIN_RECONCILIATION.json. Every other
function body is byte-identical; old receipts retain their original scope and are
not presented as new current-revision behavior. The six directly affected existing
FX helper cases passed without repeating their media/report/model siblings.

## UI, UX and typography review

Used the installed typography skill, project UI/UX verification procedure and
pinned workflow review guidance. This is self-review with independently authored
literal expectations, not an independent human review.

Actual source-built Prepare, Attempts, Audio and review chooser were inspected at
1280×720,390×844 and320×844. Checked loaded17px Source Sans3 body,14px identities,
long titles, ID wrapping, readable failure panels, full-ID navigation, pagination,
empty/loading/error, bounded read retries, retained choices/input, explicit retry,
four actual3px keyboard-focus steps and Enter disclosure activation. No page-level
horizontal overflow was observed. Intentional heading sizes were retained.

Key images include screens/attempts-320.jpg, audio-390.jpg, reviews-320.jpg,
native-attempts.jpg, persisted-failures-desktop.jpg, review-retained-error.jpg,
record-details-keyboard.jpg and recovery-harness-complete.jpg in the data folder.
The12-width/route observations are in observations.json; REVIEW.json cites their
contents and limits. A trial10px HTML-head injection remained14px after framework
handling; it is retained as attemptedTinyVariant, not a passing10px UI negative.
The review oracle uses the specified alternative omitted-typography case and a
clearly constructed10px fact counterexample to reject unsupported acceptance.

Semantic search/status reported no index for this exact checkout. Exact field,
route and caller tracing resolved ownership. No semantic/IDE evidence, new index,
agent, package installation, deployment, postdeployment, PBT, financial execution,
publication, purchased credit, overage, hosted model or actual synthesis occurred.

PRESERVATION.json records unchanged native production, speech and specification
scopes: all122 categories/recipes,42formulas and11full-source scopes are preserved.
The running user app on3000, its database/settings/media and unrelated canonical
GAPS.md work were untouched. Only owned test containers/networks were used.

## Acceptance checkpoint

The stable selection passes25/25 informationally while dirty. Commit the final
implementation and run the same exact selection with --require-clean. Only that
receipt accepts I19; task boxes remain unchecked until it passes. Native/build/
format/vet observations retain their exact stable source identities. Strict
OpenSpec1.13.1, graph/discovery and preservation are reconciled on that revision.
