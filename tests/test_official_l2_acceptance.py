"""Independent official-release literals against retained real native execution.

These development assertions read saved evidence, never corpus bytes or providers.
The native owner receipt must actually pass; counts are not populated by this test.
"""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/iteration-35-official-l2-20261027'
AUDIT=ROOT/'audit/iteration-35-official-l2-20261027'

class OfficialL2Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((AUDIT/'PLAN.json').read_text())
        cls.actual=json.loads((OUT/'observations.json').read_text())
        cls.count=cls.actual['counts']
        cls.native=[json.loads(s) for s in (OUT/'import.jsonl').read_text().splitlines()]
        cls.regression=[json.loads(s) for s in (OUT/'regression.jsonl').read_text().splitlines()]
        cls.targeted=[json.loads(s) for s in (OUT/'targeted.jsonl').read_text().splitlines()]
        cls.tiers=[json.loads(s) for s in (OUT/'tiers.jsonl').read_text().splitlines()]
        cls.versions=[json.loads(s) for s in (OUT/'versions.jsonl').read_text().splitlines()]
        cls.counts_receipt=[json.loads(s) for s in (OUT/'counts.jsonl').read_text().splitlines()]
        cls.clock=[json.loads(s) for s in (OUT/'clock.jsonl').read_text().splitlines()]
        cls.clock_repair=[json.loads(s) for s in (OUT/'repair-clock.jsonl').read_text().splitlines()]
        cls.cursor=[json.loads(s) for s in (OUT/'cursor.jsonl').read_text().splitlines()]
        cls.multi=[json.loads(s) for s in (OUT/'multi.jsonl').read_text().splitlines()]
        cls.plain=[json.loads(s) for s in (OUT/'plain-unit.jsonl').read_text().splitlines()]
        cls.extent=[json.loads(s) for s in (OUT/'extent-plain.jsonl').read_text().splitlines()]
        cls.extent_repair=[json.loads(s) for s in (OUT/'repair-extents.jsonl').read_text().splitlines()]
        cls.compatibility=[json.loads(s) for s in (OUT/'compatibility.jsonl').read_text().splitlines()]
        cls.quality=[json.loads(s) for s in (OUT/'quality.jsonl').read_text().splitlines()]
    def native_pass(self,case,rows=None):
        rows=self.native if rows is None else rows
        self.assertTrue(any(r.get('Test')==case and r['Action']=='pass' for r in rows),case)
        self.assertFalse(any(r.get('Test')==case and r['Action'] in ['fail','skip'] for r in rows),case)
    def complete(self):
        self.native_pass('TestNativeOfficialL2Full')
        self.assertEqual('0',(OUT/'import-exit-code').read_text())
        r=self.actual['report']
        self.assertEqual('complete',r['state'])
        self.assertEqual('source-native-l2-v5-v2',r['parser_version'])
        self.assertFalse(any(i['code'] in ['count_mismatch','count_unbound'] for i in r['issues']))
        self.assertTrue(r['raw_complete'])
        self.assertTrue(r['normalized_complete'])
        self.assertEqual('0',r['raw_only_records'])
        self.assertEqual('0',r['quarantined_records'])
        self.assertEqual([],r['full_release_missing_components'])
        self.assertEqual(r['observed_records'],r['accepted_records'])
    def test_admission_positive(self):
        self.complete()
        self.assertEqual(84296,self.actual['copied_members'])
        self.assertEqual({'all':84296,'linked':84296,'wave':26889,'clock':26889},self.count['assets'])
        self.native_pass('TestNativeSourceAdmittedReusePositive',self.regression)
        release=self.actual['readback']['release']
        self.assertEqual(84296,release['files']);self.assertEqual(4,release['docs'])
        self.assertEqual('official-v5-20261026',release['source_version'])
    def test_admission_negative(self):
        self.native_pass('TestNativeSourceAdmittedFailureNegative',self.regression)
        self.native_pass('TestNativeSourceIntakeNegative',self.regression)
        self.assertEqual('0',(OUT/'regression-exit-code').read_text())
        # Existing native assets were reused, not swapped for mirror bytes or
        # another download. The native command mounts the actual official ZIP.
        argv=json.loads((OUT/'import-command.json').read_text())
        self.assertIn('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/l2-arctic:/corpus:ro',argv)
        self.assertIn('--pull=never',argv)
    def test_normalization_positive(self):
        self.complete()
        want=self.plan['expected']
        self.assertEqual(want['speaker_read_counts'],self.count['transcripts_by_speaker'])
        suite=sorted(set(want['read_speakers'])-{'ASI','SKA'})
        self.assertEqual(suite,self.count['suite_speakers'])
        self.assertEqual({'read_manual':3599,'read_automatic':26867,'suitcase_manual':22},self.count['layers'])
        self.assertEqual(26889,self.count['tables']['transcripts'])
        self.assertEqual(24,self.count['tables']['speakers'])
        self.assertEqual(24,self.count['speaker_metadata']['all'])
        self.assertEqual(6,self.count['speaker_metadata']['l1_groups'])
        self.native_pass('TestNativeSourceL2SpeakerMetadataPositive',self.versions)
        self.assertEqual({'F','M'},set(self.count['speaker_metadata']['genders']))
        for prefix,ops in [('read_',{'s':14098,'d':3420,'a':1092}),('suitcase_',{'s':1673,'d':456,'a':90})]:
            for op,n in ops.items():self.assertEqual(n,self.count['operations'][prefix+op])
        l1={group:sum(want['speaker_read_counts'][s] for s in speakers)+sum(s in suite for s in speakers) for group,speakers in want['speaker_l1_groups'].items()}
        self.assertEqual(l1,self.count['transcript_l1'])
        provenance=self.count['provenance']
        self.assertGreater(provenance['all'],26889)
        for k in ['raw_asset','raw_sha','native_retained','transform_asset']:self.assertEqual(provenance['all'],provenance[k],k)
        order=self.count['tier_order']
        for k in ['with_native_order','label_unchanged','bounds_unchanged']:self.assertEqual(order['all'],order[k],k)
    def test_normalization_negative(self):
        self.complete()
        u=self.count['uncertainty'];self.assertGreater(u['bare_SD'],0)
        self.assertEqual(u['bare_SD'],u['bare_SD_not_error'])
        self.assertGreater(u['unknown_perceived'],0);self.assertGreater(u['approximate'],0)
        self.assertGreater(u['ancillary_unnamed'],0)
        self.native_pass('TestSourceL2AncillaryTierPositive',self.extent)
        self.native_pass('TestSourceL2AncillaryTierNegative',self.extent)
        joins=self.count['transcript_joins']
        self.assertEqual(0,joins['suite_auto']);self.assertEqual(0,joins['precise_pronunciation'])
        self.assertEqual(26889,joins['with_audio']);self.assertEqual(3621,joins['manual']);self.assertEqual(26867,joins['auto'])
        self.assertEqual(0,self.count['annotation_claims']['automatic_phone_claims'])
        self.assertEqual(0,self.count['annotation_claims']['approximate_flag_lost'])
        self.native_pass('TestSourceSerializedClockPositive',self.plain)
        self.native_pass('TestSourceSerializedClockNegative',self.plain)
        self.native_pass('TestNativeOfficialL2RepairClock',self.clock_repair)
        repair=json.loads((OUT/'clock-repair.json').read_text())
        self.assertEqual(1911,repair['requeued_false_projections'])
        self.assertEqual(repair['accepted_before'],repair['accepted_after'])
        self.assertTrue(repair['accepted_anchor_unchanged'])
        self.assertEqual(0,repair['source_bytes_read']);self.assertEqual(0,repair['native_rows_rewritten'])
        self.native_pass('TestNativeOfficialL2RepairExtents',self.extent_repair)
        self.native_pass('TestSourceL2ClockQualityPositive',self.compatibility)
        self.native_pass('TestSourceL2ClockQualityNegative',self.compatibility)
        self.native_pass('TestSourceAcousticBoundsPositive',self.compatibility)
        self.native_pass('TestSourceAcousticBoundsNegative',self.compatibility)
        extent=json.loads((OUT/'extent-repair.json').read_text())
        self.assertEqual(69,extent['requeued_native_extent_projections'])
        self.assertEqual(extent['accepted_before'],extent['accepted_after'])
        self.assertTrue(extent['accepted_anchor_unchanged'])
        self.assertEqual(0,extent['source_bytes_read'])
        self.native_pass('TestNativeOfficialL2QualityReadback',self.quality)
        quality=json.loads((OUT/'quality-readback.json').read_text())
        self.assertEqual({'native_extent_rows':73,'extent_unverified':73,'processing_rate_unknown':73,'serialized_endpoints':20068},quality['counts'])
        self.assertEqual(200,quality['http_status'])
        native=quality['record']['projection']['raw_metadata']
        self.assertEqual('unverified',native['clock_alignment_status'])
        self.assertIsNone(native['annotation_processing_rate_hz'])
        self.native_pass('TestNativeSourceL2SpeakerMetadataNegative',self.versions)
    def test_resume_positive(self):
        self.complete()
        stop=self.actual['interruption']
        self.assertGreater(stop['native_rows'],0);self.assertGreater(stop['revision'],0)
        self.assertTrue(stop['reopened_same_cursor'])
        self.native_pass('TestNativeSourceMappingCursorPositive',self.cursor)
        self.native_pass('TestNativeSourceMappingCursorNegative',self.cursor)
        self.native_pass('TestNativeSourceMappingMemberTablePositive',self.multi)
        self.assertTrue(self.actual['accepted_stability']['unchanged'])
        self.assertGreater(self.actual['accepted_stability']['accepted_before'],0)
        self.assertGreaterEqual(len(self.actual['resumes']),1)
        for resume in self.actual['resumes']:
            self.assertGreaterEqual(resume['revision_after'],resume['revision_before'])
    def test_resume_negative(self):
        stop=self.actual['interruption']
        self.assertEqual('failed',stop['state']);self.assertFalse(stop['normalized_complete'])
        self.assertTrue(stop['commit_rejected']);self.assertTrue(stop['stale_revision_rejected'])
        self.assertTrue(stop['stale_revision_no_row_change'])
        self.native_pass('TestNativeSourceCountRecoveryPositive',self.counts_receipt)
        self.native_pass('TestNativeSourceCountRecoveryNegative',self.counts_receipt)
        self.assertNotIn('staged',self.count['rows_by_state'])
        self.assertNotIn('unmapped',self.count['rows_by_state'])
        self.assertNotIn('quarantined',self.count['rows_by_state'])
    def test_readback_positive(self):
        self.complete();read=self.actual['readback']
        for key in ['release','report','progress','records','status','transcript','suitcase_transcript','automatic','audio']:self.assertEqual(200,read[key]['status'],key)
        status=next(r for r in read['status']['value'] if r['source_id']=='L2-ARCTIC')
        self.assertEqual('complete',status['status']);self.assertTrue(status['normalized_complete'])
        record=read['transcript']['value']['items'][0]
        self.assertEqual('ABA',record['corpus_record']['speaker_id']);self.assertEqual('Arabic',record['corpus_record']['l1'])
        self.assertEqual('L2-ARCTIC',record['corpus_record']['source_id'])
        self.assertEqual('https://psi.engr.tamu.edu/l2-arctic-corpus/#'+record['member'],record['corpus_record']['source_uri'])
        self.assertEqual('RIFF/WAVE',read['audio']['format']);self.assertGreater(read['audio']['bytes'],44)
    def test_readback_negative(self):
        read=self.actual['readback'];self.assertEqual(400,read['bad_cursor']['status'])
        record=read['suitcase_transcript']['value']['items'][0]
        raw=record['projection']['raw_metadata']
        self.assertIsNone(raw['automatic_annotation_member']);self.assertIsNone(raw['observed_pronunciation'])
        auto=read['automatic']['value']['items'][0]['projection']['raw_metadata']
        self.assertEqual('source_automatic_alignment',auto['annotation_origin']);self.assertNotIn('phone_annotation',auto)
        self.assertNotIn('external_api_transfer',record['corpus_record']['licence']['uses'])
        self.assertEqual('attachment',read['audio']['content_disposition'])

if __name__=='__main__':unittest.main()
