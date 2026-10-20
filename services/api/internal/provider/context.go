package provider

import (
	"github.com/tiktoken-go/tokenizer"
)

// ContextCounter measures each new serialized request once. Known gpt-oss
// models use the ordinary o200k ranks shared with o200k_harmony. This counts
// serialized text, not opaque provider chat framing or observed usage tokens.
// Unknown model/tokenizer pairs retain the byte-conservative fallback.
// Codec instances are request-local; no vocabulary download occurs at runtime.
type ContextCounter struct {
	Tokenizer *string
	Method    string
	codec     tokenizer.Codec
}

func NewContextCounter(p Profile) (ContextCounter, error) {
	c := ContextCounter{Method: "conservative_utf8_bytes"}
	if p.Provider != "local_responses" || (p.Model != "gpt-oss:20b" && p.Model != "gpt-oss:120b") {
		return c, nil
	}
	codec, err := tokenizer.Get(tokenizer.O200kBase)
	if err != nil {
		return c, err
	}
	name := "o200k_base-ordinary@tiktoken-go/v0.8.1"
	c.Tokenizer, c.Method, c.codec = &name, "tokenizer", codec
	return c, nil
}

func (c ContextCounter) Count(wire []byte) (int, error) {
	if c.codec == nil {
		return len(wire), nil
	}
	// Ordinary text deliberately treats special-token spellings as user data.
	return c.codec.Count(string(wire))
}
