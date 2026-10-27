package app

import "strings"

// Decoder proposals retain their origin; no character-proportional timings.
func speechWords(native, request map[string]any) []speechWord {
	text := ""
	for _, v := range request["operations"].([]any) {
		op := v.(map[string]any)
		if s, ok := op["text"].(string); ok {
			text += s
		}
	}
	result := []speechWord{}
	cursor := 0
	decoders, _ := native["decoder"].([]any)
	for _, v := range decoders {
		d := v.(map[string]any)
		offset, _ := d["start_sample"].(float64)
		words, _ := d["word_tokens"].([]any)
		for _, v := range words {
			w := v.(map[string]any)
			word := w["text"].(string)
			at := strings.Index(text[cursor:], word)
			if at < 0 {
				continue
			}
			at += cursor
			end := at + len(word)
			result = append(result, speechWord{len([]rune(text[:at])), len([]rune(text[:end])), int(offset + w["start_sample"].(float64)), int(offset + w["end_sample"].(float64))})
			cursor = end
		}
	}
	return result
}
