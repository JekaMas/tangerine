"""Actual failure of the configured local speech dependency, no fake transport."""
import os
from pathlib import Path
import subprocess
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker', 'compose', '--env-file', str(ROOT / 'deploy/local/.env'),
           '-f', str(ROOT / 'deploy/local/compose.yaml')]


@unittest.skipUnless(os.environ.get('TANGERINE_ALLOW_DEPENDENCY_STOP') == '1', 'Actual dependency stop not selected')
class ReadinessFailureTests(unittest.TestCase):
    def test_real_dependency_failure_negative(self):
        subprocess.run(COMPOSE + ['stop', 'speech'], check=True, timeout=60,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            with self.assertRaises(urllib.error.HTTPError) as received:
                urllib.request.urlopen('http://localhost:3000/health/ready', timeout=15)
            self.assertEqual(received.exception.code, 503)
        finally:
            subprocess.run(COMPOSE + ['start', '--wait', '--wait-timeout', '60', 'speech'],
                           check=True, timeout=75, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    unittest.main()
