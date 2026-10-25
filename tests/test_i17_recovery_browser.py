"""Literal oracles over observed CUA actions on the source-built test frontend.

The gateway supplies controlled failures and forwards only reads of saved local
records. These observations establish recovery/presentation, not provider quality.
"""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/iteration-17-verification-20261025'

class RecoveryBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = json.loads((DATA / 'browser-observations.json').read_text())
        cls.actions = {x['name']: x for x in cls.v['actions']}
    def test_routes_readable_positive(self):
        headings = dict(library='A better ear for English.', prepare='Prepare an exercise',
            attempts='Saved attempts', audio='Saved audio', results='Listen and respond',
            reviews='Optional LLM review', reports='Reports and quality experiments',
            sources='Sources', settings='Your LLM connection', recovery='Recovery and local data',
            cleanup='Cleanup and deletion')
        self.assertEqual(22, len(self.v['routes']))
        self.assertEqual({(name, size) for name in headings for size in ['mobile', 'desktop']},
                         {(x['name'], x['size']) for x in self.v['routes']})
        for row in self.v['routes']:
            with self.subTest(route=row['name'], size=row['size']):
                self.assertEqual(headings[row['name']], row['heading'])
                self.assertEqual('17px', row['bodySize'])
                self.assertIn('Source Sans 3', row['bodyFont'])
                self.assertFalse(row['overflow'])
    def test_all_read_failures_negative(self):
        rows = self.v['errorRoutes']
        self.assertEqual(11, len(rows))
        self.assertEqual({r['name'] for r in self.v['routes']}, {r['name'] for r in rows})
        for row in rows:
            with self.subTest(route=row['name']):
                self.assertTrue(any(row['alerts']))
                self.assertTrue(row['refreshEnabled'])
                self.assertFalse(row['rawLeak'])
                self.assertFalse(row['overflow'])
    def test_transient_read_positive(self):
        self.assertEqual(self.actions['transient_source_read'],
            dict(name='transient_source_read', alerts=[], populated=True, refreshEnabled=True))
    def test_source_recovery_positive(self):
        failed, recovered = [self.actions[x] for x in ['source_read_exhausted', 'source_read_recovered']]
        self.assertEqual(['The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.'], failed['alerts'])
        self.assertTrue(failed['refreshEnabled'])
        self.assertEqual(['review-input-retained'] * 2, [failed['retained'], recovered['retained']])
        self.assertEqual([], recovered['alerts'])
        self.assertTrue(recovered['populated'])
    def test_generation_failure_negative(self):
        row = self.actions['generation_failure_final']
        self.assertEqual('This step could not be completed. Your choices are retained. Refresh saved preparations before trying again.', row['message'])
        self.assertEqual('Repair review: travel plans.', row['topic'])
        self.assertTrue(row['generateEnabled'])
        self.assertFalse(row['overflow'])
    def test_report_failure_negative(self):
        row = self.actions['report_write_failure']
        self.assertEqual('Reports are temporarily unavailable. Your inputs and saved observations are retained. Refresh to continue.', row['message'])
        self.assertEqual('Recovery review report', row['title'])
        self.assertTrue(row['calculateEnabled'])
        self.assertFalse(row['overflow'])
    def test_keyboard_refresh_positive(self):
        row = self.actions['keyboard_refresh_reobserved']
        self.assertEqual(['BUTTON', 'Refresh', '3px', 'Recovery review report', []],
            [row['focusedTag'], row['focusedButton'], row['outline'], row['title'], row['alerts']])
    def test_refresh_during_write_negative(self):
        self.assertEqual(dict(name='refresh_during_write', calculateEnabled=False,
            refreshEnabled=True, reenabled=True), self.actions['refresh_during_write'])
    def test_saved_result_positive(self):
        row = self.actions['saved_result_final']
        self.assertTrue(row['answerReadOnly'])
        self.assertTrue(row['audioPaused'])
        self.assertTrue(row['refreshEnabled'])
        self.assertIn('Primary score: 60.0 / 100', row['score'])
        self.assertIn('Optional explanation: 100.0%', row['score'])
        self.assertIn('Found 1 of 2 mistakes · 1 missed · 0 false positives', row['score'])
    def test_readable_tables_keyboard_positive(self):
        row = self.v['tableReview']
        self.assertFalse(row['pageOverflow'])
        self.assertEqual({'Experiment progress', 'Experiment diagnostic measurements'}, {t['name'] for t in row['tables']})
        for table in row['tables']:
            self.assertLess(table['maxHeaderHeight'], 60)
            self.assertEqual('normal', table['overflowWrap'])
            self.assertGreater(table['contentWidth'], table['width'])
        self.assertGreaterEqual(row['noteWidth'], 140)
        self.assertTrue(row['keyboard']['focused'])
        self.assertEqual('3px', row['keyboard']['outline'])
        self.assertGreater(row['keyboard']['scrollLeft'], 0)
        empirical = self.v['empiricalTable']
        self.assertFalse(empirical['pageOverflow'])
        self.assertTrue(empirical['focusable'])
        self.assertLess(empirical['maxHeaderHeight'], 60)
    def test_failed_experiment_row_negative(self):
        row = self.actions['failed_experiment_row']
        self.assertEqual('This row did not complete. Refresh saved state, then retry when the selected service is available.', row['guidance'])
        self.assertFalse(row['rawLeak'])
        self.assertFalse(row['overflow'])
    def test_controlled_write_not_replayed_negative(self):
        rows = [json.loads(x) for x in (DATA / 'fixture-requests.jsonl').read_text().splitlines()]
        selected = [x for x in rows if x.get('scenario') == 'refresh-during-write']
        self.assertEqual([('POST', '/api/v1/reports/empirical')],
                         [(x['method'], x['path']) for x in selected if x['method'] != 'GET'])
        self.assertEqual(2, sum(x['path'] == '/api/v1/reports/empirical' and x['method'] == 'GET' for x in selected))

if __name__ == '__main__':
    unittest.main(verbosity=2)
