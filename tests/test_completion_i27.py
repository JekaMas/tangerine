"""Independent I27 oracles over actual native/browser/acquisition observations.

These readers dispatch no network/model/browser work. Missing owner releases or
actual input delivery remain skips and prevent iteration acceptance.
"""
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/iteration-27-sources-20261026'
REVIEW = ROOT/'data/iteration-27-verify-20261026'
IDS = ['TET-GOLD-1', 'SPEECHOCEAN762', 'L2-ARCTIC', 'WILOCNESS-2.1', 'FCE-2.1',
       'EFCAMDAT-R2', 'EFCAMDAT-SHATZ2020', 'EFCAMDAT-OKSUZ2025',
       'DOUBAO-STUDY-RECORDS', 'MOODRICK-DATA', 'NIR-DATA']


def read(path):
    directory = REVIEW if str(path).startswith('browser/') else DATA
    return json.loads((directory/path).read_text())


def events(name):
    directory = REVIEW if str(name).startswith('browser/') else DATA
    return [json.loads(line) for line in (directory/name).read_text().splitlines()
            if line.startswith('{')]


def passed(name):
    return {event.get('Test') for event in events(name) if event.get('Action') == 'pass'}


def review_errors(packet):
    """Development evidence disposition, never an application acceptance gate."""
    errors = []
    for dimension in ['ui_ux', 'typography', 'evidence']:
        if not packet.get(dimension, {}).get('observations'):
            errors.append(dimension+' omitted')
    if packet.get('release_id') != packet.get('report_release_id'):
        errors.append('release/report mismatch')
    if packet.get('claims_full_completion') and packet.get('missing_inputs'):
        errors.append('missing evidence claimed green')
    if packet.get('reference_origin') != 'independently authored literal expectations':
        errors.append('reference origin')
    if packet.get('requested_benchmark_calls', 0):
        errors.append('excluded performance campaign')
    return errors


def packet():
    fixture = read('browser/fixture.json')
    return dict(release_id=fixture['older_release']['id'],
                report_release_id=fixture['older_import']['release_id'],
                claims_full_completion=False,
                missing_inputs=['restricted owner releases', 'actual IAB activation'],
                reference_origin='independently authored literal expectations',
                requested_benchmark_calls=0,
                ui_ux=dict(observations='Actual Sources rendering/reload/focus; input activation remains unobserved.'),
                typography=dict(observations='Actual Source Sans3 17px/24.65px at1280/390/320; no overflow.'),
                evidence=dict(observations='Actual native imports, explicit constructed private fixtures and dated source-access observations.'))


class CompletionI27(unittest.TestCase):
    def test_status_meaning_positive(self):
        values = [json.loads(line) for line in (REVIEW/'status-native.jsonl').read_text().splitlines() if line.startswith('{')]
        self.assertIn('TestNativeSourceStatusMeaningPositive', {row.get('Test') for row in values if row.get('Action') == 'pass'})
        red = (REVIEW/'status-red.jsonl').read_text()
        self.assertIn('want \\\"incomplete\\\"; got \\\"format_unbound\\\"', red)

    def test_status_meaning_negative(self):
        values = [json.loads(line) for line in (REVIEW/'status-native.jsonl').read_text().splitlines() if line.startswith('{')]
        self.assertFalse([row for row in values if row.get('Action') in ['fail', 'skip']])
        self.assertIn('TestNativeSourceStatusMeaningNegative', {row.get('Test') for row in values if row.get('Action') == 'pass'})

    def test_http_diagnostics_positive(self):
        values = [json.loads(line) for line in (REVIEW/'http-native.jsonl').read_text().splitlines() if line.startswith('{')]
        self.assertIn('TestSourceHTTPFailureLoggingPositive', {row.get('Test') for row in values if row.get('Action') == 'pass'})

    def test_http_diagnostics_negative(self):
        values = [json.loads(line) for line in (REVIEW/'http-native.jsonl').read_text().splitlines() if line.startswith('{')]
        self.assertFalse([row for row in values if row.get('Action') in ['fail', 'skip']])
        self.assertIn('TestSourceHTTPFailureMessageNegative', {row.get('Test') for row in values if row.get('Action') == 'pass'})

    def test_sources_positive(self):
        actual = passed('full-native.jsonl')
        for name in ['TestNativeSourceFullFCEPositive', 'TestNativeSourceFullWIPositive']:
            self.assertIn(name, actual)
        self.assertIn('TestNativeSourceFullSpeechOceanPositive', passed('speechocean-final.jsonl'))
        self.assertIn('TestNativeSourcePrivateScopePositive', passed('native-regressions.jsonl'))
        report = read('speechocean-report.json')
        self.assertEqual(('60427', '60427', '0', '0', True, True, []),
                         (report['observed_records'], report['accepted_records'], report['quarantined_records'],
                          report['raw_only_records'], report['raw_complete'], report['normalized_complete'], report['full_release_missing_components']))
        self.assertFalse([issue for issue in report['issues'] if issue['code'] == 'import_failed'])

    def test_sources_negative(self):
        actual = passed('native-regressions.jsonl')
        for name in ['TestNativeSourceCompanionNegative', 'TestNativeSourceMirrorNegative',
                     'TestNativeSourcePrivateScopeNegative', 'TestNativeSourceFullScopeNegative',
                     'TestNativeSourceMissingComponentNegative', 'TestNativeSourceLegacyAssessmentNegative']:
            self.assertIn(name, actual)

    def test_release_lineage_positive(self):
        self.assertIn('TestNativeSourceReleaseLineagePositive', passed('native-regressions.jsonl'))
        fixture = read('browser/fixture.json')
        responses = [e['response'] for e in events('browser/requests.jsonl')
                     if e['path'] == '/api/v1/sources' and e['status'] == 200]
        latest = responses[-1]
        self.assertEqual(IDS, [item['source_id'] for item in latest])
        item = next(item for item in latest if item['source_id'] == 'FCE-2.1')
        mapping = item['release_import_report_ids']
        self.assertEqual([fixture['older_import']['id']], mapping[fixture['older_release']['id']])
        self.assertEqual([fixture['newer_import']['id']], mapping[fixture['newer_release']['id']])
        self.assertNotEqual(mapping[fixture['older_release']['id']], mapping[fixture['newer_release']['id']])

    def test_stored_assessment_positive(self):
        self.assertIn('TestNativeSourceStoredAssessmentPositive', passed('native-regressions.jsonl'))

    def test_stored_assessment_negative(self):
        self.assertIn('TestNativeSourceStoredAssessmentNegative', passed('native-regressions.jsonl'))

    def test_native_regressions_positive(self):
        observed = events('native-regressions.jsonl')
        self.assertFalse([e for e in observed if e.get('Action') in ['fail', 'skip']])
        runs = {e['Test'] for e in observed if e.get('Action') == 'run'}
        expected = json.loads((ROOT/'audit/iteration-27-sources-20261026/NATIVE-SELECTION.json').read_text())['expected_top_level_tests']
        self.assertEqual(set(expected), {name for name in runs if '/' not in name})
        self.assertTrue(runs.issubset(passed('native-regressions.jsonl')))
        self.assertIn(None, passed('native-regressions.jsonl'))
        # The original space-delimited Speech fixture remains a dated receipt.
        # Its changed tab-delimited input is observed freshly after the join fix.
        current = passed('speech-join-repair.jsonl')
        self.assertIn('TestNativeSourceSpeechPositive', current)
        self.assertIn('TestNativeSourceSpeechNegative', current)
        recovery = passed('recovery-final.jsonl')
        self.assertIn('TestNativeSourceReadFailurePositive', recovery)
        self.assertIn('TestNativeSourceReadFailureNegative', recovery)

    def test_saved_permissions_positive(self):
        actual = passed('selection-repair.jsonl')
        for name in ['TestNativeSourceSavedPermissionsPositive', 'TestNativeSourceRightsPositive',
                     'TestNativeSourceRightsNegative', 'TestNativeSourceFrozenPermissionsNegative']:
            self.assertIn(name, actual)

    def test_component_reconciliation_positive(self):
        actual = passed('component-positive.jsonl')
        self.assertIn('TestNativeSourceComponentReconciliationPositive', actual)
        self.assertIn('TestNativeSourceComponentReconciliationPositive/documented_empty_optional_component', actual)
        self.assertIn('TestNativeSourceComponentReconciliationPositive/documented_nonzero_drift', actual)

    def test_pax_archive_positive(self):
        actual = passed('pax-native.jsonl')
        self.assertIn('TestSourceArchivePAXPositive', actual)
        self.assertIn('TestSourceArchivePAXNegative', actual)
        self.assertIn('TestSourceArchiveLimitNegative', actual)
        self.assertFalse([event for event in events('pax-native.jsonl') if event.get('Action') in ['fail', 'skip']])

    def test_kaldi_separator_positive(self):
        actual = passed('kaldi-native.jsonl')
        for name in ['TestSourceKaldiDelimiterPositive', 'TestSourceKaldiDelimiterNegative',
                     'TestSourceKaldiPositive', 'TestSourceKaldiNegative']:
            self.assertIn(name, actual)
        self.assertFalse([event for event in events('kaldi-native.jsonl') if event.get('Action') in ['fail', 'skip']])

    def test_complete_media_scope_negative(self):
        actual = passed('media-scope.jsonl')
        self.assertIn('TestNativeSourceSpeechMediaScopeNegative', actual)
        counts = read('speechocean-native-counts.json')
        self.assertEqual((5245, 5000, 245), (counts['actual_archive_wave_files'], counts['scored_utterances'], counts['additional_unrated_waves']))

    def test_selected_owner_releases_positive(self):
        inventory = json.loads((ROOT/'audit/iteration-27-sources-20261026/ACQUISITIONS.json').read_text())
        selected = ['EFCAMDAT-R2', 'EFCAMDAT-SHATZ2020', 'EFCAMDAT-OKSUZ2025',
                    'DOUBAO-STUDY-RECORDS', 'MOODRICK-DATA', 'NIR-DATA']
        entries = {item['source_id']: item for item in inventory['original_sources']}
        missing = [name for name in selected if not entries[name]['full_native_bytes_acquired']]
        if missing:
            self.skipTest('Actual complete owner releases/dictionaries/terms unavailable: '+', '.join(missing))
        self.assertTrue(all(entries[name]['actual_import_receipt'] for name in selected))

    def test_official_l2_acquisition_positive(self):
        receipt = read('research/l2-official-confirmed.json')
        if receipt['status'] != 'downloaded':
            self.skipTest('Official L2 archive transfer has not completed; no acquired claim.')
        self.assertEqual(('L2-ARCTIC', 'official v5.0', 7515454814),
                         (receipt['source_id'], receipt['source_version'], receipt['bytes']))
        self.assertEqual(7515454814, Path(receipt['path']).stat().st_size)
        inventory = read('research/l2-official-inventory.json')
        self.assertEqual(receipt['sha256'], inventory['archive_sha256'])
        self.assertEqual(24, len(inventory['read_speakers']))
        self.assertEqual(26867, inventory['read_wav_count'])
        self.assertEqual(3599, inventory['read_manual_annotation_count'])
        self.assertEqual(22, inventory['suitcase_wav_count'])
        self.assertEqual('CC BY-NC 4.0', inventory['license'])
        self.assertEqual((29, 25, 84270, 84266), (inventory['outer_archive_members'], inventory['container_archive_count'], inventory['native_file_members'], inventory['speech_data_members']))
        comparison = inventory['mirror_comparison']
        self.assertEqual((84266, 0, 0, True), (comparison['matched'], comparison['missing'], comparison['different'], comparison['all_saved_native_members_match']))
        self.assertEqual(25, len(inventory['component_zip_comparison']['matched']))
        self.assertEqual([], inventory['component_zip_comparison']['different'])
        self.assertFalse(inventory['application_import_observed'])

    def test_review_positive(self):
        self.assertEqual([], review_errors(packet()))
        facts = read('browser/observations.json')
        if not facts['activation_observed']:
            self.skipTest('IAB inputs did not dispatch saved-release/Refresh reads; Chrome selection remains unanswered. Render/reload observations are separate.')
        fixture = read('browser/fixture.json')
        self.assertEqual(fixture['older_release']['id'], facts['opened_release_id'])
        self.assertEqual(fixture['older_import']['id'], facts['opened_import_id'])

    def test_layout_positive(self):
        facts = read('browser/observations.json')
        self.assertEqual([1280, 390, 320], [row['width'] for row in facts['layouts']])
        for row in facts['layouts']:
            self.assertEqual(row['width'], row['pageWidth'])
            self.assertEqual(('17px', '24.65px', True, 11),
                             (row['size'], row['line'], row['fontLoaded'], row['cards']))
            self.assertIn('Source Sans 3', row['font'])
            self.assertTrue(all(int(button['fontSize'][:-2]) >= 13 for button in row['buttons']))

    def test_unavailable_recovery_negative(self):
        facts = read('browser/observations.json')
        error = facts['states']['unavailable']
        self.assertEqual(['The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.'], error['alerts'])
        self.assertNotIn('internal diagnostic', error['main'])
        recovered = facts['states']['recovered']
        self.assertEqual((11, []), (recovered['cards'], recovered['alerts']))
        # Real page navigation/reload is observed; no button-activation claim.

    def test_zero_inference_negative(self):
        requests = events('browser/requests.jsonl')
        self.assertFalse([event for event in requests if event['method'] != 'GET'])
        self.assertEqual(0, read('browser/native-final.json')['provider_receipts'])

    def test_ux_omission_negative(self):
        value = packet(); value.pop('ui_ux')
        self.assertIn('ui_ux omitted', review_errors(value))

    def test_typography_omission_negative(self):
        value = packet(); value.pop('typography')
        self.assertIn('typography omitted', review_errors(value))

    def test_evidence_mismatch_negative(self):
        for update, expected in [({'report_release_id': 'other-release'}, 'release/report mismatch'),
                                 ({'claims_full_completion': True}, 'missing evidence claimed green'),
                                 ({'reference_origin': 'candidate-generated'}, 'reference origin'),
                                 ({'requested_benchmark_calls': 50}, 'excluded performance campaign')]:
            value = copy.deepcopy(packet()); value.update(update)
            self.assertIn(expected, review_errors(value))


if __name__ == '__main__':
    unittest.main(verbosity=2)
