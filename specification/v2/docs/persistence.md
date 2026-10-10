# Persistent data model

The reference DDL is `db/schema.sql`. The field map is `domain/persistence-map.json`.
The design stores each typed record as an immutable JSONB document.
This is not permission for arbitrary additional properties. Its exact hashed JSON Schema defines every field and null state.
The API validates that full schema and the cross-field contract before it opens the write transaction.
PostgreSQL enforces the listed identity, uniqueness, scope, and referential constraints.
PostgreSQL does not itself implement a full JSON Schema engine. Do not claim that SQL alone proves semantic validity.

`document` stores the complete field payload, schema identity, immutable content hash, and creation time.
`entity_head` stores only mutable lifecycle selection and optimistic revision. A changed payload creates a new document.
`object_node` indexes root entities and embedded units, utterances, options, propositions, and evidence subjects.
Its scope is the exact owning case version, or the named global registry scope for reference data.
`object_reference` stores each required cross-record reference with expected type, scope, and content digest.
A reference cannot target a same-named node in another case or version.
No account, access-role, user-session, or tenant table exists.

## Transaction rules

Insert the new typed document, its nodes, all required references, head change, and audit event in one transaction.
Use deferred foreign keys only to assemble an internally consistent transaction. Do not commit dangling references.
The API compares every reference-bearing field with the inserted reference set before commit.
Embedded object IDs must be unique in their declared scope. Option/proposition IDs belong to one exact unit.
Evidence-parent references form a directed acyclic graph. Cycles fail before commit.
An evidence record's asset digest, final audio digest, subject type, case version, and method version must match the referenced nodes.
Existing evidence is never repointed to a new audio file or key.

All mutable head updates use `WHERE revision = expected_revision` and increment revision by one.
A zero-row update means stale input and returns 412.
A provider call occurs outside the database transaction. Its later write also requires the current lease fence.
The live process holds no exclusive database lock during model or speech latency.

## Payload and content hashes

The raw answer hash covers the original UTF-8 bytes.
The structured payload hash covers the complete canonical JSON document before storage envelope fields.
A case content hash covers public_context, variety_policy, audio, speakers, utterances, units, taxonomy_version, and verification_policy_version.
It excludes status, review_decisions, content_provenance_ids, and its own hash, because review records cite the content hash.
A render-plan hash covers every plan field except id, schema_version, and plan_sha256.
A binding hash covers every effective field except id and binding_sha256. Secret values are excluded because only secret references appear.
Other self-digest records hash all defined fields except that record's self-digest field.
Do not apply an unrestricted generic field exclusion list to evidence, rights, or policy records.

## Deletion

Normal application writes cannot mutate historical documents or audit events.
Explicit local erasure uses a user-requested maintenance transaction; no peer review or legal approval UI is required.
It first creates a deletion plan and finds all incoming references and affected results.
It removes bytes only after the plan's actual confirmation in the local deletion plan.
Keep only permitted tombstone metadata. A hash can itself be restricted personal data and is not automatically retainable.
A deleted source makes dependent future uses unavailable. It does not produce a misleading healthy dangling reference.
The application reads a typed unavailable tombstone instead of pretending that the original evidence exists.
Implement and test this explicit erasure procedure before release. The reference DDL alone is not the complete erasure implementation.

## Migration

Keep historical schema documents and hashes. Never reinterpret old payloads as the new version without an explicit transformation.
Migrate only a documented source schema/version/hash combination.
Preserve the original payload and its historical score. Store transformed data and new scores as new documents.
The repository foundation at 6b625ef has accounts, sessions and a catalog-only migration. Its exact file/hash and drift are recorded in audit/full-release-reconciliation-20261008/repository-drift.md. This DDL is an unexecuted design reference; the source-to-v2 migration is specified in migration-compatibility.md and remain unimplemented.

## Exact deletion and immutable scope procedure

case_version_id references an immutable document, never a mutable entity head. In maintenance, freeze writes; determine the requested document/asset set and all incoming references. The deletion preview names any dependent records that must also be removed, or reports conflict without deleting. Apply the selected closure in one DB transaction: SET LOCAL tangerine.maintenance_delete=on; remove caches/playback/leases/operation links, object_reference edges, object_node rows and affected entity_head rows in dependency order; delete actual document payloads; null/remove audit links/details; insert only the requested minimal tombstones with no personal payload or retained hash unless selected. The immutable guard permits DELETE only in maintenance, and never UPDATE of a historical payload. Delete orphaned media bytes after committed DB removal; a failure leaves a recorded orphan for retry. No unerasable hash-chain payload survives deletion. Incoming references outside the selected closure block that deletion apply, not ordinary LLM use. This is a specified transaction, not executed SQL evidence.

Mutation manifests, frozen Lab datasets and judge inputs/outputs use the same typed document/private-asset storage. Their owning hash projections are generation-contract-details.md and llm-lab-contract-details.md; referenced asset hashes cover actual bytes unless explicitly JCS content hashes.

Current preparation persistence/resume is defined by preparation-persistence.md and preparation-state/preparation-settings schemas. Generation must be self-contained under self-contained-generation.md; no private contextual fact determines a scored mistake. Key repair uses key-repair-projection.md and the existing LLM operation. These are written contracts, not implemented behavior.

Full-scope extensions: [full build contract](full-build-contract.md) specifies controlled local speech selection, generated acoustic pairs, exact decoder/sample-map clocks, per-piece resume/readback, native export mapping, actual auditory-model diagnostics and their user scenarios. New private fields use existing owners/operations; original main-flow and component-score contracts remain.

Accepted payloads are trusted on read and reuse under [single validation](single-validation-policy.md). Full schema/domain admission occurs once for new external input. Existing hash fields remain provenance; they do not require revalidation after persistence.
