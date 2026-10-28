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
ElevenLabs' refreshed Free usage is8922/10000;1078remain. Gemini's project still
shows Free tier, but its current model-specific TTS quota was not established.
Azure remains at its protected Microsoft passkey step. None is permission for
paid use. Historical429,503 and subscription-policy blockers are kept distinct
in REMAINING.md.
