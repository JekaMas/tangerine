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

The official form was submitted using the user-selected independent-project identity and returned its success message. The actual automatic email supplied a complete v5 archive and component links. Google Drive returned a quota-exceeded HTML response for the full archive and disabled-download/404 responses for individual components. No response HTML or access email is counted as corpus bytes. An assistance follow-up was sent to the published maintainer address. The official package remains unacquired; the pinned raw mirror below is acquired separately, with every required component preserved. Public status is recorded in audit/corpus-acquisition-20261009/; private issued links/correspondence remain ignored under data/.

## Acquired pinned mirror and native discrepancies

A complete raw mirror is acquired from https://huggingface.co/datasets/chikingsley/l2-arctic-release-v5.0 at commit cc02fd37197966e5de11ad737f7affd577c61992. All31 repository members, including24speaker ZIPs, suitcase ZIP, LICENSE/PROMPTS/original README/PDF and mirror metadata, have exact byte/hash receipts. All84,266archive files passed full read/CRC inspection. Read speech has26,867WAV/transcript/automatic TextGrid pairs and3,599manual annotation files; suitcase has22WAV/transcript/manual annotation pairs, with lowercase native filenames corresponding to all read speakers exceptASI/SKA. Native audio is44,100Hz mono16-bitPCM. Source bytes, all tiers and unnamed ancillary tiers remain preserved.

The actual phones-tier operation-label count, trimming delimiter whitespace, is18,577substitutions/7,843deletions/1,092additions for read speech and2,158/650/90for suitcase. Published/original-README expectations are14,098/3,420/1,092and1,673/456/90. These are real discrepancies; do not relabel observed counts as published counts or silently discard labels to force agreement. Other tiers can duplicate label text: all-tier string counts are not phone-event counts. Exact native labels and the phones-only method are retained in l2-arctic-native-annotation-accounting.json and l2-native-phone-label-counts.json.

The mirror is a usable, fully acquired raw candidate with explicit third-party provenance, not a claim of byte equivalence with the unavailable official ZIP or normalized linguistic gold. The official full-source conformance status remains unresolved pending an authoritative release/hash or documented count-convention/version explanation. This status does not block ordinary local use or other source intake. A precise maintainer count/provenance follow-up has been sent. No new human peer-review workflow is introduced.
