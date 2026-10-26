# Remaining interface and adapter contracts

These details complete the continuation requirements in
`openspec/changes/implement-teacher-error-trainer/specs/completion-and-verification/spec.md`.
They are planned application behavior, not a claim of implementation. The
source-report mapping and iteration routing live in that change. The budget
scope in `ai-development.md` applies: no LLM performance/bulk benchmark campaign.

## Recognizable history without new storage machinery — iteration 19

Use existing list endpoints and storage projections. The following additive
fields are optional for compatibility with older records/responses:

| Existing response | Field | Meaning |
|---|---|---|
| `/api/v1/attempts` item | `exercise_title: string or null` | The title of the original heard exercise, falling back to its saved topic. Limit to 200 Unicode code points, using 199 plus an ellipsis when longer. A later key repair must not rename the original heard context. |
| `/api/v1/attempts` item | `answer_excerpt: string or null` | The actual saved draft/submitted answer, whitespace collapsed and trimmed, limited to 160 Unicode code points plus an ellipsis only when truncated. Blank answers yield null. |
| `/api/v1/preparations` summary | `created_at: date-time` | The existing preparation/document creation time, including saved-audio rows. It is not the list-read time. |
| `/api/v1/library` item | `created_at: date-time` | The existing listed case-version creation time, usable in the review case picker. |

The schemas are `attempt-summary`, `preparation-summary` and `library-item`.
Existing IDs, states, links, timestamps and pagination contracts remain. Render
title first, a readable English local date/time and plain-language status, and
an answer excerpt when useful. Keep the original timestamp and complete ID in
details/copy affordances. Show a readable unknown-date/untitled fallback when
metadata is absent; do not fabricate a title/date or rewrite legacy rows.
Identically titled records, including equal short-ID prefixes, remain distinct
and individually selectable by full identity. Wrap long content at narrow widths.

The API/storage owner projects existing accepted values; presentation formats
them. No migration, metadata service, new account, model call, repeated stored
validation or duplicated answer body is required. During iteration 19, update
the shipped embedded response schemas and native projection together with the
UI. This specification edit does not update application copies or runtime code.

## Replay one stored passage — iteration 20

Refresh, checking progress and the final read after Save/Submit share delivery
ownership for the listening session. An older response cannot replace a newer
accepted result, restore an editable draft after submission or replace current
recovery guidance. Starting a write supersedes outstanding pre-write reads.
Keep saved results and local unsaved text available during read failure; retry
transient reads through the existing transport owner and show authored guidance
only when the read cannot recover. These rules do not add a data-validation gate
or automatically replay a write or an LLM operation.

For an available saved interval `[start_ms,end_ms]`, label minutes/seconds
readably and expose a keyboard-operable **Replay passage** action. Activation
seeks the existing audio element to `start_ms / 1000`, plays the range and pauses
at its end using the media clock and ordinary browser-event granularity. This
does not promise a sample-accurate audio cut. Do not regenerate, re-encode or
download a separate clip merely to replay it.

Starting another range replaces the previous range. A manual seek, ordinary
full-recording Play, pause or navigation cancels the old range-stop listener so it cannot
later pause unrelated playback. Normal full-recording controls remain available.
Queued events from a previous action must not cancel a newer passage: repeated
seeking events for its own latest seek retain its end stop, and pause/ended
events reflect the current media state before cancelling. After that seek has
settled, a manual seek still cancels the range. Disposing the player removes
all listeners, including seek completion.
Read, reload, expanding findings and changing result views do not autoplay.
Each recurring occurrence uses its own saved interval on the same recording;
the grouped scoring unit is still counted once.

Absent timing is shown as **Passage timing unavailable**, with ordinary full
recording playback still available. No zero/fabricated interval is invented.
A media failure retains the answer/findings and offers explicit playback retry.
Replay and error/readback paths perform zero synthesis or LLM dispatches and
preserve existing playback-event accounting. Accepted stored intervals are
trusted; this adds no historical-data validation scan.

The literal range fixture is 9.590–14.839 s in a longer saved recording: verify
the seek, play and subsequent pause, and separately verify that switching to
another range or a manual seek does not retain the old stop handler. Merely
asserting a changed `currentTime` cannot prove passage replay.

## Guided reports, experiments and cleanup — iteration 21

Ordinary starter creation must work without typing JSON, hashes or object IDs.
Offer named starter choices, normal labelled fields and named source/dataset/
configuration selection for the supported starter paths. Prepare valid native
definitions using the existing schemas and owners. Keep advanced JSON and file
import available for the full existing feature scope; do not hide required
manual JSON edits behind a button labelled “Starter”.

Use the existing `/api/v1/lab/defaults` nonsecret configuration/bundle metadata,
saved local records and existing source/report/experiment routes. Display names
resolve to full native IDs in the saved definition. Do not invent placeholder
provider IDs, bundles, releases or participant records. A small packaged example
may use clearly labelled constructed data and existing independent expectations;
it must not be called an authentic corpus or observed learner population.

An empty workspace either offers that labelled example or useful links to
create/import the missing source/dataset or configure a provider. The user can
understand the missing input without editing JSON. Missing options, invalid
advanced JSON and failed saves retain field values and explain the next action.
No provider call occurs while loading options, choosing a starter or saving its
frozen definition. Experiment Run remains separate and explicit; it is not part
of the guided-starter acceptance or a mandatory performance benchmark.

Cleanup accepts named eligible saved-record selection and full-ID details,
preserves same-title records and pagination, then uses the existing preview and
explicit apply. Merely choosing a record or viewing a preview never deletes.
Changing selection invalidates the displayed preview/confirmation using the
existing owner; shared required audio and blocked references keep their current
deletion semantics. No new deletion service or approval ceremony is introduced.

## ElevenLabs through the real application — iteration 22

The existing `speech-service-selection.md` contract owns PLS creation,
model-specific transports, target-safe segmentation, dictionary/version
locators, free/included access and media provenance. Implement it through the
current speech adapter and preparation/render persistence owners. Freeze the
actual selected voice/model and use the admitted saved locator on the relevant
piece. Preserve non-target occurrences/speakers and native local transforms;
do not route every acoustic operation through a dictionary or erase unsupported
operations. No second speech service, queue or stored-schema archive is needed.

An ordinary-flow case must enter through the existing preparation/render path,
store the actual rendered audio/key, reload it, play it from Listen, save an
answer and obtain the independently expected native result for that key. A
single literal pronunciation unit with a fully supported detection/correction
has TP=1, FN=0, FP=0 and primary score 100; an omitted optional explanation is
not a primary-score penalty. Label constructed semantic inputs where used.
Dictionary transport and a valid WAV alone do not prove audible pronunciation
or hosted semantic accuracy; retain the actual scoped observation and limits.

Retained completed pieces and saved dictionary/version bindings are reused on
explicit resume. Invalid newly returned dictionary metadata is rejected once
before dependent synthesis with the existing native `PROVIDER_FAILED` outcome;
it never becomes a fabricated locator. The ordinary preparation HTTP envelope
retains its existing error mapping. Failures keep
their native outcome and saved work, with no hidden text-only/model/provider or
paid fallback. Error tests use a controlled provider boundary or retained genuine
failures. Do not exhaust a real account or request repeated judgments to produce
a negative case. Actual positive qualification uses only permitted remaining
included/free access and the minimum necessary calls.

## Completion and evidence

The eleven-route, typography, keyboard, media-provenance and evidence-content
checks remain in `docs/development/UI_UX_TYPOGRAPHY_VERIFICATION.md`. Each
iteration reconciles its whole affected selection with retained valid greens
and required new observations. A screenshot of a title does not prove a native
list projection; a standalone speech comparison does not prove the app adapter;
opening a JSON editor does not prove the guided path; and seeking without an
end observation does not prove finite replay. No new human review gate or
automatic model judge is required by this specification.
