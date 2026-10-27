"""Literal I35 repair/UI oracles over actual native Chrome/Node observations.

No application success data are mocked. Only connection failures are injected
by an owned GET-only gateway. These readers make zero browser/provider calls.
"""
import json
from pathlib import Path
import re
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/iteration-35-verification-20261027'
BROWSER=OUT/'browser'
RELEASE='8c5cda52-e8aa-4baf-8495-d4a2efb3918e'
IMPORT='8cd233c7-1999-44c9-9ed7-e0519f375f4d'

def read(path):return json.loads(path.read_text())

def png_size(name):
    raw=(BROWSER/name).read_bytes()
    assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    return struct.unpack('>II',raw[16:24])

class OfficialL2Verification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser=read(BROWSER/'observations.json')
        cls.node=(OUT/'source-session.tap').read_text()
        cls.executed=set(re.findall(r'^✔ (\w+) \(',cls.node,re.M))
        cls.requests=[json.loads(s) for s in (BROWSER/'requests.jsonl').read_text().splitlines()]

    def test_selection_positive(self):
        self.assertEqual(33,len(self.executed))
        self.assertIn('ℹ pass 33',self.node)
        for case in ['compact_selection_positive','compact_restore_positive','legacy_cache_migration_positive','selection_positive','later_release_positive','later_progress_positive','restore_positive']:
            self.assertIn(case,self.executed)
        self.assertEqual(dict(source='L2-ARCTIC',releaseId=RELEASE,binding='native',importId=IMPORT),self.browser['cache']['value'])
        self.assertEqual(142,self.browser['cache']['size'])
        self.assertTrue(self.browser['reportRestored'])

    def test_selection_negative(self):
        before=read(BROWSER/'before-cache-repair/observations.json')
        self.assertFalse(before['reportRestored'])
        self.assertEqual(dict(size=0,value=None),before['cache'])
        self.assertTrue(any('QuotaExceededError' in row['text'] for row in before['logs']))
        for case in ['compact_unimported_negative','compact_unavailable_negative','compact_superseded_negative','binding_reset_negative','metadata_reset_negative','superseded_failure_negative','stale_pagination_negative','cache_unavailable_negative']:
            self.assertIn(case,self.executed)
        self.assertNotIn('QuotaExceededError','\n'.join(row['text'] for row in self.browser['logs']))
        self.assertIn('ℹ fail 0',self.node)
        self.assertIn('ℹ skipped 0',self.node)

    def test_browsing_positive(self):
        html=(BROWSER/'01-full-source-status.html').read_text()
        l2=html.split('<h2>L2-ARCTIC</h2>',1)[1].split('</li>',1)[0]
        self.assertIn('Complete source release retained',l2)
        self.assertIn('original files:',l2);self.assertIn('converted records:',l2)
        self.assertIn('Observed: 1574840 · accepted: 1574840 · quarantined: 0 · rejected: 0 · raw only: 0',self.browser['report'])
        self.assertIn('Raw complete: true · normalized complete: true',self.browser['report'])
        first=self.browser['initialRows'];more=self.browser['afterMore']
        self.assertEqual(20,len(first));self.assertEqual(40,len(more))
        self.assertEqual(first,more[:20]);self.assertEqual(40,len(set(more)))
        self.assertTrue(all('ABA.zip/ABA/annotation/arctic_a0003.TextGrid' in row for row in first))
        original=(BROWSER/'downloaded-original.TextGrid').read_text()
        self.assertIn('ooTextFile',original);self.assertIn('TextGrid',original)
        self.assertEqual(7473,self.browser['originalDownload']['bytes'])
        self.assertTrue(self.browser['keyboardRefresh']);self.assertTrue(self.browser['transientRecovered'])
        self.assertTrue(any(row['path'].endswith('/issues') and row['status']==200 for row in self.requests))

    def test_recovery_negative(self):
        self.assertEqual('The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.',self.browser['failureText'])
        for scenario,want in [('transient-verified',[503,200]),('unavailable-verified',[503,503,503]),('recovery-verified',[200])]:
            rows=[row for row in self.requests if row['scenario']==scenario and row['path']=='/api/v1/sources']
            self.assertEqual(want,[row['status'] for row in rows])
        html=(BROWSER/'07-safe-error.html').read_text()
        self.assertIn('Import report',html);self.assertIn('1574840',html)
        self.assertNotIn('PRIVATE_BACKEND_CANARY',html);self.assertNotIn('SQL/private password',html)
        self.assertTrue(all(row['method']=='GET' for row in self.requests))
        self.assertTrue(self.browser['noPageErrors']);self.assertEqual([],self.browser['errors'])

    def test_typography_positive(self):
        self.assertEqual(dict(font='"Source Sans 3", sans-serif',size='17px',lineHeight='24.65px',loaded=True),self.browser['typography'])
        self.assertEqual((1280,720),png_size('03-full-import-report.png'))
        self.assertEqual((390,844),png_size('12-report-heading-390.png'))
        self.assertEqual((320,740),png_size('12-report-heading-320.png'))
        for width in [390,320]:self.assertTrue((BROWSER/f'09-navigation-{width}.png').is_file())
        video=read(BROWSER/'video.json')
        stream=video['probe']['streams'][0]
        self.assertEqual('h264',stream['codec_name']);self.assertEqual(1280,stream['width']);self.assertEqual(820,stream['height'])
        self.assertGreater(float(video['probe']['format']['duration']),10)
        self.assertEqual(2,len(video['clips']));self.assertTrue(video['cut']);self.assertTrue(video['silent'])
        for clip in video['clips']:self.assertTrue((BROWSER/clip).is_file())
        self.assertTrue((BROWSER/video['final_recovery_clip']).is_file())

    def test_layout_and_evidence_negative(self):
        self.assertEqual([390,320],[row['width'] for row in self.browser['layouts']])
        for row in self.browser['layouts']:self.assertLessEqual(row['scroll'],row['width'])
        self.assertEqual([],self.browser['errors'])
        reloads=[row for row in self.requests if row['scenario'] in ['reload-retained','resume-recovery']]
        for suffix in ['source-releases/'+RELEASE,'imports/'+IMPORT+'/progress','imports/'+IMPORT+'/records?limit=20']:
            self.assertTrue(any(row['path']=='/api/v1/'+suffix and row['status']==200 for row in reloads),suffix)
        self.assertFalse(any(row['method']!='GET' for row in self.requests))
        self.assertNotIn('PRIVATE_BACKEND_CANARY',(BROWSER/'08-recovered.html').read_text())
        self.assertEqual(1,len(read(BROWSER/'video.json')['probe']['streams'])) # no fabricated audio

if __name__=='__main__':unittest.main(verbosity=2)
