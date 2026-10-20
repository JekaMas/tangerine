package app

import (
	"fmt"
	"regexp"
	"strings"
	"testing"
)

// Independent controlled English reference for the explicitly requested test
// vocabulary. This is a test oracle, never a production grammar rule or corpus.
func agreementFixtureCanonical(text string) error {
	for _, word := range []string{"opens", "serves"} {
		if len(regexp.MustCompile(`\b`+word+`\b`).FindAllStringIndex(text, -1)) != 1 {
			return fmt.Errorf("clean fixture requires exactly one correct %s: %s", word, text)
		}
	}
	return nil
}
func agreementFixtureMutation(canonical, surface string) (string, error) {
	if err := agreementFixtureCanonical(canonical); err != nil {
		return "", err
	}
	for _, correct := range []string{"opens", "serves"} {
		at := regexp.MustCompile(`\b` + correct + `\b`).FindStringIndex(canonical)
		wrong := strings.TrimSuffix(correct, "s")
		expected := canonical[:at[0]] + wrong + canonical[at[1]:]
		if surface == expected {
			return correct, nil
		}
	}
	return "", fmt.Errorf("surface is not exactly one requested singular-agreement error; canonical=%s surface=%s", canonical, surface)
}
func agreementFixtureCorrection(expected, kind, text string) bool {
	if kind == "insert" && strings.TrimSpace(text) == "s" {
		return true
	}
	return kind == "replace" && regexp.MustCompile(`\b`+expected+`\b`).MatchString(text) && !regexp.MustCompile(`\b`+strings.TrimSuffix(expected, "s")+`\b`).MatchString(text)
}

func TestMutationQualityOpensPositive(t *testing.T) {
	c := "The café opens at seven and serves fresh coffee."
	if correct, err := agreementFixtureMutation(c, "The café open at seven and serves fresh coffee."); err != nil || correct != "opens" {
		t.Fatal(correct, err)
	}
}
func TestMutationQualityServesPositive(t *testing.T) {
	c := "The café opens at seven and serves fresh coffee."
	if correct, err := agreementFixtureMutation(c, "The café opens at seven and serve fresh coffee."); err != nil || correct != "serves" {
		t.Fatal(correct, err)
	}
}
func TestMutationQualityReverseNegative(t *testing.T) {
	if agreementFixtureCorrection("serves", "replace", "serve") {
		t.Fatal("wrong preferred correction passed")
	}
	if _, err := agreementFixtureMutation("The café opens every morning and serve fresh coffee.", "The café opens every morning and serves fresh coffee."); err == nil {
		t.Fatal("the observed reverse mutation falsely passed")
	}
}
func TestMutationQualityExtraChangeNegative(t *testing.T) {
	c := "The café opens at seven and serves fresh coffee."
	if _, err := agreementFixtureMutation(c, "The café open at eight and serves fresh coffee."); err == nil {
		t.Fatal("unrelated content change passed the controlled fixture")
	}
}
