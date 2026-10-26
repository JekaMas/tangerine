"""Literal status expectations through the actual listening progress owner."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'


class FeedbackNotice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = """
import {feedbackReadyNotice} from './services/web/app/listen/checkingProgress.js';
const status=feedback_status=>feedbackReadyNotice({status:'complete',feedback_status});
console.log(JSON.stringify({complete:status('complete'),unavailable:status('unavailable'),pending:status('not_started')}));
"""
        run = subprocess.run([str(NODE), '--input-type=module', '-e', script], cwd=ROOT,
                             capture_output=True, text=True, timeout=20)
        if run.returncode:
            raise AssertionError(run.stderr)
        cls.facts = json.loads(run.stdout)

    def test_feedback_complete_positive(self):
        self.assertEqual('Comments and recommendations are ready.', self.facts['complete'])

    def test_feedback_unavailable_negative(self):
        self.assertEqual('', self.facts['unavailable'])

    def test_feedback_pending_negative(self):
        self.assertEqual('', self.facts['pending'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
