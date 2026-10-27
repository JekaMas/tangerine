"""I37 literal acceptance over actual native/storage/UI observations.

This reconciles retained valid executions; it never launches models, imports or
repeats the full native cohort merely to move workflow stages.
"""
import hashlib, json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/iteration-37-supplements-20261027'
AUDIT = ROOT / 'audit/iteration-37-supplements-20261027'

def read(path):
    return json.loads(path.read_text())

class SpeechSupplements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.native = read(AUDIT / 'NATIVE-EVIDENCE.json')
        cls.actual = {name: read(OUT / (name + '-observations.json')) for name in ['edacc', 'elrd', 'diplomat', 'dral-base', 'dral-8']}
        cls.meaning = read(OUT / 'native-meaning-observations.json')
        cls.consumer = read(OUT / 'consumer-observations.json')
        cls.browser = read(OUT / 'browser/observations.json')
        cls.visual = read(OUT / 'browser-visual/observations.json')

    def native_cases(self, *names):
        for name in names:
            case = self.native['cases'][name]
            receipt = ROOT / case['receipt']
            self.assertEqual(case['receipt_sha256'], hashlib.sha256(receipt.read_bytes()).hexdigest())
            events = [json.loads(line) for line in receipt.read_text().splitlines() if line.strip()]
            self.assertTrue(any((r.get('Test') == name and r.get('Action') == 'pass' for r in events)))
            body = (ROOT / case['source_path']).read_text()
            match = re.search('(?ms)^func ' + re.escape(name) + '\\(.*?(?=^func |\\Z)', body)
            self.assertIsNotNone(match)
            self.assertEqual(case['function_sha256'], hashlib.sha256((match.group().strip()+'\n').encode()).hexdigest())

    def test_acquisition_positive(self):
        self.native_cases('TestSupplementNativePlanPositive', 'TestJFLEGNativePlanPositive', 'TestNativeSourceSourcesPositive', 'TestNativeSupplementFilesPositive', 'TestNativeJFLEGConsumerPositive')
        self.assertEqual(51, self.native['required_unique_go_cases'])
        self.native_cases(*self.native['cases'])
        self.assertEqual(16, self.consumer['source_cards'])
        self.assertEqual({'edacc': 96, 'elrd': 36, 'diplomat': 19, 'dral-base': 10498, 'dral-8': 3086}, read(OUT / 'file-observations.json'))
        for name, count in {'edacc': 96, 'elrd': 36, 'diplomat': 19, 'dral-base': 10498, 'dral-8': 3086}.items():
            self.assertEqual(count, self.actual[name]['retained_files'])
            self.assertTrue(self.actual[name]['report']['raw_complete'])
            self.assertEqual(0, self.actual[name]['model_usage_rows'])
        preservation = read(OUT / 'preservation.json')
        self.assertEqual(11, preservation['original_source_ids'])
        self.assertEqual(6, len(preservation['catalogues']))
        self.assertTrue(all((r['entry_sha256'] == r['current_sha256'] for r in preservation['catalogues'])))

    def test_acquisition_negative(self):
        self.native_cases('TestSupplementNativePlanNegative', 'TestSupplementHistoricalNegative', 'TestNativeSupplementFilesNegative', 'TestNativeSupplementMissingNegative')
        missing = read(OUT / 'missing-observations.json')
        self.assertEqual({'EDACC', 'ELRD', 'DIPLOMAT', 'DRAL'}, set(missing))
        self.assertTrue(all((n > 0 for n in missing.values())))
        self.assertEqual({'missing_release_status': 404, 'script_download': 'inert_attachment', 'script_sandbox': True}, read(OUT / 'file-negative.json'))

    def test_edacc_positive(self):
        self.native_cases('TestSupplementEdAccPositive', 'TestSupplementClockPositive', 'TestNativeSupplementFullEDACC', 'TestNativeSupplementReadbackPositive')
        a = self.actual['edacc']
        self.assertEqual('380098', a['report']['accepted_records'])
        self.assertEqual(19137, a['normalized_examples'])
        self.assertEqual(19137, self.meaning['edacc_keyed_text_joins'])
        self.assertEqual(282416, self.meaning['edacc_separate_asr_rows'])
        self.assertEqual(19137, self.meaning['edacc_reference_examples'])
        self.assertTrue(a['report']['normalized_complete'])
        self.assertEqual([], a['report']['full_release_missing_components'])

    def test_edacc_negative(self):
        self.native_cases('TestSupplementEdAccNegative', 'TestSupplementClockNegative', 'TestNativeSupplementReadbackNegative')
        self.assertEqual(0, read(OUT / 'native-meaning-negative.json')['invented_error_labels']['edacc'])
        self.assertEqual('source_utterance', self.consumer['sources']['edacc']['first_example']['kind'])
        self.assertFalse(self.consumer['sources']['edacc']['first_example']['accent_is_error'])
        self.assertEqual('not_inferred_from_stm_tags', self.consumer['sources']['edacc']['first_example']['background_participant_binding'])

    def test_elrd_positive(self):
        self.native_cases('TestSupplementELRDPositive', 'TestNativeSupplementFullELRD')
        self.assertEqual(589, self.actual['elrd']['normalized_examples'])
        self.assertEqual(589, self.meaning['elrd_asr_turns'])
        first = self.consumer['sources']['elrd']['first_example']
        self.assertEqual('source_asr_transcription', first['text_origin'])
        self.assertEqual({'audio': 'CC-BY-NC-ND-4.0', 'transcript': 'CC-BY-4.0'}, first['source_terms'])
        self.assertEqual('13703/1000', first['local_clock']['end'])
        self.assertTrue(self.consumer['sources']['elrd']['wave_range'])

    def test_elrd_negative(self):
        self.native_cases('TestSupplementELRDNegative', 'TestNativeSupplementReadbackNegative')
        self.assertEqual(0, read(OUT / 'native-meaning-negative.json')['invented_error_labels']['elrd'])
        self.assertEqual('not_supplied', self.consumer['sources']['elrd']['first_example']['error_labels'])
        self.assertIsNone(self.consumer['sources']['elrd']['first_example']['independent_population_count'])

    def test_diplomat_positive(self):
        self.native_cases('TestSupplementDiPlomatPartitionPositive', 'TestNativeSupplementPartitionPositive', 'TestSupplementDiPlomatPositive', 'TestNativeSupplementFullDIPLOMAT', 'TestNativeSupplementViewsPositive', 'TestNativeSupplementReadbackPositive')
        partition = read(OUT / 'partition-observations.json')
        self.assertEqual({'source_train': 29216, 'dev': 1971, 'source_test': 4068}, partition['counts'])
        self.assertEqual(5102, partition['native_nli_train_rows'])
        self.assertEqual(35255, partition['native_fields_unchanged'])
        self.assertEqual(0, partition['unassigned_native_splits'])
        self.assertEqual(35255, self.actual['diplomat']['normalized_examples'])
        self.assertEqual(35255, self.meaning['diplomat_exact_native_tasks'])
        self.assertEqual(6494, self.meaning['diplomat_correct_choice_indices'])
        self.assertEqual(1062, self.meaning['diplomat_paired_test_answers'])
        self.assertTrue(self.browser['native_choice_visible'])
        self.assertEqual(20, read(OUT / 'view-observations.json')['diplomat/PIR_second_subtask_dataset'])

    def test_diplomat_negative(self):
        self.native_cases('TestSupplementDiPlomatPartitionNegative', 'TestSupplementDiPlomatNegative', 'TestNativeSupplementViewsNegative', 'TestNativeSupplementReadbackNegative')
        first = self.consumer['sources']['diplomat']['first_example']
        self.assertIsNone(first['media'])
        self.assertIsNone(first['source_clock'])
        self.assertIsNone(first['independent_population_count'])
        self.assertEqual('DiPlomat_native_not_Tangerine', first['label_namespace'])
        self.assertEqual({'unknown_view_examples': 0, 'unknown_view_next_cursor': ''}, read(OUT / 'view-negative.json'))

    def test_dral_positive(self):
        self.native_cases('TestSupplementDRALPositive', 'TestSupplementDRALWindowPositive', 'TestNativeSupplementFullDRALBASE', 'TestNativeSupplementFullDRAL8', 'TestNativeSupplementWindowPositive', 'TestNativeSupplementReadbackPositive')
        self.assertEqual(10490, self.actual['dral-base']['normalized_examples'])
        self.assertEqual(13596, self.actual['dral-8']['normalized_examples'])
        self.assertEqual(10490, self.meaning['dral_repeated_views'])
        self.assertEqual(10520, self.meaning['dral_base_media_dependencies'])
        self.assertEqual(13294, self.meaning['dral_fragments_separate_clocks'])
        self.assertEqual(30, self.meaning['dral_source_recording_windows'])
        self.assertEqual('283/50', read(OUT / 'window-positive.json')['local_start'])
        self.assertTrue(self.browser['recording_window_visible'])
        self.assertTrue(self.browser['fragment_clocks_visible'])

    def test_dral_negative(self):
        self.native_cases('TestSupplementDRALNegative', 'TestSupplementDRALWindowNegative', 'TestNativeSupplementWindowNegative')
        self.assertEqual({'actual_recording_windows': 30, 'invented_fragment_files': 0, 'native_fragment_absence_retained': True}, read(OUT / 'window-negative.json'))
        baseline = read(OUT / 'native-recording-windows.json')
        self.assertEqual(30, baseline['count'])
        self.assertTrue(all((r['complete_recording_available'] for r in baseline['missing_fragment_files'])))
        self.assertEqual(0, read(OUT / 'native-meaning-negative.json')['invented_error_labels']['dral-8'])

    def test_persistence_positive(self):
        self.native_cases('TestNativeSupplementPersistencePositive', 'TestNativeSourceAdmittedReusePositive', 'TestNativeSourceMappingCursorPositive')
        p = read(OUT / 'persistence-observations.json')
        self.assertEqual(5, p['reopened_complete_imports'])
        self.assertEqual(192, p['accepted_rows_predating_mapping_failure'])
        self.assertTrue(p['source_versions_retained'])
        self.assertEqual('source-native-supplements-v1', p['frozen_parser'])
        self.assertTrue(all(read(OUT / 'edacc-recovery.json').values()))
        self.assertTrue(self.consumer['readback_import_count_unchanged'])
        self.assertTrue(all((r['read_without_media'] for r in self.consumer['sources'].values())))

    def test_persistence_negative(self):
        self.native_cases('TestNativeSupplementPersistenceNegative', 'TestNativeSourceAdmittedFailureNegative', 'TestNativeSourceMappingCursorNegative')
        self.assertEqual({'saved_counts_and_revisions_unchanged': True, 'stale_completed_revisions_rejected': 5}, read(OUT / 'persistence-negative.json'))
        self.assertTrue(read(OUT / 'edacc-recovery.json')['incomplete_commit_rejected'])
        self.assertTrue(read(OUT / 'edacc-recovery.json')['stale_revision_rejected'])
        self.assertEqual(0, read(OUT / 'native-meaning-negative.json')['model_usage_rows'])

    def test_consumers_positive(self):
        self.native_cases('TestNativeSupplementConsumerPositive', 'TestNativeSupplementCursorPositive', 'TestNativeSupplementFilesPositive', 'TestNativeSupplementViewsPositive')
        b = self.browser
        self.assertEqual({'edacc', 'elrd', 'diplomat', 'dral-base', 'dral-8'}, set(b['sources']))
        self.assertEqual(15, len(b['layouts']))
        self.assertEqual(15, len(self.visual['views']))
        for layout in b['layouts']:
            self.assertEqual('17px', layout['font_size'])
            self.assertTrue(layout['fonts_loaded'])
            self.assertEqual(layout['width'], layout['document_width'])
        self.assertTrue(b['finite_playback']['paused'])
        self.assertGreaterEqual(b['finite_playback']['time'], 13.703)
        self.assertLess(b['finite_playback']['time'], 14.5)
        window = read(OUT / 'browser-window/observations.json')
        self.assertEqual([5.66, 9.81], window['expected_interval'])
        self.assertGreaterEqual(window['started']['time'], 5.66)
        self.assertFalse(window['started']['paused'])
        self.assertTrue(window['ended']['paused'])
        self.assertGreaterEqual(window['ended']['time'], 9.81)
        self.assertLess(window['ended']['time'], 10.5)
        self.assertEqual('none', window['preload'])
        self.assertEqual(40, b['paginated_examples'])
        self.assertTrue(b['reopen_same_import'])
        self.assertTrue(b['original_container_link'])
        self.assertEqual([], b['page_errors'])
        self.assertEqual(['GET'], b['application_methods'])
        self.assertTrue(b['no_model_or_write_requests'])
        for file in ['speech-supplements-demo.mp4', 'dral-original-dialogue-fragment.wav', 'browser-visual/edacc-320-body.png', 'browser-visual/diplomat-320-answer.png', 'browser-visual/recording-window-320.png']:
            self.assertTrue((OUT / file).is_file())

    def test_consumers_negative(self):
        self.native_cases('TestNativeSupplementConsumerNegative', 'TestNativeSupplementViewsNegative', 'TestNativeSupplementFilesNegative')
        self.assertEqual({'missing_import_status': 404, 'invalid_cursor_status': 400, 'sources_checked': 5, 'raw_backend_detail': False}, read(OUT / 'consumer-negative.json'))
        b = self.browser
        self.assertEqual([503, 200], b['transient_statuses'])
        self.assertEqual(20, b['failure']['retained_examples'])
        self.assertTrue(b['failure']['refresh_enabled'])
        self.assertEqual('The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.', b['failure']['message'])
        self.assertTrue(b['loading_retains_examples'])
        self.assertTrue(b['recovered'])
        self.assertTrue(b['controlled_empty_view'])
        self.assertTrue(b['file_failure_retains_links'])
        self.assertEqual([], b['page_errors'])
if __name__ == '__main__':
    unittest.main()
