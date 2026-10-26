"""Current native/CUA content oracles plus scoped retained owner observations."""
import ast
import copy
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/iteration-21-verify-20261026'
OLD = ROOT / 'data/iteration-21-guided-tools-20261026'
AUDIT = ROOT / 'audit/iteration-21-guided-tools-20261026'
SPEC = importlib.util.spec_from_file_location('verify21_review', AUDIT / 'verify_review.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


def load(name):
    return json.loads((DATA / name).read_text())


def disabled(case, name):
    return next(x['disabled'] for x in case['buttons'] if x['text'] == name)


class Iteration21Verify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = load('observations.json')
        cls.c = cls.facts['cases']
        cls.old = json.loads((OLD / 'observations.json').read_text())['cases']
        cls.fixture = load('native-fixture.json')
        cls.native = load('native-final.json')
        cls.events = [json.loads(x) for x in (DATA / 'requests.jsonl').read_text().splitlines()]
        cls.writes = [json.loads(x) for x in (DATA / 'native-write-responses.jsonl').read_text().splitlines()]

    def calls(self, scenario=None, path=None, method=None):
        return [x for x in self.events if x['event'] == 'request'
                and (scenario is None or x['scenario'] == scenario)
                and (path is None or x['path'] == path)
                and (method is None or x['method'] == method)]

    def helper(self, filename, method, owner):
        raw = (DATA / filename).read_text()
        self.assertTrue(raw.rstrip().endswith('OK'))
        self.assertRegex(raw, r'test_' + method + r' \([^\n]*' + owner + r'\.test_' + method + r'\) \.\.\. ok')

    def test_starter_positive(self):
        c = self.c['nativeReport']
        self.assertIn('Report saved.', c['statuses'])
        self.assertIn('Weekend park collocations', c['headings'])
        self.assertIn('125/1', c['main'])
        self.assertEqual('', c['inputs']['Report definition']['value'])
        sent = self.calls('native-current', '/api/v1/reports/empirical', 'POST')[0]['body']
        self.assertEqual('constructed', sent['input']['population']['label_origin'])
        windows = sent['input']['windows']
        self.assertEqual(['We did a decision.', 'We made a decision.'], [w['id'] for w in windows])
        self.assertEqual([1, 0], [len(w['events']) for w in windows])
        self.assertEqual([4, 4], [w['native_tokens'] for w in windows])
        self.assertEqual(125, 1000 // sum(w['native_tokens'] for w in windows))

    def test_named_form_positive(self):
        a, b = self.c['nativeNamedReport'], self.c['nativeReopened']
        self.assertEqual(load('current-report.json')['id'], a['inputs']['Report data']['value'])
        sent = self.calls('native-current', '/api/v1/reports/empirical', 'POST')[1]['body']
        expected = load('native-report-input.json')
        expected['title'] = 'Reused park population'
        self.assertEqual(expected, sent)
        self.assertIn('Reused park population', b['headings'])
        self.assertIn('125/1', b['main'])
        self.assertIn('Experiment ' + load('current-reused-experiment.json')['id'], b['headings'])

    def test_saved_dataset_freeze_positive(self):
        a, b = load('current-experiment.json'), load('current-reused-experiment.json')
        self.assertEqual(load('native-first-dataset.json'), load('native-reused-dataset.json'))
        self.assertEqual(a['dataset_sha256'], b['dataset_sha256'])
        sent = self.calls('native-current', '/api/v1/lab/experiments', 'POST')
        self.assertEqual(a['dataset_asset_id'], sent[1]['body']['experiment']['dataset_asset_id'])
        self.assertEqual({'config', 'bundle'}, set(sent[1]['body']['assets']))
        request = sent[0]['body']['assets']['input']
        self.assertEqual(['Making plans for a riverside picnic', 75, 'B2'],
                         [request['topic'], request['text_length_words'], request['english_level']])
        frozen = load('native-frozen-config.json')
        self.assertEqual('deepseek-flash-low-v1', frozen['stage_profiles']['case_generation'])
        self.assertEqual('deepseek-flash-low-v1', frozen['llm_profile'])
        case = load('native-first-dataset.json')['cases'][0]
        self.assertEqual('constructed', case['origin'])
        self.assertEqual('authored_assertion', case['expectation_basis'])
        self.assertEqual([], case['reference_receipt_ids'])

    def test_invalid_starter_negative(self):
        c = self.c['invalidAdvanced']
        self.assertEqual('{', c['inputs']['Report definition']['value'])
        self.assertIn('Report definition is not valid JSON. Your input is retained.', c['alerts'])
        self.assertEqual({'active': 'Report title', 'invalid': ['Report title']}, self.c['requiredTitle'])
        self.assertTrue(all(x['body']['title'].strip() for x in self.calls(path='/api/v1/reports/empirical', method='POST')))

    def test_empty_workspace_negative(self):
        c = self.c['emptyWorkspace']
        self.assertIn('No saved populations yet.', c['main'])
        self.assertIn('No generation model is configured.', c['main'])
        self.assertIn('This constructed example has one mistake and one correct use.', c['main'])
        self.assertFalse(disabled(c, 'Calculate report from selection'))
        self.assertTrue(disabled(c, 'Save starter experiment'))
        self.assertEqual('', c['inputs']['Report data']['value'])
        self.assertEqual('', c['inputs']['Experiment dataset']['value'])

    def test_options_recovery_positive(self):
        for key in ['optionsFailure', 'optionsRecovered']:
            c = self.c[key]
            self.assertEqual('Keep the option retry request', c['inputs']['Experiment topic']['value'])
            self.assertEqual('C1', c['inputs']['Experiment English level']['value'])
            self.assertFalse(disabled(c, 'Calculate report from selection'))
        self.assertIn('Configured experiment choices are unavailable. Retry or open Settings. Your input is retained.', self.c['optionsFailure']['alerts'])
        self.assertFalse(disabled(self.c['optionsRecovered'], 'Save starter experiment'))

    def test_save_recovery_positive(self):
        for key in ['nativeSaveFailure', 'nativeSaveRecovered']:
            self.assertEqual('Retained park report after failure', self.c[key]['inputs']['Report title']['value'])
            self.assertIn('125/1', self.c[key]['main'])
            self.assertNotIn('private backend detail', self.c[key]['main'])
        self.assertEqual(1, len(self.calls('native-save-failure', method='POST')))
        self.assertEqual([], self.c['nativeSaveRecovered']['alerts'])
        self.assertIn('Report saved.', self.c['savedBeforeList']['statuses'])
        self.assertIn('Loading saved reports…', self.c['savedBeforeList']['statuses'])
        self.assertFalse(disabled(self.c['savedBeforeList'], 'Calculate report from selection'))
        self.assertFalse(disabled(self.c['savedBeforeList'], 'Save starter experiment'))

    def test_file_import_positive(self):
        sent = [x['body'] for x in self.calls('native-current', '/api/v1/reports/empirical', 'POST')
                if x['body']['title'] == 'Imported park observation']
        self.assertEqual([load('imported-report.json')], sent)
        c = self.c['nativeFileImport']
        self.assertEqual(load('imported-report.json'), json.loads(c['inputs']['Report definition']['value']))
        self.assertIn('Imported park observation', c['headings'])

    def test_missing_selected_dataset_negative(self):
        c = self.c['missingSelectedDataset']
        self.assertEqual(load('current-experiment.json')['id'], c['inputs']['Experiment dataset']['value'])
        self.assertIn('The selected saved dataset is unavailable. Refresh choices or select a new request. Your input is retained.', c['alerts'])
        self.assertFalse(self.calls('selected-dataset-missing-final', method='POST'))

    def test_cleanup_positive(self):
        first, second = self.fixture['first_attempt'], self.fixture['second_attempt']
        c = self.c['nativePreview']
        self.assertEqual(first, c['inputs']['Deletion subjects']['value'])
        self.assertFalse(c['inputs']['Confirm deletion']['checked'])
        self.assertTrue(disabled(c, 'Apply deletion'))
        self.assertIn('Deletion complete · 2 documents · 0 private objects', self.c['nativeApplied']['statuses'])
        self.assertFalse(self.native['first_attempt_present'])
        self.assertTrue(self.native['second_attempt_present'])
        self.assertTrue(self.native['shared_audio_present'])
        c = self.c['nativeCleanupReopened']
        self.assertIn('Select Café opening · attempt · ' + second, c['inputs'])
        self.assertNotIn('Select Café opening · attempt · ' + first, c['inputs'])
        applies = [x for x in self.calls(method='POST') if x['path'].endswith(':apply')]
        self.assertEqual(1, len(applies))
        applied = next(x['body'] for x in self.writes if x['path'].endswith(':apply'))
        self.assertEqual([first], applied['heads'])
        self.assertNotIn(second, applied['documents'])
        self.assertEqual([], applied['assets'])

    def test_cleanup_identity_negative(self):
        c = self.c['nativeSelectionChanged']
        self.assertEqual('', c['inputs']['Deletion subjects']['value'])
        self.assertNotIn('Confirm deletion', c['inputs'])
        self.assertFalse(any(x['text'] == 'Apply deletion' for x in c['buttons']))
        c = self.c['nativeShortFinal']
        self.assertEqual(self.fixture['first_attempt'][:8], c['inputs']['Deletion subjects']['value'])
        self.assertIn('Selection needs attention · 0 documents · 0 private objects', c['statuses'])
        self.assertFalse(any(x['text'] == 'Apply deletion' for x in c['buttons']))
        self.assertIn('check the full IDs', c['main'])
        self.assertIn('Selection needs attention', self.c['nativeBlockedFinal']['main'])

    def test_cleanup_race_negative(self):
        self.helper('cleanup-owner-final.log', 'old_preview_negative', 'CleanupSession')
        self.helper('cleanup-owner-final.log', 'obsolete_error_negative', 'CleanupSession')
        self.assertNotIn('Confirm deletion', self.c['cleanupPending']['inputs'])

    def test_cleanup_list_recovery_positive(self):
        # RecordPicker/useSavedList and these exact list-adapter branches are unchanged.
        a, b = self.old['cleanupListFailure'], self.old['cleanupListRecovery']
        self.assertTrue(a['previewEnabled'])
        self.assertEqual(a['inputs']['Deletion subjects']['value'], b['inputs']['Deletion subjects']['value'])
        self.assertEqual([], b['alerts'])

    def test_cleanup_pagination_positive(self):
        old_fixture = json.loads((OLD / 'native-fixture.json').read_text())
        c = self.old['cleanupPageTwo']
        self.assertIn(old_fixture['first_attempt'], c['main'])
        self.assertIn(old_fixture['second_attempt'], c['main'])
        self.assertEqual(old_fixture['first_attempt'], c['inputs']['Deletion subjects']['value'])

    def test_cleanup_empty_positive(self):
        self.assertIn('No saved records.', self.old['cleanupEmptyFinal']['main'])
        self.assertIn('Prepare an exercise', self.old['cleanupEmptyFinal']['main'])
        self.assertFalse(any(k.startswith('Select ') for k in self.old['cleanupEmptyFinal']['inputs']))

    def test_keyboard_layout_positive(self):
        rows = self.facts['layouts']
        self.assertEqual({(route, width) for route in ['reports', 'cleanup'] for width in [1280, 390, 320]},
                         {(x['route'], x['width']) for x in rows})
        for row in rows:
            self.assertFalse(row['overflow'])
            self.assertEqual(['17px', '24.65px'], [row['bodySize'], row['bodyLine']])
            self.assertTrue(row['loaded'])
            for b in row['buttons']:
                self.assertGreaterEqual(b['height'], 44)
                self.assertGreaterEqual(float(b['font'].removesuffix('px')), 13)
        self.assertEqual(['true', 'false'], [self.c['mobileMenuOpen'], self.c['mobileMenuClosed']])
        k = self.c['keyboard']
        self.assertEqual('3px', k['outline'])
        self.assertGreaterEqual(k['top'], 0)
        self.assertLessEqual(k['bottom'], k['height'])

    def test_catalogue_scope_positive(self):
        c = self.c['metricLabels']
        self.assertEqual(122, len(c['rows']))
        self.assertEqual(122, len({row.split('\t')[0] for row in c['rows']}))
        self.assertIn('Not annotated', c['main'])
        self.assertNotIn('leaf_annotation_scope_not_declared', c['main'])
        self.assertNotIn('correct_opportunity_annotations_absent', c['main'])
        self.assertIn('125/1', c['main'])

    def test_zero_dispatch_negative(self):
        self.assertEqual(0, self.native['provider_receipts'])
        self.assertFalse(any(x['event'] in ['forbidden_execution', 'fixture_error'] for x in self.events))
        self.assertEqual(2, len(self.native['experiments']))
        for exp in self.native['experiments']:
            self.assertEqual('planned', exp['status'])
            for row in exp['rows']:
                self.assertEqual('not_run', row['status'])
                self.assertEqual([], row['receipt_ids'])
                self.assertIsNone(row['output_asset_id'])
        self.assertTrue(all(x['path'] in ['/api/v1/reports/empirical', '/api/v1/lab/experiments', '/api/v1/deletions']
                            or x['path'].startswith('/api/v1/deletions/') and x['path'].endswith(':apply')
                            for x in self.calls(method='POST')))

    def test_native_receipt_positive(self):
        self.assertEqual('0', (DATA / 'native-exit-code').read_text())
        events = [json.loads(x) for x in (DATA / 'native.jsonl').read_text().splitlines()]
        self.assertEqual(['TestGuidedToolsNativeFixture'], [x['Test'] for x in events if x['Action'] == 'pass' and x.get('Test')])
        self.assertFalse(any(x['Action'] == 'fail' for x in events))

    def test_retained_helper_receipts_positive(self):
        source = json.loads((AUDIT / 'VERIFY-SOURCE.json').read_text())
        for name, expected in source['helper_dependencies'].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), name)
        groups = [('reports-session-green.log', 'tests/test_reports_session.py', 17),
                  ('cleanup-owner-final.log', 'tests/test_cleanup_session.py', 15),
                  ('starters-green.log', 'tests/test_guided_starters.py', 7)]
        for receipt, filename, count in groups:
            expected = {n.name for n in ast.walk(ast.parse((ROOT / filename).read_text()))
                        if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
            raw = (DATA / receipt).read_text()
            actual = set(re.findall(r'^(test_\w+) \([^\n]+\) \.\.\. ok$', raw, re.M))
            self.assertEqual(count, len(expected))
            self.assertEqual(expected, actual)
            self.assertTrue(raw.rstrip().endswith('OK'))
        for name in ['constructed_report_positive', 'portable_experiment_positive', 'independent_asset_hashes_positive',
                     'no_semantic_gold_invented_negative', 'invalid_fields_negative', 'selected_generation_binding_positive']:
            self.helper('existing-starters-green.log', name, 'FinalFunctionalHelpers')

    def test_report_retry_positive(self):
        old = self.facts['baseline']['reportAfterRefresh']
        self.assertNotIn('I21 · Picnic collocations', old['headings'])
        self.assertIn('I21 · Picnic collocations', self.c['reportRecovered']['headings'])
        self.assertEqual([], self.c['reportRecovered']['alerts'])
        self.assertFalse(disabled(self.c['readDoesNotBlock'], 'Calculate report from selection'))
        self.assertFalse(disabled(self.c['readDoesNotBlock'], 'Save starter experiment'))
        a = json.loads((DATA / 'constructed-report.json').read_text())
        self.assertEqual(1, len(self.calls('fixed-report-refresh', '/api/v1/reports/empirical/' + a['id'])))

    def test_old_refresh_negative(self):
        expected = 'Experiment ' + load('reused-experiment.json')['id']
        self.assertIn(expected, self.c['afterOldRefresh']['headings'])
        self.assertEqual(self.c['newerRun']['headings'], self.c['afterOldRefresh']['headings'])
        self.assertNotEqual(self.facts['baseline']['newerRun']['headings'], self.facts['baseline']['overwrittenRun']['headings'])

    def test_comparison_isolation_positive(self):
        c = self.c['comparisonFailure']
        self.assertIn('Experiment ' + load('first-experiment.json')['id'], c['headings'])
        self.assertIn('The saved experiment remains usable.', ' '.join(c['alerts']))
        self.assertFalse(disabled(c, 'Save starter experiment'))
        self.assertFalse(disabled(c, 'Run experiment'))
        self.assertNotIn('private backend detail', c['main'])

    def test_comparison_retry_positive(self):
        calls = self.calls('fixed-comparison-retry')
        self.assertEqual(['/api/v1/lab/assets/i21-comparison'], [x['path'] for x in calls])
        self.assertEqual([], self.c['comparisonRecovered']['alerts'])
        self.assertIn('Experiment ' + load('first-experiment.json')['id'], self.c['selectedRecovered']['headings'])

    def test_pending_confirmation_negative(self):
        self.assertTrue(self.facts['baseline']['confirmAfterReplacement']['inputs']['Confirm deletion']['checked'])
        self.assertFalse(self.c['cleanupReplacement']['inputs']['Confirm deletion']['checked'])
        self.assertTrue(disabled(self.c['cleanupReplacement'], 'Apply deletion'))
        self.assertNotIn('Confirm deletion', self.c['cleanupFailure']['inputs'])
        self.assertFalse(self.c['cleanupRecovered']['inputs']['Confirm deletion']['checked'])

    def test_unavailable_profile_negative(self):
        for key in ['profileUnavailable', 'profileRecovered']:
            c = self.c[key]
            self.assertEqual('deepseek-flash-low-v1', c['inputs']['Experiment LLM profile']['value'])
            self.assertEqual('Keep this request while a model needs setup', c['inputs']['Experiment topic']['value'])
            self.assertEqual('C1', c['inputs']['Experiment English level']['value'])
        self.assertIn('Choose a configured LLM profile with a generation model. Update Settings or select another profile.', self.c['profileUnavailable']['alerts'])
        self.assertFalse(self.calls('profile-unavailable-final', method='POST'))

    def test_missing_item_negative(self):
        c = self.c['missingItem']
        self.assertIn('This saved item is no longer available. Choose another saved item or create a new one.', c['alerts'])
        self.assertFalse(disabled(c, 'Calculate report from selection'))
        self.assertFalse(disabled(c, 'Save starter experiment'))

    def test_record_identity_positive(self):
        for row in self.facts['layouts']:
            if row['route'] != 'reports':
                continue
            records = row['records']
            self.assertEqual(6, len(records))
            self.assertEqual(6, len({x['text'] for x in records}))
            for record in records:
                self.assertEqual('column', record['direction'])
                self.assertGreaterEqual(float(record['identityFont'].removesuffix('px')), 14)
                self.assertLessEqual(record['width'], row['width'])

    def packet(self):
        return json.loads((AUDIT / 'VERIFY-REVIEW.json').read_text())

    def errors(self, packet, facts=None, fixture=None):
        return review.review_errors(packet, facts or self.facts, fixture or self.fixture)

    def test_review_positive(self):
        self.assertEqual([], self.errors(self.packet()))

    def test_ux_omission_negative(self):
        p = self.packet()
        p.pop('ui_ux')
        self.assertTrue(self.errors(p))
        p = self.packet()
        p['ui_ux']['references'] = ['data/iteration-21-verify-20261026/web-build-closed.log']
        self.assertTrue(self.errors(p))

    def test_typography_omission_negative(self):
        p = self.packet()
        p.pop('typography')
        self.assertTrue(self.errors(p))
        for name, value in [('bodySize', '10px'), ('overflow', True)]:
            f = copy.deepcopy(self.facts)
            f['layouts'][0][name] = value
            self.assertTrue(self.errors(self.packet(), facts=f))

    def test_evidence_mismatch_negative(self):
        n = copy.deepcopy(self.fixture)
        n['first_attempt'] = n['second_attempt']
        self.assertTrue(self.errors(self.packet(), fixture=n))
        for name, value in [('unexecuted_cases', ['planned']), ('reference_origin', 'candidate gold'),
                            ('new_model_calls', 50), ('performance_campaigns', 'required')]:
            p = self.packet()
            p[name] = value
            self.assertTrue(self.errors(p))


if __name__ == '__main__':
    unittest.main(verbosity=2)
