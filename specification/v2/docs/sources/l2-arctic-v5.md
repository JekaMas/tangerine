# L2-ARCTIC version 5

Source documentation: https://psi.engr.tamu.edu/l2-arctic-corpus-docs/
License source: https://psi.engr.tamu.edu/l2-arctic-corpus/
The published license is CC BY-NC 4.0. Commercial and other restricted uses require actual separate authorization.

## Required components

Retain README, LICENSE, PROMPTS, every speaker directory, read speech, and the suitcase extension.
The version-5 inventory describes 24 read-speech speakers and 22 suitcase speakers.
SKA and ASI are absent from the suitcase extension according to the source documentation.
This documented absence is not an importer failure. An unexpected absent speaker is an incomplete release.
The read collection includes wav, transcript, automatic textgrid, and manual annotation directories.
The suitcase extension does not provide the same forced-aligned textgrid directory. Do not fabricate it.
Preserve source rates at 44,100 Hz. Any processing-rate conversion is a separate derivative.

## Text and clocks

Pair records by exact speaker and utterance basename. Do not merge speakers that share a CMU prompt.
Retain original transcript text and all TextGrid tiers in source order.
Parse TextGrid using its declared long or short syntax, quoted-string escape rules, and source clock.
Store exact decimal boundary strings and a derived rational second value.
Validate monotonic tier intervals, nonnegative duration, file duration bounds, and speaker/utterance links.
An unknown tier remains raw and raw-only until its semantic conversion is defined.
A supplied comments tier stays separate from words and phones.

## Provenance of annotations

The textgrid directory contains automatic alignment. The annotation directory contains manual labels.
Never promote the automatic alignment into manual phonetic gold.
A manual unchanged canonical phone can remain a correct source realization, not an error.
The documented manual phone grammar has these forms:

| Source form | Meaning | Normalized preservation |
|---|---|---|
| CPL,PPL,s | Substitution | Canonical label, perceived label, substitution operation. |
| sil,PPL,a | Addition | Silence as source canonical label, perceived added label, addition operation. |
| CPL,sil,d | Deletion | Canonical label, perceived silence, deletion operation. |
| CPL,err,s | Unclear perceived substitution | Preserve unknown perceived realization. |
| Label with * | Noncanonical or approximate realization | Preserve uncertainty. Do not create a precise IPA claim. |
| Unchanged source phone | No manually marked change | Keep the actual annotation and its manual/automatic origin. |

Parse delimiters only under this release grammar. Malformed tuples remain quarantined.
Retain every original label, confidence/uncertainty marker, interval, annotator information, and comments.
A symbol conversion can label an exact phonetic symbol only when the source alphabet supports that conversion.
Do not infer a narrow project error from an ambiguous phone or an L1 stereotype.

## Grouping and completeness

Speaker, prompt, and all derivatives contribute edges to the leakage graph.
Common CMU prompts can connect a large component. Do not break it to manufacture independent splits.
Use that component in one eligible split and obtain other independent coverage from the original gold collection.
Reconcile supplied files, utterances, manual/automatic intervals, and extension membership.
Expected published totals are metadata. Only observed complete files and records satisfy ingestion.

## Actual 2026-10-09 access attempt

The official form was submitted using the user-selected independent-project identity and returned its success message. The actual automatic email supplied a complete v5 archive and component links. Google Drive returned a quota-exceeded HTML response for the full archive and disabled-download/404 responses for individual components. No response HTML or access email is counted as corpus bytes. An assistance follow-up was sent to the published maintainer address. The official package was unacquired at that date; the complete official delivery was subsequently acquired on2026-10-26 as recorded below. The pinned raw mirror remains separately identified. Public status is recorded in audit/corpus-acquisition-20261009/; private issued links/correspondence remain ignored under data/.

## Acquired pinned mirror and native discrepancies

A complete raw mirror is acquired from https://huggingface.co/datasets/chikingsley/l2-arctic-release-v5.0 at commit cc02fd37197966e5de11ad737f7affd577c61992. All31 repository members, including24speaker ZIPs, suitcase ZIP, LICENSE/PROMPTS/original README/PDF and mirror metadata, have exact byte/hash receipts. All84,266archive files passed full read/CRC inspection. Read speech has26,867WAV/transcript/automatic TextGrid pairs and3,599manual annotation files; suitcase has22WAV/transcript/manual annotation pairs, with lowercase native filenames corresponding to all read speakers exceptASI/SKA. Native audio is44,100Hz mono16-bitPCM. Source bytes, all tiers and unnamed ancillary tiers remain preserved.

The2026-10-21typed-parser and independent native-grammar audit corrects the historical label counter: require exactly three comma-separated fields, trim delimiter whitespace and normalize only the actual operation-letter case (s/S,d/D,a/A), retaining the original tuple and phone symbols. Reserved SIL/ERR aliases keep their documented silence/unknown meaning. Bare ARPAbetS/D are unchanged phones, never mutation events. Actual read operations are14,098substitutions/3,420deletions/1,092additions; suitcase has1,673/456/90, matching the original README. The earlier18,577/7,843and2,158/650figures included unchanged bare symbols; those historical receipts remain preserved and are superseded by audit/iteration-13-source-imports-20261021/L2-OPERATION-CORRECTION.json. Every original label/tier remains stored. This resolves the count-method discrepancy. The2026-10-26official delivery now also establishes the component/data-byte correspondence described below.

The mirror remains an acquired source with its actual third-party transport provenance. Its25speaker/suitcase ZIPs and all84,266native data members match the subsequently acquired official delivery byte for byte. The official LICENSE, PROMPTS and README.pdf also match the retained mirror receipts. Official README.md is separately retained and differs from the mirror README files; do not claim equality of the whole repository or an invented whole-bundle hash. The actual official package now supplies that release/provenance evidence. Neither transport nor byte correspondence establishes normalized database import or linguistic gold. Existing raw/native-parser observations retain their exact supported scope, and no new human review gate is introduced.

## User-supplied access-email reconciliation

The access email pasted by the user on2026-10-09 matches all34 Drive file IDs already recorded privately: fullv5,24speaker files, suitcase, four documentation files and four earlier releases. It supplies no replacement download link or new transfer observation. Preserve the dated official quota/disabled-download receipts and the acquired pinned mirror separately. Earlier versions1–4 are separately identified historical releases; they never substitute for the required fullv5 scope.

The email identifies [Dr. Ricardo Gutierrez-Osuna](mailto:rgutier@tamu.edu) as the contact for uses outside CC BY-NC4.0 and Anurag Das as the download-assistance contact. This source-license contact is recorded without treating the email as a broader use grant or another product approval requirement. Apache-2.0 continues to apply to original Tangerine software; the corpus retains its source terms.

See ../product-data-relevance.md for action-scoped use: preserve observed valid records/counts; aggregate drift alone does not quarantine all records or block parsing, enrichment, mutation or unrelated development. Source completeness and official-equivalence claims remain separate.

## Complete official delivery — 26 October 2026

The user-supplied v5 Drive ID now returned its complete original ZIP through the
ordinary large-file download form. Actual size:7,515,454,814bytes; SHA-256:
`490d5a43e48b0af84f6bce8e766ad453e8cd670521d5876bb4d0741cca304fda`.
Manifest:`l2-arctic-official-v5-20261026`. The inventory is
`audit/iteration-27-sources-20261026/L2-OFFICIAL.json`.

Its29top-level members are24speaker ZIPs, the suitcase ZIP and four original
documents. Expanding the25containers yields84,266native speech-data files;
including the four original documents gives84,270native files. The combined
hierarchical inventory has84,295entries because it also lists the25containers;
those are not additional utterances. All members were streamed once with native
ZIP CRC checking and digests. Previously accepted mirror digests were compared
as data; no second mirror byte audit or repeated stored-data gate was added.

Observed scope:24read speakers,26,867read WAVE/transcript/automatic-alignment
sets,3,599manual annotation files and22suitcase WAVE/transcript/manual sets.
The native license confirms CC BY-NC4.0. The prior quota/disabled-download
receipts remain dated failures rather than current acquisition blockers. This
closes official acquisition/component provenance; a full normalized database
import is not claimed by this inventory and no audio/model judgment was made.
