# Choosing an exercise

Per-speaker [recurring error profiles](recurring-errors.md) optionally repeat one
specific rule at a requested 70–95% of relevant contexts. A declared recurring
pattern counts once toward the displayed mistake total, with every changed and
correct occurrence saved. Other independent mistakes retain their existing count;
exact zero disables both. The actual rounded fraction appears after submission.

Prepare offers topic, speakers, approximate words and optional CEFR. Category
choice has two levels: broad families permit the LLM to choose applicable leaves;
specific categories restrict it to the selected registered IDs. Selecting a
specific category clears the broad selection and vice versa. Search matches
labels, descriptions and IDs; it does not clear selected items. Clear restores
automatic choice. Individual categories come from GET
`/api/v1/preparation-options`: a read-only projection of the same shipped taxonomy
used in generation. `preparation-options.schema.json` describes its version and
category records. All 122 records are returned; the eight `control=true`
acceptable-variant records are not offered as injected errors. A catalogue
failure preserves the form and provides explicit retry; broad input still works.
No dictionary service, provider call, database migration or new account is needed.

The optional `exercise_request.category_ids` array stores the exact chosen leaves;
empty/absent preserves existing broad/advanced behavior. Nonempty restricts the
mutation context to those leaves and requires at least one primary true-error
event in each for positive/automatic amounts. An explicit incompatible broad
family or advanced target is rejected by the existing selection owner. Explicit
zero preserves unchanged text and no required ordinary category events. Existing
advanced target min/max and requested acceptable controls retain their meanings.

Severity uses optional `exercise_request.severity_levels`: minor, moderate,
major, communication_breakdown. Empty/absent means any. It guides the actual
mutation LLM and is enforced in its existing single new-output admission. It is
independent of CEFR and amount, and preserves original weights 1/2/3/4. Severity
is contextual impact, never an inference from a speaker's identity or accent.

Automatic retains a null count. Low/Medium/High resolve to round(requested words
times 1/2/4 per 100), with at least one and enough to cover all explicitly selected
categories. Overlapping pronunciation parent/child families share coverage rather
than being counted twice. The UI shows the effective exact count; it estimates
density from requested length and does not claim a precise density in the final
generated text. Exact permits any nonnegative integer, including zero for an
exercise without injected errors. A positive exact number below selected coverage
is explained before generation. All explicit advanced fields override matching
simple fields; ordinary advanced admission remains authoritative.

The existing blueprint stores effective count, IDs and severity; frozen settings
and resume retain them. No new checkpoint, validation loop or observation gate
is introduced. Correct variants, native arithmetic, all original categories and
optional corpus/empirical features remain unchanged.

Per-speaker accent/voice selection, explicit local routing and preview replay are
defined in [speaker accents](speaker-accents.md).
