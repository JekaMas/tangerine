"""Assertions over retained real application/browser observations; zero inference.

The observation file is private and must be collected through the actual local
app. The teacher response is a labelled constructed input, not participant data.
Missing evidence is an error, never an invented model reply or a passing skip.
"""
from fractions import Fraction
import json
import os
from pathlib import Path
import unittest


class GenerationLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observation = json.loads(Path(os.environ['TANGERINE_GENERATION_LIVE_EVIDENCE']).read_text())

    def test_completed_generation_positive(self):
        x = self.observation
        self.assertEqual(x['origin'], 'actual_native_and_browser_observation_not_model_fixture')
        generation = x['generation']
        self.assertEqual(generation['phase_states'], {'canonical_text': 'complete', 'mutation': 'complete', 'render': 'complete'})
        self.assertTrue(generation['audio_available'])
        self.assertIsNone(generation['last_failure'])
        self.assertGreater(generation['canonical_word_count'], 0)
        progress = generation['render_progress_summary']
        self.assertGreater(progress['total_pieces'], 1)
        self.assertEqual(progress['complete_pieces'], progress['total_pieces'])
        self.assertTrue(progress['ready_to_assemble'])
        self.assertLessEqual(x['foreground_seconds'], 270)

    def test_scoring_feedback_positive(self):
        result = self.observation['result']
        self.assertEqual(result['status'], 'complete')
        score = result['score']
        self.assertEqual({k: score['counts'][k] for k in ('tp', 'fp', 'fn')}, {'tp': 1, 'fp': 1, 'fn': 0})
        # Independent exact answer-components-v2 arithmetic: F1=2/3, repair=1.
        expected = 100 * (45 * Fraction(2, 3) + 30) / (45 + 30)
        exact = score['composite']['exact_value_0_100']
        self.assertEqual(Fraction(int(exact['numerator']), int(exact['denominator'])), expected)
        self.assertEqual(score['composite']['display'], '80.0')
        matched = [d for d in result['interpretation']['decisions'] if d['decision'] == 'matched_error']
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]['correction']['status'], 'accepted')
        self.assertEqual(matched[0]['explanation']['status'], 'accepted')
        self.assertIsNotNone(result['feedback'])

    def test_false_claim_negative(self):
        result = self.observation['result']
        false = [d for d in result['interpretation']['decisions'] if d['decision'] == 'false_positive']
        self.assertEqual(len(false), 1)
        self.assertEqual(false[0]['correction']['status'], 'rejected')
        self.assertFalse(false[0]['explanation']['supplied'])
        self.assertEqual(result['score']['counts']['unresolved_claims'], 0)

    def test_playback_and_unanswered_attempt_positive(self):
        played = self.observation['playback']
        self.assertGreater(played['duration'], 0)
        self.assertGreater(played['currentTime'], 0)
        self.assertFalse(played['paused'])
        self.assertEqual(played['readyState'], 4)
        self.assertIsNone(played['error'])
        attempt = self.observation['unanswered_attempt']
        self.assertEqual(attempt['state'], 'started')
        self.assertEqual(attempt['answer_text'], '')
        self.assertIsNone(attempt['submitted_at'])


if __name__ == '__main__':
    unittest.main()
