# SpeechOcean762 source profile

Use the complete OpenSLR resource 101 and its source-owner repository documentation.
Source documentation: https://www.openslr.org/101/ and https://github.com/jimbozhang/speechocean762
The public license is CC BY 4.0. Store the actual release license and preserve required attribution.
Check any applicable participant, voice, or transfer restrictions before a new use. Do not assume a score license establishes voice-cloning consent.

## Components

Retain root documentation, scores.json, scores-detail.json, all WAVE speaker directories, and both train and test components.
For each split, retain text, utt2spk, spk2utt, wav.scp, spk2age, and spk2gender where supplied in the selected release.
Retain every supplied file even when it is not used in a metric.
Published metadata describes 5,000 utterances, 250 speakers, and five raters. These are expected source counts, not observed acquisition counts.
Preserve age and gender as source metadata. Do not infer a missing value or omit child speakers to simplify import.

## Keyed text files

Decode documented UTF-8. The first whitespace-delimited token is the source key.
For text, preserve the complete remaining sentence and its original spacing.
For utt2spk, require exactly one utterance key and one speaker key.
For spk2utt, retain every ordered utterance key and compare membership with utt2spk.
For age and gender maps, retain the original value and source scale. Missing values stay unknown.
For wav.scp, retain the original locator. Execute no shell pipeline or command from this file.
Resolve only relative paths inside the acquired release root or an explicitly supplied relocation map.
Duplicate conflicting keys, missing audio, and cross-split aliases enter quarantine.
A documented same-source duplicate remains preserved and belongs to one leakage group.

## Aggregate and individual scores

Parse utterance-keyed JSON without dropping unknown source fields. Preserve those fields in the typed raw tree.
The documented aggregate fields include accuracy, fluency, completeness, prosodic, total, and words.
Word fields include text, accuracy, stress, total, phones, and phones-accuracy.
Phones can be a source string or a source list under a version-specific binding. Never split an unknown representation by guesswork.
The detail file retains all five individual ratings and all five supplied phone-mark sequences.
Keep individual ratings and aggregates independently. Do not overwrite an aggregate with an inferred average or median.

The source documents pronunciation accuracy values on a 0-to-2 phone scale and sentence dimensions on a 0-to-10 scale.
Retain completeness with its actual release-specific scale: aggregate and individual examples use different representations.
A file with an undeclared or mixed completeness scale remains unbound. Do not multiply values by ten without a documented mapping.
Word stress labels and their aggregates also retain their original scale and aggregation provenance.

## Phone annotation grammar

For documented individual phone strings, an unwrapped phone denotes the source's highest accuracy category.
A phone in braces denotes its intermediate category. A phone in parentheses denotes its lowest category.
A phone in square brackets denotes an insertion. Preserve the exact original token and marker.
These marks express the source annotation, not the canonical IPA observed by our reviewers.
If supplied, mispronunciation records retain canonical-phone, phone-index, and pronounced-phone.
A trailing asterisk remains approximate. `<unk>` remains unknown.
A low accuracy score alone cannot populate an observed substituted phoneme.

Normalize unambiguous documented ARPAbet symbols through the separate symbol table.
Keep lexical stress digits as source annotations. Never manufacture them from an absent symbol.
A pronunciation claim needs actual source labels or new genuine review, not a guessed conversion from scalar scores.

## Outputs and completion

Store each utterance, speaker link, metadata field, word sequence, aggregate score, individual score, and original annotation as separate traceable fields.
The exact raw value tree preserves source key spelling and order.
Compare actual counts of audio, transcripts, scored utterances, and all five raters.
A missing score is an explicit missing source annotation, not zero.
Do not call ingestion fully normalized while required scale or marker semantics remain unbound.
