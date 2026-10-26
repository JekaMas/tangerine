# Iteration 24 — Azure F0 speech comparison

The follow-up verification/repair is in [VERIFY.md](VERIFY.md). It supersedes the
apply-stage implementation/evidence inventory below; the original observations
and their proof limits are retained. STATUS.json records the latest source and
full selection. I24 remains incomplete.

**Incomplete: actual Azure access is blocked at Microsoft passkey confirmation.**
No actual Azure recordings were generated, and no full playback/acoustic claim
is accepted. The source baseline was clean
`1b077a5c0666486cb22d831a619868db9f1d9693`. The affected selection is
`FIN-AZURE.P1,FIN-VERIFY.I24`; all I24 tasks remain unchecked.

## Implemented work

The native Azure compiler wrapped each text fragment around a phoneme in `<s>`.
Those fragments are not sentences: it introduced sentence boundaries before and
after the target word. The two red assertions reproduce this defect. The repair
keeps ordinary text in the XML element's text/tail positions and preserves the
original punctuation across phoneme, prosody and pause controls. This matches
Azure's SSML structure and the meaning of a sentence element in the
[Microsoft SSML documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup-structure)
and [W3C SSML specification](https://www.w3.org/TR/speech-synthesis/).
Live audibility of the repair has not been observed.

The comparison now has an executable frozen/resumable owner, native request and
response capture, atomic response/WAV persistence and exact turn/gap assembly.
Completed pieces are trusted and reused; there is no new repeated consistency
audit or learner approval gate. The original material is versioned unchanged in
`material.json`, allowing the controlled contracts to run from a fresh checkout.
The read-only loopback player displays the access blocker plainly and exposes
only its page, font and the two named complete recordings. No app provider
settings, saved exercises or media were changed.

| Turn / speaker | Word | Reference IPA | Mutated IPA |
|---|---|---|---|
| u1 / s1 | choices | tʃɔɪsɪz | ʃɔɪsɪz |
| u2 / s2 | companies | ˈkʌmpəniz | kəmˈpæniz |
| u3 / s1 | another | əˈnʌðɚ | əˈnʌzɚ |
| u4 / s2 | Collision | kəˈlɪʒən | ˈkɑlɪʒən |

The unchanged source is preparation
`9dbf8c95-51a3-4c0f-9395-b3a77a824d22`, opening four car-insurance turns.
Speaker s1 requests US Jenny, and s2 requests UK Ryan. Availability and acoustic
realization of these voices remain unobserved. This is not the later full
26-category comparison or the garden exercise.

## Native evidence and scope

The expanded DAG has 18 exact cases. The stable informational observation records
**16 passes and two skips**, through two native unittest commands. Thirteen
compiler/policy/transport/resume/player cases pass, plus three review
counterexamples. The two skipped cases require actual Azure synthesis and the
real pair's playback/review. Six related existing hosted acoustic/SSML and
unsupported-operation cases passed separately. These sibling observations are
retained; later helper/fixture changes did not invalidate their production input.

The controlled fixtures use synthetic PCM and constructed HTTP/resource metadata.
They prove literal target compilation, exact PCM ordering/gaps, F0-policy
rejection, no-dispatch failure behavior, private-route handling, native context
capture and resume. They do not prove Azure account eligibility, naturalness,
accent, audible pronunciation or a complete live comparison. The live output
directory remains empty. Zero Azure synthesis or model calls occurred.

Original red failures, an intermediate loader mistake, failed attempts to bind
already occupied comparison ports, and corrected observations remain in ignored
`data/iteration-24-azure-20261026/`. Existing servers on 8766–8768 were preserved.
The code repair has one production owner, `services/speech/backends.py`; the
comparison orchestration, player and fixtures remain separate development owners.

## UI, UX and typography review

Skills/guidance used: OpenSpec apply, SDD workflow, verification-design,
hypothesis-debugging, typography and the project's
`docs/development/UI_UX_TYPOGRAPHY_VERIFICATION.md`.

- **UI/UX: incomplete.** The real waiting view explains sign-in/resource access,
  saved pieces and Refresh without showing raw backend errors or pretending audio
  exists. No audio controls are shown while recordings are absent. Disclosure and
  keyboard activation attempts returned unchanged state; no interaction, refresh
  effect or playback pass is claimed. Input delivery or an authentication modal
  is only a hypothesis, not a demonstrated product defect. Retest interaction
  after the protected prerequisite is resolved.
- **Typography: pass for the waiting view only.** Actual screenshots, text and
  computed styles at 1280×720, 390×844 and 320×740 show loaded Source Sans 3,
  17 px body text, 24.65 px line height, readable hierarchy and no page overflow.
  Collapsed content and the future populated audio state are not accepted here.
- **Evidence: incomplete for I24.** Actual native controlled outputs and Lab
  readback exist; actual Azure audio, target observations and completed playback
  evidence do not. Build success, request IPA and constructed tones are not
  substituted for that proof.

The local MLflow experiment is `Tangerine I24 Azure - controlled preparation;
actual access blocked`, experiment 15, run
`6dda9035ba664cca8b6e2abfeb10ed74`. Uploaded contents were read back. They are
explicitly labelled controlled preparation. Export added zero inference; no
Microsoft sign-in/OAuth/passkey data or secret configuration was uploaded.

## Remaining blocker and exact resume action

The installation's Azure key and region are empty, no ambient Azure credentials
or local Azure CLI/session were available, and the selected existing Microsoft
account reached its passkey/security-window step. This is an observation of this
installation, not proof that the user owns no Azure resource elsewhere. The user
handoff is pending in the open Azure tab. No resource, key, paid trial, billing
link, payment method or terms acceptance was created during this task.

Finish Microsoft sign-in, then inspect an actual F0 Speech resource/key/region
and available free allowance. Use [the resume guide](README.md) to generate the
eight necessary turn recordings, assemble both variants, observe target audio
and complete the player review. If the account offers only a paid/trial route,
retain the blocker; no such purchase or account expansion is authorized. There
is no unresolved product decision or reason to weaken FIN-AZURE.

Structural validation is reported separately from behavior. The final committed
source and clean-run outcome are recorded in `STATUS.json` when available. An
incomplete clean run is evidence of the remaining blocker, not an acceptance
receipt. No green I24 acceptance record is issued.
