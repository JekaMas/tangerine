# Iteration 2: domain storage and asset lifecycle

Status: iteration 2 accepted. All 88 required cases have exact passing native
observations from committed clean candidates, reconciled against the unchanged
current behavior inputs in [ACCEPTANCE.json](../../openspec/changes/implement-teacher-error-trainer/evidence/iteration2/ACCEPTANCE.json).
The first composite run remains failed because Docker prevented storage startup;
its valid 36 greens are retained and the unavailable 52 cases passed in the clean
storage rerun. This is a reconciled full iteration, not a claim that the failed
composite command passed.

Scope is the approved second development iteration plus the two iteration1 review
findings. The shared storage layer is implemented through the real Go owner,
PostgreSQL and private MinIO. It stores complete schema-validated immutable
payloads, exact schema/content digests, version-scoped nodes and references,
revision heads and diagnostic audit in atomic batches. Missing/wrong scoped
references, conflicting revisions and unsafe JSON fail without a partial commit.
Original UTF8 bytes are private assets; JCS never normalizes the answer's Unicode.

The active151-schema catalog is embedded byte-identically and resolved offline.
This uniform registry/storage contract supports the later text, key, settings,
receipt and result owners. The storage fixtures do not establish their later
semantic validity, key replay, grading arithmetic or provider behavior. There is
no new public HTTP storage API, account system or human-review prerequisite.

Asset reservation saves the operation and frozen owner guards together. Unique
opaque private keys are uploaded outside a database transaction, fully read back
and measured, then linked with the new owner/reference/head/operation outcome in
one transaction. A stale owner leaves an orphan. Exact native multipart IDs are
saved before parts and incomplete uploads are aborted explicitly on recovery.
Repeated completed requests return saved outcomes; conflicting concrete request
identity fails. Explicit30-day orphan preview respects historical references and
never erases bytes automatically. Full user backup/restore/deletion remains the
already required later iteration, not a removed requirement.

Migration003 is additive;001/002 and legacy fields remain unchanged. An existing
foundation upgrade first makes an original-format native database/media backup,
records original checksums/table inventory/per-entry digests, verifies its tar and
remote bytes, then commits new schema/registry/backup receipt. Tests restore that
native dump into another real PostgreSQL database and compare the retained data.
Fresh initialization has no upgrade backup. Unknown/changed/non-prefix migration
history fails before any write. Readiness now rejects altered migration checksums,
missing catalog/domain columns, missing immutable guards and mismatched registry,
fixing the false-ready issue observed in iteration1.

The real Chrome driver observes populated Library data, safe projection, failure
alerts and Refresh recovery. It sends requests to the real application; no HTTP,
database, object-store or DOM substitute is used. Test-created draft reference
snapshots exercise the storage resolver only and are never published exercises.

Graph:14 new bounded properties,56 exact cases, two distinct positive and negative
packets per property. Together with the invalidated32-case foundation closure the
required iteration selection is88 cases. All later feature properties remain
required with their independent states. Whole-product acceptance is not claimed.
Original122taxonomy/recipe IDs,42formulas and11full-source scopes are unchanged.

Native first run retained47/52 greens and five failing fixtures. Chrome's alternate
valid101 handshake phrase and missing original required catalog fixture fields
were corrected; the five exact fixtures then passed. Later asset/migration owners
changed, so those receipts do not stand in for final acceptance. A subsequent
run was interrupted by Docker Desktop losing connectivity to its VM. Native
restart restored it temporarily; further failures were retained as unavailable,
not green. A later image-contained Go run avoids the host cache mount used during
those failures; no causal root-cause claim is made. Volumes and unrelated canonical
GAPS.md remain retained. No provider inference, synthesis, model setup, purchase,
publication or independent-review claim occurred.

The pinned Go1.26.5 race suite and vet/gofmt checks passed on the built source
image. Current strict OpenSpec, graph/discovery and2,920 finite fixture/set identity,
original registry preservation and oracle-sensitivity assertions passed. Shared
workflow mechanics were not changed and their valid retained receipts are reused.
Actual native outputs, clean candidate identities and exact per-case correspondence
are linked in the acceptance record, separate from static and focused observations.


Final source-review repairs: effective-binding hashing now excludes only its id
and own digest, while render hashing excludes exactly its specified identity
fields. Four native Go golden cases have independently generated literal digests.
Asset reservation identity retains the caller's operation context as well as
frozen byte/owner parameters. Stream uploads recover existing bytes rather than
overwriting them; recovery serializes with the asset upload owner. Three native
stream/multipart regression cases passed after those final repairs. Unused copied
domain-map files were removed from the API; the full normative maps remain in
specification/v2, and the schema catalog is the runtime consumer's only copy.

Dirty acceptance evidence:84/84 passed before the final hash/context repairs;
repaired56/56 storage/digest selection passed afterward. The unaffected32-case
foundation observations remain valid. Stream changes were then observed by their
three exact native fixtures. Final stable vet/gofmt passed. The final clean acceptance below supersedes these informational dirty observations.


Clean-candidate pass/failure disposition: foundation32/32 and typed-digest4/4
passed at clean e55e283. Storage startup observed0 cases when Docker's API lost
VM connectivity (HTTP500/no route to host); that command is unavailable evidence,
not green. The current parent-trace correction changes only nonsemantic reference
metadata, retaining identical native case/scenario/property/test/source/oracle
records and all production/test inputs. Static correspondence is revalidated;
valid committed-clean36-case observations are retained and only the unobserved
52-case storage closure is rerun. TRACE-CORRECTION.json records the exact boundary.


Final acceptance: clean e55e283 contributed32 foundation cases and4 native owned-
digest cases; clean f654b39 passed52 storage/browser cases. The reconciliation
checks every exact test identity against reparsed complete native logs, case and
scenario records, source hashes, execution bindings and all declared production/
test dependency bytes. Only the recorded parent-reference typo differs; neither
old receipts nor their fingerprints are rewritten. All44 positive and44 negative
cases are accounted for; there are no skips, substitutions or missing identities.
The same clean Go command observed all17 actual native tests with the race detector.
Stable pinned vet/gofmt and the current strict OpenSpec, graph/discovery and2,920
structural assertions remain valid.

Complete native fixture outputs are retained under evidence/iteration2/
clean-foundation-native and clean-storage-native, including the source archive
member hashes, database/object readbacks, multipart outcomes and browser DOM.
The unavailable startup output remains separately retained. The reproducible
audit/reconcile.py verifies the original clean receipts against the current DAG;
it is an evidence audit, not a substitute runtime test. Acceptance-record edits
change no application, test, fixture, graph or command inputs.

Later15-stage product work remains required: AI Lab, provider access, generation,
mutations, speech/acoustics, listening, answer checking, scoring/disputes, imports,
reports, full backup/restore/UI and release. Shared storage supports those owners;
it does not implement their semantic actions. The legacy catalog remains a safe
Library projection, not an alternate complete exercise workflow.

Local preview restored: actual existing tangerine-i1 volumes upgraded to003, with
one original-format migration backup and151 registered schemas. Ready/health/
Library returned HTTP200; the fresh Library remains empty and provider credentials
remain unconfigured. No synthesis/model setup is implied by speech readiness.
Native preview receipts are retained in evidence/iteration2/preview-*.
