# Application design

The teacher listens to a prepared recording and writes the errors in one text box.
The application saves that answer before a provider request. The teacher waits for the result in the same request.
All existing language domains remain required. This mode does not observe a teacher in a live classroom.

## Components

The author creates a blueprint, a candidate, and an audio file. The speech service supplies recorded evidence.
Two independent reviewers approve the final case. The publisher stores an immutable case version.

The browser contacts the same-origin web proxy. The proxy contacts the Go API.
The API stores the frozen attempt in PostgreSQL. It then contacts the configured LLM for extraction, mapping, audit, and feedback.
The backend calculates metrics from resolved decisions. The API stores the result before it returns success.

The API gives authorized access to private MinIO media. HTTP Range supports ordinary audio playback.
Content preparation occurs before the teacher attempt. This design requires no live ASR, Redis, Temporal, message queue, or retry daemon.
The Python speech container handles the provider audio interfaces and DSP tools.

## Binding documents

The repository root is the base for the paths in this section.
Read `docs/authority.md` for document precedence. A summary cannot override a binding contract.
If two documents conflict, stop the affected decision and record the conflict.

| Subject | Binding documents |
| --- | --- |
| Scope and permissions | `AGENTS.md`, `docs/change-control.md` |
| Language categories | `domain/error-taxonomy.v1.yaml` |
| Data fields | `contracts/`, `docs/data-dictionary.md` |
| Cross-field rules | `docs/contract-invariants.md` |
| Metrics | `domain/metrics.v1.yaml`, `docs/scoring-v1.md` |
| Source data | `domain/corpus-sources.v1.yaml`, `docs/corpus-acquisition.md` |
| Audio review | `docs/verification-v1.md` |
| Providers and prompts | `domain/providers.v1.yaml`, `docs/providers-v1.md`, `prompts/` |
| Requests and persistence | `docs/runtime-v1.md` |
| Release evidence | `domain/validation-policy.yaml`, `audit/release-gates.json` |

## Case lifecycle

A new case starts in `draft`. Successful audio generation moves it to `rendered`.
The author requests review to enter `needs_review`. All required gates and approvals must pass before the case enters `verified`.
An authorized publication transaction moves it to `published`. The transaction also records the audit event.

A nonretired case can enter `quarantined` with a recorded reason. Quarantine prevents new assignments.
Further review can move it to `needs_review`, but not directly to `published`.
A published case can enter `retired`. Retirement prevents new attempts but preserves historical access.

A change to a published payload creates a distinct draft version. Failed audio generation preserves its evidence under the draft.
A new audio attempt requires an explicit request. Failed generation does not authorize a substituted target or voice.

## Attempt lifecycle

The submission transaction moves `draft` to `submitted` and freezes the answer.
A revision-checked lease moves `submitted` or `evaluation_failed` to `evaluating`.
Evaluation ends in `complete`, `review_required`, or `evaluation_failed`.

An explicit recovery request can mark an expired lease as failed. Review resolution creates a new decision and result revision.
An earlier result remains available after a later revision. A provider request must not hold an open database transaction.
Read `docs/runtime-v1.md` for the lease values, request deadlines, and failure conditions.

## Evidence and limits

Human review remains necessary for the full acoustic domain. This requirement does not prove that reviewers cannot make mistakes.
The named LLM snapshot is a documented baseline. Real corpus results must establish its task performance.

Separate extraction, mapping, and audit requests reduce key contamination. They do not establish independent scientific confirmation.
Schema conformance constrains structure, not the truth of every decision. Unresolved evidence must keep the final score unavailable.

Written corpora supply candidate patterns only. Speech corpora supply only their actual annotations for their actual populations.
Original reviewed cases and adjudicated teacher answers form the assessment corpus. Planned asset counts do not establish acquired evidence.

## Changes and release

This package does not assume an implemented v5 application. Old drafts require explicit import and review under the contracts.
An old demonstration cannot become verified evidence through a version change. Restricted tests and unavailable sources remain outside publication.

The current request authorizes stricter change control and the language revision. It does not approve new mock cases or substitute services.
A partial pilot requires its own explicit scope approval. It cannot represent the requested full-domain release.
Read `audit/open-decisions.json` before implementation of an unresolved property.
