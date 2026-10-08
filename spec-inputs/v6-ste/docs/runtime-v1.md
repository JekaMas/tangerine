# Local synchronous runtime

The deployment contains Next.js, a Go API, PostgreSQL, private MinIO, and a Python speech service.
The speech service prepares content through real speech APIs and FFmpeg. It does not process a spoken teacher answer.
The deployment does not require Redis, Temporal, Kafka, WebSocket, or a background worker.

## Teacher procedure

The teacher selects a published exercise. The page shows the public context and the task instructions.
The teacher can play, pause, and replay the original audio. The teacher enters one English or Russian answer.
The teacher submits the answer and waits. The result shows resolved observations, missed errors, corrections, and named metrics.

The public context must state constraints needed to judge the language. A hidden dialect requirement cannot determine the score.
The page must not expose the answer key before submission. It must not expose hidden counts through metadata or errors.

## Submission and recovery

Before answer entry, freeze the case, task components, and policy versions.
Before a provider request, authorize the session and case access. Make sure that the CSRF and same-origin checks pass.
The existing answer limit is 20,000 Unicode codepoints. An empty answer is a permitted submission.

In one transaction, save the original UTF-8 answer and its SHA-256 hash.
Save the idempotency record and the submitted state in that transaction. Commit before the first provider request.
For the same key and payload, return the same attempt. For a changed payload, return HTTP 409.

Acquire a compare-and-swap lease for the frozen attempt. The existing lease duration is 300 seconds.
Do not hold a database transaction across a provider request. An active lease produces `EVALUATION_IN_PROGRESS` with HTTP 409.
A stale lease token cannot commit a result. The current revision and token must match at commit.

The existing total deadline is 270 seconds. Extraction has 40 seconds, mapping has 70 seconds, and audit has 70 seconds.
Feedback has 40 seconds. Reserve at least 5 seconds for persistence.
Allow at most one transport retry within the remaining deadline. A schema failure does not start a JSON-repair loop.
The API write timeout is 285 seconds. The proxy timeout is 300 seconds, and the browser timeout is 310 seconds.
These values are existing requirements, not measured performance.

Save successful stage inputs and outputs with their hashes. A user-triggered retry can reuse a stage only with identical input hashes.
The provider, prompt, schema, case, and answer hashes must also match. Never retry to obtain a preferred semantic answer.

HTTP 200 can contain a completed result or `review_required`.
A provider refusal or invalid structure produces HTTP 502. A deadline failure produces HTTP 504.
A failed evaluation retains the answer and a safe retry status. A disconnect does not erase the answer.
Recovery requires an explicit user request. The application must not start an automatic recovery job.

If feedback generation fails, show the approved rationale with its references.
Identify that text as stored rationale, not a fresh LLM response. Do not invent new feedback or change the score.

## Persistence and access

Use the tables listed in the design. Store tenant IDs with domain records, including records in local single-tenant use.
Use tenant-aware foreign keys. Keep provider responses and evidence in private storage with immutable hashes.
Save audit events in the same transaction as the domain change.

Use explicit public response objects. Do not serialize an internal case object to a teacher endpoint.
Protect each media request with the session and case permission. Support byte Range requests for audio playback.
The web proxy must not accept an arbitrary destination URL.

The existing local roles remain teacher, author, reviewer, and administrator.
A local role selector is not evidence of a separate reviewer identity.
No operator can satisfy the independent-review rule through two aliases for one person.
The production process must reject development authentication.

## Containers and credentials

Publish only `127.0.0.1:3000`. Keep PostgreSQL, MinIO, the API, and the speech service on the internal container network.
Use the host `.env` file only for interpolation. Do not send that whole file to each container.
The web container receives no provider or database secret.

The API receives its LLM and storage credentials. The speech service receives the keys needed for ASR and synthesis.
Missing keys must stop the corresponding real operation. No mock or substitute provider is active.
The startup process must not create example exercises, successful results, or reviewer approvals.

Start migrations after PostgreSQL readiness. Initialize a private bucket after storage readiness.
Initialize only actual local account configuration. Start the API after the required initialization succeeds.
Start the web service after API readiness. Do not replace readiness with a fixed sleep.

Named volumes retain data across stop and start. Destructive reset requires `CONFIRM_DELETE_LOCAL_DATA=yes`.
The operator must confirm that action before the command erases data.
The backup procedure must include frozen answers and their audio assets.

## Release evidence

The publisher must supply built images and actual digest locks. The operator must not resolve image versions manually.
This package has no application images. Its Compose file does not prove startup success.
The release must pass the same real-provider workflow on `linux/amd64` and `linux/arm64`.

The interface must disclose the external providers that receive the answer or audio.
The teacher must acknowledge that disclosure before the first transfer.
Local containers do not make cloud processing offline. Do not send account identities or consent records in LLM prompts.
