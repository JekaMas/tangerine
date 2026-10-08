"""Actual running image inspection, with a real wrong-architecture rejection."""
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from assert_runtime_architecture import inspect


@unittest.skipUnless(os.environ.get('TANGERINE_CHECK_ARCH'), 'Select the actual runtime architecture')
class ArchitectureTests(unittest.TestCase):
    def test_architecture_positive(self):
        expected = os.environ['TANGERINE_CHECK_ARCH']
        rows = inspect(os.environ['TANGERINE_CHECK_PROJECT'], expected)
        self.assertEqual(len(rows), 5)
        self.assertEqual({row['architecture'] for row in rows}, {expected})

    def test_architecture_negative(self):
        other = 'amd64' if os.environ['TANGERINE_CHECK_ARCH'] == 'arm64' else 'arm64'
        with self.assertRaisesRegex(ValueError, 'architecture mismatch'):
            inspect(os.environ['TANGERINE_CHECK_PROJECT'], other)


if __name__ == '__main__':
    unittest.main()
