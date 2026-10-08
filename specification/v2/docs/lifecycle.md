# State transitions

The local operator initiates each action. There are no access-role columns.
Updates to an existing mutable head require its current revision through `If-Match`. Creation uses an idempotency key and no prior revision.
A stale revision returns 412. A forbidden transition returns 409.
An absent object returns 404. Missing required evidence returns 422 with safe field paths.
All permitted transitions append an audit record in the same database transaction.
All pairs not listed in the tables are forbidden.

## Candidate operations

A generation operation precedes a case head. It refers to the saved blueprint.
The operation moves from reserved to running, then complete or failed. A cancellation produces cancelled with its reason.
A completed candidate is not a published case. Explicit acceptance creates a new draft case head.
A failed operation cannot produce a case head. Its actual provider receipt remains available.

## Cases

| From | Action | To | Additional guard and effect |
|---|---|---|---|
| draft | render | rendered | Link verified final bytes and every turn interval. |
| rendered | measure | needs_review | Save all measurements, including unavailable observations. |
| rendered | hard QC failure | verification_failed | Keep the failure and prohibit publication. |
| verification_failed | render revised version | superseded | Create a new draft child. The parent bytes stay unchanged. |
| needs_review | complete two final approvals | verified | Same context, key, final audio, rights, and resolved observations. |
| needs_review | reject | verification_failed | Preserve the observations and rejection. |
| verified | publish | published | Reapply all gates and grants at transaction commit. |
| published | quarantine | quarantined | Block new attempts and final evaluation commits immediately. |
| verified | quarantine | quarantined | Block publication. |
| quarantined | reopen review | needs_review | Keep exact bytes. Record the concern and required new review. |
| published | retire | retired | Block new attempts. Existing attempts can finish if grants remain valid. |
| quarantined | retire | retired | Preserve quarantine_open=true, its reason, and the prohibition on final commits. |
| draft | retire | retired | Preserve provenance without publication. |
| published | create changed child | superseded | The new draft references the immutable parent. No automatic replacement of attempts. |
| retired | create changed child | retired | The new draft is independent. The retired parent stays retired. |

No published key, context, correction set, or audio changes in place.
Metadata that affects public interpretation also requires a new version.
A quarantine can end only through review and publication guards. An unchanged hash does not erase the concern.
Rights revocation is stronger than retirement or historical playback permission.
Quarantine sets quarantine_open=true on the head. Retirement or supersession never clears that flag.
Only resolved human review of unchanged content can clear it before verification.
Published and verified heads require quarantine_open=false. A false flag cannot substitute for the required review evidence.
A superseded version permits existing attempts to finish only under the same guards as a retired version.

## Attempts

| From | Action | To | Additional guard and effect |
|---|---|---|---|
| started | save draft | started | Preserve draft revision. No score or answer disclosure. |
| started | submit | saved | Freeze answer, configuration, key, audio, components, and submission time. |
| saved | acquire lease | evaluating | No active lease. Case and transfer grants remain valid. |
| evaluation_failed | explicit retry | evaluating | Preserve frozen inputs. Increment lease epoch. |
| evaluating | expired-lease explicit recovery | evaluating | Require database time at or after lease expiry. Increment the epoch and retain the original frozen inputs. |
| evaluating | explicit cancellation | evaluation_failed | Revoke the active fence and preserve completed stage receipts. |
| saved | quarantine observed | review_required | Keep the original answer. Do not start providers. |
| evaluating | all semantic stages pass | completed | Save exact score and feedback disposition under the current lease. |
| evaluating | unresolved finding | review_required | Save provisional evidence. Final aggregates stay null. |
| evaluating | transport/schema/deadline failure | evaluation_failed | Save failure receipt. Keep exact answer. |
| evaluating | quarantine observed | review_required | Prohibit a final commit against the suspect key. |
| review_required | adjudicate | review_required | Append a separate result revision. Do not edit the original attempt result. |
| completed | dispute | completed | Create a dispute. Preserve the original result. |

The pre-submit view cannot reveal a key even if another activity on the same installation can access it.
After submission, the teacher view exposes the whole exact transcript and key under the proposed disclosure policy.
Unresolved findings remain labeled provisional. Historic quarantined results include a warning.
Reviewer documents, consent records, raw provider replies, and private source provenance never enter teacher DTOs. Keys are forbidden before submission. After frozen submission, only the separately gated key-disclosure projection may expose the reviewed linguistic key under GAP-002’s proposed policy.

## Feedback-only failure

A completed semantic score remains completed if only the feedback call fails.
Use approved stored rationale in the requested language and mark its origin `stored_rationale`.
If approved text in that language is absent, set commentary to unavailable.
Do not translate an unapproved explanation silently or mark a failed mapper complete.
An explicit feedback retry repeats feedback only against the same completed score and key.

## Disputes and result revisions

Disputes move from open to under_review, then resolved or dismissed. The operator can withdraw an unresolved dispute.
A resolution records actual evidence, a genuine adjudicator, its reason, and its effect on the key or semantic decisions.
A changed key creates a new version with a reviewed old-to-new unit correspondence.
Historical reconsideration uses only the recording that the teacher actually heard.
Show affected attempts. Recalculate only the explicitly selected set, synchronously and within current resource limits.
Append each result revision with its original result and correspondence. Never overwrite the historical score.
The teacher view shows the newest completed reviewed revision first and keeps the original accessible.

## Operation-state projection

The operation ledger uses reserved, running, complete, failed, cancelled, and interrupted.
`operation-status` returns that exact ledger state. It is not an attempt state.
`operation-result` shows in_progress for reserved or running, failed for failed, cancelled, or interrupted, and complete for a successful terminal effect.
A terminal effect that creates a review issue shows review_required with the actual issue IDs. The ledger still records a completed operation.
No operation-result label converts an incomplete attempt into a completed score.
