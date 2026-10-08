# Local interface operations

The canonical operation inventory is `domain/operations.yaml`. OpenAPI is `contracts/openapi.yaml`.
Every request schema is closed. Unknown properties, query parameters, or state actions are rejected.
Every mutation uses Idempotency-Key. Every revision-dependent operation uses If-Match.
All returned mutable entities include ETag with the quoted decimal revision in the HTTP header.

## Shared outcomes

Malformed JSON, duplicate keys, invalid UTF-8, and unknown fields return 400.
Unavailable IDs return 404. A cross-case reference is invalid evidence, not a successful lookup.
A state or lease conflict returns 409. A stale revision returns 412.
A declared capacity overflow returns 413. A semantic constraint or missing required evidence returns 422.
Local admission/cost guards return 429. A required local dependency failure returns 503.
Provider or output-structure failure returns 502. An elapsed request deadline returns 504.
A semantic uncertainty returns the declared review_required result with HTTP 200 because the request completed without a final score.
A feedback-only failure returns HTTP 200 with a valid score and an explicit commentary disposition.
Errors include only declared safe fields. Raw prompts, keys, hidden targets, and provider bodies stay private.

## List operations

Use stable keyset pagination ordered by database creation sequence and object ID.
The default page size is 50 and the maximum is 100.
The opaque cursor binds operation, filter, snapshot revision, last key, and an internal HMAC.
Reject a malformed, stale-incompatible, wrong-operation, or altered cursor.
Do not silently ignore a page of source records or treat a paged list as the complete corpus.
The operator can request the next page until next_cursor is null.

## Media

The API resolves the exact case or review asset on each request and rechecks current rights and availability.
Support a single valid HTTP byte range for native audio seeking.
Return 206 with correct Content-Range and Content-Length, or 416 for an unsatisfiable/multiple range.
Use the final asset hash as the ETag. Do not put target words or categories in response headers, filenames, or object metadata.
Return Cache-Control private,no-store for assessment and review APIs.
No internal MinIO hostname or signed secret URL reaches the browser.

## Disclosure allowlists

Library uses only library-item.
An unsubmitted attempt uses teacher-start-view or attempt-view. Neither contains a key, transcript, or planned event count.
A blind review uses review-context plus audio before submission. Planned unit IDs are absent.
Key disclosure has a separate POST operation and persisted prerequisite/disclosure records.
After submission, key-disclosure supplies the full linguistic key and approved rationale text under the proposed product policy.
The teacher projection removes raw review decisions, person identifiers, private provenance, and raw provider records.
Prepare uses prepare-view. It is never reused as a teacher response.
Configuration uses configuration-view, which exposes secret presence only.
Historical or quarantined results include status and rights warnings. They do not bypass a current revocation.

## Caller-supplied record fields

Evidence-import endpoints accept actual preexisting IDs and timestamps only as imported evidence fields.
The API assigns the local storage envelope ID, insertion time, audit event, and mutable revision itself.
For local review actions, the API supplies submission/disclosure timestamps and hashes.
Reject client attempts to set a completed server receipt, lease token, provider success, or publication approval as an implementation shortcut.
An imported actual human decision remains subject to genuine identity, source evidence, and conflict checks.

## Server-owned fields

`domain/operation-ownership.yaml` binds all operation identities and authoritative envelope fields.
The browser cannot select a lease epoch, current timestamp, receipt, content digest, or approval identity by posting a full record.
A create request either omits server fields through its request schema or the API compares their supplied values and replaces no conflict silently.
For a request that still uses a full record schema, allocate its identity through a prior server reservation.
The subsequent submit must use that exact reservation and unchanged source content. The server assigns submission time and the stored digest.
Source issuer dates and source record IDs remain source metadata, distinct from the current server envelope.

## Error codes

`domain/error-codes.yaml` supplies fixed codes, safe English messages, statuses, and explicit retry eligibility.
A translated message cannot include hidden values or alter the code meaning.
Use 403 for an invalid private service credential. This is not a human account boundary.
Application errors never contain raw provider payloads or the answer key.
