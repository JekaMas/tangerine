# Simultaneous speech and word masking

Iteration32 implements ENG-01 without changing the sequential default. An
on-demand mutation may retain both speakers' ordinary text and add
`overlap_intents` to the candidate, mutation manifest and frozen render plan.
This is a discourse event, not a pronunciation/accent error. The clean phase
still has no mutation instructions. Existing accepted preparations remain readable.

Each intent binds one `discourse.turn_taking` unit to an earlier target turn and
a later-listed turn by another speaker, with a literal final-surface
`target_scope` and explicit positive linear gains up to1. The source turn order
is a dependency order; the audio starts are allowed to be concurrent. The
unit names both turns and its target text. `obstructive` requires `true_error`;
`cooperative_backchannel` requires `acceptable`. Context must be audible before
the interference: for example a request to finish a safety instruction, or an
invitation to give brief acknowledgments. Overlap alone establishes no error.

The speech planner still generates separate local/service source recordings.
It resolves selected complete words from actual accepted native decoder timing,
including every retained piece's codepoint offset and targets spanning piece boundaries. Those timings are model proposals,
not heard/forced-alignment gold. A whole retained piece can use its exact source
extent without a decoder; a narrow word cannot receive invented proportional
timing. The preserved full source recordings are never replaced by silence.

The Go application composition owner starts the interrupting stream at the
selected source word's actual final start. Each retained source has an independent
half-open sample interval, final start and fixed linear gain. Target attenuation
applies only inside the declared target scope; unselected target samples retain
unity gain. The competing stream retains its full recording at its declared
gain. Both streams genuinely contribute samples during the selected passage.
The key's passage is the intersection of that selected interval and the competing
stream, not the old sequential second-turn position. The saved tracks also show
the complete competing turn and any later contextual overlap.

For each final sample n, output is `round(sum(source_sample * gain))`, with halves
rounded away from zero. Accumulation precedes rounding. There is no limiter or
global loudness normalization. A mix exceeding PCM16 range cannot be delivered
as a clipped success. Explicit gains provide headroom; independent tests cover
clipping and cancellation. Preserved source samples and source-to-final map rows
retain their original clocks and hashes. `mix_gain` records each contribution;
concurrent rows are not merged into one fictitious source. Silence rows exist
only where no track occupies the final clock.

Sequentially listed turns after an overlap start after the latest end of every
active speaker and its requested gap. A short cooperative acknowledgment cannot
cut off the main speaker or advance the next turn into unfinished speech. At
24kHz, two24000-sample recordings starting at0 and12000 produce36000samples
before any explicit trailing gap; the shared12000..24000range is the weighted
sum, not concatenation.

The resolved composition is saved in the existing render-progress asset before
mixing. Resume trusts that schedule and its accepted source/native timing, then
continues through the existing assembled asset, sample map, key and final
preparation checkpoint. Restart, repeated render and stored/range playback do
not regenerate the source recordings. There is no new learner review, audit,
corpus, provider or qualification step.

Key utterances use their actual concurrent placement. The overlapping event's
unit uses the actual selected shared passage. Ordinary acoustic unit intervals
still follow their own transforms and offsets. A cooperative control adds no
true-error opportunity, TP, FP or FN when accepted; falsely criticizing it can
still be a false positive under the existing scoring policy. Corrections and
optional supplied explanations retain their separate scoring rules.

Development evidence distinguishes exact waveform arithmetic, actual local
recordings, contextual authored labels and independent local recognition.
Synthesis intent or a loudness ratio alone does not prove complete perceptual
masking. Finite observed recordings do not qualify every future voice/phrase.
