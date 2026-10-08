# W&I+LOCNESS and FCE version 2.1

Source documentation and downloads: https://www.cl.cam.ac.uk/research/nl/bea2019st/
Keep the two releases, original licenses, partition identities, and source metadata separate.
The official distribution describes non-commercial restrictions. Do not infer commercial or external transfer permission from download access.

## Components and source identity

Ingest every supplied train, development, and test component, source metadata file, README, and license.
Keep native LOCNESS controls and their original identity. Do not label every native sentence as an error.
Preserve original learner, document, essay, and partition identifiers when supplied.
When a learner identifier is not supplied, keep it unknown. An essay ID is not proof of a distinct learner.
A withheld test correction remains `labels_not_supplied`. Do not generate replacements for it.
The distributed tokenization is authoritative. Do not retokenize a source sentence with a newer spaCy model.

## M2 grammar

Each block starts with `S ` followed by the exact source token sequence.
Each annotation starts with `A ` followed by start/end and fields separated by `|||`.
Retain start, end, source error type, correction text, historical fields, and annotator identity.
Offsets are zero-based half-open token indexes. An insertion has start=end.
A deletion can have an empty correction. Preserve the literal correction and any declared alternative representation.
A noop uses the documented -1/-1 sentinel and is not an error event.
Keep UNK, Um, detection-only, and other uncertain source labels without converting them into invented corrections.
Reject malformed sentinel combinations and out-of-range spans.

Preserve edits separately for each annotator. Do not union several alternatives into extra simultaneous errors.
For a corrected-sentence view, apply one annotator's non-overlapping edits from right to left.
At equal insertion offsets, use source annotation order only when the release specifies that order.
Otherwise retain the annotations and mark reconstructed text ambiguous.
Overlapping edits remain stored as separate source annotations and require an explicit compatible edit set before reconstruction.

## Token-to-codepoint mapping

Preserve the exact S-line string after its prefix and its original line-ending metadata.
Derive token intervals by the source's space-separated token sequence without Unicode normalization.
A token span [a,b) maps from token a's first codepoint through token b-1's final codepoint.
An insertion at a maps to the corresponding boundary. At the final boundary, use the source text length.
Keep both token and codepoint offsets. Never apply offsets to a cleaned or re-tokenized string.

## Category conversion

Keep original ERRANT operation and category separately.
M, U, and R express missing, unnecessary, and replacement edits. They do not select a project leaf by themselves.
The source labels such as DET, PREP, VERB:TENSE, VERB:SVA, NOUN:NUM, SPELL, and PUNCT supply candidate categories.
Use `domain/source-label-map.yaml` for permitted broad candidates.
A broad source label cannot become a narrower 122-leaf identity without sufficient context and approved linguistic mapping.
Spelling and punctuation labels can remain written-only records. Do not synthesize a pronunciation error from spelling automatically.
The complete raw and normalized source data remains available even when a record is not eligible as a listening gold unit.

## Outputs and acceptance

Preserve all blocks, all annotators, noops, alternatives, native controls, metadata, and label-absence states.
Reconcile source blocks and edit records independently. A block without edits is not necessarily missing data.
Pin the evaluator tool version separately from the corpus parser version.
Never claim that a newer automatically inferred tag is the original human label.
