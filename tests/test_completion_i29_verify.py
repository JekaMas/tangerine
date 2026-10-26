"""Actual bounded I29 verify observations; never dispatch providers or browsers.

The response fixture replays the same actual saved unavailable-result HTTP
envelope to test UI status only. It is not successful live recommendations.
"""
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/iteration-29-verify-20261026'
LIVE = ROOT / 'data/iteration-29-full-flow-20261026'


def read(path):
    return json.loads(path.read_text())


class CompletionI29Verify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read(DATA / 'ui-observations.json')
        cls.by = {x['name']: x for x in cls.rows}

    def test_feedback_notice_negative(self):
        self.assertIn('Saved findings refreshed.', read(DATA / 'feedback-before.json')['main'])
        for name in ['feedback-unavailable-1280', 'feedback-unavailable-390',
                     'feedback-unavailable-320', 'retry-transport-recovered']:
            row = self.by[name]
            self.assertNotIn('Saved findings refreshed.', row['main'])
            self.assertNotIn('Comments and recommendations are ready.', row['main'])
            self.assertIn('Comments and practice recommendations are unavailable.', row['main'])
            self.assertIn('60.0 / 100', row['main'])
            self.assertEqual([], row['alerts'])

    def test_retry_transport_recovery_positive(self):
        failed, recovered = self.by['retry-transport-failure'], self.by['retry-transport-recovered']
        self.assertEqual(['Checking is unavailable. Your submitted answer is retained.'], failed['alerts'])
        self.assertEqual([], recovered['alerts'])
        for row in self.rows:
            self.assertNotIn('private backend canary', row['main'])
        for row in [failed, recovered]:
            self.assertIn('60.0 / 100', row['main'])
            self.assertEqual(False, next(b['disabled'] for b in row['buttons'] if b['text'] == 'Retry comments and recommendations'))
        requests = [json.loads(x) for x in (LIVE / 'requests.jsonl').read_text().splitlines()]
        controlled = [r for r in requests if r['scenario'].startswith('verify-ui-') and r['method'] == 'POST']
        self.assertEqual([200, 503, 200], [r['status'] for r in controlled])
        self.assertEqual('saved_feedback_unavailable', controlled[-1]['controlled_response_fixture'])

    def test_navigation_reopen_positive(self):
        self.assertEqual('/', urlparse(self.by['navigation-library']['url']).path)
        self.assertIn('Organising a neighbourhood book swap', self.by['navigation-library']['main'])
        self.assertEqual('/attempts', urlparse(self.by['navigation-attempts']['url']).path)
        row = self.by['saved-result-reopened']
        self.assertEqual('8db4a113-d8b6-430c-9bb1-eaec2fc19ff5', parse_qs(urlparse(row['url']).query)['attempt'][0])
        self.assertIn('60.0 / 100', row['main'])
        self.assertIn('Optional explanation: 100.0%', row['main'])
        self.assertIn('“Many” requires a plural countable noun.', row['main'])
        self.assertTrue(row['audio'][0]['paused'])
        self.assertIsNone(row['audio'][0]['error'])

    def test_current_layout_keyboard_positive(self):
        for width in [1280, 390, 320]:
            row = self.by['feedback-unavailable-' + str(width)]
            self.assertEqual((width, width, '17px', '24.65px'), (row['width'], row['pageWidth'], row['body'], row['line']))
            self.assertIn('Source Sans 3', row['font'])
        for name, tag in [('feedback-keyboard-link', 'A'), ('feedback-keyboard-retry', 'BUTTON')]:
            self.assertEqual((tag, '3px'), (self.by[name]['active']['tag'], self.by[name]['active']['outline']))

    def test_only_feedback_calls_negative(self):
        delta = read(DATA / 'dispatch-delta.json')
        self.assertEqual((27, 29, [33, 34], [503, 503], ['feedback', 'feedback'], 4),
                         tuple(delta[k] for k in ['baseline_hosted', 'current_hosted', 'new_dispatch_indices', 'new_http_statuses', 'all_new_stages', 'local_synthesis_total']))
        self.assertEqual(0, delta['calls_from_controlled_ui_or_navigation'])
        before, after = read(DATA / 'ui-dispatches-before.json'), read(DATA / 'ui-dispatches-after.json')
        self.assertEqual(before['hosted'], after['hosted'])
        result = read(LIVE / 'attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5-result.json')
        self.assertEqual('unavailable', result['feedback_status'])
        self.assertEqual({'denominator': '1', 'numerator': '60'}, result['score']['composite']['exact_value_0_100'])
        lab = read(DATA / 'lab-readback.json')
        self.assertTrue(lab['readback'])
        self.assertEqual(0, lab['export_inference_calls'])

    def test_returned_result_retention_positive(self):
        red, green = read(DATA / 'reply-red.json'), read(DATA / 'reply-green.json')
        marker = 'Constructed UI fixture: practise make a plan and make it fun.'
        self.assertIn('Comments and recommendations are ready.', red['main'])
        self.assertIn('Comments and practice recommendations are unavailable.', red['main'])
        self.assertNotIn(marker, red['main'])
        self.assertIn(marker, green['main'])
        self.assertIn('60.0 / 100', green['main'])
        self.assertNotIn('Comments and practice recommendations are unavailable.', green['main'])
        self.assertEqual([], green['alerts'])
        requests = [json.loads(x) for x in (LIVE / 'requests.jsonl').read_text().splitlines()]
        before = [r for r in requests if r['scenario'] == 'verify-reply-red']
        after = [r for r in requests if r['scenario'] == 'verify-reply-green']
        self.assertEqual(3, sum(r['method'] == 'GET' and r['path'].endswith('/results') and r['status'] == 503 for r in before))
        self.assertFalse(any(r['method'] == 'GET' and r['path'].endswith('/results') for r in after))
        self.assertTrue(any(r.get('controlled_response_fixture') == 'constructed_feedback_complete' for r in after))
        restored = read(DATA / 'reply-restored-native.json')
        self.assertNotIn(marker, restored['main'])
        self.assertIn('Comments and practice recommendations are unavailable.', restored['main'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
