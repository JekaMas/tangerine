"""NO_TEST_DOUBLE: exact arithmetic inputs, never teacher-answer fixtures."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("metrics", ROOT / "services/speech/metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
REGISTRY = metrics.load_core_registry(ROOT / "domain/metrics.v1.yaml")

# Independent arithmetic expectations, explicitly not semantic scoring cases.
VECTORS = {
    "detection.precision": ({"TP": 3, "FP": 1}, Fraction(3, 4)),
    "detection.recall": ({"TP": 3, "G": 5}, Fraction(3, 5)),
    "detection.f1": ({"TP": 3, "FP": 1, "FN": 2}, Fraction(2, 3)),
    "detection.miss_rate": ({"FN": 2, "G": 5}, Fraction(2, 5)),
    "detection.false_discovery_rate": ({"TP": 3, "FP": 1}, Fraction(1, 4)),
    "classification.coverage": ({"LC": 2, "TP": 3}, Fraction(2, 3)),
    "classification.family_accuracy": ({"LF": 1, "LC": 2}, Fraction(1, 2)),
    "classification.exact_accuracy": ({"LE": 1, "LC": 2}, Fraction(1, 2)),
    "classification.hierarchical_accuracy": ({"H": Fraction(3, 2), "LC": 2}, Fraction(3, 4)),
    "classification.hierarchical_recall": ({"H": Fraction(3, 2), "G": 5}, Fraction(3, 10)),
    "correction.attempt_rate": ({"CA": 2, "TC": 3}, Fraction(2, 3)),
    "correction.strict_accuracy": ({"CK": 1, "CA": 2}, Fraction(1, 2)),
    "correction.graded_accuracy": ({"CQ": Fraction(3, 2), "CA": 2}, Fraction(3, 4)),
    "correction.strict_recall": ({"CK": 1, "GC": 5}, Fraction(1, 5)),
    "correction.graded_recall": ({"CQ": Fraction(3, 2), "GC": 5}, Fraction(3, 10)),
    "correction.assertion_precision": ({"CK": 1, "CA": 2, "FC": 1}, Fraction(1, 3)),
    "explanation.coverage": ({"EA": 2, "TE": 3}, Fraction(2, 3)),
    "explanation.strict_accuracy": ({"EK": 1, "EA": 2}, Fraction(1, 2)),
    "explanation.graded_accuracy": ({"EQ": Fraction(3, 2), "EA": 2}, Fraction(3, 4)),
    "explanation.graded_recall": ({"EQ": Fraction(3, 2), "GE": 5}, Fraction(3, 10)),
    "decoy.overcorrection_rate": ({"DF": 1, "D": 4}, Fraction(1, 4)),
    "decoy.unflagged_rate": ({"DF": 1, "D": 4}, Fraction(3, 4)),
    "decoy.explicit_acceptability_accuracy": ({"DA": 3, "DF": 1}, Fraction(3, 4)),
    "acceptability.explicit_accuracy": ({"SA": 3, "SN": 4}, Fraction(3, 4)),
    "weighted.precision": ({"WTP": 6, "WFP": 1}, Fraction(6, 7)),
    "weighted.recall": ({"WTP": 6, "WFN": 4}, Fraction(3, 5)),
    "weighted.f1": ({"WTP": 6, "WFP": 1, "WFN": 4}, Fraction(12, 17)),
}


class MetricsTests(unittest.TestCase):
    def test_registry_ids_match_all_independent_vectors(self):
        self.assertEqual(set(REGISTRY), set(VECTORS))

    def test_half_up_display(self):
        self.assertEqual(metrics.ratio(1, 16, "no_assertions")["percent"], "6.3")
        self.assertEqual(metrics.ratio(0, 5, "no_assertions")["percent"], "0.0")

    def test_invalid_ratios(self):
        for n, d in [(-1, 1), (1, -1), (2, 1), (1, 0)]:
            with self.assertRaises(ValueError):
                metrics.ratio(n, d, "no_assertions")

    def test_unresolved_has_no_final_metrics(self):
        self.assertEqual(metrics.evaluate_all(REGISTRY, {}, zero_reasons={}, unresolved=True),
                         {"status": "needs_review", "metrics": None})

    def test_no_executable_expressions(self):
        for formula in ["__import__('os')/1", "TP**2/G", "TP", "TP/G+1"]:
            with self.assertRaises(ValueError):
                metrics.evaluate(formula, {"TP": 1, "G": 2}, zero_reason="no_opportunities")


    def test_detection_precision_positive(self):
        counters, expected = VECTORS["detection.precision"]
        result = metrics.evaluate(REGISTRY["detection.precision"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_detection_precision_negative(self):
        counters, _ = VECTORS["detection.precision"]
        zero = metrics.evaluate(REGISTRY["detection.precision"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["detection.precision"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_detection_recall_positive(self):
        counters, expected = VECTORS["detection.recall"]
        result = metrics.evaluate(REGISTRY["detection.recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_detection_recall_negative(self):
        counters, _ = VECTORS["detection.recall"]
        zero = metrics.evaluate(REGISTRY["detection.recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["detection.recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_detection_f1_positive(self):
        counters, expected = VECTORS["detection.f1"]
        result = metrics.evaluate(REGISTRY["detection.f1"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_detection_f1_negative(self):
        counters, _ = VECTORS["detection.f1"]
        zero = metrics.evaluate(REGISTRY["detection.f1"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["detection.f1"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_detection_miss_rate_positive(self):
        counters, expected = VECTORS["detection.miss_rate"]
        result = metrics.evaluate(REGISTRY["detection.miss_rate"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_detection_miss_rate_negative(self):
        counters, _ = VECTORS["detection.miss_rate"]
        zero = metrics.evaluate(REGISTRY["detection.miss_rate"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["detection.miss_rate"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_detection_false_discovery_rate_positive(self):
        counters, expected = VECTORS["detection.false_discovery_rate"]
        result = metrics.evaluate(REGISTRY["detection.false_discovery_rate"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_detection_false_discovery_rate_negative(self):
        counters, _ = VECTORS["detection.false_discovery_rate"]
        zero = metrics.evaluate(REGISTRY["detection.false_discovery_rate"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["detection.false_discovery_rate"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_classification_coverage_positive(self):
        counters, expected = VECTORS["classification.coverage"]
        result = metrics.evaluate(REGISTRY["classification.coverage"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_classification_coverage_negative(self):
        counters, _ = VECTORS["classification.coverage"]
        zero = metrics.evaluate(REGISTRY["classification.coverage"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["classification.coverage"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_classification_family_accuracy_positive(self):
        counters, expected = VECTORS["classification.family_accuracy"]
        result = metrics.evaluate(REGISTRY["classification.family_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_classification_family_accuracy_negative(self):
        counters, _ = VECTORS["classification.family_accuracy"]
        zero = metrics.evaluate(REGISTRY["classification.family_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["classification.family_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_classification_exact_accuracy_positive(self):
        counters, expected = VECTORS["classification.exact_accuracy"]
        result = metrics.evaluate(REGISTRY["classification.exact_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_classification_exact_accuracy_negative(self):
        counters, _ = VECTORS["classification.exact_accuracy"]
        zero = metrics.evaluate(REGISTRY["classification.exact_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["classification.exact_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_classification_hierarchical_accuracy_positive(self):
        counters, expected = VECTORS["classification.hierarchical_accuracy"]
        result = metrics.evaluate(REGISTRY["classification.hierarchical_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_classification_hierarchical_accuracy_negative(self):
        counters, _ = VECTORS["classification.hierarchical_accuracy"]
        zero = metrics.evaluate(REGISTRY["classification.hierarchical_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["classification.hierarchical_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_classification_hierarchical_recall_positive(self):
        counters, expected = VECTORS["classification.hierarchical_recall"]
        result = metrics.evaluate(REGISTRY["classification.hierarchical_recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_classification_hierarchical_recall_negative(self):
        counters, _ = VECTORS["classification.hierarchical_recall"]
        zero = metrics.evaluate(REGISTRY["classification.hierarchical_recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["classification.hierarchical_recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_attempt_rate_positive(self):
        counters, expected = VECTORS["correction.attempt_rate"]
        result = metrics.evaluate(REGISTRY["correction.attempt_rate"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_attempt_rate_negative(self):
        counters, _ = VECTORS["correction.attempt_rate"]
        zero = metrics.evaluate(REGISTRY["correction.attempt_rate"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.attempt_rate"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_strict_accuracy_positive(self):
        counters, expected = VECTORS["correction.strict_accuracy"]
        result = metrics.evaluate(REGISTRY["correction.strict_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_strict_accuracy_negative(self):
        counters, _ = VECTORS["correction.strict_accuracy"]
        zero = metrics.evaluate(REGISTRY["correction.strict_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.strict_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_graded_accuracy_positive(self):
        counters, expected = VECTORS["correction.graded_accuracy"]
        result = metrics.evaluate(REGISTRY["correction.graded_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_graded_accuracy_negative(self):
        counters, _ = VECTORS["correction.graded_accuracy"]
        zero = metrics.evaluate(REGISTRY["correction.graded_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.graded_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_strict_recall_positive(self):
        counters, expected = VECTORS["correction.strict_recall"]
        result = metrics.evaluate(REGISTRY["correction.strict_recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_strict_recall_negative(self):
        counters, _ = VECTORS["correction.strict_recall"]
        zero = metrics.evaluate(REGISTRY["correction.strict_recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.strict_recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_graded_recall_positive(self):
        counters, expected = VECTORS["correction.graded_recall"]
        result = metrics.evaluate(REGISTRY["correction.graded_recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_graded_recall_negative(self):
        counters, _ = VECTORS["correction.graded_recall"]
        zero = metrics.evaluate(REGISTRY["correction.graded_recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.graded_recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_correction_assertion_precision_positive(self):
        counters, expected = VECTORS["correction.assertion_precision"]
        result = metrics.evaluate(REGISTRY["correction.assertion_precision"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_correction_assertion_precision_negative(self):
        counters, _ = VECTORS["correction.assertion_precision"]
        zero = metrics.evaluate(REGISTRY["correction.assertion_precision"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["correction.assertion_precision"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_explanation_coverage_positive(self):
        counters, expected = VECTORS["explanation.coverage"]
        result = metrics.evaluate(REGISTRY["explanation.coverage"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_explanation_coverage_negative(self):
        counters, _ = VECTORS["explanation.coverage"]
        zero = metrics.evaluate(REGISTRY["explanation.coverage"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["explanation.coverage"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_explanation_strict_accuracy_positive(self):
        counters, expected = VECTORS["explanation.strict_accuracy"]
        result = metrics.evaluate(REGISTRY["explanation.strict_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_explanation_strict_accuracy_negative(self):
        counters, _ = VECTORS["explanation.strict_accuracy"]
        zero = metrics.evaluate(REGISTRY["explanation.strict_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["explanation.strict_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_explanation_graded_accuracy_positive(self):
        counters, expected = VECTORS["explanation.graded_accuracy"]
        result = metrics.evaluate(REGISTRY["explanation.graded_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_explanation_graded_accuracy_negative(self):
        counters, _ = VECTORS["explanation.graded_accuracy"]
        zero = metrics.evaluate(REGISTRY["explanation.graded_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["explanation.graded_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_explanation_graded_recall_positive(self):
        counters, expected = VECTORS["explanation.graded_recall"]
        result = metrics.evaluate(REGISTRY["explanation.graded_recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_explanation_graded_recall_negative(self):
        counters, _ = VECTORS["explanation.graded_recall"]
        zero = metrics.evaluate(REGISTRY["explanation.graded_recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["explanation.graded_recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_decoy_overcorrection_rate_positive(self):
        counters, expected = VECTORS["decoy.overcorrection_rate"]
        result = metrics.evaluate(REGISTRY["decoy.overcorrection_rate"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_decoy_overcorrection_rate_negative(self):
        counters, _ = VECTORS["decoy.overcorrection_rate"]
        zero = metrics.evaluate(REGISTRY["decoy.overcorrection_rate"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["decoy.overcorrection_rate"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_decoy_unflagged_rate_positive(self):
        counters, expected = VECTORS["decoy.unflagged_rate"]
        result = metrics.evaluate(REGISTRY["decoy.unflagged_rate"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_decoy_unflagged_rate_negative(self):
        counters, _ = VECTORS["decoy.unflagged_rate"]
        zero = metrics.evaluate(REGISTRY["decoy.unflagged_rate"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["decoy.unflagged_rate"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_decoy_explicit_acceptability_accuracy_positive(self):
        counters, expected = VECTORS["decoy.explicit_acceptability_accuracy"]
        result = metrics.evaluate(REGISTRY["decoy.explicit_acceptability_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_decoy_explicit_acceptability_accuracy_negative(self):
        counters, _ = VECTORS["decoy.explicit_acceptability_accuracy"]
        zero = metrics.evaluate(REGISTRY["decoy.explicit_acceptability_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["decoy.explicit_acceptability_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_acceptability_explicit_accuracy_positive(self):
        counters, expected = VECTORS["acceptability.explicit_accuracy"]
        result = metrics.evaluate(REGISTRY["acceptability.explicit_accuracy"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_acceptability_explicit_accuracy_negative(self):
        counters, _ = VECTORS["acceptability.explicit_accuracy"]
        zero = metrics.evaluate(REGISTRY["acceptability.explicit_accuracy"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["acceptability.explicit_accuracy"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_weighted_precision_positive(self):
        counters, expected = VECTORS["weighted.precision"]
        result = metrics.evaluate(REGISTRY["weighted.precision"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_weighted_precision_negative(self):
        counters, _ = VECTORS["weighted.precision"]
        zero = metrics.evaluate(REGISTRY["weighted.precision"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["weighted.precision"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_weighted_recall_positive(self):
        counters, expected = VECTORS["weighted.recall"]
        result = metrics.evaluate(REGISTRY["weighted.recall"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_weighted_recall_negative(self):
        counters, _ = VECTORS["weighted.recall"]
        zero = metrics.evaluate(REGISTRY["weighted.recall"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["weighted.recall"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

    def test_weighted_f1_positive(self):
        counters, expected = VECTORS["weighted.f1"]
        result = metrics.evaluate(REGISTRY["weighted.f1"], counters, zero_reason="no_opportunities")
        self.assertEqual(Fraction(result["value"]), expected)
        self.assertEqual(result["status"], "available")

    def test_weighted_f1_negative(self):
        counters, _ = VECTORS["weighted.f1"]
        zero = metrics.evaluate(REGISTRY["weighted.f1"], dict.fromkeys(counters, 0), zero_reason="no_opportunities")
        self.assertIsNone(zero["value"])
        self.assertEqual(zero["status"], "not_applicable")
        self.assertEqual(zero["reason"], "no_opportunities")
        for invalid in [-1, 1.0, True]:
            with self.assertRaises(ValueError):
                metrics.evaluate(REGISTRY["weighted.f1"], dict.fromkeys(counters, invalid), zero_reason="no_opportunities")

if __name__ == "__main__":
    unittest.main()
