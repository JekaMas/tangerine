# Iteration 22 — production ElevenLabs dictionaries

Base: `e98b4a9`, branch `tangerine/iteration-16-release`, actual worktree
`/Users/jekamas/projects/0xatelerix/_worktrees/tangerine_iteration16_20261021`.

Selected properties: FIN-SP-01.P1, FIN-VERIFY.I22; ten literal cases. The native
OpenSpec 1.13.1 apply context and passed graph/query are retained under
`data/iteration-22-elevenlabs-20261026/`. Existing I21 acceptance remains valid.

## Anchors before production edits

- Compiler/transport owner: `services/speech/backends.py` plan/render/hosted;
  add a cohesive ElevenLabs PLS/transport helper, without a new service.
- Acoustic partition: `acoustic_plan.scopes`, orchestrated by `acoustic_runtime`.
  ElevenLabs needs exact selected whole-word/phrase pieces; correct context and
  other speakers keep literal text and their voice with no target dictionary.
- Durable lineage: `renderSpeech` saves the accepted worker plan/pieces in the
  existing render_plan_asset_id before any piece synthesis; profile, voice,
  model and admitted dictionary/version locators travel with those pieces.
  `completedSpeechPiece` and render progress reuse completed work on resume.
- Completion: `renderAcousticPiece` uses existing resolution/transform owners;
  `assembleSpeech` saves WAV/sample map/key, then `finishSpeechCase` publishes
  Library/Listen. Native answer persistence/interpreter/scorer own the result.
- Fresh dictionary response admission must reject absent/invalid id/version as
  PROVIDER_FAILED once, before dependent TTS. Saved bindings are trusted.

## Evidence and scope

The earlier comparison is standalone evidence, not production acceptance.
Current subscription readback: tier Free; 8900/10000 used, cannot extend,
max_credit_limit_extension=0, current_overage=0. Existing restricted private key
is reused without exposing it. Model-list permission returned401; official
model support and retained actual Flash v2 use establish the selected transport,
while the new actual call must establish current admission. Voices Sarah/George
are present in current account listing. No synthesis yet.

Independent fixture: speaker1 says “I think we should think again.”, selected
second “think” [18,23) /θɪŋk/ → /sɪŋk/; first [2,7) and speaker2 are correct.
One literal accepted answer must yield TP1/FN0/FP0, correction1/1, primary100;
no optional explanation penalty. Constructed semantic transport is explicit.

## Resume

Read selected contracts/owners; implement literal deterministic red cases first,
then scoped compiler/transport and native ordinary-flow qualification. UI review
must inspect actual stored playback/answer/result and recoverable errors.
Pending: implementation, tests, actual permitted speech/Lab observations,
self-review, stable dirty selection, source commit, committed-clean selection,
acceptance record. No task is checked yet.

## Verification repair checkpoint

The user requests verify plus root-cause/sibling repair and nonblocking UX.
Controlled native Go-race flow passed with expected TP1/FN0/FP0,100, complete
feedback. Live Free Flash v2 completed all pieces; intentional second-piece
interruption reused first audio and frozen dictionary/version/model despite
current configuration changing. Browser played the same stored3.456167s WAV.
One blinded existing Gemini Free audio opinion identified target /sɪŋk/ and
reference /θɪŋk/ (HTTP200); this is model opinion, not gold.

Confirmed UX defect: Listen refresh retained its previous success notice when a
later refresh exhausted three transient read retries. The new error was human
readable and text/actions stayed available, but the old success was misleading.
Owner is useListening.refresh; clear that operation's notice on entry. Siblings:
write and retryChecking already clear both; preparation generate clears progress
on failure. This changes only refresh notice state and invalidates that
browser counterexample; speech/score/provider observations remain valid.

Harness corrections retained: initial mounted path import failure; constructed
feedback initially omitted language, then claim-linked component feedback.
These were test-boundary failures, repaired before live synthesis. A browser
wait matched Next.js's empty global alert; scoped text selectors replaced it.
Native/protocol original failure logs remain. No quota exhaustion or paid use.

Final source review removed an unnecessary phone_start condition for complete
phone_pair scopes: recipe phone coordinates are intent metadata and do not
require hosted word timing. The retained pre-repair source reproduced the
rejection; the focused local HTTP positive passes. Vowel/VOT/subword timing
limits remain explicit. This invalidates the scope oracle/registered selection
only; the existing live nil-coordinate requests/audio/key/score remain valid.
The complete dirty selection is rerun after final registration, with no hosted
redispatch. No provider observation is repeated for evidence/export stages.

Stable dirty iteration selection:13/13 passed (`dirty-final.json`). This is
evidence only, not clean acceptance. Source behavior, UI/typography inspection,
Go race/vet, web build, Python owner observations and original-scope preservation
are complete. Native/Lab artifacts retained; owned stack/tab closed, viewport
restored and user app3000 readiness200. Next: source commit, same13-case clean
selection, then canonical I22 checkboxes and acceptance-only commit.
