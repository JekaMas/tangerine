# Retention, capacity, and recovery

## Local resource policy

Allow one paid foreground operation at a time. Stored playback and status reads remain available.
Use one database admission lock and a persisted operation record. Do not create a tenant billing service.
The proposed guard is USD 10 per UTC day and USD 100 per UTC calendar month.
The operator can change those explicit guard values before work starts. No operation can change its own budget.
A price profile must identify the actual provider price units, date, and source.
A guard is an application estimate, not a guarantee that a provider invoice has that exact value.
Reserve the upper-bound estimated call cost before a paid operation.
Count actual known costs, outstanding reservations, failed calls, canceled calls, and transport retries separately.
If billing is uncertain, retain the reservation as an unknown-charge amount until actual evidence reconciles it.
Never treat unknown charge as zero or release the same reservation twice.
Without a usable price profile, show cost_unknown and require explicit approval for that exact paid operation.

The proposed limits are 20,000 answer codepoints, 1,000 extracted clauses, and 1,000 target units per case.
The whole request still must fit its provider profile and deadline. Do not truncate to these limits.
The proposed full-source archive limits are 32 GiB compressed, 128 GiB expanded, and 250,000 members.
A single expanded member cannot exceed 32 GiB. Nested archive expansion is forbidden.
A larger required release needs an explicit increased bounded configuration, not a sample-only import.
A source archive cannot set or bypass these limits.

## Retention classes

Keep published content, genuine reviewer evidence, source grants, frozen answers, semantic receipts, and final results until explicit deletion or a binding rights condition.
Make unreferenced failed/draft payloads and diagnostic logs eligible for explicit cleanup after 30 days.
Eligibility does not authorize automatic deletion. Show the exact cleanup plan and obtain confirmation.
A record required by a current case, dispute, result, qualification, or retained backup is not an unreferenced draft.
Apply shorter binding consent/license terms where they restrict continued retention.
Do not silently lengthen a third party's permitted retention period.

A revocation increments the local permission epoch and blocks new source use, external transfer, derivative publication, and invalid cache reuse.
Historical results remain readable only to the extent permitted by the actual retained evidence and grant.
Show evidence_unavailable when removal prevents reconstruction. Do not show a healthy reconstructable evidence graph.
Retain hashes or tombstones only when their continued retention is itself permitted.
A hash is not automatically anonymous or unrestricted data.
Provider-side retention and deletion follow the actual provider agreement. A local erase operation cannot claim remote erasure without a receipt.

## Consistent backup

Backup is an explicit foreground maintenance operation, not a recurring background service.
Enter maintenance mode and reject new writes and paid work.
Wait for active database mutations to finish and cancel or finish active provider work under its existing deadline.
Freeze a database snapshot and the committed asset-reference set at a recorded audit sequence and permission epoch.
Export every typed document, head, reference, raw answer, review, source record, provider receipt, and applicable rights record.
Copy all referenced immutable media and evidence bytes into the backup.
Record each object's path, count, hash, schema version, and source release identity in a manifest.
Record migration history, configuration hashes, the exact contract-vector digest, and the current revocation/tombstone ledger. No formal software release manifest is required.
Do not include cloud or internal secret values in an ordinary data backup. Preserve secrets in a separate explicitly protected procedure.
Read back the completed backup and verify every asset and count before marking it complete.
Then leave maintenance mode. A failed backup does not erase the running data.

## Restore

Inspect the uploaded archive using the same path and expansion restrictions as source imports.
Reject tampered hashes, unknown schemas, missing assets, unsupported migrations, and inconsistent references before switching the active workspace.
Restore into new isolated volumes. Do not merge an existing workspace silently.
Apply compatible migrations only with the exact recorded source checksums and supported version path.
Apply the most recent available revocation and deletion ledger before any restored content becomes readable or transferable.
If that ledger is missing or older than the known installation epoch, block external use pending explicit reconciliation.
Validate every restored document, typed reference, audio digest, and original answer/result link.
Run actual local readiness checks on the restored instance.
After explicit switch confirmation, point the launcher to the restored volumes.
Preserve the prior volumes until the approved rollback/retention decision permits deletion.
A partially restored environment cannot report healthy full restoration.
