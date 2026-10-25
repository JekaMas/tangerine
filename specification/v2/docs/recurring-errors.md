# Recurring speaker mistakes (fossilized-pattern simulation)

Prepare optionally gives each speaker one recurring mistake pattern, a target
frequency (70–95%, default85%) and optional plain-language guidance. Automatic
selection chooses a contextually valid rule from the same requested categories;
guidance narrows that rule without changing the permitted taxonomy, severity or
English-variety policies. Profiles belong to the current exercise and are frozen
with its blueprint. They do not diagnose a real person or infer a defect from an
accent, first language or demographic label.

Fossilization research describes selective, persistent, variable patterns; it does
not establish one universal70–95% per-opportunity error rate. These percentages
are configurable practice settings, not empirical estimates. References and the
research/evidence boundary are retained in audit/recurring-errors-20261025/REPORT.md.
Temporary stabilization and observed recurrence do not prove lifelong permanence.

The optional exercise_request.recurring_errors array contains one profile per
enabled speaker: speaker_number (one-based order in the frozen blueprint),
target_percent (integer70–95) and instruction (string or null). Reducing/growing
the UI count retains hidden profiles but submits only active roles. Advanced
exercise_request values override the corresponding simple controls. Empty/absent
profiles preserve legacy behavior. Explicit mutation_count=0 disables all errors,
including recurring ones, while retaining the requested settings in saved data.

A recurring rule is one scored unit with several actual text spans/audio intervals.
It counts once toward mutation_count, category coverage and the existing42score
formulas. Every occurrence remains separately represented in its opportunity
ledger; unrelated events are never merged merely because their category matches.
The amount UI explicitly describes this rule when recurring mode is enabled.
Every enabled speaker receives one recurring unit unless zero errors are requested.
The total requested count must accommodate those units; automatic/density modes
retain the existing coverage floor extended to enabled-speaker count.

The clean-text LLM provides natural, correct opportunities for the requested rule,
preferably at least four per enabled speaker while keeping the topic coherent.
The mutation LLM identifies a specific rule, enumerates all its applicable
contexts in that speaker's canonical text, and returns each canonical span,
corresponding final-surface span and mutated flag in unit.recurrence. Other
speakers and irrelevant words are excluded from the denominator. Legitimate
regional forms and contextually appropriate alternatives are not opportunities
for an error. A lexical rule may target a specific collocation; a grammar rule
may target a finite morphological environment; an acoustic rule names the actual
supported phoneme/stress/connected-speech operation and its eligible context.
The same named rule must hold across its occurrences, not just the same category.
The grouped realization.canonical_text/surface_text fields may summarize a
representative example; the opportunity ledger is the complete literal record.

For N eligible opportunities and requested integer percentage P, choose
M=max(1,min(N,floor((P*N+50)/100))) distinct mutations. At least two opportunities
are needed to represent recurrence. The rule stays correct at N−M opportunities.
Save both kinds. Short-text rounding is explicit: P85,N7 gives M6 and85.7%;
P85,N4 gives M3 and75%; P85,N2 gives M2 and100%. The UI displays target and actual
M/N percentage, never claims the target was exactly attained. Selection among
equally eligible contexts belongs to the LLM; the accepted ledger freezes the
result, so resume never resamples it. No extra scheduling/randomness layer is needed.

Each mutated ledger entry corresponds exactly to a text_span of that unit. A
textual mutation changes its declared wording; an acoustic mutation retains its
actual typed operation at that scope. A correct entry retains the clean wording
and cannot receive an acoustic mutation at the same scope. Canonical/surface
locations are Unicode codepoint intervals. The existing single output admission
checks identity, quota and these literal correspondences; it does not pretend to
algorithmically prove every linguistic opportunity or run another model audit.
Accepted candidate, manifest, rendered key and post-answer result preserve this
metadata. Existing source/clock provenance and unknown acoustic observations stay
unchanged. Repeated phone operations remain distinct by unit plus surface scope,
including multiple repetitions in one utterance, without replacing a whole phrase
with another occurrence's variant.

The render plan explicitly lists recurring_unit_ids per affected turn. Local
Kokoro/Melo compile one full-phrase alternative containing that unit's complete
set of phone changes, then reuse it for each distinct scoped crop. This bounds
model invocations by recurring patterns per piece, rather than repetitions.
Unchanged correct occurrences remain in the original reference recording.
Ordinary non-recurring independent-scope variants retain their original behavior.

A listener may identify the speaker's common rule once, with an appropriate
repair/rule or valid examples; listing every repetition is optional. Corrections
and optional explanations retain their separate judgments. A particular correct
exception is not an error; an overgeneralization such as “all plural nouns need
-s” is judged on its actual truth. One speaker's pattern gives no credit for a
different speaker's unrelated event. Results show pattern, target, actual M/N,
and saved correct/mutated contexts after submission; no answer key is exposed
beforehand. Feedback describes an authored simulation, not a diagnosis of a real
speaker's learning history. No human review, corpus acquisition or paid service
is required.
