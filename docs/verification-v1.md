# Audio publication procedure

A requested sound is not an observed sound. A synthesis instruction cannot approve its own output.
The publication decision must refer to the final delivered audio bytes. Earlier WAV checks do not approve a changed delivery file.

## Required checks

The publication process must complete these checks:

1. Make sure that schemas, references, counts, intervals, and source hashes satisfy the contracts.
2. Make sure that the source rights permit each intended use.
3. Examine the script, mutations, corrections, context, and negative controls.
4. Measure the decoded final audio with the recorded method.
5. Compare the independent ASR hypothesis with the surface transcript.
6. Record the actual phonetic, prosodic, or timing evidence.
7. Obtain the independent whole-recording reviews.
8. Resolve disagreements before publication.

A schema failure, corrupted audio, or missing rights blocks publication.
A reviewer cannot override these failures. An unsupported method produces `needs_review`, not `pass`.

## Mechanical measurements

The existing profile requires finite samples and a nonempty mono stream. Duration must satisfy the blueprint limits.
Peak absolute sample amplitude must not exceed 0.9999 full scale.
Integrated loudness must be within 2 LUFS of -18 LUFS. True peak must not exceed -1 dBTP.
Measure these values after delivery encoding. A clipped or truncated output fails the check.

Unplanned leading or trailing digital silence over 1,500 milliseconds requires review.
Unplanned interior near-silence over 2,000 milliseconds requires review.
The detector uses 20-millisecond RMS windows and a -50 dBFS threshold. Zero RMS has negative-infinite dBFS.
An intentional pause is not an automatic failure. The reviewer compares the pause with the planned target.

## Transcript and pronunciation

The ASR result is an independent hypothesis. Compare it with the erroneous surface transcript, not the corrected script.
The WER definition is in `domain/metrics.v1.yaml`. WER over 0.10 requires review.
A smaller WER does not prove that an intended error exists. The reviewers must examine every target interval.
The ASR must not approve a TTS correction that removed the intended error.

For segmental targets, record observed IPA and the supporting audio interval.
The record must include the reviewer qualification and the final audio hash.
Keep canonical IPA, intended IPA, and observed IPA separate. Unknown observed IPA remains null.

For prosody, record the named target and the audible interpretation.
Numerical F0 claims require a method, units, bounds, and measurement evidence.
A low provider pronunciation score cannot identify a substituted phone.
An accent label cannot prove a phoneme error or a level of teacher skill.

Speech rate includes pauses inside the speech interval. Articulation rate excludes the separately annotated non-speech intervals.
A rate outside the blueprint tolerance requires review. Changed audio must pass the publication procedure again.

## Independent review

Two qualified people must first listen without the planned answer key.
Each person records observed errors, permitted variants, and intervals. Each person then examines the proposed key and corrections.
Each person must examine the whole recording, not only selected targets.
For acoustic targets, at least one reviewer must have evidence of phonetics competence.

A reviewer record must come from an authenticated action. A model cannot create a reviewer or a qualification.
The same person under two accounts does not satisfy independence.
A disagreement requires a third adjudicator or continued publication blocking.

Every approval names the case version and the final audio hash.
A change to audio, context, corrections, or the key invalidates approval for the new version.
Historical approvals remain attached to their original bytes. They cannot approve a replacement artifact.

## Disputes

A plausible off-key observation creates `potential_key_defect`. Save the attempt and quarantine the case for new attempts.
Do not mark that observation false merely because it is absent from the key.
A confirmed defect requires a new case version and an explicit result revision.
An unsupported allegation requires evidence before it counts as a false positive.
The frozen teacher answer does not change during review.
