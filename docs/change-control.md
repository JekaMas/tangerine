# Approval for each case

An approval is an explicit decision from the project owner. Each approval applies to one defined request.
The request must name the exact change and its boundaries. General consent does not approve unnamed cases.

## Restricted actions

Approval is required before each of these actions:

- Add a product feature, metric, data field with new behavior, or acceptance rule.
- Add a mock, stub, fake, canned result, test double, or substitute integration.
- Add artificial examples that can act as expected evidence in a test or assessment.
- Change a formula, threshold, model, voice, corpus, fallback, or error interpretation.
- Use a human recording instead of required synthetic speech.
- Relax a publication gate or a data-use restriction.

A request to simplify infrastructure does not approve reduced language coverage.
A request for tests does not approve fake integration success. A request for synthetic learner speech does not approve fake verification.
The requested synthetic speech is product content. It still requires real provider output and the stated publication checks.

## Approval request

Before implementation, record the following fields in one request:

- The request ID and the exact affected paths.
- The parent requirement and the purpose of the change.
- The exact proposed behavior and the behavior that it replaces.
- The artifact hashes or the bounded artifact pattern.
- The permitted environment, data use, and expiry condition.
- The risks, removal procedure, and acceptance evidence.

Use `contracts/approval-record.schema.json` for the record.
The owner must provide an explicit decision for that request ID and scope.
Save a reference to the actual owner message. Do not create or infer that message.

An approval is valid only while its scope, artifact hashes, environment, and expiry match the action.
A modified case requires a new decision. An expired or revoked approval permits no further use.
An approval for one mock does not approve another mock. An approval for testing does not permit production substitution.

## Default state

`approvals/decisions.json` contains no approvals in this package.
The application must reject unapproved artificial provider paths. The release process must reject unapproved substitute artifacts.
No seed process can create a completed teacher attempt or an approved reviewer decision.
An empty real exercise bank must remain empty. It must not display an invented demonstration as a real exercise.

The inherited v5 illustrations and test constructions are not new evidence.
They remain identified in the inherited artifact register. Their presence does not authorize new similar constructions.
Do not use an inherited construction in a live exercise or a benchmark result.

## Conflict and correction

A text-only translation can preserve a requirement without a new feature approval.
A direct enforcement of the current explicit prohibition can remove an unauthorized path.
A semantic correction that changes valid inputs or results requires a separate decision record.
Until that decision exists, mark the affected release gate `blocked`.
Do not implement a guessed correction merely to close the review.

## Requested synthetic speech

Synthetic exercise speech is an explicit product requirement. Label that audio as synthetic and apply the full case-review procedure.
This requirement does not authorize invented provider responses, human approvals, test outcomes, or source rights.
The existing taxonomy illustrations remain unreviewed reference text. They are not a seed dataset or a completed corpus.
