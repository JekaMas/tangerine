package app

// This small catalogue is shared by simple preparation, metadata and the frozen
// composite profile. Selection is explicit; it never changes workspace defaults.
type localVoice struct {
	ID          string `json:"id"`
	Label       string `json:"label"`
	Accent      string `json:"accent"`
	AccentLabel string `json:"accent_label"`
	Locale      string `json:"locale"`
	Engine      string `json:"engine"`
	PreviewURL  string `json:"preview_url"`
}

const localAccentProfile = "local-english-accents-v1"

var localVoices = []localVoice{
	{"af_heart", "Heart", "american", "American English", "en-US", "Kokoro", "/previews/af_heart.wav"},
	{"am_adam", "Adam", "american", "American English", "en-US", "Kokoro", "/previews/am_adam.wav"},
	{"bf_emma", "Emma", "british", "British English", "en-GB", "Kokoro", "/previews/bf_emma.wav"},
	{"bm_george", "George", "british", "British English", "en-GB", "Kokoro", "/previews/bm_george.wav"},
	{"melo_en_au", "Australian voice", "australian", "Australian English", "en-AU", "MeloTTS", "/previews/melo_en_au.wav"},
	{"melo_en_in", "Indian voice", "indian", "Indian English", "en-IN", "MeloTTS", "/previews/melo_en_in.wav"},
}

func findLocalVoice(id string) (localVoice, bool) {
	for _, v := range localVoices {
		if v.ID == id {
			return v, true
		}
	}
	return localVoice{}, false
}

func localAccentSpeechProfile() map[string]any {
	voices := []any{}
	for _, v := range localVoices {
		voices = append(voices, map[string]any{"id": v.ID, "locale": v.Locale, "accent_description": v.AccentLabel})
	}
	return map[string]any{"id": localAccentProfile, "provider": "local_english_accents", "adapter_version": localAccentProfile, "model": "Kokoro-82M + MeloTTS-English", "endpoint": nil, "billing_mode": "local", "account_tier": nil, "overage_disabled": nil, "credential_refs": []any{}, "voices": voices, "capabilities": controlledCapabilities, "voice_settings": map[string]any{"speed": nil}}
}

func requestedLocalVoices(req map[string]any, n int) ([]any, bool, error) {
	choices, ok := req["speaker_voice_ids"].([]any)
	if !ok || len(choices) == 0 {
		return nil, false, nil
	}
	if len(choices) != n {
		return nil, false, ErrConflict
	}
	explicit := false
	for _, v := range choices {
		if v == nil {
			continue
		}
		if _, ok := findLocalVoice(v.(string)); !ok {
			return nil, false, ErrConflict
		}
		explicit = true
	}
	return choices, explicit, nil
}
