package empirical

import "testing"

func TestSourceWritingMappingPositive(t *testing.T) {
	cases := [][4]string{{"R:VERB:SVA", "go", "goes", "grammar.verbs.subject_verb_agreement"}, {"R:NOUN:NUM", "book", "books", "grammar.nouns.number"}, {"M:DET", "", "a", "grammar.determiners.article_omission"}, {"U:DET", "the", "", "grammar.determiners.article_addition"}, {"R:DET", "an", "the", "grammar.determiners.article_choice"}, {"R:PREP", "on", "in", "grammar.prepositions_particles.preposition_choice"}, {"M:PREP", "", "to", "grammar.prepositions_particles.preposition_omission"}, {"U:PREP", "to", "", "grammar.prepositions_particles.preposition_addition"}, {"R:WO", "often go", "go often", "grammar.syntax.word_order"}}
	for _, c := range cases {
		leaf, rule := WritingMapping(c[0], c[1], c[2])
		if leaf != c[3] || rule == "not-resolved" {
			t.Fatal(c, leaf, rule)
		}
	}
}
func TestSourceWritingMappingNegative(t *testing.T) {
	for _, c := range [][3]string{{"M:DET", "", "this"}, {"U:DET", "some", ""}, {"R:DET", "this", "the"}, {"R:VERB:TENSE", "was", "has been"}, {"R:OTHER", "do", "make"}, {"R:SPELL", "freind", "friend"}} {
		leaf, rule := WritingMapping(c[0], c[1], c[2])
		if leaf != "" || rule != "not-resolved" {
			t.Fatal("Ambiguous source tag became a category", c, leaf)
		}
	}
}
func TestSourcePhoneMappingPositive(t *testing.T) {
	for _, c := range [][4]string{{"IH1", "IY0", "s", "vowel_substitution"}, {"TH", "S", "s", "consonant_substitution"}, {"T", "sil", "d", "consonant_omission"}, {"sil", "T", "a", "consonant_insertion"}, {"sil", "AH0", "a", "vowel_insertion_epenthesis"}} {
		leaf, _ := PhoneMapping(c[0], c[1], c[2], false)
		if leaf != "pronunciation.segmental."+c[3] {
			t.Fatal(c, leaf)
		}
	}
}
func TestSourcePhoneMappingNegative(t *testing.T) {
	for _, c := range [][3]string{{"IY", "sil", "d"}, {"TH", "err", "s"}, {"TH*", "S", "s"}, {"TH", "IY", "s"}, {"IH0", "IH1", "s"}, {"T", "T", "s"}, {"sil", "sil", "unchanged"}} {
		leaf, _ := PhoneMapping(c[0], c[1], c[2], false)
		if leaf != "" {
			t.Fatal("Unknown contrast or accent became a category", c, leaf)
		}
	}
	if leaf, _ := PhoneMapping("TH", "S", "s", true); leaf != "" {
		t.Fatal("Approximate contrast invented certainty")
	}
}
