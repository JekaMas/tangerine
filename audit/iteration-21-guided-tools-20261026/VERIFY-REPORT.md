# Iteration21 verification and repair

Scope: UX-08, FIN-UI-08.P1 and FIN-VERIFY.I21. Review baseline438687b was clean.
This verification supersedes the apply report's no-findings conclusion. The
original cf0f32d receipts and failed baseline observations remain retained.
Current acceptance revision and exact outcomes are in VERIFY-ACCEPTANCE.json.
Later continuation iterations and full-change release acceptance are out of scope.

## Findings, causes and sibling repairs

| Finding | Trigger, consequence and repair | Verification |
|---|---|---|
| V21-01 · P2 · intended selection and Refresh | Refresh cleared a failed report's guidance without retrying its detail. A held old collection refresh could reload experimentA after the user selectedB. Global read/action busy and error deliveries also mixed responsibilities. One reports session now owns intended IDs, per-record request order, separate error channels, write progress and late action readback. Reads start with the chosen identity and do not disable unrelated Save controls. | Baseline/current real CUA failures/recovery, held old Refresh/new selection, failed-new-selection retry, concurrent saves, obsolete action success/failure, malformed input during a read, disposal and completed Save before a slow list. |
| V21-02 · P2 · optional comparison blocks a valid record | Main experiment delivery awaited a comparison asset. Its503 hid an otherwise readable saved experiment. The main record is delivered independently; optional details have their own authored guidance/retry and request order. Same-asset prior comparisons survive temporary failure. | Actual browser experiment remains visible and usable through comparison503; dedicated Retry requests only the asset. Current owner cases cover obsolete comparisons and retained prior observations. No Run/Resume/Cancel is clicked. |
| V21-03 · P2 · confirmation belongs to a preview | Starting a replacement preview left the previous confirmation control visible. Confirming during the pending request enabled Apply for the unseen returned plan. Clear the replaced preview and accept confirmation only for its delivered current plan. | Actual baseline confirmation violation; corrected pending/replacement/failure/retry UI and owner cases. Real native confirmation/apply erases only the chosen first attempt; second and shared audio remain. Unknown shortened IDs safely return a blocked plan, not an assumed422. Shared presentation now says Selection needs attention and gives full-ID/named-choice guidance for both unavailable and referenced records. |
| V21-04 · P2 · selected model eligibility disagrees | The chooser hid unselected models but the builder checked only profile ID/role. A previously selected profile could be frozen with model unselected while another model existed. One shared generationProfiles predicate now supplies both chooser and builder. | Original builder red, current7 builder passes, actual setup-needed selection/topic/C1 retention and zero POST. Recovery preserves the chosen profile; no silent fallback or provider call. |
| V21-05 · P3 · file read error/order | The page awaited File.text without an error/order owner. A rejected read escaped guidance; an older file could replace newer or typed content. One definition-file owner per editable definition now retains input, suppresses obsolete delivery and provides local recovery text. | Current literal deferred read/failure/retry/edit/disposal assertions and actual browser file chooser → native report import with exact population. A failing browser filesystem read is not claimed; that exception is qualified at the production file owner. |
| V21-06 · P3 · ordinary diagnostic readability | Same-minute saved experiment buttons were indistinguishable; unavailable metric captions exposed backend reason tokens. Full identities/date captions and authored unavailable labels preserve content. The first corrective mobile image exposed cramped row-oriented identity captions; final stacked secondary controls restore hierarchy and readability. | Native122-row category view, exact unchanged arithmetic, distinct full IDs, six actual responsive layouts, loaded typography, keyboard/mobile-menu observations and inspected screenshots. Full native diagnostic payloads remain available in Advanced. |

No material product choice or unresolved I21 finding remains. No additional API,
schema, database migration, byte archive, accepted-data rescan, peer review,
provider fallback or learner gate was introduced. Pages render, session/file
owners coordinate delivery, builders construct submissions, the shared client
logs/retries safe transient reads, and native owners retain freezing/arithmetic/
lineage/deletion responsibilities. Failed writes are not replayed automatically.

## UI/UX — pass

Current source-built browser observations cover valid/empty/populated/loading/
failure/retry states, retained topic/level/profile/definition inputs, intended
record recovery, optional diagnostics, independent Save controls, exact identities,
preview/confirmation/apply and native reopen. Three list-only CUA observations
(RecordPicker failure/pagination/empty) are reused because their component,
saved-list/client and adapter branches are unchanged. Current native selection
and current deferred owner cases cover the changed lifecycle. This is scoped
self-review using independent literal expectations, not a separate reviewer.

## Typography — pass

Used the installed typography skill and pinned project UI/UX procedure. Actual
reports and Cleanup are inspected at1280×720,390×844,320×740. Source Sans3 loads
at17px/24.65px body; controls are at least44px tall, helper/identity text14px,
keyboard focus3px, with no horizontal document overflow. Primary Save controls
remain distinct from secondary saved-record choices. Tables keep local scrolling.
Full-page Cleanup captures can position sticky navigation/Skip focus at a scroll
offset; those capture artifacts are retained and not called product clipping.
The browser's native required-field popup follows its installed locale; authored
application guidance remains English. Mechanical checks do not certify aesthetics.

## Evidence — pass within the selected boundaries

All32 registered current verification oracles have independent literal outcomes.
They inspect actual native/CUA contents and retain45 observed owner assertions
(17 reports/file/metric/request,15 Cleanup,7 builders,6 existing starter cases)
and one fresh native Go-race pass. The completion command rechecks recorded
content and stable bindings without redispatching those boundaries. Native
Postgres/MinIO/HTTP saves/import/reopen/delete are real; controlled status/delay/
empty replies are explicitly test-owned. Constructed text/key/PCM and offline
models establish no linguistic, acoustic, authentic corpus or live-provider claim.

The native finalizer records0 provider receipts, two planned/not_run experiments
with no outputs/receipts, first attempt absent, second present and shared audio
present. No inference/synthesis, paid credits/overage, PBT, financial action,
deployment/postdeployment, installation, publication or subagent occurred.
No semantic/IDE index claim is made; exact selected owners were already known.

The final frontend source build passes. OpenSpec1.13.1 strict validation reports
zero issues; DAG/discovery/compatibility pass structurally. Native Go and its
fixture dependency set are unchanged, so the original minimal unfiltered vet
receipt remains valid; the new real race observation also passes. The original
all122 categories/recipes,42 formulas and11 source scopes remain unchanged.
See VERIFY-PRESERVATION.json, VERIFY-SOURCE.json, VERIFY-REVIEW.json and
VERIFY-SELECTION.json. Raw evidence is local/ignored under
data/iteration-21-verify-20261026/. Original baseline reds and the registration
adapter's corrected unreferenced-command error remain retained.

Owned test containers/network/gateway/tab were removed. Existing user app3000
remains HTTP200; its settings/database/media, prior browser tabs and canonical
GAPS.md are preserved. Changes are committed in the iteration worktree, without
activation in the user's existing running app.
