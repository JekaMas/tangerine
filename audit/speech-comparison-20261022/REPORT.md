# Same-dialogue speech comparison, 2026-10-22

The user requests actual comparison recordings of the same dialogue with
pronunciation mistakes across the previously discussed speech options. Only
local inference and verified free provider quota are authorized. Purchased
credits, billing linkage, trials, overage and paid fallback remain forbidden.

This is a finite listening experiment. It does not change the selected
application providers, the saved exercise, its key, any learner answer, or the
production adapters. Provider capability claims and emitted audio remain
separate from demonstrated auditory correctness.

## Shared material

The exact first four clean turns of preparation
`9dbf8c95-51a3-4c0f-9395-b3a77a824d22`, the existing car-insurance dialogue,
are used in every full comparison. This is an excerpt, not the complete
596-word, twenty-turn exercise. The original exercise remains unchanged.

| Turn / speaker | Word | Requested deviation | Requested pronunciation |
|---|---|---|---|
| u1 / s1 | choices | ch to sh | /ʃɔɪsɪz/ |
| u2 / s2 | companies | second-syllable stress | /kəmˈpæniz/ |
| u3 / s1 | another | voiced th to z | /əˈnʌzɚ/ |
| u4 / s2 | Collision | first-syllable stress | /ˈkɑlɪʒən/ |

Each selected word occurs once in the shared excerpt. Clean and altered
variants retain the same speaker assignment. Qwen's separately labelled
respelling route changes the provider-visible spelling at those four targets;
the canonical dialogue and intended targets remain the same. Natural accent
differences are not scored mistakes. Neither speech speed nor loudness is
equalized between providers.

## Actual provider routes

| Route | Method and access | Observation |
|---|---|---|
| Kokoro local | Existing native plan/render/resolve/transform owners, Heart US and George UK, paired phonemes | Complete clean and altered WAVs, 47.700 s and 47.850 s |
| ElevenLabs Flash v2 | Sarah US and George UK, explicit IPA dictionary, four individual turns per variant | Complete clean and altered WAVs, about 39.4 s each |
| ElevenLabs v4 dialogue | Same voices, native multi-speaker endpoint, same dictionary on the altered variant | Complete clean and altered WAVs, 44.096 s and 44.017 s |
| Gemini 3.8 Flash-Lite TTS | Existing unbilled project, Kore/Puck, literal text plus turn-level accent/pronunciation directions | Complete clean and altered WAVs, 40.120 s and 44.280 s; direction acceptance is not exact phoneme control |
| Qwen local | Cached pinned 0.6B CustomVoice, Ryan/Aiden, targeted phonetic respelling | No completed common-dialogue pair; genuine 5.6 s native preview retained separately |
| Azure Speech | No configured key/region/resource; the selected identity reaches Microsoft sign-in/passkey confirmation | No Azure audio, F0 resource, trial or billing account created |

The ElevenLabs account's actual subscription API reports `tier=free`,
`can_extend_character_limit=false`, `allowed_to_extend_character_limit=false`
and zero overage. A new restricted comparison key has a 5,000-unit cap within
the included free allowance. It is stored only in ignored private data; it is
not selected as an ordinary Tangerine provider. Pronunciation-dictionary
creation and synthesis requests returned HTTP 200. The free allowance is not a
purchase or an authorization to purchase credits.

The initial unnecessary Qwen model download was stopped when the accepted
local model cache from iteration 7 was located. The cached model was copied
into the existing local speech model volume. The full-turn float32 client
failed after approximately 260.34 s (artifact timestamps); its HTTP response
body was not retained, so an exact status is not asserted. The native short-piece route
produced one complete piece in 166.39 s; its next piece was explicitly
cancelled for the separate CPU-int8 experiment. That first native piece is not
presented as a completed common-dialogue comparison. The first int8 setup
failed on a dependency deepcopy; its failure is retained. The subsequent
in-place dynamic-int8 batch experiment had not completed even its clean
variant after 635 s and was explicitly stopped. No full Qwen pair is claimed,
no production quantization/adapter change occurred, and no long-running Qwen
comparison job is left consuming the application CPU. Interrupted model-call
encoded-input/output capture is incomplete; submitted text, model/compute
selection, exact helper source and cancellation observations are retained.

## Listening evidence and limits

The Gemini 3.8 Flash audio judge returned HTTP 503/high demand for all three
initial pairs. An explicitly selected alternate **free** Gemini 3.1 Flash-Lite
judge received the actual candidate and reference audio, common transcript,
targets and the complete written comparison prompt. Its opinions did not
confirm all four targets: the initial Kokoro and Flash v2 opinions support
only the collision stress request; the Gemini TTS opinion contradicts all
four. The later v4 audio-judge request also returned HTTP 503. These are automated opinions, not human listening, independent gold,
or proof that a sound is absent. One stress explanation also uses misleading
"correctly" wording. No provider is declared a quality winner.

The native auditory decoder projected only the first object when the judge
returned several JSON objects; another response used a `results` wrapper.
This experiment preserves the entire native response and separately projects
all emitted records without more inference or invented judgments. It does not
claim to repair the application's diagnostic decoder. The listening sheet
shows the complete opinions under optional details rather than silently
discarding findings or claiming a green auditory gate.

## Retained artifacts

Ignored directory: `data/speech-comparison-20261022/`.

- `output/shared-material.json`: exact excerpt, source association and targets.
- `output/*-request.json`, `*-response.json`, `*.raw`, `*-receipt.json`: actual
  synthesis and auditory context, model/voice bindings, output and failures;
  credential headers are excluded.
- `output/*-clean.wav`, `*-mistakes.wav`: eight actual normalized 24 kHz mono PCM16
  recordings. Original hosted MP3/native responses are retained too.
- `compare.py`, `judge.py`, `qwen_batch.py`, `project_opinions.py`: exact
  experimental producers and lossless opinion projection.
- `serve.py`: loopback-only listening sheet at `http://localhost:8766/`, serving
  only its page and the explicitly named WAVs. Private files and raw captures
  are not served.
- Account/browser observations and screenshots; the Azure page remains an
  access handoff.

`output/final-observation.json` records the common transcript/target checks,
actual WAV properties/non-silence and three rejected private-file routes. The
eight full recordings were loaded by the actual browser with `readyState=4`
and no media error. The additional Qwen preview is explicitly partial.

Actual local MLflow experiment **2**, run
`66fc97dd9f4c4c5db9249a30e6b81b17`, retains **128 artifacts**, including all
eight full recordings, the partial preview, requests, responses, producer
sources and failures. Artifact readback succeeded; the export dispatched zero
inference calls. The operator initially failed to parse extra stdout after the
successful export. Its receipt was recovered from the existing finished run
and already downloaded readback artifact without rerunning synthesis,
judgment, export or download. Receipt: `data/speech-comparison-20261022/mlflow-readback.json`.

No whole-release acceptance or unchanged test rerun is implied by these
experiment artifacts. Azure still needs the user sign-in and an actual F0
resource/key. Qwen still needs a completed full pair on a practical local
runtime; the stopped CPU probes are evidence of this setup's timing, not proof
that Qwen cannot synthesize the dialogue on other hardware or in a longer run.

## Documentation checked

- [ElevenLabs pronunciation dictionaries](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/pronunciation-dictionaries)
- [ElevenLabs dialogue API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert)
- [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Gemini free-tier model pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Qwen3-TTS model and speaker documentation](https://github.com/QwenLM/Qwen3-TTS)
- [Azure Speech prerequisites](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech)
