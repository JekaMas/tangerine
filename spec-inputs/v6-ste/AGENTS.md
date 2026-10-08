# Instructions for implementation agents

Read the whole OpenSpec change before implementation. Read the contracts, registries, and procedures that each requirement names.
Use `docs/authority.md` to resolve document precedence. If documents conflict, stop the affected implementation.
Report the conflict with exact paths and requirement IDs. Do not select a convenient interpretation.

## Approval

Do not add a product feature without explicit owner approval for that exact change.
Do not add a mock, fake, stub, simulator, canned response, or substitute provider without explicit approval for that exact case.
This rule applies to application code, tests, examples, seed data, documentation, and delivery scripts.
A test label does not create an exception. A local deployment does not create an exception.

Use `docs/change-control.md` for each approval request. An agent cannot approve its own request.
A general implementation instruction is not approval for an extra feature. Silence is not approval.
A competitor feature is not approval. A research example is not approval.

Do not invent consent, reviewer identities, source rights, citations, corpus records, model IDs, image digests, or measured results.
Do not create a successful response when a service fails. Do not change an incomplete task to completed.
A missing credential must stop the real provider request. It must not select a test provider.

## Data and metrics

Preserve the 122 taxonomy IDs. Do not remove difficult acoustic targets.
Preserve the metric formulas unless the owner approves an exact formula change.
Do not infer a phoneme from a low pronunciation score. Do not infer a teacher correction from the answer key.
Keep source text, intended speech, observed speech, and teacher text separate.
An unresolved semantic decision must not produce a final score.

Use exact codepoint spans for quoted teacher text. Make sure that each referenced identifier exists in the permitted scope.
Make sure that each evidence reference belongs to the correct case, unit, audio hash, and revision.
A valid schema does not prove that a linguistic judgment is true. Keep the required independent reviews and held-out evaluation.

## Language and evidence

Use the language rules in `language/README.md` for new prose. Do not rewrite protected learner errors or IPA as ordinary English.
Do not translate code identifiers or status values. Do not use shorter prose to remove a condition or exception.

Record actual commands and actual outputs. Mark unperformed tests `not_run`.
Record the source file hashes for retained evidence. Do not copy an old PASS into a new review.
No rule permits an absolute accuracy claim without the corresponding evidence.
