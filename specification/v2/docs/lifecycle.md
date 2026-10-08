# Lifecycle and ordinary local use

Case states remain draft, rendered, verification_failed, needs_review, verified, published, quarantined, retired and superseded. They describe evidence and user choices, not human approval stages.

| From | Event | To and effect |
|---|---|---|
| draft | real synthesis succeeds | rendered; link exact final audio |
| draft/rendered | synthesis or WAV decoding fails | verification_failed; retain reason, retry available |
| rendered/needs_review | LLM case review supports key | verified; save machine judgments |
| rendered | relevant evidence uncertain | needs_review; save warning and offer LLM reconsideration |
| rendered/needs_review/verified | user uses or lists a playable case | published; retain quality status/warnings, no human signature or full-bank gate |
| published | key/audio changed | new draft version; old immutable version retained |
| any playable version | supported key defect or user quarantine | quarantined; hide from new default selection, retain history |
| quarantined | LLM resolves issue or user revises | new version or restored supported version, with reasons |
| published/quarantined | user retires | retired; preserve referenced history |
| published | successor explicitly replaces it | superseded; preserve predecessor |

A valid WAV and a machine-produced key are necessary to score a generated listening exercise. Unknown acoustic confirmation is a visible quality warning, not human-review dependency. Imported actual annotated audio can also supply a key. The first generated case is usable without the 732-case benchmark or all corpus downloads. Fresh startup never fabricates an existing bank.

Attempts retain started, saved, evaluating, completed, evaluation_failed and review_required. Draft saving is allowed while started; submit freezes the exact answer as saved before a call. The evaluation lease then selects evaluating. Supported semantic decisions and exact arithmetic give completed. Transport/output failure gives evaluation_failed with saved answer and retry. Genuine unresolved scorable interpretation gives review_required, meaning LLM reconsideration/provisional result, never a human queue. Audit-only disagreement does not erase a valid score.

Before submit the teacher sees audio/public task context only. After submit show answer, claims, detections/classifications/corrections/explanations, metrics and key/rationales under the approved disclosure policy. Private credentials, raw provider bodies, source personal metadata and imported reviewer identities stay off teacher views. Retrying feedback does not regrade. Retrying evaluation preserves all prior receipts and result revisions.

Disputes retain open, resolving and resolved states as declared by their schema. A real user statement opens a dispute; adjudication is an LLM operation. A changed mapping/key appends a version and explicit old-to-new unit correspondence. Ordinary history is preserved; explicit local deletion uses maintenance cleanup, not an unerasable audit requirement.
