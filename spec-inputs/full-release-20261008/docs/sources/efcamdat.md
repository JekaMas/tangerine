# EFCAMDAT releases

The required scope includes the full second release and both named derivatives.
Register EFCAMDAT-R2, EFCAMDAT-SHATZ2020, and EFCAMDAT-OKSUZ2025 separately.
A derivative does not replace the full source or another derivative.

Owner access page: https://ef-lab.mmll.cam.ac.uk/EFCAMDAT.html
Published agreement: https://ef-lab.mmll.cam.ac.uk/assets/pdf/EFCamDat-User-Agreement-2023.pdf
The owner page supplies access by an approved Google account for eligible academic researchers.
The agreement restricts ordinary use to the stated academic/non-commercial scope and imposes additional conditions on derivatives and transfer.
Obtain separate written permission for commercial use, unrestricted distribution, or other uses outside that grant.
Do not assume that an API key or a Google account changes the terms.

## Second-release XML

The author guide describes selection/meta and selection/writings/writing structures.
Retain the selection ID and every metadata field, including title, version, URL, key/user fields, date, nationality selection, and unit selection.
Treat account-related metadata as private source data. Do not send it to an LLM.
Each writing has source id, level, and unit attributes.
Retain learner id/nationality, topic id/text, date, grade, original text, corrections, and annotations.
Nationality is source metadata. It is not a direct observation of an individual's first language.

Inside text, preserve mixed XML content in exact document order.
A change element contains the original selection and its tag/correct information.
Build the original-text view from literal text and selection content, excluding correction suggestions.
Build a proposed corrected view only through a separate declared transformation.
Preserve empty selections, empty corrections, tag symbols, multiple corrections, and ambiguous/nested markup.
Compute offsets against the original-text projection, not against XML markup bytes or corrected text.
Store XML byte locators and the projection method so both representations remain traceable.

Retain annotation id, sentence count, sentence id/tokencount, token id, lemma, pos, head, rel, and token text.
Keep each annotation layer distinct. The source's automatic parse is not a manually validated syntactic truth.
Source teacher corrections are pedagogical feedback. They are not guaranteed exhaustive error gold.
The label map retains AG, AR, AS, CO, C, D, EX, HL, IS, MW, NS, NSW, PH, PL, PO, PR, PS, PU, RS, SI, SP, VT, WC, WO, and XC.
Broad labels generate candidate mappings only. Unknown labels remain preserved and unbound.

The guide's XML examples do not prove that a privately supplied full release uses an identical complete schema.
Before activation, compare actual release documentation and all observed elements with the exact `source-format-binding`.
Unknown required semantics keep the release unbound. They do not disappear from the full-source inventory.

## Shatz2020 and Oksuz2025 derivatives

Acquire the complete owner-supplied workbooks and their actual documentation through the authorized source channel.
Preserve all workbooks, sheets, cells, native fields, IDs, correction information, task prompts, and supplied partitions.
Do not silently replace a derivative with the full XML projection or a third-party subset.
Use a closed source-format-binding that names exact workbook/sheet/header locators and their source meaning.
For each required meaning, bind the source column, raw type, null markers, label inventory, offset clock, and conversion rule.
Required meanings include writing identity, learner grouping, task/prompt grouping, original text, proficiency context, correction/annotation provenance, and source-release identity.
An unsupplied meaning remains explicitly missing. The importer cannot invent a learner ID or a span annotation.

The actual private workbook headers, full data dictionaries, and permissions were not supplied for this package.
Therefore the native derivative bindings are not falsely marked complete.
The format-binding schema and ingestion process are defined; source-specific bindings remain external prerequisites.
This package contains no acquired derivative records and no invented full-release counts.

## Leakage and use

Join records across releases by genuine source writing/learner/task identities and documented derivative links.
When a direct link is absent, use exact text hashes only as possible duplicate evidence, not as proof of identity.
Keep related original and derivative records in the same connected split group.
Before an external LLM receives an excerpt, evaluate every contributing source grant for that recipient and purpose.
A cleaned record does not automatically remove restrictions from the original data.
