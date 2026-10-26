"""Literal oracles for current CUA and real disposable native observations.

These inspect saved observations; they never start an experiment or another
browser/stack. Constructed input is not a learner population or model result.
"""
import copy
import importlib.util
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/iteration-21-guided-tools-20261026'
AUDIT = ROOT / 'audit/iteration-21-guided-tools-20261026'
SPEC = importlib.util.spec_from_file_location('i21_review', AUDIT / 'review.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)
ROW = 'lexis.collocation\t1\t1/1\t1/2\t1/2\t125/1'


def read(name):
    return json.loads((DATA / name).read_text())


def button(case, name):
    return next(row for row in case['buttons'] if row['text'] == name)


class CompletionI21(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = read('observations.json')
        cls.c = cls.facts['cases']
        cls.fixture = read('native-fixture.json')
        cls.final = read('native-final.json')
        cls.events = [json.loads(x) for x in (DATA / 'requests.jsonl').read_text().splitlines()]
        cls.writes = [json.loads(x) for x in (DATA / 'native-write-responses.jsonl').read_text().splitlines()]

    def table(self, name, title='Empirical category measurements'):
        return next(t['rows'] for t in self.c[name]['tables'] if t['name'] == title)

    def requests(self, scenario=None, path=None, method=None):
        return [x for x in self.events if x['event'] == 'request'
                and (scenario is None or x['scenario'] == scenario)
                and (path is None or x['path'] == path)
                and (method is None or x['method'] == method)]

    def test_starter_positive(self):
        c = self.c['constructedReport']
        self.assertIn('Report saved.', c['statuses'])
        self.assertEqual([ROW], self.table('constructedReport'))
        self.assertEqual('I21 · Picnic collocations', c['inputs']['Report title']['value'])
        self.assertTrue(all(not row['open'] for row in c['advanced']))
        self.assertEqual('', c['inputs']['Report definition']['value'])
        report = read('constructed-report.json')
        self.assertEqual('I21 · Picnic collocations', report['title'])
        submission = self.requests('native-populated', '/api/v1/reports/empirical', 'POST')[0]['body']
        windows = submission['input']['windows']
        self.assertEqual(['We did a decision.', 'We made a decision.'], [w['id'] for w in windows])
        self.assertEqual([4, 4], [w['native_tokens'] for w in windows])
        self.assertEqual([1, 1], [w['opportunities']['lexis.collocation'] for w in windows])
        self.assertEqual([1, 0], [len(w['events']) for w in windows])
        self.assertEqual('constructed', submission['input']['population']['label_origin'])
        self.assertEqual([], submission['attempts'])
        # Independent arithmetic: one event / two windows/opportunities, 1/8*1000.
        self.assertEqual(125, 1000 // sum(w['native_tokens'] for w in windows))

    def test_named_form_positive(self):
        c = self.c['namedReport']
        first = read('constructed-report.json')
        self.assertEqual(first['id'], c['inputs']['Report data']['value'])
        submission = self.requests('native-populated', '/api/v1/reports/empirical', 'POST')[1]['body']
        expected = read('report-input.json')
        expected['title'] = 'I21 · Saved Picnic population'
        self.assertEqual(expected, submission)
        self.assertEqual([ROW], self.table('namedReport'))
        self.assertEqual([ROW], self.table('reopenedReport'))
        self.assertIn('I21 · Saved Picnic population', self.c['reopenedReport']['main'])
        self.assertTrue(all(not row['open'] for row in c['advanced']))
        for key in ['newExperiment', 'reusedExperiment']:
            self.assertEqual('', self.c[key]['inputs']['Experiment definition']['value'])
            self.assertIn('Experiment saved. Run it when you choose.', self.c[key]['statuses'])

    def test_saved_dataset_freeze_positive(self):
        first, reused = read('first-experiment.json'), read('reused-experiment.json')
        original, resolved = read('first-dataset.json'), read('reused-dataset.json')
        self.assertEqual(original, resolved)
        self.assertEqual(first['dataset_sha256'], reused['dataset_sha256'])
        sent = self.requests('native-populated', '/api/v1/lab/experiments', 'POST')
        self.assertEqual(first['dataset_asset_id'], sent[1]['body']['experiment']['dataset_asset_id'])
        self.assertEqual({'bundle', 'config'}, set(sent[1]['body']['assets']))
        data = sent[0]['body']['assets']['input']
        self.assertEqual('I21 picnic plans at the museum café', data['topic'])
        self.assertEqual(75, data['text_length_words'])
        self.assertEqual('B2', data['english_level'])
        frozen = read('frozen-config.json')
        self.assertEqual('deepseek-flash-low-v1', frozen['stage_profiles']['case_generation'])
        self.assertEqual('deepseek-flash-low-v1', frozen['llm_profile'])
        self.assertEqual({k: None for k in ['adjudication', 'blind_claim_extraction', 'case_review',
                                          'claim_mapping', 'feedback', 'linguistic_audit', 'mapping_audit']},
                         {k: v for k, v in frozen['stage_profiles'].items() if k != 'case_generation'})
        case = original['cases'][0]
        self.assertEqual(['constructed', 'authored_assertion', 'development'],
                         [case['origin'], case['expectation_basis'], case['split']])
        self.assertEqual([], case['reference_receipt_ids'])
        self.assertIn('planned · 0/1 completed', self.c['reopenedExperiment']['statuses'])
        self.assertIn(reused['id'], self.c['reopenedExperiment']['main'])

    def test_invalid_starter_negative(self):
        c = self.c['invalidAdvanced']
        self.assertEqual('{', c['inputs']['Report definition']['value'])
        self.assertIn('Report definition is not valid JSON. Your input is retained.', c['alerts'])
        self.assertTrue(all(x['body']['title'].strip() for x in self.requests(path='/api/v1/reports/empirical', method='POST')))
        self.assertEqual({'active': 'Report title', 'invalid': ['Report title'], 'alerts': []},
                         self.c['requiredTitle'])

    def test_empty_workspace_negative(self):
        c = self.c['emptyWorkspaceFinal']
        self.assertIn('This constructed example has one mistake and one correct use.', c['main'])
        self.assertIn('No saved populations yet.', c['main'])
        self.assertIn('No generation model is configured.', c['main'])
        self.assertFalse(button(c, 'Calculate report from selection')['disabled'])
        self.assertTrue(button(c, 'Save starter experiment')['disabled'])
        self.assertEqual('', c['inputs']['Experiment dataset']['value'])
        self.assertEqual('', c['inputs']['Report data']['value'])
        self.assertEqual([], c['tables'])

    def test_options_recovery_positive(self):
        for key in ['choicesFailure', 'choicesRecovery']:
            c = self.c[key]
            self.assertEqual('Keep the picnic topic during option failures', c['inputs']['Experiment topic']['value'])
            self.assertEqual('C1', c['inputs']['Experiment English level']['value'])
            self.assertEqual('deepseek-flash-low-v1', c['inputs']['Experiment LLM profile']['value'])
        self.assertEqual([], self.c['choicesRecovery']['alerts'])
        c = self.c['initialChoicesFailure']
        self.assertIn('Configured experiment choices are unavailable. Retry or open Settings. Your input is retained.', c['alerts'])
        self.assertFalse(button(c, 'Calculate report from selection')['disabled'])
        for key in ['initialChoicesFailure', 'initialChoicesRecovered']:
            self.assertEqual('Keep this request while configuring a model', self.c[key]['inputs']['Experiment topic']['value'])
        self.assertEqual([], self.c['initialChoicesRecovered']['alerts'])
        self.assertFalse(button(self.c['initialChoicesRecovered'], 'Save starter experiment')['disabled'])

    def test_save_recovery_positive(self):
        for key in ['saveFailure', 'saveRecovered']:
            self.assertEqual('I21 retained report after save failure', self.c[key]['inputs']['Report title']['value'])
            self.assertEqual([ROW], self.table(key))
            self.assertNotIn('private backend detail', self.c[key]['main'])
        self.assertIn('Your inputs and saved observations are retained.', self.c['saveFailure']['alerts'][0])
        self.assertEqual(1, len(self.requests('report-save-failure', method='POST')))
        self.assertEqual([], self.c['saveRecovered']['alerts'])
        self.assertIn('Report saved.', self.c['saveRecovered']['statuses'])

    def test_file_import_positive(self):
        sent = self.requests('advanced-file', '/api/v1/reports/empirical', 'POST')
        self.assertEqual([read('file-report-definition.json')], [x['body'] for x in sent])
        definition = json.loads(self.c['fileSaved']['inputs']['Report definition']['value'])
        self.assertEqual('I21 · Advanced file population', definition['title'])
        self.assertIn('Report saved.', self.c['fileSaved']['statuses'])
        self.assertIn('I21 · Advanced file population', self.c['fileSaved']['main'])

    def test_missing_selected_dataset_negative(self):
        c = self.c['missingSelectedDataset']
        self.assertEqual(read('first-experiment.json')['id'], c['inputs']['Experiment dataset']['value'])
        self.assertIn('The selected saved dataset is unavailable. Refresh choices or select a new request. Your input is retained.', c['alerts'])
        self.assertFalse(self.requests('selected-dataset-unavailable', method='POST'))

    def test_cleanup_positive(self):
        first, second = self.fixture['first_attempt'], self.fixture['second_attempt']
        preview = json.loads(self.c['cleanupPreview']['details'])
        self.assertEqual([first], preview['heads'])
        self.assertIn(first, preview['documents'])
        self.assertNotIn(second, preview['documents'])
        self.assertEqual([], preview['assets'])
        c = self.c['cleanupFinalPreview']
        self.assertIn('Preview ready · 2 documents · 0 private objects', c['statuses'])
        self.assertTrue(button(c, 'Apply deletion')['disabled'])
        self.assertTrue(self.c['cleanupConfirmed']['confirmed'])
        self.assertFalse(button(self.c['cleanupConfirmed'], 'Apply deletion')['disabled'])
        self.assertIn('Deletion complete · 2 documents · 0 private objects', self.c['cleanupApplied']['statuses'])
        self.assertFalse(self.final['first_attempt_present'])
        self.assertTrue(self.final['second_attempt_present'])
        self.assertTrue(self.final['shared_audio_present'])
        names = set(self.c['cleanupReopened']['inputs'])
        self.assertIn('Select Café opening · attempt · ' + second, names)
        self.assertNotIn('Select Café opening · attempt · ' + first, names)
        apply = [x for x in self.requests(method='POST') if x['path'].endswith(':apply')]
        self.assertEqual(1, len(apply))
        plan = next(x['body'] for x in self.writes if '/'+x['body'].get('id', '?')+':apply' == apply[0]['path'].removeprefix('/api/v1/deletions'))
        self.assertEqual({'confirmed_plan_sha256': plan['confirmation_sha256']}, apply[0]['body'])

    def test_cleanup_identity_negative(self):
        self.assertFalse(self.c['cleanupPreview']['applyEnabled'])
        self.assertEqual('', self.c['cleanupChanged']['inputs']['Deletion subjects']['value'])
        self.assertFalse(any(x['text'] == 'Apply deletion' for x in self.c['cleanupChanged']['buttons']))
        self.assertEqual(self.fixture['first_attempt'][:8], self.c['cleanupShort']['inputs']['Deletion subjects']['value'])
        self.assertIn('Your selection is retained.', self.c['cleanupShort']['alerts'][0])
        short = self.requests('cleanup-short-id', method='POST')
        self.assertEqual([{'subject_ids': [self.fixture['first_attempt'][:8]], 'orphan_cleanup': False}],
                         [x['body'] for x in short])
        self.assertFalse(any(x['path'].endswith(':apply') for x in short))
        blocked = self.c['cleanupBlockedFinal']
        self.assertIn('Still in use · 3 documents · 0 private objects', blocked['statuses'])
        self.assertNotIn('blocked_active_reference', blocked['main'])
        self.assertFalse(any(x['text'] == 'Apply deletion' for x in blocked['buttons']))
        self.assertFalse(any(x['path'].endswith(':apply') for x in self.requests('cleanup-preview-race')))

    def test_cleanup_race_negative(self):
        before, after = self.c['cleanupRaceNewer'], self.c['cleanupRaceAfter']
        self.assertEqual(json.loads(before['details']), json.loads(after['details']))
        self.assertEqual([self.fixture['second_attempt']], json.loads(after['details'])['heads'])
        self.assertTrue(after['confirmed'])
        requests = self.requests('cleanup-preview-race', '/api/v1/deletions', 'POST')
        self.assertEqual([[self.fixture['first_attempt']], [self.fixture['second_attempt']]],
                         [x['body']['subject_ids'] for x in requests])

    def test_cleanup_list_recovery_positive(self):
        a, b = self.c['cleanupListFailure'], self.c['cleanupListRecovery']
        self.assertIn('Saved record choices are unavailable. Retry; your selection is retained.', a['alerts'])
        self.assertTrue(a['previewEnabled'])
        self.assertEqual(a['inputs']['Deletion subjects']['value'], b['inputs']['Deletion subjects']['value'])
        self.assertEqual(self.fixture['second_attempt'], b['inputs']['Deletion subjects']['value'])
        self.assertEqual([], b['alerts'])
        self.assertNotIn('private backend detail', a['main'])

    def test_cleanup_pagination_positive(self):
        c = self.c['cleanupPageTwo']
        for key in ['first_attempt', 'second_attempt']:
            self.assertIn(self.fixture[key], c['main'])
        self.assertEqual(self.fixture['first_attempt'], c['inputs']['Deletion subjects']['value'])
        calls = self.requests('cleanup-pagination', '/api/v1/attempts', 'GET')
        self.assertTrue(any('cursor=i21-second-page' in x['query'] for x in calls))
        self.assertTrue(all('limit=50' in x['query'] for x in calls))

    def test_cleanup_empty_positive(self):
        c = self.c['cleanupEmptyFinal']
        self.assertIn('No saved records.', c['main'])
        self.assertIn('Prepare an exercise', c['main'])
        self.assertEqual(self.fixture['audio_asset_id'], c['inputs']['Deletion subjects']['value'])
        self.assertFalse(any(k.startswith('Select ') for k in c['inputs']))

    def test_keyboard_layout_positive(self):
        rows = self.facts['layouts']
        self.assertEqual({(route, width) for route in ['reports', 'cleanup'] for width in [1280, 390, 320]},
                         {(x['route'], x['width']) for x in rows})
        for row in rows:
            self.assertFalse(row['overflow'])
            self.assertEqual(['17px', '24.65px'], [row['bodySize'], row['bodyLine']])
            self.assertTrue(row['loaded'])
            self.assertEqual('loaded', row['fonts'])
            self.assertIn('Source Sans 3', row['font'])
            for b in row['buttons']:
                self.assertGreaterEqual(b['height'], 44)
                self.assertGreaterEqual(float(b['font'].removesuffix('px')), 13)
            self.assertTrue(all(float(x.removesuffix('px')) >= 13 for x in row['fieldHelp']))
        k = self.c['cleanupKeyboard']
        self.assertEqual('3px', k['outline'])
        self.assertGreaterEqual(k['top'], 0)
        self.assertLessEqual(k['bottom'], k['height'])

    def test_catalogue_scope_positive(self):
        rows = self.table('allCategories')
        self.assertEqual(122, len(rows))
        self.assertEqual(122, len({x.split('\t')[0] for x in rows}))
        self.assertIn(ROW, rows)
        self.assertIn('acceptable_variant.dialect_variant\t0\t0/1\tN/A: leaf_annotation_scope_not_declared', '\n'.join(rows))

    def test_zero_dispatch_negative(self):
        self.assertEqual(0, self.final['provider_receipts'])
        self.assertFalse(any(x['event'] in ['fixture_error', 'forbidden_execution'] for x in self.events))
        for x in self.requests(method='POST'):
            self.assertTrue(x['path'] in ['/api/v1/reports/empirical', '/api/v1/lab/experiments', '/api/v1/deletions']
                            or x['path'].startswith('/api/v1/deletions/') and x['path'].endswith(':apply'))
        self.assertEqual(2, len(self.final['experiments']))
        for exp in self.final['experiments']:
            self.assertEqual('planned', exp['status'])
            self.assertIsNone(exp['judge_policy_asset_id'])
            for row in exp['rows']:
                self.assertEqual('not_run', row['status'])
                self.assertEqual([], row['receipt_ids'])
                self.assertEqual([], row['trace_ids'])
                self.assertIsNone(row['output_asset_id'])

    def test_native_receipt_positive(self):
        self.assertEqual('0', (DATA / 'native-exit-code').read_text())
        events = [json.loads(x) for x in (DATA / 'native.jsonl').read_text().splitlines()]
        self.assertEqual(['TestGuidedToolsNativeFixture'], [x['Test'] for x in events if x['Action'] == 'pass' and x.get('Test')])
        self.assertFalse(any(x['Action'] == 'fail' for x in events))

    def test_retained_helper_receipts_positive(self):
        source = json.loads((AUDIT / 'SOURCE.json').read_text())
        for path, expected in source['files'].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), path)
        receipts = {
            'starters-green.log': ('GuidedStarters', [
                'named_population_positive', 'no_saved_population_mutation_negative', 'named_dataset_positive',
                'selected_binding_positive', 'unsupported_input_negative', 'constructed_scope_positive']),
            'cleanup-owner-final.log': ('CleanupSession', [
                'selection_during_preview_positive', 'old_preview_negative', 'selection_clears_confirmation_negative',
                'unconfirmed_apply_negative', 'apply_exact_plan_positive', 'obsolete_error_negative',
                'current_failure_retains_selection_positive', 'blocked_apply_negative', 'readable_status_positive',
                'unknown_status_negative', 'orphan_scope_positive', 'disposal_negative']),
            'retained-starter-regression.log': ('FinalFunctionalHelpers', [
                'constructed_report_positive', 'portable_experiment_positive', 'independent_asset_hashes_positive',
                'no_semantic_gold_invented_negative', 'invalid_fields_negative', 'selected_generation_binding_positive']),
        }
        for path, (owner, methods) in receipts.items():
            raw = (DATA / path).read_text()
            self.assertIn('Ran ' + str(len(methods)) + ' tests', raw)
            self.assertTrue(raw.rstrip().endswith('OK'), path)
            for name in methods:
                self.assertRegex(raw, r'test_' + name + r' \([^\n]*' + owner + r'\.test_' + name + r'\) \.\.\. ok')

    def packet(self):
        return json.loads((AUDIT / 'REVIEW.json').read_text())

    def errors(self, packet, facts=None, native=None):
        return review.review_errors(packet, facts or self.facts, native or self.fixture)

    def test_review_positive(self):
        self.assertEqual([], self.errors(self.packet()))

    def test_ux_omission_negative(self):
        p = self.packet()
        p.pop('ui_ux')
        self.assertTrue(self.errors(p))
        p = self.packet()
        p['ui_ux'] = {'observations': ['build and picture count'], 'references': ['data/iteration-21-guided-tools-20261026/web-build-final.log']}
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
        self.assertTrue(self.errors(self.packet(), native=n))
        for name, value in [('unexecuted_cases', ['planned']), ('reference_origin', 'candidate gold'),
                            ('new_model_calls', 50), ('performance_campaigns', 'required')]:
            p = self.packet()
            p[name] = value
            self.assertTrue(self.errors(p))


if __name__ == '__main__':
    unittest.main(verbosity=2)
