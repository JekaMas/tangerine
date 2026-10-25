# Choosing speaker accents and voices

Ordinary preparation offers Automatic and four explicit English accent groups:
American (Kokoro Heart/Adam), British (Kokoro Emma/George), Australian (MeloTTS
EN-AU/speaker3) and Indian (MeloTTS EN_INDIA/speaker2). The latter two are named
trained voices, not representations of every regional or individual variety.
Each role selects its own accent/voice; mixed accents keep their identity across
turns. The current catalogue is included in GET /api/v1/preparation-options.

The optional exercise_request.speaker_voice_ids list is ordered by active role.
Empty/absent/all-null preserves configured defaults. Otherwise it has exactly
speaker_count entries, each a registered local voice or null for the existing
local default. Active roles alone are submitted; reducing/growing the UI count
retains previous choices. Explicit advanced speakers override simple choices;
explicit conflicting service/profile selection uses existing conflict admission.
Selecting a named local voice explicitly selects local-english-accents-v1 for
that exercise; workspace provider settings are never changed. Expansion projects
all existing full speaker fields and persists them through the same saved
blueprint/checkpoint/render/key path. No new persistence layer or repeated audit.

The local composite routes US/UK to existing Kokoro, AU/IN to pinned
myshell-ai/MeloTTS-English. Text target_locale remains independent: a speaker's
en-AU/en-IN locale comes from its voice, without expanding the existing written
variety contract or treating the accent itself as an injected mistake.

Install assets explicitly with:

    sh scripts/tangerine model-setup local-english-accents-v1

This acquires Kokoro if needed and the approximately650MB Melo English/BERT
assets plus pinned upstream VITS runtime sources and CMU pronunciation data.
No provider account/key/payment is required. Startup and inference never download
assets; absent assets return MODEL_SETUP_REQUIRED, retaining completed work.
Accepted manifests/data are trusted in memory or storage. Fixed actual generated
preview WAVs ship with the UI and replay without synthesis or provider calls.

Melo uses the upstream VITS model and BERT conditioning with an English-only
CMU/espeak frontend, English language ID2 and tone offset7. Controlled IPA inputs
are projected to its model phones/tones, including stress. Actual decoder
attention supplies proposed phone/word intervals, normalized to24kHz; it is not
an auditory verifier. Complete reference/mutated clips retain the same trained
speaker embedding. Existing native acoustic operations, stored source/interval
correspondence and local Lab capture retain their responsibilities. Unsupported
phones/voices fail explicitly without falling back or erasing a requested edit.

Primary sources: https://github.com/myshell-ai/MeloTTS and
https://huggingface.co/myshell-ai/MeloTTS-English. Code/model/BERT revisions,
actual input/output and development limits are retained in the accent audit.
