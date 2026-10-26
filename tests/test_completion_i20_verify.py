"""Independent literal assertions on current CUA and actual media observations.

The HTTP fixture controls reads/writes; it does not simulate native persistence,
new grading or acoustic correctness. Original unaffected evidence is retained.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/iteration-20-verification-20261026'
AUDIT = ROOT / 'audit/iteration-20-verification-20261026'
module = importlib.util.spec_from_file_location('i20_verify_review', AUDIT / 'review.py')
review = importlib.util.module_from_spec(module)
module.loader.exec_module(review)
SCORE = 'Primary score: 60.0 / 100'
DRAFT = 'I heard “two ticket”. Use “two tickets”.'


class CompletionI20Verify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = json.loads((DATA / 'observations.json').read_text())
        cls.c = cls.facts['cases']
        cls.before = json.loads((DATA / 'baseline.json').read_text())
        cls.events = [json.loads(line) for line in (DATA / 'requests.jsonl').read_text().splitlines()]

    def responses(self, scenario, ending):
        return [row for row in self.events if row.get('scenario') == scenario
                and row['event'] == 'response' and row['path'].endswith(ending)]

    def test_obsolete_refresh_negative(self):
        self.assertIsNone(self.before['obsolete']['score'])
        self.assertEqual([SCORE, SCORE], [self.c[k]['score'] for k in ['manualNewer', 'manualAfterOld']])
        self.assertEqual([1, 3, 2], [row['ordinal'] for row in self.responses('manual-fixed', '/results')])
        self.assertEqual([], self.c['manualAfterOld']['alerts'])

    def test_obsolete_progress_negative(self):
        self.assertIsNone(self.before['progressObsolete']['score'])
        for key in ['progressNewer', 'progressAfterOld', 'progressFinal']:
            self.assertEqual(SCORE, self.c[key]['score'])
            self.assertTrue(self.c[key]['readOnly'])
        # Later successful polls were held until after the old-response snapshot.
        self.assertEqual([2, 1], [row['ordinal'] for row in self.responses('progress-final-fixed', '/results')[:2]])

    def test_prewrite_read_negative(self):
        self.assertFalse(self.before['writeObsolete']['readOnly'])
        value = self.c['writeAfterOld']
        self.assertEqual(SCORE, value['score'])
        self.assertTrue(value['readOnly'])
        self.assertFalse(value['submitVisible'])
        self.assertEqual('Two ticket should be two tickets.', value['answer'])
        self.assertEqual([1, 3, 2], [row['ordinal'] for row in self.responses('write-fixed', '4f6bbb22-0dec-487c-a64e-afd05c2902e3')])

    def test_obsolete_failure_negative(self):
        value = self.c['obsoleteFailure']
        self.assertEqual(SCORE, value['score'])
        self.assertEqual([], value['alerts'])
        self.assertIn('Saved state refreshed.', value['statuses'])
        self.assertEqual([1, 3, 2], [row['ordinal'] for row in self.responses('obsolete-failure-fixed', '/results')[:3]])

    def test_bounded_failure_recovery_positive(self):
        failure, recovered = self.c['resultsFailure'], self.c['resultsRecovered']
        self.assertEqual([200, 503, 503, 503, 200],
                         [row['status'] for row in self.responses('failure-fixed', '/results')])
        self.assertEqual([SCORE, SCORE], [failure['score'], recovered['score']])
        self.assertEqual(failure['answer'], recovered['answer'])
        self.assertTrue(failure['refreshEnabled'])
        self.assertEqual(['Your answer is saved. Findings are temporarily unavailable. Refresh to retry.'], failure['alerts'])
        self.assertEqual([], recovered['alerts'])
        self.assertNotIn('private backend detail', failure['main'])

    def test_malformed_recovery_positive(self):
        failure, recovered = self.c['malformed'], self.c['malformedRecovered']
        self.assertEqual([SCORE, SCORE], [failure['score'], recovered['score']])
        self.assertEqual(failure['answer'], recovered['answer'])
        self.assertEqual(['Your answer is saved. Findings are temporarily unavailable. Refresh to retry.'], failure['alerts'])
        self.assertEqual([], recovered['alerts'])
        self.assertNotIn('private backend detail', failure['main'])
        self.assertTrue(any(row['message'].startswith('Tangerine display recovery') for row in self.facts['logs']))

    def test_queued_native_events_positive(self):
        for key in ['mediaRapid', 'mediaPause']:
            self.assertTrue(any(row['current'] > 16.5 and not row['paused'] for row in self.before[key]))
            stops = [row for row in self.c[key] if row['kind'] == 'pause' and row['paused']]
            self.assertEqual(1, len(stops))
            self.assertGreaterEqual(stops[0]['current'], 16)
            self.assertLess(stops[0]['current'], 16.4)
        self.assertGreaterEqual(sum(row['kind'] == 'seeking' for row in self.c['mediaRapid']), 2)
        self.assertTrue(any(row['kind'] == 'pause' and not row['paused'] for row in self.c['mediaPause']))

    def test_ordinary_replay_positive(self):
        for start_key, end_key, start, end in [
            ('replayStart', 'replayEnd', 9.59, 14.839),
            ('secondStart', 'secondEnd', 15.5, 16.5),
            ('replacedStart', 'replacedEnd', 23.5, 24.5),
        ]:
            a, b = self.c[start_key]['audio'], self.c[end_key]['audio']
            self.assertFalse(a['paused'])
            self.assertGreaterEqual(a['current'], start)
            self.assertLess(a['current'], start + 1)
            self.assertTrue(b['paused'])
            self.assertGreaterEqual(b['current'], end)
            self.assertLess(b['current'], end + .4)
            self.assertEqual(a['src'], b['src'])
        self.assertIn('Passage timing unavailable. Use the full recording above.', self.c['currentComplete']['main'])

    def test_manual_interrupt_negative(self):
        a, b = self.c['manualStart']['audio'], self.c['manualAfter']['audio']
        self.assertEqual(0, a['current'])
        self.assertFalse(a['paused'])
        self.assertEqual(25.875, b['current'])
        self.assertTrue(self.c['manualAfter']['ended'])
        self.assertEqual(a['src'], b['src'])
        self.assertEqual('Prepare an exercise', self.c['nextPractice'])
        self.assertEqual(0, self.c['returned']['audio']['current'])
        self.assertTrue(self.c['returned']['audio']['paused'])

    def test_media_recovery_positive(self):
        a, b = self.c['mediaFailure'], self.c['mediaRecovered']
        self.assertEqual([SCORE, SCORE], [a['score'], b['score']])
        self.assertEqual(a['answer'], b['answer'])
        self.assertTrue(any('Saved audio is temporarily unavailable.' in text for text in a['alerts']))
        self.assertNotIn('private backend detail', a['main'])
        self.assertEqual([], b['alerts'])
        self.assertFalse(b['audio']['paused'])
        self.assertGreaterEqual(b['audio']['current'], 15.5)
        self.assertIn('playback_revision=1', b['audio']['src'])
        self.assertEqual(a['audio']['src'].split('?')[0], b['audio']['src'].split('?')[0])

    def test_draft_retention_positive(self):
        self.assertTrue(self.c['draftFailure']['saveEnabled'])
        self.assertEqual(['Saved attempt is unavailable. Your text is retained. Refresh to retry.'], self.c['draftFailure']['alerts'])
        for key in ['draftFailure', 'draftRefreshed', 'draftSaved', 'draftReopened']:
            self.assertEqual(DRAFT, self.c[key]['answer'])
            self.assertFalse(self.c[key]['readOnly'])
            self.assertIsNone(self.c[key]['score'])
        self.assertIn('Draft saved.', self.c['draftSaved']['statuses'])
        self.assertTrue(any('Your unsaved text is retained.' in text for text in self.c['draftRefreshed']['statuses']))
        self.assertIsNone(self.c['checking']['score'])
        self.assertTrue(any('Answer saved. Checking findings' in text for text in self.c['checking']['statuses']))
        self.assertEqual('Primary score: uncertain', self.c['uncertain']['score'])

    def test_zero_dispatch_negative(self):
        events = [row for row in self.events if row.get('scenario', '').endswith('fixed') or row.get('scenario') == 'checking-final-screen']
        writes = [row for row in events if row['event'] == 'request' and row['method'] != 'GET']
        self.assertTrue(all(row['path'].endswith(('/playback', '/answer', ':submit')) for row in writes))
        explicit = [row for row in writes if not row['path'].endswith('/playback')]
        self.assertEqual({
            'progress-fixed': 'POST', 'progress-final-fixed': 'POST', 'write-fixed': 'POST',
            'draft-recovery-fixed': 'PUT', 'checking-layout-fixed': 'POST', 'checking-final-screen': 'POST',
        }, {row['scenario']: row['method'] for row in explicit})
        self.assertEqual(6, len(explicit))
        self.assertFalse(any(row['event'] == 'fixture_error' for row in self.events))

    def test_current_typography_positive(self):
        rows = self.c['layouts']
        self.assertEqual({('completed', 320), ('completed', 390), ('completed', 1280),
                          ('draft', 320), ('checking', 320), ('uncertain', 390)},
                         {(row['state'], row['width']) for row in rows})
        for row in rows:
            self.assertEqual(['17px', '24.65px'], [row['bodySize'], row['bodyLine']])
            self.assertTrue(row['sourceSans'])
            self.assertEqual('loaded', row['fonts'])
            self.assertFalse(row['overflow'])
            for button in row['buttons']:
                self.assertGreaterEqual(button['height'], 44)
                self.assertEqual('16px', button['font'])
            if row['state'] == 'completed':
                self.assertEqual('nowrap', row['value']['whiteSpace'])
                self.assertLessEqual(row['value']['width'], row['value']['parentWidth'])
                self.assertEqual(['15px'] * 6, row['passageSizes'])
        focus = self.c['keyboard']
        self.assertEqual('Replay passage 2.1', focus['name'])
        self.assertEqual('3px', focus['outline'])
        self.assertGreater(focus['top'], 0)
        self.assertLessEqual(focus['bottom'], focus['height'])

    def packet(self):
        return json.loads((AUDIT / 'REVIEW.json').read_text())

    def test_current_review_positive(self):
        self.assertEqual([], review.review_errors(self.packet(), self.facts))

    def test_review_omission_negative(self):
        for dimension in ['ui_ux', 'typography', 'evidence']:
            packet = self.packet()
            packet.pop(dimension)
            self.assertTrue(review.review_errors(packet, self.facts))
        facts = copy.deepcopy(self.facts)
        facts['cases']['layouts'][0]['overflow'] = True
        self.assertTrue(review.review_errors(self.packet(), facts))
        packet = self.packet()
        packet['new_model_calls'] = 1
        self.assertTrue(review.review_errors(packet, self.facts))


if __name__ == '__main__':
    unittest.main(verbosity=2)
