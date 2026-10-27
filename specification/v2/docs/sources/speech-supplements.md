# Acquired speech and dialogue supplements

Iteration37 selects EDACC (replacement DOI10.7488/ds/7914), ELRD owner7e4c8f3,
DIPLOMAT owner8fc673f and DRAL16kHzbase plus8.0fixes/test increment. They supplement
the original eleven source IDs and JFLEG. Every acquired file/container/notice is
retained inert. No source code, external model or speech synthesis runs on import.
The full acquired scope is not every historical/high-resolution representation.

## Durable ownership and normalized examples

Use existing source admission, source_release/member/file/assets, staged source_row,
frozen native parser/method, accepted projections and atomic completed-import commit.
New-source identity is computed once; existing admitted inventories/DB identities
are reused privately. No recurring stored-byte/schema/hash audit is introduced.
Source parser version is source-native-supplements-v1. On cancellation/reopen,
explicit resume trusts accepted state and stages/projects remaining locators.

Each interpreted primary unit has a saved `source_example` in its source-row
projection. It records source ID/version/native member and row, native identity,
kind, raw source fields, source task/partition, text or explicitly absent text,
text/label origin, source speakers/session, original media locators (asset/member,
actual release, observed clock), source interval and local-media interval, and
group relations with their method/limits. Unsupported/incomplete source meaning
stays explicit. No taxonomy label, teacher answer, pronunciation error or semantic
grade is inferred. Original assets and raw rows preserve exact content.

Times retain original strings and exact rational seconds, avoiding floating-point
rounding or guessed interval endpoints. Invalid/unknown source clocks stay unknown
with original values retained. Readback trusts saved projections. Untranscribed
DRAL units remain audio examples with no fabricated corpus text.

## EdAcc

94owner file members include76WAV and122background CSV rows. Dev/test have9848/9289
segments and the same numbers of text, utt2spk, STM and filtered STM rows; company
CTM has137020/145396rows. Join segments/text/utt2spk by exact utterance key inside
the same native partition, never by file order. Segment fields name recording,
start/end and utterance; media resolves the exact named recording. Preserve
speaker/session identity and raw source text, including fillers/special tokens.

Background CSV fields remain native metadata, including source survey values;
session association does not invent an undocumented A/B-to-participant mapping.
Company CTM is ASR output. STM tags are source evaluation examples with the owner's
reliability warning, not verified demographic/error labels. stm.filt/glm are
scoring views; they never replace/delete the original text. A different variety
is a contextual reference/control. The replacement is CC-BY-SA4.0; retain its
current README/license rather than withdrawn predecessor licensing.

## ELRD

35owner members include15WAV/transcript pairs and589JSONL turns. Pair by exact
meeting stem in audios/ and diarized_transcripts/. Preserve speaker IDs, scenario,
clock strings such as0:00:13.703000, original text and all source turns. Diarization
and transcripts are automatically obtained; they are not human error gold.
Audio remains original CC-BY-NC-ND4.0; transcript CC-BY4.0 and role-play notice
remain separate. Read access grants no audio modification or voice-cloning right.

## DiPlomat

All19members and35255native task rows are retained. Native .json files contain
JSON lines. CQA train/val/test counts are15585/1559/2338; first PIR3341/168/668;
second PIR5188/244/1062; both NLI views2551each. Retain native arrays/order,
speaker orientation, correct_turn_number, choices, label, questions, answer,
gold_statement and human answer. Second-PIR label is the zero-based correct-choice index into choice; it is not a pragmatic class or a Tangerine error category. All five choices, including duplicate strings, remain ordered. The source-selected choice is an explicit projection of that index.

Exact serialized context+speaker equivalence can group overlapping task views,
labelled as derived exact-context equivalence, not a global original-dialogue ID.
NLI paired-position relationships require actual supplied text/context support;
otherwise keep them unknown. No count sums source task rows into independent
conversations or people. Source splits remain train/val/test, with NLI's documented
single train view declared in the retained owner builder (DiPlomat.py, _split_generators).
Keep that declared native train partition even though the file is named dataset.json;
record partition_origin=owner_dataset_builder. Normalize train to source_train,
val to dev, test to source_test in corpus_record, retaining the native partition
and filename. Complete native corpus-record counts are29,216source_train,
1,971dev and4,068source_test, including both2,551-row NLI training views.
Unknown tasks do not receive invented owner splits. No audio or timing is supplied. Keep CC-BY-NC-SA4.0 and owner
citation. Bundled dataset code remains inert.

## DRAL

The base has10497members/10490WAV and metadata rows:208conversations,4496long
fragments,5786short fragments,205participant rows and2producer rows. The acquired
8.0increment has3085members/3076WAV,272conversations,5692long/7632short fragments,
matching5692/7632set rows,272participant rows and2producer rows. Both containers
and native nested/container/doc assets remain preserved. CC0 applies.
Base recording IDs cover104EN,96ES,4BN,2JA,2FR;8.0covers136EN,128ES,4BN,2JA,2FR.
Translation pairs retain these actual languages, not an English/Spanish-only assumption.

Register base version `16kHz-base` before `8.0-fixes-plus-testdata` to resolve
increment references to existing base media. The selected compatible base release
is saved in actual media/dependency locators; reads never recompute that selection.
Missing base/media links stay explicit, without inventing audio or blocking
unrelated rows. Latest compatible base is selected by stored release order; no
source/permission re-audit runs per fragment.

Native CSV headers identify participants, conversations, language, original versus
reenacted roles, fragment IDs, translation partner, recording start/end and native
set. Conversation recordings and short/long fragment recordings are different
views. A supplied fragment file begins at0; its source interval locates the window
in the full conversation and never gets reused as a local fragment offset.
Thirty acquired long-fragment rows (EN_049/BN_049, #1–#15 each) have no separate
fragment file, but their complete recordings are available. Bind those native
intervals to the actual complete recording, retain its nonzero local clock, mark
media_representation=native_recording_window and native_fragment_file=not_supplied_in_selected_assets.
The native interval must lie inside that actual saved recording. No clip is
manufactured; an absent/unusable recording/window remains explicitly unavailable.
All supplied roles/participants remain, including two-speaker long fragments.

Group a native fragment/recording identity consistently across compatible releases
while retaining version-specific rows/assets and corrected metadata. Native
participant identifiers and corrected unique-ID fields retain their actual version.
Conversation/translation families group their fragments and both language roles;
never add fragments, languages, reenactments or overlapping releases as extra
independent conversations. No learner-error/phonetic label is supplied by pairing.
Other48kHz/third-party representations remain separately scoped unavailable data.

## Consumers and acceptance

Existing Sources intake/native preset, saved progress/report/row/asset reads remain
ordinary controls. Primary normalized examples must be inspectable with actual
speaker/media/clock/group meaning, without editing a mapping JSON. Transient reads
use the existing logged retry/authored guidance and preserve saved selections.
Ordinary generated exercises require no corpus, human review or qualification.

Complete selected claims require actual full native imports, independent source
counts, positive/negative meaning/association tests, interruption/reopen/resume,
committed application readback and media locators. Constructed negatives test the
native owner but do not establish source/gold populations. Work is tracked in the
canonical I37 tasks, verification.json and audit/iteration-37-supplements-20261027/.

PIR test views preserve the owner-specified order. Each first-PIR test row corresponds to the following number of second-PIR rows given by its correct_turn_number count. Derive that relation only where context, speakers and target-turn membership agree; source target-turn order itself need not be sorted. All 1,062 second-PIR test rows have this supported relationship to the 668 first-PIR rows. Train/validation records use exact context equivalence without an invented positional relation.

Saved examples are read through GET /api/v1/imports/{id}/examples using the existing (member, table, ordinal) cursor, limit 1–200 (default 50), items and next_cursor envelope. Optional view selects the exact native task name (DiPlomat) or recordings/fragments-short/fragments-long (DRAL); an absent view selects all saved examples and an unknown view returns an empty page. The ordinary Sources selector provides these named views. It selects saved source_example projections without re-parsing bytes, revalidating stored records or initiating models. Original WAVE bytes support ordinary HTTP byte ranges for local playback/seeking; other retained source assets remain inert downloads. Missing import IDs use the existing source-not-found response and the shared authored retry guidance.

GET /api/v1/source-releases/{id}/files returns the already admitted source.Member list (relative_path, sha256, byte_count, component, partition, asset_id, optional media_metadata). It uses saved source_member/source_file data only. The ordinary Original files disclosure loads on demand, shows twenty members at a time, filters notices/media/archives, and provides original-byte links. It includes inert documents, scripts and containers which do not yield normalized rows. The selected supplied releases have 96/36/19/10,498/3,086 retained members respectively, including four original archive containers and the separate EdAcc licence.
