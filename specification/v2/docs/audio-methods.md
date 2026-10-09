# Audio compilation and measurements

The delivery file is an uncompressed WAV with mono signed 16-bit PCM at 24,000 Hz.
It is the same byte payload that the machine review records. There is no separately approved lossy derivative.
A later codec conversion creates a new asset/version and records actual measurements; separate machine review remains optional.

## SSML compiler

Create one `speak` root with version 1.0, the synthesis namespace, and the selected xml:lang.
Create one voice element for the exact registered voice.
Escape all text and attribute data with a proper XML serializer. Never concatenate user XML.
A text operation emits its surface text without correction.
A phoneme operation emits one phoneme element with alphabet=ipa, ph=intended IPA, and original spelling as element text.
A pause operation emits break time as an integer followed by ms.
A prosody operation emits only non-null rate, pitch, and volume controls.
Rate uses an explicit signed percentage. Pitch uses an explicit signed semitone value followed by st.
Volume uses an explicit signed decibel value followed by dB.
A contour requires strictly increasing positions from 0 to 100 and an allowed baseline voice capability.
Do not combine contour with a separate pitch value for the same scope.
At least one prosody control must be present. Nested or overlapping scopes are invalid.
Remote audio, lexicon URLs, arbitrary tags, style identifiers, and vendor extensions are available only through a documented compiler capability.
Call turns in source order. Each turn references exactly one existing utterance and speaker.
Preserve every provider response, its format, plan hash, and actual call receipt.

## Assembly

Decode each actual response and reject any unexpected clock, channels, malformed data, or truncated frame.
Do not trim leading or trailing silence automatically. Do not time-stretch, pitch-shift, normalize loudness, or repair target speech silently.
Append each turn’s samples in order and insert exactly gap_after_ms*24 zero samples after it; gap_after_ms is the render-plan integer field. Apply it to every turn, including the final turn, when nonzero. No unspecified gap_ms field exists. These planned intervals are retained on the final sample clock.
Keep source-response and final-turn offsets as integer sample indices.
An observed interval uses half-open sample bounds. Convert to milliseconds only for display.
Start milliseconds use floor(1000*start/24000). End milliseconds use ceil(1000*end/24000).
The master-to-advisory 16-kHz conversion uses the pinned FFmpeg resampler and its recorded options.
It does not change the final delivery identity. Advisory offsets map back by exact rational clock conversion.

## Mechanical quality

Normalize PCM16 sample x to x/32768 for numerical measurements.
Reject NaN, infinity, inconsistent byte counts, zero channels, or a zero-length file.
Sample peak is max(abs(x)). Report peak>=0.9999 as a QC warning.
Calculate integrated loudness with the release-pinned FFmpeg `ebur128` filter under ITU-R BS.1770 gating.
Enable true-peak calculation and record the actual FFmpeg version, build configuration, binary hash, and measurement command.
The reported loudness target is -20 through -16 LUFS inclusive.
The reported true-peak target is <=-1 dBTP. Treat unavailable integrated loudness as a unavailable quality measure, not zero.
A recording that is too short for the method is not_measurable for this method and displays a quality warning.

Use 480-sample RMS windows and a 240-sample hop for silence at 24 kHz.
For a final partial window, divide by its actual sample count. Do not zero-pad the denominator.
RMS is sqrt(sum(x*x)/N). A window is silent when RMS<=10^(-45/20).
Map a silent window to its covered sample interval. Merge intersecting or touching intervals.
A planned pause covers only its exact inserted-sample interval, not every nearby provider silence.
Subtract the union of planned-pause intervals before measuring unwanted silence.
Keep wanted and unwanted silence separate. A targeted pause is still part of elapsed speech duration.
An unwanted interval of at least 2,000 ms reports a QC warning. Boundary equality triggers the same warning, not publication failure.
All-silent audio fails regardless of planned pauses or duration targets.

## Speech tokens and intervals

A reviewed token is one completed lexical word that was actually spoken.
Contractions such as don't count as one lexical token. The original spelling and boundaries remain available.
Count each completed repetition. Record partial-word attempts and nonlexical fillers separately.
Expand a number only to the actual spoken words documented by review. Do not guess its spoken form from digits.
Punctuation is not a token. A hyphenated form follows its reviewed spoken lexical realization.
Keep raw tokens, normalized comparison tokens, final-sample boundaries, and source annotation IDs.

Speech WPM = 60*lexical_token_count/elapsed_speech_seconds.
Elapsed speech runs from the first reviewed spoken onset through the final reviewed spoken offset, including internal pauses.
Articulation WPM uses the union of reviewed speech intervals as its denominator.
Merge overlaps before summing durations. Do not count an overlap twice.
Zero duration with nonzero tokens is invalid. An empty valid population is unavailable, not zero WPM.
Disfluency density counts only genuine reviewed error events under the public context.
Ordinary fillers and self-repair are not automatically errors. They can remain descriptive events.

## Prosody features

| Feature | Unit | Method | Missingness |
|---|---|---|---|
| lexical_stress | category | LLM inference from actual acoustic observations of lexical syllable prominence. | Uncertain syllabification or stress uses LLM reconsideration or remains an explicit unknown observation. |
| nuclear_stress | category | Automatically aligned phrase boundary and final main prominence annotation. | Unknown phrase boundary uses LLM reconsideration or remains an explicit unknown observation. |
| f0_range_semitones | semitones | Praat autocorrelation F0, then P95 minus P5 on semitones. | Fewer than 20 eligible voiced frames is not_measurable. |
| f0_slope_semitones_per_second | semitones_per_second | Least-squares slope on eligible F0 frames in the reviewed phrase. | Fewer than 20 frames or zero time variance is not_measurable. |
| syllable_duration_ratio | ratio | Reviewed target syllable samples divided by reviewed reference syllable samples. | Missing boundary or zero reference duration uses LLM reconsideration or remains an explicit unknown observation. |
| rhythm | category | LLM interpretation of acoustic observations: target_matched, target_not_matched, uncertain. | Uncertain is not_measurable with an explicit reason; LLM reconsideration is optional. |
| boundary | category | LLM interpretation of acoustic observations: rising, falling, level, complex, uncertain. | Uncertain is not_measurable with an explicit reason; LLM reconsideration is optional. |
| weak_form | category | LLM interpretation of acoustic observations of the actual segment sequence and context. | No reliable observation uses LLM reconsideration or remains an explicit unknown observation. |
| linking | category | LLM interpretation of acoustic observations: present, absent, uncertain, with exact boundary. | Unknown boundary uses LLM reconsideration or remains an explicit unknown observation. |
| assimilation | category | Native annotation or measured/model-inferred input/output segment relation. | Unsupported perceived segment uses LLM reconsideration or remains an explicit unknown observation. |
| elision | category | Native annotation or measured/model-inferred retained/deleted segment relation. | A low ASR confidence is insufficient. |

Use the release-pinned Praat engine through the pinned Python binding.
Use autocorrelation with time step 0.01 s, floor 60 Hz, ceiling 500 Hz, 15 candidates, and very accurate mode.
Set silence threshold 0.03, voicing threshold 0.45, octave cost 0.01, octave-jump cost 0.35, and voiced/unvoiced cost 0.14.
Exclude unvoiced frames, nonfinite F0, and frames outside reviewed voiced intervals. Do not interpolate missing frames.
Convert F0 to semitones with `12*log2(F0/100 Hz)`.
Use linear percentile interpolation at index `(N-1)*p` after sorting values.
Use the same frozen frame method for every compared recording.
These parameters are a declared engineering method, not proof that all voices fit its pitch range.
Record a range mismatch and require a separately versioned approved method, not an automatic pitch-range switch.

## Advisory normalization

Whisper receives the audio without a reference transcript prompt and returns verbose JSON with word timestamps.
Preserve the raw hypothesis before any reference-conditioned operation.
Tokenize WER with the reviewed comparison-token policy. Use edit distance with substitution, deletion, and insertion cost one.
A missing ASR hypothesis is unavailable. It is not zero WER or an observed pronunciation label.

Azure assessment uses non-overlapping chunks at reviewed utterance boundaries, each no longer than 25 seconds.
Split a longer utterance only at a reviewed word boundary. If none exists, leave that advisory result unavailable.
Use exactly the surface words inside the chunk for ReferenceText. Do not include canonical corrections.
Preserve raw Offset and Duration ticks. One tick is 100 nanoseconds.
Map chunk-relative intervals to final samples using floor for start and ceil for end, plus the exact chunk origin.
Retain RecognitionStatus, NBest text/confidence, word/syllable/phoneme scores, errors, and raw response fields.
NoMatch, missing score, and unsupported prosody remain explicit statuses.
Do not map absent fields to zero. Do not infer observed IPA from a reference-conditioned score.

## Target qualification and drift

Every one of the 122 taxonomy leaves has a target contract, including its permitted controls.
A qualification key contains provider, model/engine observation, voice, locale, render operations, method versions, and target combination.
A supported capability report uses actual target/control audio, exact final hashes, relevant measurements and one LLM review with explicit evidence modality. No capability report is a normal-use prerequisite.
Explicit user render retries have no candidate-lifetime ceiling. Retain monotonic attempt history and every failure; each foreground action retains its deadline/idempotency/bounded automatic retries. A failure never deletes the target requirement.
Changed profiles may serve new content immediately; optional canary diagnostics retain the exact actual profile and observations.
Keep old published bytes and their review evidence. Do not retroactively assert that an alias stayed unchanged.

## Concrete method bindings and warning semantics

Define method family ffmpeg-ebur128-v1: execute the installed FFmpeg on the private final WAV with `-nostdin -hide_banner -i <wav> -filter_complex ebur128=peak=true -f null -`; parse its final integrated-I and true-peak summaries, preserve stderr as private method evidence, and report null if no valid summary is available. Define resample-v1 with `-ar 16000 -ac 1 -sample_fmt s16` for an advisory derivative only. Define praat-ac-v1 through praat-parselmouth using the exact autocorrelation parameters above. Build-time dependency lockfiles select actual package/binary versions; runtime receipts record them. Do not hardcode an invented binary hash into a spec. Missing FFmpeg/Praat is measurement_unavailable, not a zero score or startup approval request.

Token method lexical-v1 uses actual independent ASR/source tokens and times: Unicode NFC for comparison only, lowercase, strip leading/trailing Unicode punctuation, preserve internal apostrophes and hyphens, remove empty comparison tokens; no digit expansion except actual aligned spoken words. Source words and source offsets remain unchanged. WER uses these comparison tokens and cost1 for S/D/I. Token boundaries are actual source/alignment/ASR intervals; uncertainty is retained.

Every target-capability entry defines its exact linguistic inclusion/exclusion predicate from the full taxonomy. A selected blueprint expands a finite matrix of its targetIDs × chosen voiceIDs × chosen locales × operation signatures × methodIDs; test each requested combination, not an arbitrary universal cartesian product before use. The full report covers122leaves and preserves failed/unobserved combinations. Repeated synthetic voice identity is stratification metadata, not proof of common learner identity.

Mechanical thresholds and acoustic predicates remain quality measurements and warnings. Corrupt/unplayable audio fails delivery. A valid playable WAV outside loudness/silence bounds is shown with a warning and may be used; it does not require a human waiver. No scalar score or transcript proves a requested phoneme/prosody was realized. A text-only LLM marks unavailable acoustic observations unknown; an explicitly audio-capable adapter may produce model-inferred auditory labels, still distinct from native source labels and numerical measurements.

Controlled Kokoro phoneme injection and local independent ASR are specified in [full development readiness](full-development-readiness.md). They reuse the existing private speech owner and measurements; ASR is not phone assessment.
