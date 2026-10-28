# Speech services and exact mutation capability

The starter uses local Kokoro, independent of ChatGPT or DeepSeek billing. For more accents, first try an ElevenLabs free account; optionally use its included subscription pool with overage disabled. Qwen3-TTS is an optional entirely local expressive alternative when the machine can run it. Azure Speech F0 is an optional free SSML route when precise pronunciation/prosody input is wanted. Do not purchase another LLM plan for speech. The research catalogue preserves OpenAI TTS as an optional metered adapter candidate, unavailable under the current included_only policy. ChatGPT consumer voice is not a speech-export API for Tangerine.

| Backend | Useful input/control | Accent use | Acoustic mutation limit | Current access |
|---|---|---|---|---|
| Kokoro82M | Literal text, preset speaker voice, pace preference, local timed pauses | Registered US/GB voices | Plain-text baseline lacks phone control; kokoro-phonemes-v1 adds vocabulary-scoped phone/lexical-stress input; fine pitch remains unsupported | Local model; no account or usage bill |
| Qwen3-TTS | VoiceDesign description; save synthetic reference; Base reuse per speaker | Described accent/style, not a verified L1 identity | Best effort; no documented arbitrary IPA guarantee | Local Apache model; selected CustomVoice0.6B Mac runtime observed below, other bindings unqualified |
| ElevenLabs | Voice ID, model ID, voice settings; pinned English IPA/CMU pronunciation dictionary | Select catalogue voice/accent metadata, optionally voice design | Phoneme tags require a supporting model; other models ignore them | Included Free/Starter pool; no top-up or usage billing |
| Azure standard neural | Existing typed SSML IPA/prosody/break compiler | Selected locale/voice, expanded available English locales only when configured | Exact sound still unobserved; don't assume HD voices support standard SSML | F0 neural allowance, currently500kcharacters/month; S0 excluded |
| OpenAI gpt-4o-mini-tts | Text plus natural-language accent/style instructions | Prompted accent/style | Not a guaranteed IPA compiler | Separate API usage billing; excluded now |
| eSpeak NG | Supported phonetic notation with explicit converter | Synthetic locale/voice variants | Robotic sound; IPA-to-engine binding must be specified/qualified | Optional local binary, separate GPL notices |

Preserve all122categories. Unsupported precise sound effects do not erase categories or change the requested family. Automatic selection chooses feasible instances for the backend; explicit unsupported targets retain the request and offer a compatible configured backend. Do not substitute a grammar error for a requested phone substitution. Ordinary generated audio can be used without a separate review/certification. Requested accent is context, not an error or a severity multiplier; allowed systematic varieties are accepted.

Text errors: synthesize the actual saved mutated surface text, including its nonstandard grammar/wording. Do not ask the speech service to fix grammar or regenerate dialogue. Phones: retain canonical/surface spelling when the mistake is acoustic-only and compile the unit's explicit phoneme operation through a supporting backend. Prosody: use supported scope-local stress/rate/pitch operations; local FFmpeg can insert the exact planned silence without asking a model. An instruction describing a mistake is synthesis intent, not proof it occurred. Save actual bytes, operations, provider request and warnings. A text-only grader never claims to have heard a phone contrast.

## Extension adapter contracts

All backends reuse speech-render-request/result, render-plan, audio asset/provenance and the existing private Python speech service. They normalize actual delivered audio to the declared final24kHz mono16-bit WAV and recompute real durations/turn offsets after conversion and pauses. Render each ordered speaker turn separately, join it using the saved plan, and keep one fixed voice binding per role. No live conversational service or separate public speech API is introduced.

ElevenLabs: server-side ELEVENLABS_API_KEY, GET `/v1/models` and the account voice listing, then select the model-specific transport. v4/v3 use POST `/v1/text-to-dialogue` with inputs text/voice_id and explicit model_id; older supported single-voice models use POST `/v1/text-to-speech/{voice_id}` with xi-api-key and text/model_id/voice_settings. The dialogue route uses its own supported settings, not the TTS voice_settings object. See [full development readiness](full-development-readiness.md) for exact segmentation and controls. Use mp3_44100_128 as the broadly available delivery preference and decode locally; do not assume premium PCM entitlement. Select eleven_v4 only when returned as available on its supported transport, otherwise explicitly select another supported model. There is no fallback after a render starts. Persist catalogue/voice metadata snapshots, requested locale/accent, exact model, request settings and per-turn receipts. Provider content retention cannot be disabled universally: enable_logging=false is an enterprise-only zero-retention option, not a free-tier guarantee.

For IPA, the typed compiler builds a case-sensitive English PLS pronunciation dictionary from the relevant scope's phoneme operations, creates it through the documented dictionary API and saves its dictionary/version locator. Use pronunciation_dictionary_locators on that turn. If an occurrence needs a different pronunciation from another occurrence of the same word, split synthesis at the target span and apply the locator only to that piece; retain target/segment coordinates, natural joins and actual audio interval. Do not silently apply one word rule to every occurrence. Freeze dictionary version/model and delete no retained evidence. Documented supporting models currently include eleven_v4, eleven_v3 and eleven_flash_v2; dictionary support is model-specific. Model headline sizes and endpoint limits are separate: the v4/v3 dialogue transport uses target-safe pieces with at most 2,000 total text characters for reliable requests. Older models use their actual frozen model/account request limit; flashv2 and flashv2.5 are distinct IDs. Split at actual utterance boundaries or recorded target-safe segments; unsupported segmentation fails that requested render without corrupting its key. Source: [pronunciation dictionaries](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/pronunciation-dictionaries), [speech API](https://elevenlabs.io/docs/api-reference/text-to-speech/convert), [models](https://elevenlabs.io/docs/overview/models).

Qwen local: explicitly select VoiceDesign1.7B to design each speaker from a versioned trusted voice description, save generated reference WAV/text, then create/save the Base clone-conditioning artifact and reuse it on that speaker's turns. Save each model/tokenizer/weight digest, runtime/device identity, actual conditioning inputs, seeds when supported and final outputs under existing native/MLflow evidence. These are owned synthetic references, not required corpus recordings. CustomVoice presets remain a separate explicit profile. No provider API key; heavy model assets are an optional setup, never required by the small default. No hardware latency or all-accent quality is asserted without runs. Source: [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), [model licence](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign).

Azure: existing endpoint/credentials/compiler stay unchanged. For included_only, resolve an actual Speech resource marked F0; a user-configured S0 key is unavailable to this route even if its budget is small. The actual resource/plan setting is visible in Settings. Never upgrade to S0. Report exact provider quota errors and retain partial completed turn assets. Source: [free-tier pricing](https://azure.microsoft.com/en-us/pricing/details/speech/), [phoneme SSML](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-pronunciation).

## Minimal provider setup and quotas

Kokoro: no new account; use the explicit model setup. ElevenLabs: create free account, obtain an API key and choose available voices/model. Free currently includes10kcredits/month; Creative Starter's regular price is$6/month for30kcredits, before tax. This is optional; no purchase is made here. Included credits are shared with other provider uses; model character costs differ. Account-specific API plan/remaining allowance and whether overage is disabled take precedence over dated marketing totals. Do not infer delivered minutes or guaranteed character allowance from credits. Free/Starter exhaustion is documented as waiting for the next cycle; paid plans that offer usage-based billing must keep it disabled. Source: [pricing](https://elevenlabs.io/pricing), [API access](https://help.elevenlabs.io/hc/en-us/articles/28184926326033-How-much-does-it-cost-to-use-the-API), [exhaustion behavior](https://help.elevenlabs.io/hc/en-us/articles/14668178389265-What-happens-when-I-run-out-of-credits).

Provider setup records the actual eligible route once; unavailable/unknown route affects that selected action only. No application-managed top-up, credit purchase or automatic provider fallback exists. Unknown allowance is displayed unknown; a fixed no-overage tier can still be used until the provider refuses. A tier permitting overage with unverified settings is unavailable under included_only. Other account activity can consume the same pool, so local estimates are not a claim of a remaining remote balance. Speech request accounting and Lab traces remain distinct from model quality/actual phone observations.

Configured extensions are typed by speech-profile.schema.json in configuration.speech_profiles. Freeze exact profile/model/voice catalogue, account tier/overage status, voice settings, model/tokenizer and per-voice generated reference/conditioning assets. Registry capability names retain render-plan semantics. Unused voice settings are null and omitted on wire; unsupported settings are never sent. Qwen voice-description assets are versioned trusted fragments under ai-development.md, with actual final instructions/conditioning captured through the speech owner. Resolve voice IDs/locale from the saved profile; raw provider labels do not establish observed accent. Original registry profiles retain their existing actual locked-asset contract. Profile IDs are unique across the combined registry and extensions; duplicates are a configuration conflict.

## Registration and generated-media terms

Local Kokoro, Qwen3-TTS and eSpeak NG need no provider account. For the recommended optional cloud extension, prepare ElevenLabs Free signup using the selected existing Google identity; select no paid plan, top-up or usage billing. Its signup button accepts legal terms, so the browser tool requires confirmation at that step. Registration and API-key creation are distinct; a key is not needed merely to inspect the account plan. Do not create duplicate accounts or credentials in anticipation of an unimplemented adapter. Azure F0 is an alternative, not an additional starter registration requirement. Optional Gemini/Claude/Platform accounts are not required by this setup. Actual status is in [registration audit](../../../audit/provider-registration-20261009/REPORT.md).

### Selected runtime and API observations, 2026-10-28

The approved isolated Mac Qwen runtime completed the same four-turn clean and
mutated CustomVoice0.6B pair:79.12s and63.52s. The explicit frozen selection is
MPS/float32 generation plus CPU audio codec. The ordinary Docker default stays
CPU; no device fallback or universal hardware/IPA claim follows from this finite
comparison. Actual model inputs, outputs, failed earlier candidates, loaded
placement and local Lab readback are retained in the completion follow-up audit.

The existing unbilled Gemini project displayed Free TTS limits of3requests/minute
and10/day, with0used in the selected one-day view before this follow-up. This is
a dated account observation, not a future quota reservation. Resuming the legacy
Flash-Lite request returned400 for `speech_config.mode=conversational`.
The current [Interactions API reference](https://ai.google.dev/api/interactions-api)
defines speaker configuration without that field, while the
[speech guide](https://ai.google.dev/gemini-api/docs/speech-generation) still
contains a conflicting REST example. Native failure is authoritative for this
selected operation; do not retry the unsupported field or silently rewrite its
saved plan.

A new explicitly versioned comparison omits `mode` in both complete requests,
keeping the same Flash-Lite model, Kore/Puck voices,20source turns and26target
directions. Two Free requests completed; finite recordings are207.12s/223.56s.
The default cadence is not the legacy conversational-mode control. Original
mode-present recordings, quota failure and new400remain separate. Normalization
uses the existing production audio owner, which rewrites streaming WAV headers
to finite RIFF without new inference. This is a standalone provider comparison;
it neither adds a production Gemini speech adapter nor proves every requested
phone, accent or intonation was realized. Actual current allowance, model/context,
saved playback and Lab observations remain scoped to these selected recordings.

ElevenLabs Free-generated speech has non-commercial use terms. Public sharing requires the provider attribution specified by its current terms (currently elevenlabs.io or 11.ai in the title). A later paid upgrade does not retroactively grant commercial rights to earlier Free audio. Keep the generation-time provider/plan and terms reference with existing audio provenance/export information; Apache-2.0 covers Tangerine software, not every third-party recording. Local playback needs no publication ceremony. Commercial audio use can select the local default; no purchase or automatic plan upgrade is required. Source: [provider publication terms](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform).

Current account readback superseding the prepared-signup receipt: [full readiness audit](../../../audit/full-development-readiness-20261009/REPORT.md). ElevenLabs Free registration completed with user approval; no key or synthesis was created. The Free creative page displayed 0/10,000 credits and API access; the API page displayed Free, Auto Top Up Off, and model-specific included allowance tables. These are dated account observations, not guaranteed future quota or observed API generation.

For complete acoustic production beyond ordinary Kokoro speech, see full-build-contract.md: scoped phoneme rendering plus declared native pitch/duration/pause/VOT transforms reuse the Python owner; actual observations stay separate. Qwen2.5-Omni local auditory diagnostics and optional Gemini free auditory transport are separate from Qwen3-TTS synthesis and ordinary ChatGPT text grading.
