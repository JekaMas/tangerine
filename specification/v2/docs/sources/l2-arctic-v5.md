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
An unknown tier remains raw and quarantined for semantic conversion.
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
