# Which services to use and what each one does

Start with **your existing ChatGPT Pro account for text and answer checking, plus local Kokoro for speech**. This covers the ordinary listening-exercise flow with one LLM connection and one local speech backend. No additional paid subscription or corpus download is needed.

This guide describes the specified product setup. Tangerine's revised launcher, ChatGPT connection and complete exercise flow are not implemented yet. The historical foundation instructions in the repository README are separate; this guide does not claim that future Settings actions already work.

## Services in the ordinary flow

| Step | Who does the work | What the service receives and returns |
|---|---|---|
| Enter a request | Tangerine's local browser UI | Topic, speaker count and approximate word length; optional English level and broad mistake categories. |
| Generate clean dialogue | Configured LLM; start with ChatGPT Pro | Request and saved generation settings -> clean text with speaker turns. Tangerine stores the result. |
| Generate mistakes | The configured LLM | Clean text and selected category/recipe definitions -> changed text or acoustic instructions, mutation locations, explanations and valid corrections. Tangerine applies the returned edits and saves the mutation list/key. |
| Generate audio | Speech backend; start with local Kokoro | Saved mutated speaker turns and voice settings -> audio files. Tangerine stores and assembles the final recording with its actual intervals. |
| Listen and answer | Local browser UI | Play the stored audio; the listener writes the mistakes they heard and proposed corrections in free text. An explanation is optional. |
| Check the answer | The configured LLM | Original text, mutated text, mutation key and listener answer -> semantic matches, correction judgments, findings/misses and comments. If an explanation was supplied, assess it separately and give feedback. |
| Calculate scores and show practice advice | Tangerine's native scorer, then configured LLM feedback | Native code calculates the exact specified scores from the judgments. The LLM explains findings/misses and recommends practice. Omitted explanations carry no penalty. |

ChatGPT-plan access handles text processing. It is not the speech-export backend. Accent generation is a speech capability; an accent alone is not a mistake. Acoustic-only mistakes need a backend that supports the requested pronunciation or prosody control.

## What to connect or install

| Service | Needed for | Account or credentials | Selection |
|---|---|---|---|
| **ChatGPT Pro through official ChatGPT-plan sign-in** | Clean text, mutations, answer checking, comments and recommendations; also selected Lab experiments | Use the existing account and Tangerine's own OAuth sign-in. No Platform API key for this route. Check actual plan-use eligibility/model availability and disable purchased-credit use after limits for Tangerine. | Recommended starting LLM. |
| **Kokoro82M locally** | Stored speech with American/British voices and multiple speaker turns | No account or API key. Explicitly download the configured local model/voice assets through model setup. | Recommended starting speech backend. The baseline is plain text; the specified controlled adapter adds vocabulary-scoped phone/lexical-stress input. Fine pitch remains unsupported locally. |
| **ElevenLabs Free** | Optional wider voice/accent choice and supported English pronunciation dictionaries | Free account; server-side ELEVENLABS_API_KEY when configuring the adapter. Inspect actual available models, voices and included allowance. | First optional cloud speech extension. No top-up or usage billing. Free media has non-commercial terms and attribution requirements when published. |
| **Azure Speech F0** | Optional standard SSML pronunciation, stress/prosody and pauses | Microsoft/Azure account with an actual F0 Speech resource, AZURE_SPEECH_KEY and AZURE_SPEECH_REGION/endpoint. | Alternative for controlled acoustic mutations. S0 is separately billed and excluded by the current policy. |
| **Qwen3-TTS locally** | Optional described accents/styles and reusable synthetic speaker voices | No provider account or API key; explicit local model setup and sufficient hardware. | Richer local speech alternative. Hardware performance and exact acoustic realization require observation. |
| **DeepSeek** | Alternative LLM for the same text stages | Existing profile and server-side DEEPSEEK_API_KEY. The key's presence does not prove an included API allowance. | Keep the existing fast profile. Official token billing is excluded under the current policy unless a documented eligible non-purchased allowance is established. |
| **Ollama locally** | Optional local LLM for the same text stages | No cloud account; configured local runner and downloaded local model. | Local alternative if the machine supports it. Quality/latency remain to be measured. |

Choose one configured LLM and one speech backend for a new exercise. Freeze those settings with the preparation. Changing a selection affects new work; it does not silently replace a provider in a saved checkpoint or running request. If limits are reached, retain completed text/key/audio/answers and retry after reset or explicitly select another eligible backend.

Claude included API allowance and Gemini's free API tier are researched LLM alternatives, not additional signup requirements. Separately billed OpenAI Platform text/speech/transcription is also preserved as a configurable route for other installations; it is excluded by this operator's current spending policy. Full candidate details and primary sources are in [provider access](provider-access.md), [speech selection](speech-service-selection.md) and [service catalogue](../domain/service-research.v1.json).

## Local components supplied by the project

| Component | What it does | What the user needs to arrange |
|---|---|---|
| Docker/Compose | Runs the local application and its dependencies | A supported Docker installation and running daemon, as described in [local delivery](local-delivery.md). |
| Next.js browser UI | Request entry, playback, answers, settings and results | Open the local URL after startup. No Tangerine account or public hosting setup. |
| Go application service | Coordinates requests, saved checkpoints, provider connections and exact scoring | The launcher manages it; no separate service account or host Go installation. |
| PostgreSQL | Stores requests, texts, mutation keys, attempts, settings and results | The launcher creates the private local instance; no database signup. |
| MinIO | Stores audio and retained artifacts | The launcher creates the private local instance; no cloud storage account. |
| Python speech service and FFmpeg | Runs local synthesis or speech adapters, assembles/converts recordings and records intervals | Included in the local application build; select and set up the speech model or service. No separate Python/FFmpeg host setup. |
| MLflow Lab | Prompt/context versions, traces, quality comparisons and debugging during AI development | Local optional Lab for ordinary users; required evidence tooling for future AI-affecting development. No cloud MLflow account. |

Database/media/internal service credentials are generated and kept privately by the future launcher. Provider keys are supplied only for the selected dependent adapters; OAuth credentials are obtained through the provider connection. Neither goes into browser-visible configuration, Git, prompts or Lab exports.

## Starter sequence

When the specified launcher and provider adapter are implemented:

1. Download the GitHub source ZIP or clone, ensure Docker is running, and follow the launcher setup in [local delivery](local-delivery.md). Supply keys only for selected key-based adapters; ChatGPT-plan sign-in uses OAuth instead.
2. Start Tangerine and open the local UI. In Settings choose **Continue with ChatGPT** and authorize Tangerine using the existing Pro account. Choose a model actually returned for that connection.
3. In [ChatGPT Usage settings](https://chatgpt.com/settings/usage), select Tangerine and disable purchased-credit use after plan limits. Automatic reload off alone is insufficient. Record the external-setting confirmation once.
4. Select **local Kokoro** and perform the explicit model setup. The specified helper action is `sh scripts/tangerine model-setup`; ordinary startup performs no model download or inference.
5. Enter a topic, speaker count and word length. Generate the clean text, mutations and audio on demand; listen, answer and receive LLM comments plus exact scores.
6. Add ElevenLabs Free, Azure F0 or Qwen only when a requested voice/acoustic capability needs it. Keep the local default available; no silent switch or paid upgrade occurs.

Current setup observations are in the [full readiness audit](../../../audit/full-development-readiness-20261009/REPORT.md): existing Pro verified; Tangerine OAuth not performed because its adapter is unimplemented; ElevenLabs Free registration completed, with actual Free allowance read back. Account creation does not establish synthesis or answer-checking quality.

## Optional data and diagnostics

No corpus is generated or downloaded before an ordinary exercise. The configured LLM creates the clean text and mutations from the user's request; the speech backend creates the audio. Tangerine saves those records for listening, checking and replay.

All original corpus/import features remain available as optional authentic examples, enrichment and source-scoped reports. Complete releases are needed only when selecting their full imports/completeness reports. Real frequency/relationship estimates need annotated populations and denominators; observed difficulty needs genuine attempts. Those data do not replace the LLM-generated mutation key.

ASR/transcription and pronunciation assessment support optional acoustic diagnostics or disputes; they are not required for the ordinary free-text answer comparison. Configure a separately supported local/free/included route only when selecting such measurements. ChatGPT-plan sign-in does not grant transcription/audio-input API access, and a metered key is not silently used. Selected Lab evaluation fixtures and full benchmarks are development/evaluation work, not startup exercise pregeneration. See [exact data needs](empirical-data-needs.md).

The complete feature/service/data acceptance map, controlled speech and diagnostic contracts are in [full development readiness](full-development-readiness.md). A starter setup does not by itself qualify every optional feature or all acoustic targets. Full product scope is retained; development iterations may repair implementations, not defer product features.
