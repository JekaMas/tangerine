# Iterations 1 and 2 repair

Baseline: 75c4950615c8a6c72427eaf85da19de4013cb391. Both previous acceptance records remain historical; the latest native review supersedes their completeness conclusions.

## Anchors and durable transitions

1. assets.go and multipart.go: one acquired per-asset advisory-lock connection must serve all guarded reads and short transactions, without a transaction during transfer. Native ten-connection witness must progress and preserve exact bytes.
2. domain.go validateProjection and precommit graph validation: parent_evidence_ids has a mandatory evidence-parent role; WriteDocuments and LinkAsset share validation before committing documents, references, heads, audit and operation.
3. multipart.go recovery: exact native abort finalizes the original operation as failed with an immutable typed error and asset result, preserving request identity. Explicit retry with a different key and identical frozen intent reserves a new operation/asset; old key cannot complete.
4. storage.go readiness: expected guards must be enabled, attached to the expected tables/events and frozen function. Rejection keeps liveness independent; restoring guards recovers readiness.
5. Existing I1 checksum/required-column regressions and populated/error/Refresh Chrome cases remain required and are revalidated with the complete combined selection.

## Invalidation

Shared app/domain/asset/multipart/storage production inputs change, invalidating all dependency-bound I1/I2 native cases. New native regression fixtures and command inputs invalidate their own cases. Update source/dependency fingerprints once the batch stabilizes. Historical receipt bytes remain unchanged. Original taxonomy, recipes, formulas, registries and migration001/002/003 are preserved.

## Completion

Direct native regressions, complete combined selection, Go race/vet/format, strict OpenSpec/DAG/discovery and preservation checks; commit candidate, run same selection with --require-clean, commit acceptance record, fast-forward canonical checkout preserving unrelated GAPS.md and restore existing preview volumes. No provider inference or later-product acceptance.

## Additional native finding in the frozen-retry closure

The first retry implementation permitted an existing retry key to return a different original failed upload when both requests had identical content. A disposable native counterexample returned success. The same-key operation must belong to one immutable input failure result. Anchor: reserveOperation created identity and reserveAsset input_document_id finalizer in the same transaction. A newly inserted retry sets its immutable input association; an existing operation must already carry that exact association, otherwise the entire transaction rejects. It must never retroactively label an independent reservation as a retry. Extend I2-17 negative packets and retain the red witness. Also strengthen the ownerless-publication negative so its valid UUID/payload/reference cannot be rejected for an unrelated reason. Only the affected native fixtures and production owner inputs are invalidated.

## Native acceptance transport repair

The normal Docker API proxy became unreachable again; Docker Desktop native docker.raw.sock continued to list the actual containers. Both endpoints previously returned the identical engine ID6020eda6-a299-4f73-8cef-7170e0dc683c/version29.6.2. Explicitly bind DOCKER_HOST for the four local native evidence commands to the observed native endpoint. This changes execution input and invalidates their previous fingerprints; all104 cases must receive fresh committed-clean observations. Product launcher/default configuration and Docker/VPN settings are unchanged. Stop the interrupted owned runner and dispose only its labelled project4205 resources. Retain interrupted logs and do not relabel them green.
