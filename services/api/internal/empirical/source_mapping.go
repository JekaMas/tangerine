package empirical

import "strings"

// SourceMappingVersion names deliberately narrow derived rules. Native tags
// remain the evidence; a rule does not certify absence of a project category.
const SourceMappingVersion = "native-context-1"

func WritingMapping(label, before, after string) (leaf, rule string) {
	article := func(s string) bool {
		s = strings.ToLower(strings.TrimSpace(s))
		return s == "a" || s == "an" || s == "the"
	}
	switch label {
	case "R:VERB:SVA":
		return "grammar.verbs.subject_verb_agreement", "verb-agreement"
	case "R:NOUN:NUM":
		return "grammar.nouns.number", "noun-number"
	case "M:PREP":
		return "grammar.prepositions_particles.preposition_omission", "preposition-omission"
	case "U:PREP":
		return "grammar.prepositions_particles.preposition_addition", "preposition-addition"
	case "R:PREP":
		return "grammar.prepositions_particles.preposition_choice", "preposition-choice"
	case "R:WO":
		return "grammar.syntax.word_order", "word-order"
	case "M:DET":
		if article(after) {
			return "grammar.determiners.article_omission", "missing-article"
		}
	case "U:DET":
		if article(before) {
			return "grammar.determiners.article_addition", "unnecessary-article"
		}
	case "R:DET":
		if article(before) && article(after) {
			return "grammar.determiners.article_choice", "article-choice"
		}
	}
	return "", "not-resolved"
}

// CMU phone classes, not accent judgements or narrow acoustic measurements.
// Approximate/unknown labels are left to native counts rather than guessed.
func PhoneMapping(canonical, perceived, operation string, approximate bool) (leaf, rule string) {
	if approximate {
		return "", "not-resolved"
	}
	class := func(phone string) string {
		phone = strings.TrimRight(strings.ToUpper(phone), "012")
		for _, v := range strings.Fields("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW") {
			if v == phone {
				return "vowel"
			}
		}
		for _, v := range strings.Fields("B CH D DH F G HH JH K L M N NG P R S SH T TH V W Y Z ZH") {
			if v == phone {
				return "consonant"
			}
		}
		return ""
	}
	a, b := class(canonical), class(perceived)
	switch operation {
	case "s":
		if strings.TrimRight(strings.ToUpper(canonical), "012") == strings.TrimRight(strings.ToUpper(perceived), "012") {
			return "", "not-resolved"
		}
		if a != "" && a == b {
			return "pronunciation.segmental." + a + "_substitution", "same-class-phone-substitution"
		}
	case "d":
		if a == "consonant" && strings.EqualFold(perceived, "sil") {
			return "pronunciation.segmental.consonant_omission", "consonant-deletion"
		}
	case "a":
		if strings.EqualFold(canonical, "sil") && b == "consonant" {
			return "pronunciation.segmental.consonant_insertion", "consonant-addition"
		}
		if strings.EqualFold(canonical, "sil") && b == "vowel" {
			return "pronunciation.segmental.vowel_insertion_epenthesis", "vowel-addition"
		}
	}
	return "", "not-resolved"
}
