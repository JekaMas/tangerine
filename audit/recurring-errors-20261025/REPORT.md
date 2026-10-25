# Recurring speaker errors

Status: completed for the scoped recurring-pattern feature. Base:
67c811bd4f7a942a2d7bf02618618e983c62167d. The actual user requested research
and implementation of fossilized-like speaker mistakes in roughly 70–95% of
relevant cases. The existing exercise, settings, all 122 categories/recipes,
42 formulas and 11 source scopes are preserved. No paid credits, overage,
subagents, new accounts, host installs or external publication were used.

Research: Han 2004, “Fossilization: five central issues,”
https://doi.org/10.1111/j.1473-4192.2004.00060.x distinguishes local/global patterns,
stabilization and fossilization. Han 2014, “From Julie to Wes to Alberto,”
https://benjamins.com/catalog/lllt.39.05ch3 describes selective/idiosyncratic/
contingent outcomes. Lardiere 1998, “Case and Tense in the ‘fossilized’ steady
state,” https://doi.org/10.1191/026765898674105303 reports approximately 34% tense
morphology suppliance in obligatory contexts for one longitudinally observed
speaker, not a universal error rate. Wu 2023,
https://pmc.ncbi.nlm.nih.gov/articles/PMC10011781/ discusses context fluctuations
and the difficulty of proving permanence. These primary sources provide no
universal 70–95% rule. Publisher/search excerpts and inaccessible full texts are
not represented as a complete full-text review.

Design: configurable practice target, default 85%; denominator = eligible contexts
for one specific rule in one speaker. Count a deliberately declared recurrent
pattern once, while preserving every actual occurrence and correct exception.
Use the existing generation, mutation, key, interpretation and scoring owners;
no new LLM pass or repeated stored-value audit. The complete contract is
specification/v2/docs/recurring-errors.md. These are exercise-specific simulation
settings; no persistent real-person learner diagnosis or population frequency is
inferred. A pattern is specific to a linguistic rule and context, not a category
label or an accent.

## Behavior and ownership

Prepare has an optional control in each speaker card: enable one recurring rule,
select an integer target from 70–95%, optionally describe the rule. Hidden role
choices survive speaker-count changes; only active enabled roles are submitted.
Advanced request fields retain precedence. Disabled/absent recurrence preserves
ordinary behavior; exact zero suppresses all mistakes while retaining settings.
Automatic selection uses the same category/severity/variety choices as the rest
of generation. A recurring group counts once toward the requested mistake count;
unrelated errors count separately. The UI states this explicitly.

The existing clean-text and mutation LLM stages create the correct text and
complete opportunity ledger. For N opportunities and target P, M is
max(1,min(N,floor((P*N+50)/100))). The accepted ledger saves changed occurrences
and correct exceptions, with canonical/final Unicode spans. Native admission
checks the new output once; persistence, speech and scoring reuse accepted data.
Short-text rounding is visible: 6/7 = 85.7%, 3/4 = 75%, and 2/2 = 100% at a
target of 85%. No claim of exact fractional rates on short texts is made.

The feature's pure request/admission/projection helpers live in
services/api/internal/app/recurring_errors.go. The existing orchestration,
storage, semantic interpretation and exact numeric scoring owners remain in
charge. Candidate, manifest, ground-truth, evaluation, teacher disclosure,
score-result and feedback-score contracts retain the optional metadata. Review
projection preserves it and treats changes to the pattern as primary changes.
No new database migration, controller or human approval workflow was introduced.

Repeated acoustic edits retain their own scopes. Explicit recurring units use
one shared full-phrase alternative per unit/piece in local Kokoro/Melo, then crop
and apply each declared occurrence. Correct exceptions use original reference
samples. Independent non-recurring scopes retain separate variants. This avoids
one full inference per repetition. The two model runs are not a controlled
latency benchmark; invocation count and actual recordings are retained.

## Actual observations

The browser generated a B1 train dialogue using the existing included ChatGPT
profile and local Australian/Indian Melo voices. It produced 128 words against
an approximate 140-word request, nine rendered pieces and 46.10 seconds of audio.
Independent literal enumeration found seven eligible “two tickets” phrases for
Speaker 1, six changed to “two ticket”, with the last occurrence correct. Speaker
2's two correct phrases remained unchanged and were excluded from the denominator.
The persisted key matches the ledger. This deliberately controlled prompt and
the answers below demonstrate behavior; they are not independent learner data.

| Probe | Independently expected and observed outcome |
|---|---|
| Common-pattern report and “two tickets” repair, with the false optional explanation “all plural nouns must end in -s” | One detected group, no miss/false positive; primary 100/100; optional explanation 0. Comments explain the irregular-plural counterexamples without erasing primary credit. |
| Calling the unchanged “two tickets” in the final line wrong and replacing it with “two ticket” | One false positive, one missed group, primary 0/100. Comments distinguish the correct exception from earlier errors and recommend targeted practice. |
| Four “think” opportunities; change the first, second and fourth from theta to s | Actual Melo Australian and Kokoro American synthesis each retain three distinct edits using one shared variant. The third occurrence's waveform is byte-identical before/after its timing projection. Scoped transforms make zero model calls. |
| Catalogue transport block while editing controls | Actual UI error/recovery, retained topic/rule/rate/voices and zero generation dispatches. The test-owned block was removed before live generation. It does not prove a real storage outage. |

Native model inputs, context, bindings, output and actual recordings are retained
under ignored data/recurring-errors-20261025. Seventeen native packets comprise
eight text-stage calls (two generation, two extraction, two mapping, two feedback)
and nine local dialogue speech receipts. The separate two-engine pronunciation
experiment is retained alongside them. All were exported to and read back from
the existing local MLflow experiment 9, run 18805aa087ac49df80609360aaa4a6cb,
without further inference. No new auditory-judge claim is made.

## Findings, repairs and evidence reuse

The live test exposed two missing consumer fields: evaluation-key rejected the
saved unit recurrence, and feedback-score rejected its native result summary.
Both contracts and their native copies are repaired. The read-only native
projection test reproduces both earlier failures using the actual captured key
and scored outputs, then passes against the repaired contracts. The teacher-key
copy was included in the complete projection review. Model scoring, comments and
recommendations now complete through the actual UI.

The first development restart also omitted the existing initializer's new-schema
registration step. PostgreSQL reported the exact missing ground-truth registry
entry. Running the normal initializer fixed that deployment omission. Resume
reused all nine saved audio pieces and the original text/mutations; no replacement
LLM generation or synthesis was needed. Failure records remain retained.

Other retained test/setup failures were corrected without weakening product
requirements: a typed error-detail assertion, unsupported early evidence-route
reads, the explicit null defaults added during request expansion, nested speech
wire-receipt extraction, and a teacher disclosure fixture that incorrectly kept
private evidence_ids. A summary-negative test initially expected a redundant
numeric range recheck on trusted native data; it now checks an actually invalid
field type. No repeated runtime consistency check was added. A transient
individual-file bind read during a speech experiment was resolved by running the
completed script copy from the evidence mount before inference.

RECONCILIATION.json maps all 30 selected cases (15 positive, 15 negative) across
FOS-01 through FOS-04 to observed native receipts. Only changed assertions,
contracts and directly affected cases were repeated. The remaining valid greens
were retained, including the 81-pass affected native observation, 8 existing
request tests, 5 accent request tests and 3 acoustic regression tests. All 22
protected registry/migration files compare byte-for-byte with the base revision.

The stable production web build, native Go race observations, Go vet/gofmt,
Python syntax checks, 388 current static contract/index/assembly assertions,
strict native OpenSpec 1.13.1 and DAG/discovery validation pass. The cached pinned
OpenSpec package was used; no tool was installed. Temporary Lab flags were
restored, the original user attempt was read back unchanged, and credential
names/presence match the baseline. The canonical checkout's unrelated GAPS.md
edit was left untouched. Actual text bindings are included_subscription; speech
is local. Purchased-credit use and automatic reload were verified off in the
account UI before inference. No paid fallback was enabled or used.

This is a scoped, self-reviewed feature acceptance. The finite fixtures and two
authored answers do not prove exhaustive linguistic opportunity identification,
universal model accuracy, actual human fossilization, perceptual correctness for
every acoustic operation, new hosted-provider qualification or a renewed pass of
every historical release test. No further product decision is needed for the
implemented behavior.
