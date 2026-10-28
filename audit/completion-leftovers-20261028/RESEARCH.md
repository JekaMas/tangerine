# Local runtime and allowance follow-up

The selected model remains Qwen CustomVoice0.6B revision
85e237c12c027371202489a0ec509ded67b5e4b5. The approved project-only environment
uses Python3.12, Torch/Torchaudio2.9.1 and the other repository version bindings.
No weights were downloaded or audited again. Global Python remains unchanged.

The actual float16 MPS native request failed at sampling with nonfinite/invalid
probabilities. A separately frozen float32 candidate generated codes but failed
in the audio tokenizer convolution: MPS does not support that operation's output
channel count. Original native failure journals and directed stack traces are in
ignored data/completion-leftovers-20261028, not rewritten as passes.

The official [model inference owner](https://github.com/QwenLM/Qwen3-TTS/blob/main/qwen_tts/inference/qwen3_tts_model.py)
and [speech tokenizer owner](https://github.com/QwenLM/Qwen3-TTS/blob/main/qwen_tts/inference/qwen3_tts_tokenizer.py)
separate autoregressive generation and audio decoding. The selected repair moves
only the codec to CPU explicitly, retains float32 MPS generation, freezes that
choice in every planned piece and separates the in-memory model cache by it.
[Upstream MPS reports](https://github.com/QwenLM/Qwen3-TTS/issues/69) concern
other hardware/precisions and are background, not proof of this candidate.

The actual selected candidate completed all26pieces and both four-turn WAVs.
Independent exact assembly/context tests and actual Chrome playback/readback
prove this finite operation. They do not prove arbitrary accents, exact IPA,
universal phoneme correctness or throughput. No SDPA/MLX/model sweep, automatic
fallback, hidden sampling clamp, larger deadline or hosted request was selected.

ACCOUNT-OBSERVATIONS.json records the actual read-only provider account views.
ElevenLabs' refreshed Free usage is8922/10000;1078remain. Gemini's expanded one-day model table subsequently showed0/10requests used,
3RPM/10kinputTPM. These dated observations precede the resumed requests.
Azure remains at its protected Microsoft passkey step. None is permission for
paid use. Historical429,503 and subscription-policy blockers are kept distinct
in REMAINING.md.

## Current Gemini API compatibility

The original mode-present Flash-Lite request returned HTTP400 rather than429.
The actual error is Unknown parameter mode at structured_speech_config. The
[official API reference](https://ai.google.dev/api/interactions-api) defines
speaker configuration without mode. The
[official speech guide](https://ai.google.dev/gemini-api/docs/speech-generation)
still contains a conflicting REST example, while its SDK examples omit mode.
The operation's actual rejection is retained; no undocumented replacement value
or automatic transport fallback was tried.

A new explicit whole-dialogue candidate omits mode in both variants and retains
all20turns,26target directions, model and Kore/Puck voice bindings. Two actual
Free requests completed and are exported to local Lab25/run
04f7146f04fc46088b435e12395d6f99. Both full recordings have actual Chrome playback,
keyboard/Refresh and three-width observations. This is not the old cadence setting
or a production Gemini speech adapter, and no perceptual qualification is inferred.

The first experimental container projection incorrectly retained FFmpeg's streaming
unknown-size RIFF header, producing a false24-hour duration. The provider's native
WAV/PCM and responses were already correct. Reusing the actual production
normalization owner repairs the finite header and preserves every PCM sample.
The malformed artifacts and original wrong result remain separately retained;
no new model request was made for this repair. Final durations are207.12/223.56s.
