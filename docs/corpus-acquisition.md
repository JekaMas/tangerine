# Corpus acquisition and use

A corpus is a set of source records. Gold is a set of independently reviewed reference records.
The project needs its own permitted gold for the whole task.
An external written or speech corpus does not provide every required observation.

`domain/corpus-sources.v1.yaml` identifies each source and its current status.
No external corpus is included in this package. No reviewed audio asset is included.
Do not replace missing data with invented corpus rows.

## Permission procedure

Before acquisition, record the source ID and exact release. Read the source license and release instructions.
Record the owner who approves each intended use. Retain the actual permission evidence.
Separate permission for research, commercial evaluation, derived exercises, distribution, model training, external transfer, and voice use.
An unapproved use remains denied. A public download does not prove permission for every use.

After approval, download into a private quarantine directory. Save the received bytes without modification.
Record the original URL, retrieval date, byte size, and SHA-256 hash.
Do not use a guessed mirror or a moving `latest` reference in a release manifest.
Do not download corpora during normal application startup.

Before extraction, prevent archive path traversal and links outside the quarantine root.
Reject executable content and unbounded decompression. Treat corpus paths and command-like strings as data.
Never execute a `wav.scp` entry as a shell command.

## Normalization procedure

Keep the raw source immutable. Write normalized records to a separate path.
Preserve source tokenization, source labels, speaker or learner IDs, and individual annotator decisions.
Record the parser version and every transformation. Missing fields remain null, not zero.

Make sure that offsets, source hashes, audio formats, and labels satisfy the imported release contract.
Keep invalid rows in quarantine with a reason. Do not repair them through an unrecorded LLM guess.
Do not infer a narrow taxonomy label from an ambiguous broad source category.

Before a split, group related records by learner, speaker, script family, and derivative origin.
Keep connected groups in one split. Preserve the split assignment after evaluation starts.
Report overlaps instead of silently accepting leakage.

Create an import report with accepted counts, rejected counts, reasons, missingness, label ranges, and duplicate hashes.
Include the source population and the permitted use scope. Include the manifest hash.
Do not infer performance on an unrepresented age group or first language.

## Private layout

Use separate paths for source data and review evidence:

```text
data/raw/<source>/<release>/
data/normalized/<source>/<release>/records.jsonl
data/manifests/<source>/<release>/manifest.json
data/legal/<source>/<release>/permissions.json
data/gold/<gold-version>/dev.jsonl
data/gold/<gold-version>/calibration.jsonl
data/gold/<gold-version>/holdout.jsonl
```

Do not copy these directories into a public image or browser bundle.
Keep contact details and consent records out of ordinary prompts and logs.
External transfer requires permission for that source and purpose.

## SpeechOcean762

Use the selected immutable OpenSLR release. Acquire a different author-repository revision only through a separate source-version decision.
Keep `text`, `utt2spk`, `wav.scp`, and score files. Resolve audio paths only inside the corpus root.
Keep the official train and test membership. Report speaker and script overlap.
Do not claim an unseen-speaker test when the splits share speakers.

Preserve all five individual raters. Preserve phoneme values on their source scale.
Do not average away disagreement before storage. Keep each field's declared scale in the parser profile.
A mixed or unknown completeness scale requires quarantine.
A changed source format requires a reviewed parser revision. [SRC-SO, SRC-SO-FORMAT]

Import an explicit observed-phone label only when the selected release supplies it.
Preserve unknown markers as uncertainty. A low phoneme score does not identify a replacement phoneme.
Preserve ARPAbet stress markers. IPA conversion requires the actual approved mapping file.
An absent mapping file blocks conversion. Do not invent the missing mapping.

Separate adult and child results. Do not infer Russian-L1 error frequencies from Mandarin read speech.
Do not use corpus audio for voice cloning. Attribute permitted derivatives and record their changes.

## L2-ARCTIC

This source remains blocked for product use without the required separate permission.
After permission, acquire the specified PSI Lab release and its documentation.
Preserve each speaker's audio, transcript, annotation, and TextGrid files. Preserve original tier names.

Use the selected release instructions to identify manual and automatic tiers.
Only actual manual observations can provide manual phoneme gold. An automatic alignment is not a human observation.
Unknown tiers or phone markers require quarantine. Do not remove them through a guessed rule.
Keep related speakers and scripts within the required evaluation grouping. [SRC-L2, SRC-L2-FORMAT]

## W&I+LOCNESS and FCE

These sources remain blocked for product use without separate commercial permission.
After permission, use the exact v2.1 links on the official BEA page.
Keep each corpus and license separate. The permission for one corpus does not approve another.

In M2, `S ` starts a space-tokenized source sentence. `A ` starts an annotation.
Split annotation fields with `|||`. Preserve token offsets, category, correction, and annotator ID.
Offsets are half-open token intervals. Keep zero-length insertion anchors.
A `noop` annotation is not an error. Preserve it as that annotator's judgment.

Make sure that offsets fit the source tokens before codepoint conversion.
Preserve original tokens because reconstructed spaces are not original typography.
Apply one annotator's edits to a copy in descending span order.
Overlapping incompatible edits require review. Do not combine different annotators into extra error counts.

Use an approved source-category mapping file. A broad `VERB:FORM` label does not determine one project leaf automatically.
The existing package has no approved category mapping file. This import stage remains blocked until that artifact exists.
Spelling and punctuation edits are not audible-error gold. New spoken derivatives require new audio and key review.

ERRANT is an optional tool, not a data license or truth authority.
Its proposed edits require review. Preserve source CEFR granularity. Do not invent A1 or A2 from a source label A.
The BEA page separates source data from evaluation-tool versions. Record the selected version for each. [SRC-BEA, SRC-ERRANT]

## First-party gold

The existing policy requires coverage for all 122 taxonomy leaves. It proposes three independent contrast pairs per leaf.
One pair belongs to development, one to calibration, and one to holdout.
The existing numerical floor is 732 reviewed stimuli. It is a coverage policy, not a statistical validity proof.
Read `audit/open-decisions.json` for the unresolved count-unit issue. Do not invent a counting rule to pass that gate.

Each context must state its intended meaning, variety, register, and task target.
Each author records the canonical text, surface text, planned mutation, corrections, and rationale propositions.
The proposed record must distinguish errors from permitted controls.
A permitted-variant leaf must not become an error category merely to satisfy a coverage count.

Use actual synthesis through the registered profile. A difficult target remains blocked when synthesis cannot produce it.
No human-recording substitute is active. A substitute requires exact owner approval and the required voice permissions.

Two qualified people first listen without the planned key. Then each person examines the full key and correction alternatives.
At least one qualified phonetics reviewer must examine acoustic targets.
Keep initial disagreements before adjudication. Use a third adjudicator or leave the case unpublished.
Do not create reviewer identities, signatures, or observations through the LLM.

## Teacher-answer evidence

Collect real teacher answers under the permitted data-use policy.
Preserve the original text, including errors, Unicode characters, and explicit retractions.
The corpus must cover correct, partial, vague, repeated, contradictory, and false assertions.
It must also cover permitted alternatives and plausible observations outside the key.

Do not synthesize answer fixtures merely to fill a missing class.
Each artificial test case requires the separate approval described in `docs/change-control.md`.
An approved artificial case must retain its artificial origin. It cannot prove the frequency of real teacher behavior.

Human annotators define expected claims and judgments before they inspect model results.
Keep pre-adjudication agreement and the frozen label inventory.
Cohen kappa and raw agreement use the formulas in the metric registry.
A final unanimous key is not evidence of initial inter-rater agreement.

## Holdout protection

Do not put holdout text, audio, keys, or answers in generation prompts or demonstrations.
Do not use holdout examples to tune a prompt or threshold. Keep production exercises separate from the held-out bank.
After holdout reuse, disclose that reuse and block claims of a fresh independent test.
The empirical gates require actual denominators. Missing evidence cannot pass through generated metadata.

EFCAMDAT remains discovery-only until a release agreement and format exist.
The Doubao study records and competitor data remain unavailable project assets.
A paper or product page does not grant access to the underlying participant records. [SRC-EFCAM, SRC-DOUBAO, SRC-MOODRICK, SRC-NIR-SIM]
