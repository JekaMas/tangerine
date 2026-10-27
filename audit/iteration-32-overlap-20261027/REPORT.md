# Iteration 32 — simultaneous speech and word masking

Implementation and verification repairs are complete. Committed-clean acceptance
is recorded in ACCEPTANCE.json after the selected final run.

## Result and ownership

ENG-01 / ALL-AUDIT.2 now uses the production Go composer. Fresh mutation admission
binds each contextual overlap to an exact unit, two different speakers, a selected
surface passage and explicit gains. The manifest and frozen render plan preserve
that intent. Absent intent keeps the sequential default.

Responsibilities are separated:

- `mutation_overlap.go`: fresh intent/unit/turn/scope admission, once.
- `speech_words.go`: accepted decoder/codepoint correspondence.
- `speech_composition.go`: pure sample scheduling, weighted PCM and clock projection.
- `speech_assembly.go`: assets, durable composition and finalization orchestration.
- `speech_key.go`: concurrent utterance and selected shared-passage intervals.
- `speech_http.go`: speech outcome/recovery policy; the shared frontend
  `failureMessage.js` projects the saved outcome for Prepare and Saved audio.

The resolved composition is saved in existing preparation progress before mixing.
An actual native cancellation followed by a fresh server resumes using the same
source assets and schedule, without synthesis. Later turns wait for the latest
active speaker. Split target pieces and independent acoustic units retain their
own source/final clocks. Sample-map rows retain each contribution and local gain.
There is no global normalization, clipped-success output, extra learner review,
stored-data audit or schema-byte archive.

## Findings, repairs and sibling coverage

All four verification findings are closed; FINDINGS.json links their observations.

1. **Missing range evidence.** The native test claimed range playback while checking
   only a full response. Both real scenes now assert HTTP 206, exact mixed bytes
   crossing the selected passage and Content-Range. An impossible range returns 416.
2. **Incomplete UI evidence.** A comparison page alone did not show ordinary stored
   playback/results. Chrome now observes the ordinary unchanged Listen/results
   owners, keyboard replay, full playback, retained answer/score, transparent
   transient retry and persistent-failure recovery. The supplied saved-attempt and
   feedback envelopes are explicitly constructed presentation fixtures; the WAV,
   key intervals and score arithmetic are actual native outputs.
3. **Ineffective Resume for fixed failures.** Clipping or absent word timing on
   accepted recordings cannot repair itself by repeating frozen inputs. The speech
   outcome now records these failures as non-retryable; immediate response agrees
   with saved state. Prepare and Saved audio use one action/message owner and offer
   a new exercise with compatible voice/settings. A misleading “Ready to assemble”
   caption is omitted for this known fixed outcome. Temporary service/setup errors,
   missing credentials and interruption retain Resume. No raw backend string is
   displayed and no provider, voice or gain changes automatically. Native missing
   timing retains both actual recordings; helper, API and browser cases cover the
   fixed and recoverable siblings.
4. **Overbroad development receipt scope.** The contracts/Lab recorder included
   application files that neither tested package imports or embeds. Their original
   hashes remain preserved as non-dependency metadata. The active binding now
   covers the actual contracts/Lab dependencies. The unchanged 59 observations
   were reused, without updating an old hash or recounting them as new execution.
   The initial failing evidence-consumer run remains retained.

The implementation review also repaired split-source target resolution, latest-end
scheduling, sequential key accumulation, final-clock sample-map ordering and a
noncanonical developer scoring verdict. Their original failures and regressions
remain retained. Accepted model timing is projected through the existing acoustic
transform owner before composition; the composer does not invent proportional word
timing. Quality warning/unavailable/malformed responses remain advisory; cancellation
still stops the foreground operation.

## Exact and actual media evidence

At 24 kHz, two 24,000-sample recordings starting at 0 and 12,000 produce 36,000
samples before an explicit gap. Independent tests compare the weighted sum after
one rounding step, unchanged unselected samples, clipping, cancellation, source
mapping, split targets, following turns and concurrent answer-key intervals.

The selected actual Kokoro recordings use `af_heart` and `am_adam` with en-US
bindings. Requested accent text is not an actual accent observation; key accent
status remains unverified. Canonical/mutation LLM and semantic decisions are
constructed external-boundary inputs. No hosted LLM quality qualification is claimed.

| Scene | Selected shared interval | Independent local recognition | Score fixture |
|---|---|---|---|
| Obstructive interruption | 1.900–2.450 s | The source contains “Do not touch the wire”; the mix contains B’s “I want to speak now” and omits the critical warning. | 1 true error, 1 TP, 0 FP, 0 FN. |
| Invited cooperative backchannel | 2.875–3.750 s | Both source and mix retain the museum message. | 0 true errors, 0 TP, 0 FP, 0 FN. |

The recognizer writes the invitation’s “mm-hm” as “ma’am” in both recordings. This
is retained machine output, not a pronunciation defect or human gold. Four actual
local TTS calls and four local Whisper recognitions were performed during apply;
verification reuses their exact WAVs and performs zero new inference. The finite
recognition contrast does not qualify every future voice/phrase or establish
universal human perceptual masking. MLflow records the actual contexts, native
outputs, model bindings, source/key/WAVs and current review artifacts with download
readback; see MLFLOW.json. Export performs no inference.

## UI/UX, typography and video

**UI/UX: pass for the affected scope.** Review uses the OpenSpec verify skill,
pinned SDD verification/code-inspection guidance and Tangerine’s UI review adapter.
Listen/results, Prepare and Saved audio are inspected in actual Chrome at
1280 × 720, 390 × 844 and 320 × 740. Keyboard actions, visible focus, mobile
navigation, retained topic, saved answer/score and no autoplay/automatic dispatch
are observed. Two controlled 503 reads recover to 200 without an alert. A persistent
outage makes three bounded reads, displays authored guidance, preserves the result
and recovers with keyboard Refresh. Only labelled playback acknowledgments use POST;
no generation, synthesis, grading, settings or user-data write passes the UI transport.

**Typography: pass.** Used the available typography skill and inspected actual
screenshots and computed styles. Source Sans 3 renders at 17 px / 24.65 px; passage
captions are 15 px. New longer recovery text wraps at both narrow widths without
horizontal overflow. A 3 px keyboard focus outline remains visible. Fixed failures
have an actionable new-exercise link; temporary work retains an enabled Resume.
No unrelated visual redesign or new UI package was introduced.

**Evidence: pass for the stated finite scope.** Actual pictures and encoded video
frames were inspected. The 42-frame listening/replay/retry video shortens static
waits from the original 236.904-second capture; the edited video is about 36.3 s.
A second 25-frame video shows the final repaired Prepare/Saved audio views and
keyboard continuation. Both videos use actual Chrome frames, pad portrait views
without cropping and have no inserted audio. Original timestamps/frames remain.
The actual source/mixed WAVs are separate. These videos do not claim a newly
inferred, uninterrupted complete product flow.

- [Listening video](../../data/iteration-32-overlap-20261027/tangerine-i32-ui-review.mp4)
- [Recovery video](../../data/iteration-32-overlap-20261027/tangerine-i32-recovery-review.mp4)
- [Obstructive source](../../data/iteration-32-overlap-20261027/selected/obstructive/source-1.wav)
- [Obstructive mix](../../data/iteration-32-overlap-20261027/selected/obstructive/mixed.wav)
- [Cooperative source](../../data/iteration-32-overlap-20261027/selected/cooperative_backchannel/source-1.wav)
- [Cooperative mix](../../data/iteration-32-overlap-20261027/selected/cooperative_backchannel/mixed.wav)

## Validation, preservation and limits

The selected DAG has 5 properties and 39 executable positive/negative cases.
It reads original native observations and independently compares actual waveform,
clock, key, score, context, UI and permitted-reuse data. Receipt reuse is not called
new Go or model execution. Physical evidence comprises 144 Go method/subcase
observations, 7 native cases and 59 unchanged contract/Lab observations: 210 distinct
observations in total. The directly dependent JS helper/sibling cohort passed 52
cases. No I32 case remains planned or substituted for the actual composer.

Go 1.26.5 race/native checks, stable vet/format, the final source-built Next build,
pinned OpenSpec 1.13.1 strict validation, 390 structural specification assertions
and graph/discovery checks pass. A stale complete-contract vector was refreshed
once after the final specification text changed; no schema-byte archive or runtime
check was added. Structural success is separate from committed-clean acceptance.

All 122 category/recipe identities, 42 formulas and 11 source scopes remain
unchanged; PRESERVATION.json records the entry bindings. The canonical GAPS edit,
app on port 3000, existing provider settings, records, media and pre-existing tabs
are preserved. Disposable stacks and UI fixtures are separate. No deployment,
postdeployment, PBT, financial operation, paid credit, overage, provider fallback,
installation, acquisition or publication occurred. Other iteration/provider/source
qualifications retain their original scope; this is the full I32 verdict.
