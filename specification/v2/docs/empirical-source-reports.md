# Reports from imported sources — iteration 38

This extends the existing empirical report owner. It introduces no service,
queue, login, approval, model call or practice prerequisite. Original categories,
mutation recipes, grading formulas and source scopes remain unchanged.

## Ordinary operation and source selection

Open Reports → Explore imported data. Select a named source/view, optionally
name the report, then Create source report. The private GET
`/api/v1/reports/source-populations` returns an array of
`{title,description,source,release,release_id,source_manifest,source_name,data_origin,imported_at}` choices. Source is
`{import_id,member,table,basis}` plus the existing optional selection fields.
Only published imports with a completed native phase are offered. Repeated
imports of the same source/version/stored manifest select the most recent
completed import rather than offering duplicate populations. This uses admitted
metadata, without rehashing any bytes. Other versions/views remain separate. Constructed
releases (recorded constructed origin/version) are visibly labelled developer
examples, not acquired corpora. Versions, members and views remain separate.
Unsupported sources retain the existing explicit-window/custom-report route.
An empty list or unavailable import does not block saved reports or practice.

POST `/api/v1/reports/empirical` accepts `{title,source}` for a named source.
The selected basis is `m2`, `manual_phones_read`, `manual_phones_suitcase` or
`coverage`. The selector must name an actually offered view of that import.
This selects accepted stored rows; it does not re-download or hash the corpus,
re-run source conversion, guess labels with an LLM or impose a completeness gate.
The existing explicit input/window_pointer/operator crosswalk route remains.

## Populations and exact denominators

- FCE and W&I: one original M2 member per report. Lowest integer annotator ID
  present in each sentence is the default, recorded explicitly. Advanced input
  can select another annotator; an absent annotator borrows no observations.
  Each sentence is one window. Noop annotations establish no-change observations
  but not errors. Invalid positions and unresolved native tags are excluded and
  make that window incomplete. Withheld W&I originals are coverage only. JSON
  representations, component groups and ABC/ABCN aggregate views are not added
  together as extra independent sentences.
- L2-ARCTIC: one manually annotated TextGrid utterance per window. Read speech
  and Suitcase are different task populations. Only the source-manual phones
  tier supplies native s/d/a events. Unchanged intervals are counted separately
  in coverage; automatic alignment, words, silence and annotator comments are
  not extra mistakes. Saved event identities retain import/member/interval
  ordinals. Coverage also records available transcript utterances in that task
  and utterances with manual phone annotations. Phone intervals are not word
  tokens, correct-use opportunities or independently verified acoustic facts.
  The manually selected difficult subset is not a random learner population.
- JFLEG: each original dev/test view retains its sentence count and all supplied
  alternative corrections. Four references are four alternatives, not four
  simultaneous mutations. Experimental tool-derived M2 is not error gold.
- SpeechOcean: score records and original recordings have distinct counts.
  Native graded ratings remain ratings, not binary localized error events.
  Coverage units distinguish original sentences, rated utterances, conversation
  segments/turns, dialogue task examples and conversation/fragment records.
  These views have no applied category crosswalk (not-supplied); their modality
  and any supplied partition are retained, without inventing a split.
- EdAcc, ELRD, DiPlomat, DRAL: one original segment/turn/task/fragment member and
  release per coverage report. Linked contextual examples are counted where
  supplied. Accents, ASR, task answers and translations are not error labels.
  Related DRAL releases and short/long fragments share source material. No
  independent learner/population count is inferred by summing their views.

The existing exact arithmetic is retained. Native error share is original
eligible error events of a label / all eligible original error events. Native
prevalence is fully annotated source windows with the label / fully annotated
source windows. Source windows containing unresolved/invalid labels do not
supply complete absence measurements. Native word exposure is the token sum
only over those complete windows; it is null if there are none or exposure is
unknown. Counts of valid observed events can still be shown separately.

For two distinct events in one fully annotated window, support = joint/N,
conditional(B|A) = joint/A, lift = joint×N/(A×B). Same-type pairs require at least
two distinct events; additional labels on a single event create no pair. Both
directions of different types are retained. Sparse unlisted pairs mean zero
only inside known complete annotation scope; elsewhere they are unmeasured.

`report.native_population` stores observed_windows, annotated_windows,
unannotated_windows, inspected_native_tokens and eligible_events. Native results
are `native_frequencies`, `native_pairs`, `native_unlisted_pair_meaning` and the
existing native_label_counts. They do not borrow the project's smaller mapped
population or denominators. Exact integer numerator/denominator and reduced
fraction/null with missing_reason remain in the downloadable saved output.

## Derived mapping version native-context-1

Localized events retain source labels and optional `mapping_rule`; population
crosswalk_version identifies the rule version. The written rules map:
R:VERB:SVA → subject–verb agreement; R:NOUN:NUM → noun number; M/U/R:PREP →
preposition omission/addition/choice; R:WO → word order. M:DET maps to article
omission only for a supplied single article correction; U:DET to article
addition only for a single article source span; R:DET to article choice only
when both are articles (a/an/the, case insensitive). Other determiner, lexical,
tense/aspect and ambiguous tags stay unassigned.

Phone mappings use documented CMU consonant/vowel classes: different phones in
the same class → the existing consonant/vowel substitution category; consonant
→ silence deletion → consonant omission; silence → consonant/vowel addition →
consonant insertion/vowel epenthesis. Stress digits alone do not establish a
segment substitution. Approximate, unknown, equal-base or cross-class contrasts
stay unassigned. No generic vowel-omission category is invented.

Mappings are derived, not source-authored project categories. Their event-share
denominator contains only mapped events. All 122 project categories remain in the
output. A mapping of positive events is not complete absence annotation: these
adapters declare no project absence scope. Category prevalence, opportunity
rates and density stay unmeasured unless supplied by another explicitly
annotated input. Genuine learner attempts/difficulty remain a separate existing
population; source records never become participants or effectiveness evidence.

## Saved state, reuse and UI

The existing empirical_report row finalizes immutable input/output assets. Input
contains the actual selected windows, source selection, mapping rules, population
metadata and source_summary. Output also contains readable category_labels and
source_summary `{source_id,source_name,source_version,view_label,unit,
mapping_version,source_manifest,notes,coverage:[{label,count}],constructed}`. These describe the
saved report; reads do not recalculate or inspect original bytes.

To reuse saved observations, POST `{title,reuse_input_asset_id}`. The server
reads that saved input once and calculates from its frozen observations and
summary, retaining the source selection as lineage. It does not re-select the
current import, reapply a newer crosswalk, or dispatch a model. Creating a new
source report is the explicit way to read a source again. Missing saved input
returns authored recovery guidance and leaves prior reports usable.

The ordinary result leads with source/view, example/error counts and coverage.
It uses category names, readable source-label descriptions, percentages and
counts such as “2 out of 10”. “Not measured” has an authored reason. Exact
fractions, native codes/IDs and full provenance are in Download report. Native
and mapped relationships remain distinct; no all-English or causal conclusion
is made. Selected results appear before saved history and focus on delivery.
Tables scroll within their containers at narrow widths; important captions
remain14 CSS px and the existing body typography is preserved.

Reads use the existing logged bounded transient retry. Final errors retain
selected source, report name and any saved result. Explicit retry uses the same
form. Writes are not blindly replayed after an ambiguous result. Source choice
failure, an empty import list and unavailable observations do not block saved
work, optional other tools or ordinary practice. Opening reports, saving,
reading, reusing and downloading them make zero model/speech/provider calls.

An invalid report definition or incompatible attempt population is a correctable
input response, rather than a temporary service failure. Existing validation is
classified by the report owner; no extra admission or read checks are added.
An actual database/media failure remains a service failure. After an ambiguous
save, guidance asks the user to check saved reports before explicitly trying
again. A zero denominator means no eligible observations for that measurement;
it does not by itself mean that sentence annotations are missing.
Save feedback belongs beside the source, saved-input or advanced form that
submitted it. The shared feedback owner reveals that form and focuses its
authored message, preserving every field and the previous saved result.
