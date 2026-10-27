"""Execute historical literal arithmetic through its existing production owner.

This is registry arithmetic, not semantic grading, an empirical population or a
hosted provider observation. Expected fractions come from the original authored
fixture collection, never from metrics.evaluate or a model.
"""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("historical_metrics", ROOT / "services/speech/metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
FIXTURES = json.loads((ROOT / "specification/v2/domain/verification-fixtures.v1.json").read_text())
BINDINGS = {row["case_id"]: row for row in FIXTURES["case_bindings"]}
REGISTRY = metrics.load_core_registry(ROOT / "domain/metrics.v1.yaml")


class HistoricalLiterals(unittest.TestCase):
    def test_core_set2_positive(self):
        rows = [BINDINGS[f"MET-{n:02d}.P1.SET2.POSITIVE"] for n in range(1, 28)]
        self.assertEqual(27, len(rows))
        for row in rows:
            with self.subTest(case=row["case_id"]):
                supplied = copy.deepcopy(row["input"])
                before = copy.deepcopy(supplied)
                counters = {key: Fraction(str(value)) for key, value in supplied["stats"].items()}
                result = metrics.evaluate(REGISTRY[supplied["metric"]], counters,
                                          zero_reason="no_opportunities")
                self.assertEqual(Fraction(row["expected"]["exact"]), Fraction(result["value"]))
                self.assertEqual("available", result["status"])
                self.assertEqual(before, supplied)

    def test_core_set2_negative(self):
        rows = [BINDINGS[f"MET-{n:02d}.P1.SET2.NEGATIVE"] for n in range(1, 28)]
        self.assertEqual(27, len(rows))
        for row in rows:
            with self.subTest(case=row["case_id"]):
                supplied = copy.deepcopy(row["input"])
                before = copy.deepcopy(supplied)
                counters = {key: Fraction(str(value)) for key, value in supplied["stats"].items()}
                result = metrics.evaluate(REGISTRY[supplied["metric"]], counters,
                                          zero_reason="no_opportunities")
                self.assertEqual(Fraction(row["expected"]["exact"]), Fraction(result["value"]))
                self.assertNotEqual(Fraction(supplied["proposed_result"]), Fraction(result["value"]))
                self.assertFalse(row["expected"]["proposed_result_accepted"])
                self.assertTrue(row["expected"]["original_inputs_retained"])
                self.assertEqual(before, supplied)

    def test_ratio_positive(self):
        for case in ["DOM-05.P1.POSITIVE", "DOM-05.P1.SET2.POSITIVE",
                     "DOM-05.P2.SET2.POSITIVE"]:
            row = BINDINGS[case]
            with self.subTest(case=case):
                value = row["input"]
                result = metrics.ratio(Fraction(value["numerator"]),
                                       Fraction(value["denominator"]), "no_assertions")
                self.assertEqual(row["expected"]["exact"],
                                 {key: result[key] for key in ["numerator", "denominator"]})
                self.assertEqual(row["expected"]["percent"], result["percent"])

    def test_ratio_invalid_negative(self):
        value = BINDINGS["DOM-05.P1.NEGATIVE"]["input"]
        for numerator, denominator in [(value["numerator"], 3), (1, value["denominator"]),
                                       (value["numerator"], value["denominator"])]:
            with self.subTest(numerator=numerator, denominator=denominator):
                with self.assertRaises(ValueError):
                    metrics.ratio(numerator, denominator, "no_assertions")

    def test_ratio_historical_inconsistent_vector_negative(self):
        # This observes an existing fixture disagreement; it does not turn the
        # original 1/0 -> N/A plan into an executed passing behavior.
        row = BINDINGS["DOM-05.P2.SET2.NEGATIVE"]
        self.assertEqual({"numerator": "1", "denominator": "0"}, row["input"])
        self.assertEqual("not_applicable", row["expected"]["status"])
        with self.assertRaises(ValueError):
            metrics.ratio(Fraction(1), Fraction(0), "no_assertions")


if __name__ == "__main__":
    unittest.main()
