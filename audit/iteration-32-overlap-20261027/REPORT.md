# Iteration 32 — simultaneous speech and word masking

Status: implementation and selected informational checks passed; committed-clean
acceptance is recorded separately after the implementation commit.

## Result and ownership

ENG-01 is implemented through the production Go audio composer. The new fresh
mutation admission binds typed overlap intent to the exact discourse unit and
two different saved speakers. The mutation manifest and frozen render plan keep
that intent. Ordinary absent/empty intent retains sequential synthesis.

Responsibilities remain separated:
- mutation_overlap.go: fresh output semantics, alongside existing mutation admission;
- speech_words.go: accepted decoder/codepoint correspondence;
- speech_composition.go: pure sample schedule, weighted PCM and clock projection;
- speech_assembly.go: existing private assets, saved progress, composition and finalization orchestration;
- speech_key.go: actual concurrent utterance and selected masked-passage intervals.

The composition is saved before mixing in the existing preparation progress.
Native cancellation after that checkpoint and restart through a fresh server
reuse the accepted source recordings and schedule. Reopen/playback do not invoke
synthesis. Following turns wait for the latest active speaker. Split target
pieces and other acoustic-unit timing use the same final placement.

Gains are explicit and local. Unselected source samples retain unity gain; both
sources retain their original sample clocks. There is no global normalization,
clipped-success recording, schema-byte archive, repeated stored-data validation,
human approval or new learner gate.

## Observed evidence

The stable physical cohorts contain199 exact passed Go observations (see
NATIVE-COVERAGE.json and the ignored OBSERVATIONS.json/raw streams), including
original admission/manifest/planner/key/controller regressions, the new exact
mixer cases, native PostgreSQL/MinIO rendering and full contract/Lab tests.
They are retained with unchanged semantic source bindings. The current DAG
executes20 explicit positive/negative evidence assertions over those original
observations and the actual waveform/key/score/context data. It does not present
receipt reuse as another Go/model execution. Each of the five I32 properties
has positive and negative cases; there are no I32 planned placeholders.

At24kHz, the independent literal test verifies two24000-sample sources at0 and
12000 yielding36000samples. Every shared sample equals the declared weighted
sum. Forbidden clipping, guessed native timing, wrong speaker/unit/scope,
lookahead source, obsolete sequential timing, cancellation and counterfeit or
incomplete evidence are covered. Source map rows preserve both clock systems
and contribution gains. Existing authentic/empirical/hosted evidence is not
promoted by these developer fixtures.

Actual local Kokoro source recordings use af_heart and am_adam with en-US
bindings. Native key accent observations remain unverified; requested accent
text is not claimed as an actual perceptual result. Four actual local source
inferences and four independent local Whisper recognitions were performed.
The later stable native cohort reused the source clips and dispatched no new
synthesis. Canonical/mutation LLM and semantic score replies are constructed
external-boundary inputs; this work claims no hosted LLM quality qualification.

| Scene | Selected shared passage | Observed finite contrast | Score fixture |
|---|---|---|---|
| Obstructive interruption |1.900–2.450s|Source recognition contains “Do not touch the wire”; mixed recognition contains B’s “I want to speak now” and omits the critical warning.|1true error,1TP,0FP,0FN for a constructed correct detection.|
| Cooperative backchannel |2.875–3.750s|Both source and mixed recognition retain “We will visit the museum tomorrow morning”; the short competing stream remains quiet.|0true errors,0TP,0FP,0FN for accepting the control.|

The recognizer writes the invitation’s “mm-hm” as “ma’am” in both versions.
This is retained machine output, not a pronunciation error or human gold. The
control tests the audible invitation/continued main message and a quiet overlap.
Synthesis intent, gains and recognition do not establish universal perceptual
masking or qualify every future phrase/voice. Actual selected WAVs, contexts,
keys, source/final maps, native receipts and recognition inputs/outputs are kept
under data/iteration-32-overlap-20261027; MLflow export/readback is in MLFLOW.json.

## Review, repairs and siblings

Self-review used the OpenSpec apply skill, the pinned SDD delivery/verification
and code-inspection guidance, and the typography skill. It is not an independent
human or separate-agent review.

Resolved findings and their siblings:
1. The production composer concatenated turns. One timed PCM owner now handles both sequential and concurrent delivery, avoiding a second mixer in the speech worker.
2. Sequential key accumulation misplaces the second speaker under overlap. Key projection now consumes the persisted actual placements and selected shared passage; independent ordinary acoustic scopes keep their shifted offsets.
3. Cross-piece targets and short backchannels could lose a clock or advance the following turn too early. Multiple source ranges and the latest active end fix both; exact literal cases cover them.
4. The first native score fixture used a noncanonical verdict and lacked a TP assertion. The repaired fixture uses matched_error and checks1TP/0FN. Original output remains retained as superseded evidence.
5. The new clipping error needed authored recovery text. It now preserves saved work without displaying its backend identifier.
6. Final source rows needed deterministic final-clock order and valid source/gain provenance. Assembly sorts those rows once; tests inspect exact native rows and actual waveform arithmetic.
7. The first graph draft duplicated existing Go test/property edges and left orphaned discovery scope IDs. The final graph consumes original observations explicitly via20 current assertions and a separate exact native coverage trace; prior case registrations/reviews remain unchanged.

## UI, UX, typography and limits

Product routes/styles are unchanged. Their accepted I31 eleven-route and
controlled recovery observations remain valid and were not rerun. This iteration
adds no form, extra confirmation or frontend gate. The new clipping cause has
an authored saved-work recovery message; advisory quality remains advisory.

The read-only local recording comparison was inspected in Chrome at1280×720,
390×844 and320×740. Actual playback advanced with no media error. Body text is
17px/24.65px, captions14px, and no page overflow was observed. Desktop/narrow
pictures and browser observations are retained. These are actual recording
comparison observations, not a claim that an old running app3000 has been
upgraded or that a new full eleven-route video was executed. No visual model,
hosted provider, new account, installation or purchase was used.

UI/UX: pass for the affected saved-media comparison and unchanged frontend scope.
Typography: pass for the reviewed comparison; product typography unchanged.
Evidence: pass for the finite native/source/clock/recognition/Lab scope stated
above; no human/perceptual or all-voices claim.

## Preservation and completion

The122category taxonomy/recipe registries,42formula registry and11source
identities remain byte-identical to the entry revision; see PRESERVATION.json.
The separately edited canonical GAPS.md, app3000, settings, records, media and
pre-existing tabs were preserved. Disposable native stacks removed only their
own containers/networks. No paid provider call, overage, fallback, deployment
or publication occurred.

Go1.26.5 race/native checks and vet/format passed. The pinned OpenSpec1.13.1
strict check and390 current specification assembly assertions passed. Graph and
discovery checks are structural; final clean acceptance is the separate exact
iteration gate, not an inference from those structural results.
