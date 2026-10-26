"""Exact I28 review regressions over actual native/Chrome observations.

No browser, native test, model or speech dispatch is performed by these readers.
All report and participant-shaped inputs remain constructed developer fixtures.
"""
import json
from pathlib import Path
import unittest
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-28-verify-20261026'


class CompletionI28Verify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts=json.loads((DATA/'browser-observations.json').read_text())
        cls.fixture=json.loads((DATA/'browser-fixture.json').read_text())

    def scope(self,name):
        value=self.facts['cases'][name]
        native=self.fixture[name]['report']
        self.assertEqual(self.fixture[name]['id'],parse_qs(urlparse(value['url']).query)['report'][0])
        self.assertEqual([],value['alerts'])
        self.assertEqual(1,len(native['annotated_leaf_ids']))
        self.assertEqual(0,native['annotated_windows'])
        self.assertIn('Declared annotation scope: 1 of 122 categories.',value['report'])
        self.assertIn('Absence measurements require fully inspected mapped windows.',value['report'])
        self.assertNotIn('categories inspected for absence',value['report'])
        self.assertEqual(1,len(value['rows']))
        self.assertIn('No eligible observations',value['rows'][0])
        self.assertIn('Correct-use observations needed',value['rows'][0])
        self.assertIn('0 fully inspected mapped windows',self.facts['red'][name]['report'])
        self.assertIn('1 of 122 categories inspected for absence',self.facts['red'][name]['report'])
        return native,value

    def test_declared_scope_without_observations_negative(self):
        native,value=self.scope('unobserved')
        self.assertEqual((0,0),(native['observed_windows'],native['source_annotated_windows']))
        self.assertIn('0 distinct mapped mistakes',value['report'])

    def test_incomplete_mapping_absence_negative(self):
        native,value=self.scope('unmapped')
        self.assertEqual((1,1,1),(native['observed_windows'],native['source_annotated_windows'],native['mapping_incomplete_windows']))
        self.assertEqual(1,native['unmapped_events'])
        self.assertIn('1 unmapped events',value['report'])
        self.assertIn('R:VERB:SVA',json.dumps(native['native_frequencies']))

    def test_current_layout_positive(self):
        self.assertEqual([(1280,720),(390,844),(320,740)],[(r['width'],r['height']) for r in self.facts['layouts']])
        for row in self.facts['layouts']:
            self.assertEqual(row['width'],row['pageWidth'])
            self.assertEqual(('17px','24.65px',True,'left'),tuple(row[k] for k in ['size','line','fontLoaded','metadataAlignment']))
            self.assertTrue(row['counts'])
            self.assertEqual({'14px'},set(row['counts']))
            self.assertGreaterEqual(row['reportTop'],90 if row['width']<960 else 0)
            self.assertLess(row['reportTop'],row['height'])
        self.assertEqual(self.facts['cases']['populated'],self.facts['cases']['reopened'])

    def test_current_keyboard_positive(self):
        row=self.facts['cases']['keyboard']
        self.assertEqual(('TABLE','3px',284,320,320),tuple(row[k] for k in ['tag','outline','tableWidth','pageWidth','width']))
        self.assertGreater(row['scrollWidth'],row['tableWidth'])
        self.assertGreater(row['scrollLeft'],0)

    def test_current_zero_execution_negative(self):
        final=json.loads((DATA/'browser-final.json').read_text())
        self.assertEqual(0,final['provider_receipts'])
        native=[json.loads(x) for x in (DATA/'browser-native.jsonl').read_text().splitlines() if x.startswith('{')]
        self.assertIn('TestSavedReportsBrowserFixture',{r.get('Test') for r in native if r['Action']=='pass'})
        self.assertFalse([r for r in native if r['Action'] in ['fail','skip']])
        requests=[json.loads(x) for x in (DATA/'browser-requests.jsonl').read_text().splitlines()]
        self.assertTrue(requests)
        self.assertFalse([r for r in requests if r['forbidden']])
        self.assertFalse([r for r in requests if r['method']!='GET' and r['path']!='/api/v1/reports/empirical'])

    def test_report_download_positive(self):
        receipt=json.loads((DATA/'download-receipt.json').read_text())
        downloaded=json.loads((DATA/'downloaded-report.json').read_text())
        self.assertEqual(self.fixture['unmapped'],downloaded)
        self.assertEqual('empirical-'+downloaded['id']+'.json',receipt['filename'])
        self.assertEqual(downloaded['id'],receipt['report_id'])
        self.assertTrue(receipt['native_snapshot_equal'])
        self.assertEqual((0,1,1,1),tuple(downloaded['report'][k] for k in ['annotated_windows','source_annotated_windows','mapping_incomplete_windows','unmapped_events']))
        self.assertEqual('constructed',downloaded['report']['population']['label_origin'])


if __name__=='__main__': unittest.main(verbosity=2)
