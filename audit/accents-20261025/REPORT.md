# Australian/Indian English and selectable speaker voices

Status: complete within the scope and evidence limits below. Base:
51b1da6ec99b654c0c4965afab1b099d07f71349.
Actual user asks to add accents and selects Australian and Indian English. The
preceding real full-flow video request remains in scope after the controls work.
Use the existing SDD workflow and typography. No subagents, paid credits, overage,
new accounts, host prerequisites, remote publication or user-data replacement.

Design: existing Kokoro US/UK voices plus explicit local MeloTTS-English Australian
(EN-AU, speaker3) and Indian (EN_INDIA, speaker2) bindings. No imitation by changing
spellings, accent-to-error inference or silent hosted fallback. Add per-speaker
accent/voice controls and fixed actual local preview recordings. Preserve simple
Automatic and advanced overrides. Frozen speaker choices use the existing durable
blueprint/render/key path. Keep text variety policy distinct from speaker accent.

Research: official https://github.com/myshell-ai/MeloTTS README lists all four
English accents and CPU inference. https://huggingface.co/myshell-ai/MeloTTS-English
config records speaker IDs. Code209145371cff8fc3bd60d7be902ea69cbdb7965a,
modelbb4fb7346d566d277ba8c8c7dbfdf6786139b8ef, BERT
86b5e0934494bd15c9632b12f734a8a67f723594. Model assets are explicitly installed
once; normal inference stays offline and trusts accepted data. English-only
adapter reuses upstream VITS model code and BERT conditioning, with a documented
CMU/espeak frontend instead of loading unrelated multilingual packages.

## Delivered behavior and ownership

Prepare now offers per-role Accent → Voice choices and stored audio previews.
The six choices are Heart/Adam (American), Emma/George (British), and the Melo
Australian/Indian trained speakers. Reducing and restoring the speaker count
retains choices; only active roles are submitted. Automatic retains configured
defaults, while explicit advanced speakers take precedence. Workspace provider
settings are unchanged. The new local composite freezes the selected profile
through the existing blueprint/checkpoint/render/key path and honors saved
profiles on resume. Missing models and unsupported phones/voices fail explicitly.

The API catalogue/blueprint/profile owners select and persist voices; the web
component owns controls and preview playback. The speech routing module owns
per-voice backend choice; the English frontend/model adapter owns the Melo phone,
tone, BERT and native decoder inputs. Existing acoustic owners retain waveform
transforms and stored correspondence. No duplicate persistence or approval layer
was added. Startup/inference does not download models, and accepted assets are
trusted rather than repeatedly hashed. Assets are installed in the existing local
speech volume; other machines use the documented explicit model-setup command.

## Actual observations

All six previews were synthesized locally from the same sentence and are shipped
as WAVs. AU and IN also produced complete same-speaker reference/mutated pairs
for “I think the train leaves at noon.” Literal independently expected phone
inputs change th/ih/ng/k to s/ih/ng/k. Native attention proposes the saved
phone/word intervals; the existing transform uses those observations without an
extra model call. Real output waveforms differ. These are production/input/output
observations, not a perceptual certificate or every-controller qualification.

The real browser demo generated a 62-word B1 dialogue with AU/IN speakers and two
minor errors (number and collocation). All four speech pieces completed, and the
stored 21.85-second audio played fully in the browser. The submitted answer
deliberately identifies “two ticket” → “two tickets” and misses “did a mistake” →
“made a mistake.” Native results show TP1/FN1/FP0, exact primary score60/100,
separate explanation feedback, comments on both findings/misses and two practice
recommendations. The authored demo answer used the saved key; this is a controlled
application demonstration, not an independent learner or linguistic benchmark.

Before included-plan inference, ChatGPT Usage showed Tangerine access enabled,
credit use after plan limits disabled and automatic reload disabled. No financial
setting changed. Text uses the existing included ChatGPT profile, speech is
local, and no separately billed provider route/purchased credits/overage was used.
Lab content/trace capture was temporarily enabled for the synthetic demo through
the normal configuration owner, then restored exactly. Credential presence and
the original user attempt match their saved baseline. API recreation explicitly
kept the originally absent DeepSeek runtime key absent.

Private evidence is in data/accents-20261025/. The 81.19-second demo.mp4 uses
actual browser frames, shortens idle waits and synchronizes the exact saved
preview/dialogue WAVs to actual playback cues. The video labels both edits;
there is no microphone/system-audio capture. Original timing is retained in
original.mp4 (758.47seconds) and the raw261-frame timestamp/cue index. Both MP4
streams were inspected; H264 video and AAC audio are present. Saved screenshots
include the controls at desktop/390px and real saved/results screens.

Local MLflow experiment8/run1b92f5de28cc4602aa57e3d3a7e2b46b stores/readbacks all
selected voice/phone observations, the actual dialogue/key/results and six native
prompt/context/model/output capture packets. Export/readback makes zero inference
calls. Source snapshots are development context: the demo preceded the subsequent
resume/advanced-precedence repairs, whose independent native tests establish those
branches without repeating unaffected generation.

## Verification and repair

[RECONCILIATION.json](RECONCILIATION.json) maps all25 selected DAG cases to exact
observed passing identities and independently specified expectations: eight native
race-detector cases, five pure shipped-JavaScript request cases, four pure phone/
route/missing-model cases, three actual speech evidence readbacks and five real
browser/demo/preservation readbacks. Four properties each have positive and
negative cases. Twenty existing affected native regressions are retained; only
the subsets affected by the resume/override changes were repeated. Metadata and
record-only changes did not trigger repeated synthesis or a whole-suite rerun.

Real browser failure checks explicitly block the catalogue/preview transport,
then restore it. They establish UI error/input retention and recovery, not a real
API/storage outage. Ordinary demo requests have no network/model substitution.
Repeated preview playback uses the same static WAV with zero synthesis requests.

Review found and repaired saved-profile precedence and advanced speaker-count
precedence. Each has a retained failing counterexample and passing regression.
An advanced test initially expected plain Kokoro while its unrestricted category
fixture correctly requested the existing controlled profile; the fixture now
explicitly selects lexis to isolate advanced precedence. Other retained setup
failures include a container GitHub proxy403 (resumed successfully from the host
using the same pinned official assets), the initial DAG unittest command shape,
and a contract vector missing the new/updated documentation. Failed UI locator
and evidence-route reads are retained; existing supported controls/native Lab
readback completed the observations without a new production endpoint.

387 current schema/reference/vector/prompt/ownership assertions, strict native
OpenSpec1.13.1 (no issues), DAG/discovery validation, Go vet/gofmt and the stable
production web build pass. Python syntax parsing covers the new/changed owners;
executed artifact scripts parse themselves. The installed global OpenSpec is
1.14.3, so the already cached pinned1.13.1 package was used without installing a
global tool. The older wrapper large-output parser limitation is not relabelled
green; native strict validation is the actual current OpenSpec observation.

All22 protected generation registries, taxonomy/recipes/formulas/source scopes
and migrations compared byte-for-byte with baseline are unchanged. The canonical
checkout’s unrelated audit/spec-fullness-20261008/GAPS.md remains untouched. This
was this agent’s source review, not an independent external review. No unselected
hosted service, universal accent/naturalness, all acoustic mutations or renewed
full-release acceptance is claimed. The new voices represent two trained model
speakers; regional variety and subjective quality remain listening judgments.
