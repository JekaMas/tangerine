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
Explicit rights-aware erasure uses a separately reviewed maintenance transaction.
It first creates a deletion plan and finds all incoming references and affected results.
It removes bytes only after the plan's actual confirmation and applicable legal retention decision.
Keep only permitted tombstone metadata. A hash can itself be restricted personal data and is not automatically retainable.
A deleted source makes dependent future uses unavailable. It does not produce a misleading healthy dangling reference.
The application reads a typed unavailable tombstone instead of pretending that the original evidence exists.
Implement and test this explicit erasure procedure before release. The reference DDL alone is not the complete erasure implementation.

## Migration

Keep historical schema documents and hashes. Never reinterpret old payloads as the new version without an explicit transformation.
Migrate only a documented source schema/version/hash combination.
Preserve the original payload and its historical score. Store transformed data and new scores as new documents.
The current repository's actual migration history is not available here. Do not claim that this DDL was applied to it.
