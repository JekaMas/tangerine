"""Direct exact-ratio boundary checks, independent of expression parsing."""
from fractions import Fraction
import unittest
import test_metrics as arithmetic


class RatioBoundaryTests(unittest.TestCase):
    def test_exact_fraction_positive(self):
        result = arithmetic.metrics.ratio(Fraction(1, 2), Fraction(3, 2), 'no_assertions')
        self.assertEqual(result['value'], '1/3')

    def test_inexact_types_negative(self):
        for numerator, denominator in [(1.0, 2), (1, 2.0), (True, 2), (1, True)]:
            with self.assertRaises(ValueError):
                arithmetic.metrics.ratio(numerator, denominator, 'no_assertions')
