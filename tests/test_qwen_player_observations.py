"""Retained actual browser observations of controlled PCM/player read recovery.

No new browser or model call is dispatched here. Click/keyboard/playback remain
explicitly unverified when input delivery failed; metadata is not an audio test.
"""
import json
from pathlib import Path
import unittest

AUDIT = Path(__file__).resolve().parents[1]/'audit/iteration-25-qwen-20261026'


class QwenPlayerObservations(unittest.TestCase):
    def facts(self):
        return json.loads((AUDIT/'browser-observations.json').read_text())

    def state(self, name):
        return next(s['observation'] for s in self.facts()['states'] if s['state'] == name)

    def test_rendered_layout_positive(self):
        facts = self.facts()
        self.assertEqual(0, facts['actual_model_calls'])
        self.assertEqual([1280, 390, 320], [s['width'] for s in facts['layouts']])
        for view in facts['layouts']:
            self.assertEqual(view['width'], view['pageWidth'])
            self.assertTrue(view['fontLoaded'])
            self.assertEqual(('17px', '24.65px'), (view['size'], view['line']))
            self.assertTrue(all(a['paused'] for a in view['audio']))
        partial = self.state('partial')
        self.assertEqual(1, len(partial['audio']))
        self.assertEqual('/partial/qwen-clean.wav', partial['audio'][0]['src'])
        self.assertIn('4 of 8 pieces saved', partial['status'])

    def test_saved_media_retry_positive(self):
        facts = self.state('media_transient_recovered')
        http = json.loads((AUDIT/'media-http-observations.json').read_text())
        for variant in ['clean', 'mistakes']:
            self.assertEqual(2, http['counts']['/transient/qwen-'+variant+'.wav'])
        self.assertEqual(['', ''], facts['messages'])
        self.assertTrue(all(a['readyState'] == 4 and a['duration'] == 6 and a['paused'] for a in facts['audio']))

    def test_saved_media_failure_negative(self):
        facts = self.state('media_failure_after_retry')
        http = json.loads((AUDIT/'media-http-observations.json').read_text())
        for variant in ['clean', 'mistakes']:
            self.assertEqual(2, http['counts']['/failure/qwen-'+variant+'.wav'])
        self.assertEqual(['The saved recording could not be played. Refresh saved recordings and try again. No new audio is generated.']*2, facts['messages'])
        self.assertTrue(all(not b['disabled'] for b in facts['buttons']))
        self.assertEqual(0, http['model_calls'])

    def test_read_failure_rendered_negative(self):
        path = AUDIT.parents[1]/'data/iteration-25-verify-20261026/read-failure-browser.json'
        facts = json.loads(path.read_text())
        self.assertEqual(0, facts['actual_model_calls'])
        self.assertIn('constructed six-second PCM', facts['origin'])
        self.assertEqual([1280, 390, 320], [view['width'] for view in facts['layouts']])
        for view in facts['layouts']:
            self.assertEqual(view['width'], view['pageWidth'])
            self.assertEqual(('17px', '24.65px'), (view['size'], view['line']))
            self.assertTrue(view['fontLoaded'])
            self.assertIn('One complete recording is available.', view['status'])
            self.assertIn('Progress details are temporarily unavailable.', view['status'])
            self.assertNotIn('JSONDecodeError', view['bodyText'])
            self.assertEqual([dict(text='Refresh saved recordings', disabled=False)], view['buttons'])
            self.assertEqual(1, len(view['audio']))
            self.assertEqual(('/read_failure/qwen-clean.wav', 6, True),
                             (view['audio'][0]['src'], view['audio'][0]['duration'], view['audio'][0]['paused']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
