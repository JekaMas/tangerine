# Internal local interface

The full operation inventory remains domain/operations.yaml with exact method/path/request/response references in contracts/openapi.yaml. These are internal UI/service interfaces, not a user-managed public API. One local workspace has no accounts, roles or complex authentication.

The main preparation action accepts contracts/exercise-request.schema.json through blueprint-write.exercise_request. The server expands speaker/word-length/optional-level/category defaults into the existing blueprint; the UI orchestrates existing generate/render/listen/submit/result operations. No new public API or separate review action is required.

## Exact field ownership

For every mutation, its named request schema is the canonical content schema unless an explicit request projection is listed. domain/operation-ownership.yaml contains request_fields, server_fields and imported_source_fields per operation. Full stored-record schemas are never posted with fabricated server IDs/times. A create/submit request consists of exactly request_fields; the server assigns every server_field. No preliminary generic reservation exists or is needed. If a record is imported, its original identity/time/author fields are stored in the raw asset/source metadata; its new local envelope uses actual local identity/time. Referenced case/audio/configuration hashes in request_fields are legitimate equality preconditions.

Use Idempotency-Key for mutation retry deduplication and If-Match on revision-dependent updates. The browser/helper supplies these automatically. Equal operation/key/content returns the saved outcome; conflicting content409. ETag is quoted decimal revision. Safe error statuses remain400 malformed content,404 missing ID,409 conflicting state,412 stale revision,413 configured size,422 invalid semantic reference,429 concurrency/optional cap,502 exhausted provider normalization failure,503 unavailable required dependency and504 deadline. A completed provisional result/feedback-only failure returns200 with explicit status.

Local JSON requests ignore harmless unknown additive fields after retaining raw request diagnostics; fields claiming server identity/success/lease/publication approval are not trusted. Wrong scorable references or wrong required content are errors. Canonical storage projection remains closed. Provider normalization is defined separately. Do not reject a harmless reply fence/unknown vendor field as a new product boundary.

Lists use stable creation-sequence/objectID keyset pagination, default50/max100. Cursor contains the last key and selected filter/snapshot; no secret signing scheme is necessary for one local workspace. Invalid cursor400, next_cursor=null at actual completion. Reading one page never establishes full-corpus acquisition.

## Review and disclosure

start_review triggers case_review through the configured LLM. get_review returns blind-review-view for imported/diagnostic observations. blind_submit/review_disclose/review_decide remain internal processing operations that store machine observations/disclosure/decision; no human person or qualification is requested. create_person/qualification/get_person retain imported native metadata only, without a review UI prerequisite. teacher_gold accepts native imported labels or LLM labels with explicit origin. resolve_dispute/adjudicate/reconsider use the LLM and append versions.

Before answer submission, teacher DTOs exclude the key, transcript and planned-event count. After submission teacher-key/teacher-rationale expose the full approved pedagogical content, excluding raw provider records, secret values, private native persons and source personal metadata. Settings show key presence only. Preparation views are separate from teacher projections.

Audio resolves private linked bytes, supports a valid single HTTP range206,416 otherwise, and uses final hash ETag. No MinIO hostname/key or signed credential URL reaches the browser. UI/service binds local interfaces; internal service key is helper-generated, with no human authentication setup. Metadata used by the teacher view does not reveal target words before submission.

LLM Lab uses the existing configuration owner for active_prompt_bundle_id and local capture flags. Saved bundle/snapshot/experiment records use existing document/asset storage; Lab helper actions are local tooling, with no additional public HTTP API. Its upstream local MLflow UI/SDK/OTLP interfaces are defined in llm-lab.md.
