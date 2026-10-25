"""Literal positive/negative comparisons, not simulated hearing evidence."""
import copy
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/speech"))
from category_validation import blind_input, compare_probe, coverage, make_probe, saved_observation

FIXTURES = json.loads((ROOT / "audit/category-realization-20261025/FIXTURES.json").read_text())["fixtures"]
BINDING = {"backend": "constructed", "model": "none", "voice": "fixture", "locale": "en-US"}


def probe(fixture):
    return make_probe(fixture, {r: "correct.wav" if r == "misleading_metadata" else r + ".wav"
                                for r in ("clean", "mutated", "acceptable", "misleading_metadata")}, BINDING, 17)


def replies(value):
    # The oracle is declared literally from the test roles, not copied from
    # the probe's computed expected field or a candidate's mutation key.
    control = value["category_id"].startswith("acceptable_variant.")
    return {"receipt": {"inference_calls": 1}, "physical": {"status": "supported", "observations": [{"sample_count": 30000, "fixture": "constructed_logic_only"}]},
            "output": {"findings": [
                {"unit_id": r["unit_id"], "feature": "category_probe",
                 "status": "supported" if r["role"] == "mutated" and not control else "contradicted",
                 "reason": "Constructed parser/aggregation judgment; no actual hearing claim."}
                for r in value["withheld"]]}}


class CategoryComparisons(unittest.TestCase):
    def test_grammar_determiners_article_omission_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_omission'), 'complete_positive')(self)

    def test_grammar_determiners_article_omission_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_omission'), 'false_metadata_negative')(self)

    def test_grammar_determiners_article_omission_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_omission'), 'missing_audio_negative')(self)

    def test_grammar_determiners_article_omission_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_omission'), 'uncertain_negative')(self)

    def test_grammar_determiners_article_addition_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_addition'), 'complete_positive')(self)

    def test_grammar_determiners_article_addition_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_addition'), 'false_metadata_negative')(self)

    def test_grammar_determiners_article_addition_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_addition'), 'missing_audio_negative')(self)

    def test_grammar_determiners_article_addition_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_addition'), 'uncertain_negative')(self)

    def test_grammar_determiners_article_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_choice'), 'complete_positive')(self)

    def test_grammar_determiners_article_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_choice'), 'false_metadata_negative')(self)

    def test_grammar_determiners_article_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_choice'), 'missing_audio_negative')(self)

    def test_grammar_determiners_article_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.article_choice'), 'uncertain_negative')(self)

    def test_grammar_determiners_demonstrative_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.demonstrative_choice'), 'complete_positive')(self)

    def test_grammar_determiners_demonstrative_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.demonstrative_choice'), 'false_metadata_negative')(self)

    def test_grammar_determiners_demonstrative_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.demonstrative_choice'), 'missing_audio_negative')(self)

    def test_grammar_determiners_demonstrative_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.demonstrative_choice'), 'uncertain_negative')(self)

    def test_grammar_determiners_possessive_determiner_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.possessive_determiner'), 'complete_positive')(self)

    def test_grammar_determiners_possessive_determiner_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.possessive_determiner'), 'false_metadata_negative')(self)

    def test_grammar_determiners_possessive_determiner_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.possessive_determiner'), 'missing_audio_negative')(self)

    def test_grammar_determiners_possessive_determiner_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.possessive_determiner'), 'uncertain_negative')(self)

    def test_grammar_determiners_quantifier_determiner_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.quantifier_determiner'), 'complete_positive')(self)

    def test_grammar_determiners_quantifier_determiner_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.quantifier_determiner'), 'false_metadata_negative')(self)

    def test_grammar_determiners_quantifier_determiner_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.quantifier_determiner'), 'missing_audio_negative')(self)

    def test_grammar_determiners_quantifier_determiner_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.quantifier_determiner'), 'uncertain_negative')(self)

    def test_grammar_determiners_other_determiner_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.other_determiner'), 'complete_positive')(self)

    def test_grammar_determiners_other_determiner_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.other_determiner'), 'false_metadata_negative')(self)

    def test_grammar_determiners_other_determiner_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.other_determiner'), 'missing_audio_negative')(self)

    def test_grammar_determiners_other_determiner_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.determiners.other_determiner'), 'uncertain_negative')(self)

    def test_grammar_nouns_number_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.number'), 'complete_positive')(self)

    def test_grammar_nouns_number_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.number'), 'false_metadata_negative')(self)

    def test_grammar_nouns_number_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.number'), 'missing_audio_negative')(self)

    def test_grammar_nouns_number_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.number'), 'uncertain_negative')(self)

    def test_grammar_nouns_countability_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.countability'), 'complete_positive')(self)

    def test_grammar_nouns_countability_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.countability'), 'false_metadata_negative')(self)

    def test_grammar_nouns_countability_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.countability'), 'missing_audio_negative')(self)

    def test_grammar_nouns_countability_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.countability'), 'uncertain_negative')(self)

    def test_grammar_nouns_possessive_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.possessive'), 'complete_positive')(self)

    def test_grammar_nouns_possessive_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.possessive'), 'false_metadata_negative')(self)

    def test_grammar_nouns_possessive_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.possessive'), 'missing_audio_negative')(self)

    def test_grammar_nouns_possessive_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.possessive'), 'uncertain_negative')(self)

    def test_grammar_nouns_noun_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.noun_form'), 'complete_positive')(self)

    def test_grammar_nouns_noun_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.noun_form'), 'false_metadata_negative')(self)

    def test_grammar_nouns_noun_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.noun_form'), 'missing_audio_negative')(self)

    def test_grammar_nouns_noun_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.nouns.noun_form'), 'uncertain_negative')(self)

    def test_grammar_pronouns_subject_object_case_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.subject_object_case'), 'complete_positive')(self)

    def test_grammar_pronouns_subject_object_case_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.subject_object_case'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_subject_object_case_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.subject_object_case'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_subject_object_case_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.subject_object_case'), 'uncertain_negative')(self)

    def test_grammar_pronouns_reference_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reference'), 'complete_positive')(self)

    def test_grammar_pronouns_reference_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reference'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_reference_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reference'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_reference_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reference'), 'uncertain_negative')(self)

    def test_grammar_pronouns_agreement_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.agreement'), 'complete_positive')(self)

    def test_grammar_pronouns_agreement_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.agreement'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_agreement_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.agreement'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_agreement_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.agreement'), 'uncertain_negative')(self)

    def test_grammar_pronouns_reflexive_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reflexive'), 'complete_positive')(self)

    def test_grammar_pronouns_reflexive_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reflexive'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_reflexive_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reflexive'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_reflexive_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.reflexive'), 'uncertain_negative')(self)

    def test_grammar_pronouns_relative_pronoun_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.relative_pronoun'), 'complete_positive')(self)

    def test_grammar_pronouns_relative_pronoun_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.relative_pronoun'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_relative_pronoun_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.relative_pronoun'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_relative_pronoun_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.relative_pronoun'), 'uncertain_negative')(self)

    def test_grammar_pronouns_pronoun_omission_addition_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.pronoun_omission_addition'), 'complete_positive')(self)

    def test_grammar_pronouns_pronoun_omission_addition_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.pronoun_omission_addition'), 'false_metadata_negative')(self)

    def test_grammar_pronouns_pronoun_omission_addition_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.pronoun_omission_addition'), 'missing_audio_negative')(self)

    def test_grammar_pronouns_pronoun_omission_addition_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.pronouns.pronoun_omission_addition'), 'uncertain_negative')(self)

    def test_grammar_verbs_tense_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense'), 'complete_positive')(self)

    def test_grammar_verbs_tense_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense'), 'false_metadata_negative')(self)

    def test_grammar_verbs_tense_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense'), 'missing_audio_negative')(self)

    def test_grammar_verbs_tense_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense'), 'uncertain_negative')(self)

    def test_grammar_verbs_aspect_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.aspect'), 'complete_positive')(self)

    def test_grammar_verbs_aspect_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.aspect'), 'false_metadata_negative')(self)

    def test_grammar_verbs_aspect_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.aspect'), 'missing_audio_negative')(self)

    def test_grammar_verbs_aspect_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.aspect'), 'uncertain_negative')(self)

    def test_grammar_verbs_tense_aspect_combination_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense_aspect_combination'), 'complete_positive')(self)

    def test_grammar_verbs_tense_aspect_combination_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense_aspect_combination'), 'false_metadata_negative')(self)

    def test_grammar_verbs_tense_aspect_combination_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense_aspect_combination'), 'missing_audio_negative')(self)

    def test_grammar_verbs_tense_aspect_combination_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.tense_aspect_combination'), 'uncertain_negative')(self)

    def test_grammar_verbs_subject_verb_agreement_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.subject_verb_agreement'), 'complete_positive')(self)

    def test_grammar_verbs_subject_verb_agreement_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.subject_verb_agreement'), 'false_metadata_negative')(self)

    def test_grammar_verbs_subject_verb_agreement_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.subject_verb_agreement'), 'missing_audio_negative')(self)

    def test_grammar_verbs_subject_verb_agreement_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.subject_verb_agreement'), 'uncertain_negative')(self)

    def test_grammar_verbs_auxiliary_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.auxiliary'), 'complete_positive')(self)

    def test_grammar_verbs_auxiliary_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.auxiliary'), 'false_metadata_negative')(self)

    def test_grammar_verbs_auxiliary_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.auxiliary'), 'missing_audio_negative')(self)

    def test_grammar_verbs_auxiliary_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.auxiliary'), 'uncertain_negative')(self)

    def test_grammar_verbs_do_support_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.do_support'), 'complete_positive')(self)

    def test_grammar_verbs_do_support_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.do_support'), 'false_metadata_negative')(self)

    def test_grammar_verbs_do_support_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.do_support'), 'missing_audio_negative')(self)

    def test_grammar_verbs_do_support_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.do_support'), 'uncertain_negative')(self)

    def test_grammar_verbs_modal_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_choice'), 'complete_positive')(self)

    def test_grammar_verbs_modal_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_choice'), 'false_metadata_negative')(self)

    def test_grammar_verbs_modal_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_choice'), 'missing_audio_negative')(self)

    def test_grammar_verbs_modal_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_choice'), 'uncertain_negative')(self)

    def test_grammar_verbs_modal_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_form'), 'complete_positive')(self)

    def test_grammar_verbs_modal_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_form'), 'false_metadata_negative')(self)

    def test_grammar_verbs_modal_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_form'), 'missing_audio_negative')(self)

    def test_grammar_verbs_modal_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.modal_form'), 'uncertain_negative')(self)

    def test_grammar_verbs_infinitive_gerund_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.infinitive_gerund'), 'complete_positive')(self)

    def test_grammar_verbs_infinitive_gerund_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.infinitive_gerund'), 'false_metadata_negative')(self)

    def test_grammar_verbs_infinitive_gerund_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.infinitive_gerund'), 'missing_audio_negative')(self)

    def test_grammar_verbs_infinitive_gerund_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.infinitive_gerund'), 'uncertain_negative')(self)

    def test_grammar_verbs_participle_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.participle'), 'complete_positive')(self)

    def test_grammar_verbs_participle_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.participle'), 'false_metadata_negative')(self)

    def test_grammar_verbs_participle_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.participle'), 'missing_audio_negative')(self)

    def test_grammar_verbs_participle_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.participle'), 'uncertain_negative')(self)

    def test_grammar_verbs_finite_nonfinite_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.finite_nonfinite_form'), 'complete_positive')(self)

    def test_grammar_verbs_finite_nonfinite_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.finite_nonfinite_form'), 'false_metadata_negative')(self)

    def test_grammar_verbs_finite_nonfinite_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.finite_nonfinite_form'), 'missing_audio_negative')(self)

    def test_grammar_verbs_finite_nonfinite_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.finite_nonfinite_form'), 'uncertain_negative')(self)

    def test_grammar_verbs_passive_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.passive'), 'complete_positive')(self)

    def test_grammar_verbs_passive_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.passive'), 'false_metadata_negative')(self)

    def test_grammar_verbs_passive_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.passive'), 'missing_audio_negative')(self)

    def test_grammar_verbs_passive_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.passive'), 'uncertain_negative')(self)

    def test_grammar_verbs_causative_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.causative'), 'complete_positive')(self)

    def test_grammar_verbs_causative_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.causative'), 'false_metadata_negative')(self)

    def test_grammar_verbs_causative_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.causative'), 'missing_audio_negative')(self)

    def test_grammar_verbs_causative_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.causative'), 'uncertain_negative')(self)

    def test_grammar_verbs_irregular_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.irregular_form'), 'complete_positive')(self)

    def test_grammar_verbs_irregular_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.irregular_form'), 'false_metadata_negative')(self)

    def test_grammar_verbs_irregular_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.irregular_form'), 'missing_audio_negative')(self)

    def test_grammar_verbs_irregular_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.verbs.irregular_form'), 'uncertain_negative')(self)

    def test_grammar_prepositions_particles_preposition_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_choice'), 'complete_positive')(self)

    def test_grammar_prepositions_particles_preposition_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_choice'), 'false_metadata_negative')(self)

    def test_grammar_prepositions_particles_preposition_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_choice'), 'missing_audio_negative')(self)

    def test_grammar_prepositions_particles_preposition_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_choice'), 'uncertain_negative')(self)

    def test_grammar_prepositions_particles_preposition_omission_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_omission'), 'complete_positive')(self)

    def test_grammar_prepositions_particles_preposition_omission_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_omission'), 'false_metadata_negative')(self)

    def test_grammar_prepositions_particles_preposition_omission_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_omission'), 'missing_audio_negative')(self)

    def test_grammar_prepositions_particles_preposition_omission_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_omission'), 'uncertain_negative')(self)

    def test_grammar_prepositions_particles_preposition_addition_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_addition'), 'complete_positive')(self)

    def test_grammar_prepositions_particles_preposition_addition_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_addition'), 'false_metadata_negative')(self)

    def test_grammar_prepositions_particles_preposition_addition_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_addition'), 'missing_audio_negative')(self)

    def test_grammar_prepositions_particles_preposition_addition_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.preposition_addition'), 'uncertain_negative')(self)

    def test_grammar_prepositions_particles_particle_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.particle_choice'), 'complete_positive')(self)

    def test_grammar_prepositions_particles_particle_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.particle_choice'), 'false_metadata_negative')(self)

    def test_grammar_prepositions_particles_particle_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.particle_choice'), 'missing_audio_negative')(self)

    def test_grammar_prepositions_particles_particle_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.prepositions_particles.particle_choice'), 'uncertain_negative')(self)

    def test_grammar_syntax_word_order_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.word_order'), 'complete_positive')(self)

    def test_grammar_syntax_word_order_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.word_order'), 'false_metadata_negative')(self)

    def test_grammar_syntax_word_order_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.word_order'), 'missing_audio_negative')(self)

    def test_grammar_syntax_word_order_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.word_order'), 'uncertain_negative')(self)

    def test_grammar_syntax_question_formation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.question_formation'), 'complete_positive')(self)

    def test_grammar_syntax_question_formation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.question_formation'), 'false_metadata_negative')(self)

    def test_grammar_syntax_question_formation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.question_formation'), 'missing_audio_negative')(self)

    def test_grammar_syntax_question_formation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.question_formation'), 'uncertain_negative')(self)

    def test_grammar_syntax_negation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.negation'), 'complete_positive')(self)

    def test_grammar_syntax_negation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.negation'), 'false_metadata_negative')(self)

    def test_grammar_syntax_negation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.negation'), 'missing_audio_negative')(self)

    def test_grammar_syntax_negation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.negation'), 'uncertain_negative')(self)

    def test_grammar_syntax_subject_omission_addition_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subject_omission_addition'), 'complete_positive')(self)

    def test_grammar_syntax_subject_omission_addition_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subject_omission_addition'), 'false_metadata_negative')(self)

    def test_grammar_syntax_subject_omission_addition_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subject_omission_addition'), 'missing_audio_negative')(self)

    def test_grammar_syntax_subject_omission_addition_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subject_omission_addition'), 'uncertain_negative')(self)

    def test_grammar_syntax_expletive_subject_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.expletive_subject'), 'complete_positive')(self)

    def test_grammar_syntax_expletive_subject_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.expletive_subject'), 'false_metadata_negative')(self)

    def test_grammar_syntax_expletive_subject_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.expletive_subject'), 'missing_audio_negative')(self)

    def test_grammar_syntax_expletive_subject_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.expletive_subject'), 'uncertain_negative')(self)

    def test_grammar_syntax_complementation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.complementation'), 'complete_positive')(self)

    def test_grammar_syntax_complementation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.complementation'), 'false_metadata_negative')(self)

    def test_grammar_syntax_complementation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.complementation'), 'missing_audio_negative')(self)

    def test_grammar_syntax_complementation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.complementation'), 'uncertain_negative')(self)

    def test_grammar_syntax_clause_structure_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.clause_structure'), 'complete_positive')(self)

    def test_grammar_syntax_clause_structure_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.clause_structure'), 'false_metadata_negative')(self)

    def test_grammar_syntax_clause_structure_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.clause_structure'), 'missing_audio_negative')(self)

    def test_grammar_syntax_clause_structure_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.clause_structure'), 'uncertain_negative')(self)

    def test_grammar_syntax_relative_clause_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.relative_clause'), 'complete_positive')(self)

    def test_grammar_syntax_relative_clause_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.relative_clause'), 'false_metadata_negative')(self)

    def test_grammar_syntax_relative_clause_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.relative_clause'), 'missing_audio_negative')(self)

    def test_grammar_syntax_relative_clause_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.relative_clause'), 'uncertain_negative')(self)

    def test_grammar_syntax_conditional_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.conditional'), 'complete_positive')(self)

    def test_grammar_syntax_conditional_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.conditional'), 'false_metadata_negative')(self)

    def test_grammar_syntax_conditional_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.conditional'), 'missing_audio_negative')(self)

    def test_grammar_syntax_conditional_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.conditional'), 'uncertain_negative')(self)

    def test_grammar_syntax_comparison_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.comparison'), 'complete_positive')(self)

    def test_grammar_syntax_comparison_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.comparison'), 'false_metadata_negative')(self)

    def test_grammar_syntax_comparison_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.comparison'), 'missing_audio_negative')(self)

    def test_grammar_syntax_comparison_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.comparison'), 'uncertain_negative')(self)

    def test_grammar_syntax_coordination_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.coordination'), 'complete_positive')(self)

    def test_grammar_syntax_coordination_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.coordination'), 'false_metadata_negative')(self)

    def test_grammar_syntax_coordination_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.coordination'), 'missing_audio_negative')(self)

    def test_grammar_syntax_coordination_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.coordination'), 'uncertain_negative')(self)

    def test_grammar_syntax_subordination_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subordination'), 'complete_positive')(self)

    def test_grammar_syntax_subordination_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subordination'), 'false_metadata_negative')(self)

    def test_grammar_syntax_subordination_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subordination'), 'missing_audio_negative')(self)

    def test_grammar_syntax_subordination_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.subordination'), 'uncertain_negative')(self)

    def test_grammar_syntax_agreement_other_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.agreement_other'), 'complete_positive')(self)

    def test_grammar_syntax_agreement_other_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.agreement_other'), 'false_metadata_negative')(self)

    def test_grammar_syntax_agreement_other_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.agreement_other'), 'missing_audio_negative')(self)

    def test_grammar_syntax_agreement_other_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.syntax.agreement_other'), 'uncertain_negative')(self)

    def test_grammar_morphology_inflection_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.inflection'), 'complete_positive')(self)

    def test_grammar_morphology_inflection_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.inflection'), 'false_metadata_negative')(self)

    def test_grammar_morphology_inflection_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.inflection'), 'missing_audio_negative')(self)

    def test_grammar_morphology_inflection_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.inflection'), 'uncertain_negative')(self)

    def test_grammar_morphology_derivation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.derivation'), 'complete_positive')(self)

    def test_grammar_morphology_derivation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.derivation'), 'false_metadata_negative')(self)

    def test_grammar_morphology_derivation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.derivation'), 'missing_audio_negative')(self)

    def test_grammar_morphology_derivation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.derivation'), 'uncertain_negative')(self)

    def test_grammar_morphology_word_class_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.word_class_form'), 'complete_positive')(self)

    def test_grammar_morphology_word_class_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.word_class_form'), 'false_metadata_negative')(self)

    def test_grammar_morphology_word_class_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.word_class_form'), 'missing_audio_negative')(self)

    def test_grammar_morphology_word_class_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'grammar.morphology.word_class_form'), 'uncertain_negative')(self)

    def test_lexis_lexical_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_choice'), 'complete_positive')(self)

    def test_lexis_lexical_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_choice'), 'false_metadata_negative')(self)

    def test_lexis_lexical_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_choice'), 'missing_audio_negative')(self)

    def test_lexis_lexical_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_choice'), 'uncertain_negative')(self)

    def test_lexis_collocation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.collocation'), 'complete_positive')(self)

    def test_lexis_collocation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.collocation'), 'false_metadata_negative')(self)

    def test_lexis_collocation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.collocation'), 'missing_audio_negative')(self)

    def test_lexis_collocation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.collocation'), 'uncertain_negative')(self)

    def test_lexis_phraseology_idiom_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phraseology_idiom'), 'complete_positive')(self)

    def test_lexis_phraseology_idiom_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phraseology_idiom'), 'false_metadata_negative')(self)

    def test_lexis_phraseology_idiom_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phraseology_idiom'), 'missing_audio_negative')(self)

    def test_lexis_phraseology_idiom_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phraseology_idiom'), 'uncertain_negative')(self)

    def test_lexis_phrasal_verb_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phrasal_verb'), 'complete_positive')(self)

    def test_lexis_phrasal_verb_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phrasal_verb'), 'false_metadata_negative')(self)

    def test_lexis_phrasal_verb_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phrasal_verb'), 'missing_audio_negative')(self)

    def test_lexis_phrasal_verb_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.phrasal_verb'), 'uncertain_negative')(self)

    def test_lexis_word_formation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.word_formation'), 'complete_positive')(self)

    def test_lexis_word_formation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.word_formation'), 'false_metadata_negative')(self)

    def test_lexis_word_formation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.word_formation'), 'missing_audio_negative')(self)

    def test_lexis_word_formation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.word_formation'), 'uncertain_negative')(self)

    def test_lexis_false_friend_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.false_friend'), 'complete_positive')(self)

    def test_lexis_false_friend_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.false_friend'), 'false_metadata_negative')(self)

    def test_lexis_false_friend_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.false_friend'), 'missing_audio_negative')(self)

    def test_lexis_false_friend_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.false_friend'), 'uncertain_negative')(self)

    def test_lexis_semantic_precision_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.semantic_precision'), 'complete_positive')(self)

    def test_lexis_semantic_precision_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.semantic_precision'), 'false_metadata_negative')(self)

    def test_lexis_semantic_precision_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.semantic_precision'), 'missing_audio_negative')(self)

    def test_lexis_semantic_precision_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.semantic_precision'), 'uncertain_negative')(self)

    def test_lexis_selectional_restriction_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.selectional_restriction'), 'complete_positive')(self)

    def test_lexis_selectional_restriction_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.selectional_restriction'), 'false_metadata_negative')(self)

    def test_lexis_selectional_restriction_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.selectional_restriction'), 'missing_audio_negative')(self)

    def test_lexis_selectional_restriction_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.selectional_restriction'), 'uncertain_negative')(self)

    def test_lexis_redundancy_pleonasm_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.redundancy_pleonasm'), 'complete_positive')(self)

    def test_lexis_redundancy_pleonasm_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.redundancy_pleonasm'), 'false_metadata_negative')(self)

    def test_lexis_redundancy_pleonasm_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.redundancy_pleonasm'), 'missing_audio_negative')(self)

    def test_lexis_redundancy_pleonasm_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.redundancy_pleonasm'), 'uncertain_negative')(self)

    def test_lexis_lexical_register_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_register'), 'complete_positive')(self)

    def test_lexis_lexical_register_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_register'), 'false_metadata_negative')(self)

    def test_lexis_lexical_register_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_register'), 'missing_audio_negative')(self)

    def test_lexis_lexical_register_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'lexis.lexical_register'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_substitution_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_substitution'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_substitution_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_substitution'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_substitution_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_substitution'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_substitution_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_substitution'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_omission_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_omission'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_omission_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_omission'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_omission_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_omission'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_omission_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_omission'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_insertion_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_insertion'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_insertion_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_insertion'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_insertion_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_insertion'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_insertion_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_insertion'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_voicing_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_voicing'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_voicing_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_voicing'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_voicing_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_voicing'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_voicing_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_voicing'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_devoicing_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_devoicing'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_devoicing_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_devoicing'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_devoicing_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_devoicing'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_devoicing_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_devoicing'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_cluster_simplification_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_cluster_simplification'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_cluster_simplification_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_cluster_simplification'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_cluster_simplification_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_cluster_simplification'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_cluster_simplification_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_cluster_simplification'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_aspiration_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_aspiration'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_aspiration_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_aspiration'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_aspiration_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_aspiration'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_aspiration_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_aspiration'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_consonant_place_manner_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_place_manner'), 'complete_positive')(self)

    def test_pronunciation_segmental_consonant_place_manner_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_place_manner'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_consonant_place_manner_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_place_manner'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_consonant_place_manner_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.consonant_place_manner'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_vowel_substitution_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_substitution'), 'complete_positive')(self)

    def test_pronunciation_segmental_vowel_substitution_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_substitution'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_vowel_substitution_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_substitution'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_vowel_substitution_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_substitution'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_vowel_length_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_length'), 'complete_positive')(self)

    def test_pronunciation_segmental_vowel_length_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_length'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_vowel_length_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_length'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_vowel_length_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_length'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_vowel_reduction_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_reduction'), 'complete_positive')(self)

    def test_pronunciation_segmental_vowel_reduction_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_reduction'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_vowel_reduction_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_reduction'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_vowel_reduction_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_reduction'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_diphthong_realization_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.diphthong_realization'), 'complete_positive')(self)

    def test_pronunciation_segmental_diphthong_realization_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.diphthong_realization'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_diphthong_realization_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.diphthong_realization'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_diphthong_realization_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.diphthong_realization'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_vowel_insertion_epenthesis_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_insertion_epenthesis'), 'complete_positive')(self)

    def test_pronunciation_segmental_vowel_insertion_epenthesis_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_insertion_epenthesis'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_vowel_insertion_epenthesis_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_insertion_epenthesis'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_vowel_insertion_epenthesis_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.vowel_insertion_epenthesis'), 'uncertain_negative')(self)

    def test_pronunciation_segmental_final_segment_realization_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.final_segment_realization'), 'complete_positive')(self)

    def test_pronunciation_segmental_final_segment_realization_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.final_segment_realization'), 'false_metadata_negative')(self)

    def test_pronunciation_segmental_final_segment_realization_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.final_segment_realization'), 'missing_audio_negative')(self)

    def test_pronunciation_segmental_final_segment_realization_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.segmental.final_segment_realization'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_lexical_stress_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.lexical_stress'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_lexical_stress_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.lexical_stress'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_lexical_stress_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.lexical_stress'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_lexical_stress_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.lexical_stress'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_compound_stress_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.compound_stress'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_compound_stress_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.compound_stress'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_compound_stress_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.compound_stress'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_compound_stress_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.compound_stress'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_sentence_stress_prominence_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.sentence_stress_prominence'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_sentence_stress_prominence_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.sentence_stress_prominence'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_sentence_stress_prominence_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.sentence_stress_prominence'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_sentence_stress_prominence_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.sentence_stress_prominence'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_rhythm_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.rhythm'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_rhythm_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.rhythm'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_rhythm_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.rhythm'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_rhythm_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.rhythm'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_intonation_contour_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_contour'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_intonation_contour_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_contour'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_intonation_contour_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_contour'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_intonation_contour_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_contour'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_intonation_function_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_function'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_intonation_function_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_function'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_intonation_function_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_function'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_intonation_function_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.intonation_function'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_weak_form_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.weak_form'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_weak_form_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.weak_form'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_weak_form_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.weak_form'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_weak_form_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.weak_form'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_linking_resyllabification_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.linking_resyllabification'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_linking_resyllabification_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.linking_resyllabification'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_linking_resyllabification_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.linking_resyllabification'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_linking_resyllabification_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.linking_resyllabification'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_assimilation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.assimilation'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_assimilation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.assimilation'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_assimilation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.assimilation'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_assimilation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.assimilation'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_elision_reduction_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.elision_reduction'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_elision_reduction_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.elision_reduction'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_elision_reduction_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.elision_reduction'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_elision_reduction_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.elision_reduction'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_thought_group_chunking_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.thought_group_chunking'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_thought_group_chunking_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.thought_group_chunking'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_thought_group_chunking_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.thought_group_chunking'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_thought_group_chunking_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.thought_group_chunking'), 'uncertain_negative')(self)

    def test_pronunciation_suprasegmental_pitch_range_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.pitch_range'), 'complete_positive')(self)

    def test_pronunciation_suprasegmental_pitch_range_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.pitch_range'), 'false_metadata_negative')(self)

    def test_pronunciation_suprasegmental_pitch_range_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.pitch_range'), 'missing_audio_negative')(self)

    def test_pronunciation_suprasegmental_pitch_range_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pronunciation.suprasegmental.pitch_range'), 'uncertain_negative')(self)

    def test_fluency_speech_rate_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.speech_rate'), 'complete_positive')(self)

    def test_fluency_speech_rate_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.speech_rate'), 'false_metadata_negative')(self)

    def test_fluency_speech_rate_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.speech_rate'), 'missing_audio_negative')(self)

    def test_fluency_speech_rate_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.speech_rate'), 'uncertain_negative')(self)

    def test_fluency_excessive_pausing_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.excessive_pausing'), 'complete_positive')(self)

    def test_fluency_excessive_pausing_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.excessive_pausing'), 'false_metadata_negative')(self)

    def test_fluency_excessive_pausing_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.excessive_pausing'), 'missing_audio_negative')(self)

    def test_fluency_excessive_pausing_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.excessive_pausing'), 'uncertain_negative')(self)

    def test_fluency_pause_location_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.pause_location'), 'complete_positive')(self)

    def test_fluency_pause_location_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.pause_location'), 'false_metadata_negative')(self)

    def test_fluency_pause_location_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.pause_location'), 'missing_audio_negative')(self)

    def test_fluency_pause_location_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.pause_location'), 'uncertain_negative')(self)

    def test_fluency_hesitation_fillers_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.hesitation_fillers'), 'complete_positive')(self)

    def test_fluency_hesitation_fillers_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.hesitation_fillers'), 'false_metadata_negative')(self)

    def test_fluency_hesitation_fillers_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.hesitation_fillers'), 'missing_audio_negative')(self)

    def test_fluency_hesitation_fillers_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.hesitation_fillers'), 'uncertain_negative')(self)

    def test_fluency_repetition_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.repetition'), 'complete_positive')(self)

    def test_fluency_repetition_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.repetition'), 'false_metadata_negative')(self)

    def test_fluency_repetition_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.repetition'), 'missing_audio_negative')(self)

    def test_fluency_repetition_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.repetition'), 'uncertain_negative')(self)

    def test_fluency_false_start_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.false_start'), 'complete_positive')(self)

    def test_fluency_false_start_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.false_start'), 'false_metadata_negative')(self)

    def test_fluency_false_start_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.false_start'), 'missing_audio_negative')(self)

    def test_fluency_false_start_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.false_start'), 'uncertain_negative')(self)

    def test_fluency_self_repair_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.self_repair'), 'complete_positive')(self)

    def test_fluency_self_repair_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.self_repair'), 'false_metadata_negative')(self)

    def test_fluency_self_repair_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.self_repair'), 'missing_audio_negative')(self)

    def test_fluency_self_repair_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.self_repair'), 'uncertain_negative')(self)

    def test_fluency_breakdown_abandonment_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.breakdown_abandonment'), 'complete_positive')(self)

    def test_fluency_breakdown_abandonment_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.breakdown_abandonment'), 'false_metadata_negative')(self)

    def test_fluency_breakdown_abandonment_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.breakdown_abandonment'), 'missing_audio_negative')(self)

    def test_fluency_breakdown_abandonment_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.breakdown_abandonment'), 'uncertain_negative')(self)

    def test_fluency_disfluency_density_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.disfluency_density'), 'complete_positive')(self)

    def test_fluency_disfluency_density_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.disfluency_density'), 'false_metadata_negative')(self)

    def test_fluency_disfluency_density_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.disfluency_density'), 'missing_audio_negative')(self)

    def test_fluency_disfluency_density_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'fluency.disfluency_density'), 'uncertain_negative')(self)

    def test_discourse_cohesion_reference_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.cohesion_reference'), 'complete_positive')(self)

    def test_discourse_cohesion_reference_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.cohesion_reference'), 'false_metadata_negative')(self)

    def test_discourse_cohesion_reference_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.cohesion_reference'), 'missing_audio_negative')(self)

    def test_discourse_cohesion_reference_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.cohesion_reference'), 'uncertain_negative')(self)

    def test_discourse_connector_choice_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.connector_choice'), 'complete_positive')(self)

    def test_discourse_connector_choice_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.connector_choice'), 'false_metadata_negative')(self)

    def test_discourse_connector_choice_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.connector_choice'), 'missing_audio_negative')(self)

    def test_discourse_connector_choice_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.connector_choice'), 'uncertain_negative')(self)

    def test_discourse_logical_relation_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.logical_relation'), 'complete_positive')(self)

    def test_discourse_logical_relation_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.logical_relation'), 'false_metadata_negative')(self)

    def test_discourse_logical_relation_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.logical_relation'), 'missing_audio_negative')(self)

    def test_discourse_logical_relation_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.logical_relation'), 'uncertain_negative')(self)

    def test_discourse_sequencing_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.sequencing'), 'complete_positive')(self)

    def test_discourse_sequencing_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.sequencing'), 'false_metadata_negative')(self)

    def test_discourse_sequencing_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.sequencing'), 'missing_audio_negative')(self)

    def test_discourse_sequencing_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.sequencing'), 'uncertain_negative')(self)

    def test_discourse_coherence_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.coherence'), 'complete_positive')(self)

    def test_discourse_coherence_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.coherence'), 'false_metadata_negative')(self)

    def test_discourse_coherence_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.coherence'), 'missing_audio_negative')(self)

    def test_discourse_coherence_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.coherence'), 'uncertain_negative')(self)

    def test_discourse_topic_management_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.topic_management'), 'complete_positive')(self)

    def test_discourse_topic_management_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.topic_management'), 'false_metadata_negative')(self)

    def test_discourse_topic_management_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.topic_management'), 'missing_audio_negative')(self)

    def test_discourse_topic_management_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.topic_management'), 'uncertain_negative')(self)

    def test_discourse_turn_taking_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.turn_taking'), 'complete_positive')(self)

    def test_discourse_turn_taking_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.turn_taking'), 'false_metadata_negative')(self)

    def test_discourse_turn_taking_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.turn_taking'), 'missing_audio_negative')(self)

    def test_discourse_turn_taking_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.turn_taking'), 'uncertain_negative')(self)

    def test_discourse_response_relevance_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.response_relevance'), 'complete_positive')(self)

    def test_discourse_response_relevance_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.response_relevance'), 'false_metadata_negative')(self)

    def test_discourse_response_relevance_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.response_relevance'), 'missing_audio_negative')(self)

    def test_discourse_response_relevance_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.response_relevance'), 'uncertain_negative')(self)

    def test_discourse_information_structure_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.information_structure'), 'complete_positive')(self)

    def test_discourse_information_structure_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.information_structure'), 'false_metadata_negative')(self)

    def test_discourse_information_structure_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.information_structure'), 'missing_audio_negative')(self)

    def test_discourse_information_structure_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.information_structure'), 'uncertain_negative')(self)

    def test_discourse_clarification_repair_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.clarification_repair'), 'complete_positive')(self)

    def test_discourse_clarification_repair_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.clarification_repair'), 'false_metadata_negative')(self)

    def test_discourse_clarification_repair_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.clarification_repair'), 'missing_audio_negative')(self)

    def test_discourse_clarification_repair_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'discourse.clarification_repair'), 'uncertain_negative')(self)

    def test_pragmatics_register_formality_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.formality'), 'complete_positive')(self)

    def test_pragmatics_register_formality_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.formality'), 'false_metadata_negative')(self)

    def test_pragmatics_register_formality_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.formality'), 'missing_audio_negative')(self)

    def test_pragmatics_register_formality_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.formality'), 'uncertain_negative')(self)

    def test_pragmatics_register_politeness_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.politeness'), 'complete_positive')(self)

    def test_pragmatics_register_politeness_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.politeness'), 'false_metadata_negative')(self)

    def test_pragmatics_register_politeness_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.politeness'), 'missing_audio_negative')(self)

    def test_pragmatics_register_politeness_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.politeness'), 'uncertain_negative')(self)

    def test_pragmatics_register_directness_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.directness'), 'complete_positive')(self)

    def test_pragmatics_register_directness_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.directness'), 'false_metadata_negative')(self)

    def test_pragmatics_register_directness_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.directness'), 'missing_audio_negative')(self)

    def test_pragmatics_register_directness_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.directness'), 'uncertain_negative')(self)

    def test_pragmatics_register_speech_act_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.speech_act'), 'complete_positive')(self)

    def test_pragmatics_register_speech_act_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.speech_act'), 'false_metadata_negative')(self)

    def test_pragmatics_register_speech_act_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.speech_act'), 'missing_audio_negative')(self)

    def test_pragmatics_register_speech_act_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.speech_act'), 'uncertain_negative')(self)

    def test_pragmatics_register_sociolinguistic_appropriacy_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.sociolinguistic_appropriacy'), 'complete_positive')(self)

    def test_pragmatics_register_sociolinguistic_appropriacy_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.sociolinguistic_appropriacy'), 'false_metadata_negative')(self)

    def test_pragmatics_register_sociolinguistic_appropriacy_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.sociolinguistic_appropriacy'), 'missing_audio_negative')(self)

    def test_pragmatics_register_sociolinguistic_appropriacy_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.sociolinguistic_appropriacy'), 'uncertain_negative')(self)

    def test_pragmatics_register_audience_context_fit_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.audience_context_fit'), 'complete_positive')(self)

    def test_pragmatics_register_audience_context_fit_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.audience_context_fit'), 'false_metadata_negative')(self)

    def test_pragmatics_register_audience_context_fit_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.audience_context_fit'), 'missing_audio_negative')(self)

    def test_pragmatics_register_audience_context_fit_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.audience_context_fit'), 'uncertain_negative')(self)

    def test_pragmatics_register_pragmatic_force_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.pragmatic_force'), 'complete_positive')(self)

    def test_pragmatics_register_pragmatic_force_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.pragmatic_force'), 'false_metadata_negative')(self)

    def test_pragmatics_register_pragmatic_force_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.pragmatic_force'), 'missing_audio_negative')(self)

    def test_pragmatics_register_pragmatic_force_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.pragmatic_force'), 'uncertain_negative')(self)

    def test_pragmatics_register_naturalness_idiomaticity_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.naturalness_idiomaticity'), 'complete_positive')(self)

    def test_pragmatics_register_naturalness_idiomaticity_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.naturalness_idiomaticity'), 'false_metadata_negative')(self)

    def test_pragmatics_register_naturalness_idiomaticity_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.naturalness_idiomaticity'), 'missing_audio_negative')(self)

    def test_pragmatics_register_naturalness_idiomaticity_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'pragmatics_register.naturalness_idiomaticity'), 'uncertain_negative')(self)

    def test_acceptable_variant_grammar_variant_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.grammar_variant'), 'complete_positive')(self)

    def test_acceptable_variant_grammar_variant_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.grammar_variant'), 'false_metadata_negative')(self)

    def test_acceptable_variant_grammar_variant_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.grammar_variant'), 'missing_audio_negative')(self)

    def test_acceptable_variant_grammar_variant_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.grammar_variant'), 'uncertain_negative')(self)

    def test_acceptable_variant_lexical_variant_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.lexical_variant'), 'complete_positive')(self)

    def test_acceptable_variant_lexical_variant_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.lexical_variant'), 'false_metadata_negative')(self)

    def test_acceptable_variant_lexical_variant_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.lexical_variant'), 'missing_audio_negative')(self)

    def test_acceptable_variant_lexical_variant_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.lexical_variant'), 'uncertain_negative')(self)

    def test_acceptable_variant_pronunciation_variant_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.pronunciation_variant'), 'complete_positive')(self)

    def test_acceptable_variant_pronunciation_variant_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.pronunciation_variant'), 'false_metadata_negative')(self)

    def test_acceptable_variant_pronunciation_variant_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.pronunciation_variant'), 'missing_audio_negative')(self)

    def test_acceptable_variant_pronunciation_variant_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.pronunciation_variant'), 'uncertain_negative')(self)

    def test_acceptable_variant_dialect_variant_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.dialect_variant'), 'complete_positive')(self)

    def test_acceptable_variant_dialect_variant_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.dialect_variant'), 'false_metadata_negative')(self)

    def test_acceptable_variant_dialect_variant_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.dialect_variant'), 'missing_audio_negative')(self)

    def test_acceptable_variant_dialect_variant_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.dialect_variant'), 'uncertain_negative')(self)

    def test_acceptable_variant_register_variant_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.register_variant'), 'complete_positive')(self)

    def test_acceptable_variant_register_variant_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.register_variant'), 'false_metadata_negative')(self)

    def test_acceptable_variant_register_variant_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.register_variant'), 'missing_audio_negative')(self)

    def test_acceptable_variant_register_variant_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.register_variant'), 'uncertain_negative')(self)

    def test_acceptable_variant_informal_acceptable_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.informal_acceptable'), 'complete_positive')(self)

    def test_acceptable_variant_informal_acceptable_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.informal_acceptable'), 'false_metadata_negative')(self)

    def test_acceptable_variant_informal_acceptable_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.informal_acceptable'), 'missing_audio_negative')(self)

    def test_acceptable_variant_informal_acceptable_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.informal_acceptable'), 'uncertain_negative')(self)

    def test_acceptable_variant_stylistic_preference_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.stylistic_preference'), 'complete_positive')(self)

    def test_acceptable_variant_stylistic_preference_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.stylistic_preference'), 'false_metadata_negative')(self)

    def test_acceptable_variant_stylistic_preference_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.stylistic_preference'), 'missing_audio_negative')(self)

    def test_acceptable_variant_stylistic_preference_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.stylistic_preference'), 'uncertain_negative')(self)

    def test_acceptable_variant_alternative_standard_complete_positive(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.alternative_standard'), 'complete_positive')(self)

    def test_acceptable_variant_alternative_standard_false_metadata_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.alternative_standard'), 'false_metadata_negative')(self)

    def test_acceptable_variant_alternative_standard_missing_audio_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.alternative_standard'), 'missing_audio_negative')(self)

    def test_acceptable_variant_alternative_standard_uncertain_negative(self):
        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == 'acceptable_variant.alternative_standard'), 'uncertain_negative')(self)

def category_case(fixture, kind):
    def check(self):
        value = probe(fixture)
        response = replies(value)
        if kind == "complete_positive":
            result = compare_probe(value, response)
            self.assertEqual(result["audio_confirmation"], "confirmed")
            self.assertEqual(result["false_alarms"], 0)
            self.assertEqual([r["outcome"] for r in result["cases"]], ["passed"] * 4)
        elif kind == "false_metadata_negative":
            row = next(r for r in value["withheld"] if r["role"] == "misleading_metadata")
            next(r for r in response["output"]["findings"] if r["unit_id"] == row["unit_id"])["status"] = "supported"
            result = compare_probe(value, response)
            self.assertEqual(result["audio_confirmation"], "uncertain")
            self.assertEqual(result["false_alarms"], 1)
            self.assertFalse(result["controls_passed"])
        elif kind == "missing_audio_negative":
            result = compare_probe(value, None)
            self.assertEqual(result["audio_confirmation"], "not_run")
            self.assertEqual([r["outcome"] for r in result["cases"]], ["not_run"] * 4)
        elif kind == "uncertain_negative":
            response["output"]["findings"][0]["status"] = "uncertain"
            self.assertEqual(compare_probe(value, response)["audio_confirmation"], "uncertain")
    return check



class CategoryValidation(unittest.TestCase):
    def test_inventory_positive(self):
        self.assertEqual(len(FIXTURES), 122)
        self.assertEqual(sum(r["control"] for r in FIXTURES), 8)
        self.assertEqual(len({r["taxonomy_id"] for r in FIXTURES}), 122)

    def test_unselected_binding_negative(self):
        rows = coverage(FIXTURES, {}, {})
        self.assertEqual(rows["category_count"], 122)
        self.assertEqual(rows["confirmed"], 0)
        self.assertEqual(len(rows["unconfirmed"]), 122)

    def test_blind_projection_positive(self):
        value = probe(FIXTURES[0])
        actual = blind_input(value)
        self.assertEqual(set(actual), {"task", "clips"})
        self.assertEqual([r["unit_id"] for r in actual["clips"]], ["clip-1", "clip-2", "clip-3", "clip-4"])
        self.assertEqual(set(actual["clips"][0]), {"unit_id", "public_context", "question"})

    def test_private_claims_cannot_change_input_negative(self):
        value = probe(FIXTURES[0]); other = copy.deepcopy(value)
        other.update(category_id="wrong", answer="CORRECT", intended_ipa="LEAK", mutation_key={"all": "wrong"})
        for r in other["withheld"]:
            r.update(expected="supported", claimed_mutation=True, audio_path="wrong.wav")
        self.assertEqual(blind_input(value), blind_input(other))

    def test_order_is_explicit_positive(self):
        value = make_probe(FIXTURES[0], {r: r + ".wav" for r in ("clean", "mutated", "acceptable", "misleading_metadata")}, BINDING, 17)
        self.assertEqual([r["role"] for r in value["withheld"]], ["clean", "acceptable", "mutated", "misleading_metadata"])

    def test_conflicting_findings_negative(self):
        value = probe(FIXTURES[0]); result = replies(value)
        contrary = dict(result["output"]["findings"][0], status="supported")
        result["output"]["findings"].append(contrary)
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "uncertain")

    def test_unheard_mutation_negative(self):
        value = probe(FIXTURES[0]); result = replies(value)
        for r in result["output"]["findings"]: r["status"] = "contradicted"
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "not_realized")

    def test_physical_observation_positive(self):
        value = probe(next(r for r in FIXTURES if r["taxonomy_id"].endswith("rhythm")))
        result = replies(value)
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "confirmed")

    def test_intention_is_not_measurement_negative(self):
        value = probe(next(r for r in FIXTURES if r["taxonomy_id"].endswith("rhythm")))
        result = replies(value); result.pop("physical")
        result["requested_parameters"] = {"duration_ratio": 1.5}
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "uncertain")

    def test_status_without_measurement_negative(self):
        value = probe(next(r for r in FIXTURES if r["taxonomy_id"].endswith("rhythm")))
        result = replies(value); result["physical"] = {"status": "supported"}
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "uncertain")

    def test_measured_change_with_deaf_judge_negative(self):
        value = probe(next(r for r in FIXTURES if r["taxonomy_id"].endswith("rhythm")))
        result = replies(value)
        for row in result["output"]["findings"]: row["status"] = "contradicted"
        compared = compare_probe(value, result)
        self.assertEqual(compared["audio_confirmation"], "uncertain")
        self.assertTrue(compared["physical_auditory_conflict"])
        self.assertEqual(compared["physical"], result["physical"])

    def test_persist_once_positive(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "saved.json"
            self.assertEqual(saved_observation(path, lambda: calls.append(1) or {"actual": 17}), {"actual": 17})
            self.assertEqual(saved_observation(path, lambda: self.fail("A read must not dispatch")), {"actual": 17})
            self.assertEqual(calls, [1])

    def test_missing_is_not_cached_pass_negative(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(saved_observation(Path(d) / "not-run.json"))

    def test_saved_request_is_not_overwritten_positive(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("category_probe_runner", ROOT / "audit/category-realization-20261025/run.py")
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            (directory / "request.json").write_text('{"frozen": "original"}')
            (directory / "response.json").write_text('{"actual": 17}')
            self.assertEqual(runner.worker({"different": "new request"}, directory), {"actual": 17})
            self.assertEqual(json.loads((directory / "request.json").read_text()), {"frozen": "original"})

    def test_interrupted_request_not_redispatched_negative(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("category_probe_interrupted", ROOT / "audit/category-realization-20261025/run.py")
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d); (directory / "request.json").write_text('{"frozen":"already initiated"}')
            self.assertEqual(runner.worker({"new": "request"}, directory)["error"], "INTERRUPTED_OBSERVATION")
            self.assertFalse((directory / "response.json").exists())

    def test_alternate_report_keeps_default_evidence_negative(self):
        import contextlib
        import importlib.util
        import io
        spec = importlib.util.spec_from_file_location("category_probe_alternate", ROOT / "audit/category-realization-20261025/run.py")
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        target = ROOT / "audit/category-realization-20261025/COVERAGE.json"
        before = target.read_bytes()
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            runner.OUT = Path(d); runner.report(FIXTURES)
            self.assertEqual(json.loads((Path(d) / "coverage.json").read_text())["confirmed"], 0)
        self.assertEqual(target.read_bytes(), before)

    def test_missing_acoustic_plan_negative(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("category_acoustic_unknown", ROOT / "audit/category-realization-20261025/generate_acoustic.py")
        generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(generator.generate_case("unregistered", Path(d), lambda *args: self.fail("No native dispatch for an absent plan"), ROOT))

    def test_native_auditory_clip_labels_positive(self):
        from diagnostic_models import auditory_conversation
        result = auditory_conversation("probe", "context", ["one.wav", "two.wav"], blind=True)
        labels = [r["text"] for r in result[1]["content"] if r["type"] == "text"]
        self.assertEqual(labels, ["context", "clip-1", "clip-2", "probe"])

    def test_ordinary_diagnostic_unchanged_positive(self):
        from diagnostic_models import auditory_conversation
        result = auditory_conversation("ordinary", "context", ["one.wav", "two.wav"])
        labels = [r["text"] for r in result[1]["content"] if r["type"] == "text"]
        self.assertEqual(labels, ["context", "Target audio", "Reference audio", "ordinary"])

    def test_gemini_wire_blind_positive(self):
        import os
        from diagnostic_models import auditory
        value = probe(FIXTURES[0]); value["task"] = "blind_category_probe"
        value["mutation_key"] = {"answer": "PRIVATE_EXPECTATION"}
        calls = []
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self):
                return json.dumps({"status": "completed", "steps": [{"type": "model_output", "content": [{"type": "text", "text": '{"findings":[]}'}]}]}).encode()
        class Opener:
            def open(self, request, timeout):
                calls.append(json.loads(request.data)); return Response()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fixture-secret"}), patch("urllib.request.build_opener", return_value=Opener()):
            result = auditory({"provider": "gemini_interactions", "model": "fixture", "billing_mode": "free_tier", "max_output_tokens": 512}, "managed-probe", value, [b"first-wave", b"second-wave"])
        self.assertEqual(len(calls), 1)
        parts = calls[0]["input"]
        self.assertEqual(json.loads(parts[0]["text"]), blind_input(value))
        self.assertEqual([p["text"] for p in parts[1:] if p["type"] == "text"], ["clip-1", "clip-2"])
        self.assertEqual([base64.b64decode(p["data"]) for p in parts if p["type"] == "audio"], [b"first-wave", b"second-wave"])
        self.assertNotIn("PRIVATE_EXPECTATION", json.dumps(calls))
        self.assertNotIn("fixture-secret", json.dumps(result))

    def test_native_blind_dispatch_positive(self):
        import math
        import struct
        from audio import wav_bytes
        import diagnostic_runtime
        raw = wav_bytes(b"".join(struct.pack("<h", int(6000 * math.sin(2 * math.pi * 180 * i / 24000))) for i in range(24000)))
        value = blind_input(probe(FIXTURES[0]))
        packet = dict(method_id="gemini-audio-v1", audio_base64=base64.b64encode(raw).decode(),
                      additional_audio_base64=[base64.b64encode(raw).decode()] * 3, input=value,
                      profile={"model": "fixture"}, prompt="managed-probe")
        with patch.object(diagnostic_runtime, "auditory", return_value={"output": {"findings": []}}) as boundary:
            result = diagnostic_runtime.execute(packet)
        self.assertEqual(boundary.call_count, 1)
        self.assertEqual(boundary.call_args.args[3], [raw] * 4)
        self.assertEqual(result["receipt"]["inference_calls"], 1)
        self.assertNotIn("measurements", result)

    def test_missing_requested_finding_negative(self):
        value = probe(FIXTURES[0]); result = replies(value)
        result["output"]["findings"] = []
        self.assertEqual(compare_probe(value, result)["audio_confirmation"], "uncertain")

    def test_actual_clips_wrapper_positive(self):
        from diagnostic_models import decode_findings
        row = dict(unit_id="clip-1", feature="category_probe", status="contradicted", reason="The actual model hears I bought a pen.")
        self.assertEqual(decode_findings(json.dumps({"clips": [row]}))["findings"][0]["status"], "contradicted")

    def test_wrong_clips_wrapper_negative(self):
        from diagnostic_models import decode_findings
        with self.assertRaisesRegex(ValueError, "DIAGNOSTIC_OUTPUT_INVALID"):
            decode_findings('{"clips":"not a finding list"}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
