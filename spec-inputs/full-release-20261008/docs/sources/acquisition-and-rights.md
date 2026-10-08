# Complete source acquisition

The source inventory is mandatory for the first release. It is not a list of optional future work.
All source components remain visible when rights, bytes, or interfaces are absent.
A complete importer preserves every supplied record and distinguishes accepted, quarantined, and rejected records.
A small selected set of excerpts can support a generation request. It cannot satisfy full-release acquisition.

## Intended uses

The operator declares every intended use in configuration before import or transfer.
The supported uses are local_analysis, internal_training, commercial_evaluation, derivative_exercises, distribution, model_training, external_api_transfer, and voice_use.
No use inherits permission from another use.
A local research permission does not automatically allow commercial use, redistribution, model training, or transfer to an external LLM.
A valid account or key proves access only. It is not a license or consent record.
The operator supplies actual grant documents with grantee, grantor, scope, dates, recipients, and restrictions.
A competent source-owner or legal review must establish ambiguous permission. The LLM cannot approve it.

## Acquisition procedure

1. Obtain the complete authorized release from the named source owner.
2. Retain the exact README, license, data dictionary, access agreement, and release identification.
3. Record every archive, partition, component, path, original size, and actual SHA-256.
4. Preserve the original bytes in private immutable storage.
5. Register the exact release format and its source-field binding.
6. Apply each declared intended-use grant before parsing, deriving, exporting, or making a provider request.
7. Parse every component with the matching versioned profile.
8. Save normalized records and exact raw records separately.
9. Save all skipped, quarantined, and rejected rows with locators and reasons.
10. Reconcile component counts before marking full ingestion complete.

## Safe parsing and reconciliation

Reject absolute paths, parent traversal, symlinks, hardlinks, devices, executable archive members, duplicate normalized paths, and nested archive expansion.
Compare declared and expanded sizes with configured bounds. Stop rather than truncate a full source.
Disable DTDs, entities, XInclude, and external resolution for XML.
Do not execute XLSX formulas or external links. Preserve formula text and cached values separately.
Preserve hidden sheets, duplicate headers, blank rows, merged-cell metadata, and original cell types.
Never guess a missing native label, learner ID, phoneme, or corpus partition.

For each count unit, observed = accepted + quarantined + rejected.
Every source file appears in exactly one component inventory and one disposition.
Every normalized record links its source bytes, source locator, format binding, parser version, and transformation.
A component with inaccessible test labels reports `labels_not_supplied`. It cannot claim a fully labeled test partition.
A release with unresolved required semantics remains `format_unbound`, even if raw bytes were preserved.
An unknown hash is null in an acquisition plan and forbidden in a completed release manifest.

## External provider transfer

Compute the dependency closure of each requested excerpt or derived record.
Every contributing source must allow the exact recipient and purpose at the time of transfer.
Show the operator the recipient, data classes, source IDs, and requested use before first transfer under a grant.
Save the actual disclosure record and grant identities.
A revoked or expired grant blocks future calls and invalidates stage-cache reuse.
A derived exercise is not presumed free of source restrictions merely because an LLM rewrote it.

## Full-source acceptance

Full-source acceptance requires actual complete bytes, real rights, exact format binding, reconciled records, and supported source semantics.
The user request includes EFCAMDAT second release, Shatz2020, and Oksuz2025 as three distinct releases.
The user permits authorized private access to Moodrick and NIR, with credentials in local configuration.
The package does not claim that either vendor supplies an API, export, corpus license, or private answer bank.
The Doubao participant records remain a required unresolved acquisition unless the owner explicitly changes that scope.
Neither a paper count nor a product demo is a data release.
