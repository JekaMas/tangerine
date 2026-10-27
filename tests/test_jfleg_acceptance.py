"""I36 literal obligations against actual retained native/Chrome observations.

No import, model, speech or browser is replayed by this reconciliation command.
Native test identities and independently fixed source strings/counts are checked.
"""
import json
from pathlib import Path
import struct
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/iteration-36-jfleg-20261027'
VERIFY=ROOT/'data/iteration-36-verification-20261027'

class JFLEGAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=cls.read('observations.json')
        cls.native_expected=cls.read('native-expected.json')
        cls.consumer=cls.read('consumer-observations.json')
        cls.browser=cls.verified('browser-regression-fixed/observations.json')
        cls.datasets={p:cls.read('dataset-'+p+'.json') for p in ['dev','test']}
    @staticmethod
    def read(path):return json.loads((OUT/path).read_text())
    @staticmethod
    def verified(path):return json.loads((VERIFY/path).read_text())
    def session_pass(self,*names):
        text=(VERIFY/'sessions-green.tap').read_text()
        self.assertEqual(0,int((VERIFY/'sessions-green-exit-code').read_text()))
        self.assertNotRegex(text,r'(?m)^not ok ')
        for name in names:self.assertRegex(text,r'(?m)^ok \d+ - '+re.escape(name)+r'\s*$')
    def native_pass(self,name,filename):
        rows=[json.loads(s) for s in (OUT/filename).read_text().splitlines()]
        self.assertTrue(any(r.get('Test')==name and r['Action']=='pass' for r in rows),name)
        self.assertFalse(any(r.get('Test')==name and r['Action'] in ['fail','skip'] for r in rows),name)
    def complete(self):
        self.native_pass('TestNativeJFLEGFull','full.jsonl')
        self.assertEqual('0',(OUT/'full-exit-code').read_text())
        report=self.actual['report']
        self.assertEqual('complete',report['state'])
        self.assertTrue(report['raw_complete']);self.assertTrue(report['normalized_complete'])
        self.assertEqual('34789',report['observed_records']);self.assertEqual('34789',report['accepted_records'])
        self.assertEqual('0',report['quarantined_records']);self.assertEqual('0',report['raw_only_records'])
        self.assertEqual([],report['full_release_missing_components'])
    def test_acquisition_positive(self):
        self.complete()
        self.assertEqual(29,len(self.native_expected['files']))
        self.assertEqual(30,self.actual['assets'])
        self.assertEqual(1501,self.actual['corpus_records'])
        self.assertEqual({'dev':754,'test':747},self.actual['datasets'])
        self.native_pass('TestJFLEGNativePlanPositive','unit.jsonl')
        self.native_pass('TestJFLEGCompleteMembersPositive','repair-unit.jsonl')
        self.native_pass('TestNativeJFLEGCompletenessPositive','completeness.jsonl')
        self.native_pass('TestNativeSourceSourcesPositive','status.jsonl')
        self.assertEqual(12,self.consumer['source_cards'])
    def test_acquisition_negative(self):
        self.native_pass('TestJFLEGNativePlanNegative','unit.jsonl')
        self.native_pass('TestJFLEGCompleteMembersNegative','repair-unit.jsonl')
        self.native_pass('TestNativeJFLEGPartialNegative','partial.jsonl')
        self.native_pass('TestNativeJFLEGCompletenessNegative','completeness.jsonl')
        partial=self.read('partial-observations.json')
        self.assertFalse(partial['normalized_complete']);self.assertTrue(partial['full_missing'])
        missing=self.read('completeness-negative.json')['missing']
        for label in ['dev.ref.m2 edits: expected 11611, observed 0','test.ref.m2 edits: expected 10938, observed 0','coded_sentences.csv: expected 100, observed 0','pairwise.csv: expected 1629, observed 0','sample.csv: expected 4, observed 0']:
            self.assertIn(label,missing)
    def test_pairing_positive(self):
        self.complete()
        self.native_pass('TestSourceJFLEGProjectionPositive','unit.jsonl')
        groups=set();positions=0
        for part,count in [('dev',754),('test',747)]:
            examples=self.datasets[part]['examples'];self.assertEqual(count,len(examples))
            for index,e in enumerate(examples):
                self.assertEqual(f'{part}:{index}',e['id']);self.assertEqual(part,e['source_partition'])
                self.assertEqual(self.native_expected['lines'][f'{part}/{part}.src'][index],e['original']['text'])
                self.assertEqual(index,e['original']['line_index']);self.assertEqual('source_original',e['original']['origin'])
                owner='jfleg-ee06ff806a208aba815ac45313f4e750a48330a5/'
                self.assertEqual(owner+f'{part}/{part}.src',e['original']['member']);self.assertEqual('\n',e['original']['line_ending'])
                self.assertEqual(4,len(e['references']));self.assertEqual('complete',e['reference_completeness'])
                self.assertEqual(self.native_expected['lines'][f'{part}/{part}.spellchecked.src'][index],e['spellchecked']['text'])
                self.assertEqual('source_tool_derivation',e['spellchecked']['origin'])
                self.assertNotIn(e['group_id'],groups);groups.add(e['group_id'])
                for j,r in enumerate(e['references']):
                    self.assertEqual(f'ref{j}',r['reference_id'])
                    self.assertEqual(self.native_expected['lines'][f'{part}/{part}.ref{j}'][index],r['text'])
                    self.assertEqual(index,r['line_index']);self.assertEqual('source_annotation',r['origin'])
                    self.assertEqual(owner+f'{part}/{part}.ref{j}',r['member']);self.assertEqual('\n',r['line_ending']);positions+=1
        self.assertEqual(1501,len(groups));self.assertEqual(6004,positions)
    def test_pairing_negative(self):
        self.native_pass('TestSourceJFLEGProjectionNegative','unit.jsonl')
        self.native_pass('TestJFLEGReferenceEvaluationNegative','stable-go.jsonl')
        partial=self.read('partial-observations.json')['examples']
        self.assertEqual(2,len(partial));self.assertEqual('They goes . ',partial[0]['original']['text'])
        self.assertEqual(['ref0'],[r['reference_id'] for r in partial[0]['references']])
        self.assertEqual('partial',partial[0]['reference_completeness'])
        self.assertEqual('Second .',partial[1]['references'][0]['text'])
        self.assertEqual(829,self.actual['unchanged_references'])
    def test_mapping_positive(self):
        self.native_pass('TestJFLEGCoarseDifferencePositive','unit.jsonl')
        total=0
        for dataset in self.datasets.values():
            for e in dataset['examples']:
                refs={r['reference_id']:r['text'] for r in e['references']}
                for d in e['derived_differences']:
                    a,b=d['original_codepoint_span'];self.assertEqual(e['original']['text'][a:b],d['original_text'])
                    replay=e['original']['text'][:a]+d['replacement_text']+e['original']['text'][b:]
                    self.assertEqual(refs[d['reference_id']],replay)
                    self.assertEqual('unicode-common-ends-v1',d['method']);total+=1
        self.assertEqual(6004,total);self.assertEqual(6004,self.actual['coarse_replays'])
        self.assertEqual('source_annotation',self.consumer['origins']['jfleg_ref3'])
        self.assertEqual('source_experimental_annotation',self.consumer['origins']['records'])
    def test_mapping_negative(self):
        self.native_pass('TestJFLEGCoarseDifferenceNegative','unit.jsonl')
        self.native_pass('TestSourceJFLEGToolAnnotationPositive','repair-unit.jsonl')
        self.native_pass('TestSourceJFLEGToolAnnotationNegative','repair-unit.jsonl')
        self.assertEqual(19,self.actual['tool_invalid_annotations']);self.assertEqual(5,self.actual['tool_affected_sentences'])
        self.assertEqual(24,self.consumer['tool_findings_retained'])
        self.assertEqual('source_tool_derivation',self.consumer['origins']['edits'])
        for dataset in self.datasets.values():
            for e in dataset['examples']:
                for d in e['derived_differences']:
                    self.assertEqual('not_computed',d['linguistic_alignment']);self.assertEqual('not_supplied',d['category_mapping'])
        self.assertEqual(['source_tool_annotation'],[i['code'] for i in self.actual['report']['issues']])
    def test_resume_positive(self):
        self.complete()
        self.assertGreaterEqual(self.actual['staging_interruption_rows'],128)
        self.assertGreaterEqual(self.actual['mapping_interruption_accepted'],64)
        self.assertTrue(self.actual['accepted_anchor_unchanged']);self.assertTrue(self.actual['reopened_same_cursor'])
        self.assertEqual({'edits':22549,'sentences':1501,'records':1733,'jfleg_source':1501,'jfleg_spellchecked':1501,**{f'jfleg_ref{i}':1501 for i in range(4)}},self.actual['tables'])
    def test_resume_negative(self):
        self.complete()
        self.assertTrue(self.actual['stale_revision_rejected']);self.assertTrue(self.actual['incomplete_commit_rejected'])
        self.assertTrue(self.consumer['readback_import_count_unchanged'])
        self.assertTrue(self.consumer['readback_without_media'])
        self.native_pass('TestNativeSourceMappingCursorNegative','regression.jsonl')
    def test_consumers_positive(self):
        self.native_pass('TestNativeJFLEGConsumerPositive','metadata.jsonl')
        self.native_pass('TestNativeJFLEGCursorPositive','consumers.jsonl')
        self.assertEqual({'dev':754,'test':747},self.consumer['download_counts'])
        self.assertEqual({'pages':8,'distinct_examples':1501,'includes_dev_0':True,'includes_test_746':True},self.read('cursor-observations.json'))
        for part,count in [('dev',754),('test',747)]:
            d=self.verified(f'browser-regression-fixed/downloads/jfleg-{part}-correction-references.json')
            self.assertEqual(count,len(d['examples']));self.assertEqual('CC-BY-NC-SA-4.0',d['licence'])
            self.assertEqual('ee06ff806a208aba815ac45313f4e750a48330a5',d['source_version'])
            self.assertEqual(part,d['source_partition'])
        self.assertTrue(self.browser['reload_same_import']);self.assertLess(self.browser['compact_locator_bytes'],200)
    def test_consumers_negative(self):
        self.native_pass('TestNativeJFLEGConsumerNegative','consumers.jsonl')
        self.assertEqual({'cursor':400,'missing':404,'partition':400},self.read('consumer-negative.json')['statuses'])
        self.assertEqual([503,200],self.browser['transient_statuses'])
        failure=self.browser['failure'];self.assertEqual(20,failure['retained_examples'])
        self.assertEqual('The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.',failure['message'])
        self.assertTrue(failure['raw_payload_absent']);self.assertTrue(failure['refresh_enabled']);self.assertTrue(self.browser['recovered'])
    def test_evaluation_positive(self):
        self.native_pass('TestJFLEGReferenceEvaluationPositive','stable-go.jsonl')
        self.native_pass('TestNativeJFLEGLabPositive','evaluation.jsonl')
        r=self.read('evaluation-positive.json');self.assertEqual(6004,r['rows_checked'])
        self.assertEqual({'logical_examples':1501,'logical_examples_with_outputs':1501,'not_in_reference_set':0,'reference_matches':6004,'submitted_outputs':6004,'unknown_examples':0,'unsubmitted_examples':0},r['totals'])
        self.assertTrue(r['saved_report_readback_equal']);self.assertTrue(r['input_dataset_and_outputs_equal'])
        self.assertTrue(r['input_asset_id']);self.assertEqual(0,r['provider_calls']);self.assertEqual('exact_native_text_v1',r['match_policy'])
    def test_evaluation_negative(self):
        self.native_pass('TestJFLEGReferenceEvaluationNegative','stable-go.jsonl')
        self.native_pass('TestNativeJFLEGLabNegative','evaluation.jsonl')
        r=self.read('evaluation-negative.json');self.assertEqual(0,r['provider_calls'])
        self.assertTrue(r['invalid_payload_no_asset']);self.assertTrue(r['incorrect_grade_absent'])
        self.assertEqual(['not_in_reference_set','unknown_example'],[x['status'] for x in r['report']['rows']])
        for row in r['report']['rows']:
            self.assertEqual([],row['matched_reference_ids']);self.assertEqual('not_run',row['semantic_judgment'])
        self.assertEqual(0,r['report']['totals']['reference_matches'])
    def test_ui_positive(self):
        self.assertEqual('0',(VERIFY/'browser-regression-fixed/exit-code').read_text());self.assertEqual('0',(VERIFY/'browser-visual/exit-code').read_text())
        b=self.browser;self.assertEqual(12,b['source_cards']);self.assertEqual(20,b['initial_examples']);self.assertEqual(40,b['paginated_examples'])
        self.assertTrue(b['keyboard_disclosure']);self.assertEqual({'focused':True,'outline':'solid','width':'3px'},b['focus'])
        self.assertEqual(self.native_expected['lines']['dev/dev.src'][0],b['visible_original'])
        self.assertEqual([self.native_expected['lines'][f'dev/dev.ref{i}'][0] for i in range(4)],b['visible_references'])
        self.assertTrue(b['spellcheck_separate']);self.assertTrue(b['provenance_disclosed'])
        self.assertTrue(self.verified('browser-visual/observations.json')['keyboard_download_focus'])
        for layout in b['layouts']:
            self.assertTrue(layout['fonts_loaded']);self.assertEqual('17px',layout['font_size']);self.assertEqual('24.65px',layout['line_height'])
            self.assertGreaterEqual(layout['button_height'],44)
    def test_ui_negative(self):
        self.assertTrue(self.browser['no_example_before_selection']);self.assertTrue(self.browser['loading_retains_examples'])
        self.assertEqual([],self.browser['page_errors']);self.assertEqual(['GET'],self.browser['application_methods']);self.assertTrue(self.browser['no_model_or_write_requests'])
        self.assertEqual([1280,390,320],[x['viewport'] for x in self.browser['layouts']])
        for row in self.browser['layouts']:self.assertEqual(row['viewport'],row['document_width'])
        requests=self.verified('browser-regression-fixed/requests.json')
        self.assertEqual([503,503,503],[x['status'] for x in requests if x['scenario']=='unavailable'])
        self.assertTrue(all(r['method']=='GET' for r in requests))
        media=self.verified('media-observations.json');self.assertTrue(media['silent']);self.assertFalse(media['cut'])
        self.assertGreater(float(media['probe']['format']['duration']),0)
        self.assertEqual({'video'},{s['codec_type'] for s in media['probe']['streams']})
        for part in ['1280','390','320']:
            png=(VERIFY/f'browser-visual/all-references-{part}.png').read_bytes()
            self.assertEqual(b'\x89PNG\r\n\x1a\n',png[:8]);w,h=struct.unpack('>II',png[16:24]);self.assertGreater(w,200);self.assertGreater(h,400)
    def test_read_order_positive(self):
        self.session_pass('corrections_append_positive','corrections_failure_retains_then_recovers_positive')
        actual=self.verified('browser-green/observations.json')
        self.assertEqual(20,actual['after_superseded_more']);self.assertEqual(40,actual['current_more_after_refresh'])
        self.assertEqual([],actual['page_errors'])
    def test_read_order_negative(self):
        self.session_pass('corrections_refresh_supersedes_more_negative','corrections_old_completion_preserves_loading_negative','corrections_old_error_is_ignored_negative','corrections_disposal_ignores_late_results_negative')
        red=self.verified('browser-red/observations.json');self.assertEqual(40,red['after_superseded_more'])
        green=self.verified('browser-green/observations.json');self.assertEqual(20,green['after_superseded_more']);self.assertEqual([],green['alerts'])
        self.assertEqual('1',(VERIFY/'browser-red/exit-code').read_text());self.assertEqual('0',(VERIFY/'browser-green/exit-code').read_text())
    def test_history_positive(self):
        self.session_pass('history_append_positive','history_positive','history_recovery_negative')
        self.assertIn('# pass 46',(VERIFY/'sessions-green.tap').read_text())
    def test_history_negative(self):
        self.session_pass('history_refresh_supersedes_more_negative','history_refresh_supersedes_error_negative','source_rows_refresh_supersedes_more_negative')
        red=(VERIFY/'history-red.tap').read_text();self.assertRegex(red,r'(?m)^not ok \d+ - history_refresh_supersedes_more_negative')
        self.assertRegex(red,r'(?m)^not ok \d+ - history_refresh_supersedes_error_negative');self.assertEqual(1,int((VERIFY/'history-red-exit-code').read_text()))
    def test_export_recovery_positive(self):
        self.session_pass('corrections_download_survives_refresh_positive')
        actual=self.verified('browser-green/observations.json');self.assertTrue(actual['download_remains_pending_after_refresh'])
        self.assertEqual(754,actual['development_download']);self.assertEqual(747,actual['test_download_recovered'])
        self.assertEqual(1501,actual['downloaded_originals_checked']);self.assertEqual(6004,actual['downloaded_references_checked'])
    def test_export_recovery_negative(self):
        self.session_pass('corrections_download_failure_does_not_hide_examples_negative')
        actual=self.verified('browser-green/observations.json');self.assertEqual(20,actual['download_failure_retains_examples'])
        replies=self.verified('browser-green/requests.json')
        self.assertEqual([503,503,503],[r['status'] for r in replies if r['scenario']=='unavailable' and 'format=dataset&partition=test' in r['path']])
        self.assertEqual({r['method'] for r in replies},{'GET'})
    def test_partial_ui_positive(self):
        rows=[json.loads(line) for line in (VERIFY/'native.jsonl').read_text().splitlines()]
        self.assertTrue(any(r.get('Test')=='TestNativeJFLEGVerifyUIFixtures' and r['Action']=='pass' for r in rows))
        actual=self.verified('browser-green/observations.json')['constructed_views']['partial'];self.assertEqual({'examples':2,'reference_count':1,'refresh_enabled':True},actual)
        example=self.verified('verify-ui-fixtures.json')['partial']['examples'][0]
        self.assertEqual('They goes . ',example['original']['text']);self.assertEqual(['They go . '],[r['text'] for r in example['references']]);self.assertEqual('partial',example['reference_completeness'])
        states=self.verified('browser-states/observations.json');self.assertTrue(states['mobile_navigation_works'])
        self.assertEqual([1280,390,320],[r['width'] for r in states['views'] if r['kind']=='partial'])
    def test_empty_ui_negative(self):
        actual=self.verified('browser-green/observations.json')['constructed_views']['empty'];self.assertEqual({'examples':0,'reference_count':0,'refresh_enabled':True},actual)
        self.assertEqual([],self.verified('verify-ui-fixtures.json')['empty']['examples'])
        rows=[json.loads(line) for line in (VERIFY/'native-commit.jsonl').read_text().splitlines()]
        self.assertTrue(any(r.get('Test')=='TestNativeJFLEGVerifyCommitFixtures' and r['Action']=='pass' for r in rows));self.assertTrue(self.verified('verify-fixtures-commit.json')['published'])
        self.assertEqual('0',(VERIFY/'browser-states/exit-code').read_text())
        states=self.verified('browser-states/observations.json')
        self.assertEqual([1280,390,320],[r['width'] for r in states['views'] if r['kind']=='empty'])
        for layout in states['views']:self.assertEqual(layout['width'],layout['document_width']);self.assertEqual(1,layout['sidebar_count'])

if __name__=='__main__':unittest.main(verbosity=2)
