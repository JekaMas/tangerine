"""Literal diagnostic/fixture regressions. No network, synthesis or model call."""
import copy
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services/speech'))
import diagnostic_models as models
from category_validation import blind_input, compare_probe, make_probe


def intent():
    return dict(
        task_target='The policy is one thought group. Ordinary boundary pauses are permitted.',
        canonical_text='We changed the policy.', surface_text='We changed the policy.',
        source_interval=dict(start=0, end=48000), clip_duration_seconds=2,
        planned_units=[dict(id='boundary', corrections=['PRIVATE_CORRECTION'],
                           rationale='PRIVATE_RATIONALE',
                           realization=dict(mode='temporal_fluency', canonical_ipa='same',
                                            intended_ipa='same', planned_pause_ms=600,
                                            observed_pause_ms=999, prosody=[]))],
        acoustic_edits=[dict(unit_id='boundary', controller='pause_insert',
                            scope=dict(start=15, end=21),
                            parameters=dict(pause_ms=600, accepted_reference='PRIVATE_REFERENCE'))],
        answer='PRIVATE_ANSWER', previous_score=100, mutation_key='PRIVATE_KEY')


class SavedAudioDiagnostics(unittest.TestCase):
    def request(self, value, native=False):
        received, capture = [], []
        class Response(io.BytesIO):
            status = 200
        body = dict(status='completed', steps=[dict(type='model_output', content=[dict(
            type='text', text='{"findings":[{"unit_id":"boundary","feature":"pause_insert",'
            '"status":"uncertain","reason":"The boundary cannot be distinguished."}]}')])])
        class Opener:
            def open(self, request, timeout):
                received.append(json.loads(request.data))
                return Response(json.dumps(body).encode())
        profile = dict(provider='gemini_interactions', model='constructed-no-inference',
                       billing_mode='free_tier', max_output_tokens=512)
        with patch.dict(models.os.environ, {'GEMINI_API_KEY': 'PRIVATE_CREDENTIAL'}), \
                patch.object(models.urllib.request, 'build_opener', return_value=Opener()):
            if native:
                import diagnostic_runtime
                candidate = (ROOT/'data/connected-speech-20261023/output/chunking-candidate.wav').read_bytes()
                reference = (ROOT/'data/connected-speech-20261023/output/chunking-reference.wav').read_bytes()
                value = {**value, 'audio_sha256':hashlib.sha256(candidate).hexdigest()}
                with patch.object(diagnostic_runtime,'checkpoint',side_effect=capture.append):
                    result = diagnostic_runtime.execute(dict(
                        method_id='gemini-audio-v1', profile=profile, prompt='Owned diagnostic prompt',
                        audio_sha256=value['audio_sha256'], input=value, audio_base64=base64.b64encode(candidate).decode(),
                        reference_audio_base64=base64.b64encode(reference).decode()))
            else:
                result = models.auditory(profile, 'Owned diagnostic prompt', value,
                                         [b'target-wave', b'reference-wave'], capture=capture.append)
        self.assertEqual(1, len(received))
        return received[0], result, capture

    def test_native_diagnostic_context_positive(self):
        wire, result, capture = self.request(intent(), native=True)
        self.assertEqual('boundary',json.loads(wire['input'][0]['text'])['targets'][0]['unit_id'])
        self.assertNotIn('PRIVATE_',json.dumps(wire))
        self.assertEqual(2,len([p for p in wire['input'] if p['type']=='audio']))
        measurement = result['measurements'][0]
        self.assertEqual(('boundary','pause_insert','not_measurable'),
                         (measurement['target_unit_id'],measurement['feature'],measurement['status']))
        self.assertIsNone(measurement['numeric_value'])
        self.assertEqual('uncertain',measurement['auditory_finding']['status'])
        self.assertEqual(wire,capture[-1]['request'])

    def test_gemini_projected_context_positive(self):
        before = intent(); source = copy.deepcopy(before)
        wire, result, capture = self.request(source)
        visible = json.loads(wire['input'][0]['text'])
        self.assertEqual(visible, dict(
            task_target=before['task_target'], canonical_text='We changed the policy.',
            surface_text='We changed the policy.', source_interval=dict(start=0, end=48000),
            clip_duration_seconds=2, targets=[dict(
                unit_id='boundary', features=['pause_insert'],
                realization=dict(mode='temporal_fluency', planned_pause_ms=600, prosody=[]),
                controllers=[dict(controller='pause_insert',
                                  text_scope_codepoints=dict(start=15, end=21),
                                  parameters=dict(pause_ms=600))])]))
        self.assertEqual(['Target audio', 'Reference audio'],
                         [p['text'] for p in wire['input'][1:] if p['type'] == 'text'])
        self.assertEqual('uncertain', result['output']['findings'][0]['status'])
        self.assertEqual(before, source)
        self.assertEqual(wire, capture[-1]['request'])

    def test_private_key_cannot_bias_context_negative(self):
        source = intent()
        wire, result, capture = self.request(source)
        self.assertNotIn('PRIVATE_', json.dumps([wire, result, capture]))
        other = copy.deepcopy(source)
        other.update(answer='OTHER_ANSWER', previous_score=0, mutation_key='OTHER_KEY')
        other['planned_units'][0]['realization']['observed_pause_ms'] = 1
        changed, _, _ = self.request(other)
        self.assertEqual(wire, changed)

    def test_blind_context_and_audio_order_positive(self):
        probe = dict(task='blind_category_probe', clips=[dict(
            unit_id='clip-1', public_context='Careful British speech is allowed.',
            question='Is there an actual error?', expected='PRIVATE_EXPECTED')],
            withheld=['PRIVATE_ROLES'], mutation_key='PRIVATE_KEY')
        wire, _, _ = self.request(probe)
        self.assertEqual(blind_input(probe), json.loads(wire['input'][0]['text']))
        self.assertEqual(['clip-1', 'clip-2'],
                         [p['text'] for p in wire['input'][1:] if p['type'] == 'text'])
        self.assertNotIn('PRIVATE_', json.dumps(wire))

    def fixture(self):
        return dict(taxonomy_id='pronunciation.suprasegmental.weak_form', control=False,
                    context='An unstressed reduced to is requested; a full form may express emphasis.',
                    control_context='Contrastive TO, careful speech and the declared accent are allowed.',
                    question='Is the heard form incompatible with the audible context?',
                    control_question='Is the permitted form actually incorrect?',
                    expected_by_role={'mutated': 'uncertain'},
                    expectation_note='A full vowel alone does not establish a neutral-context error.')

    def probe(self):
        return make_probe(self.fixture(), {r: r+'.wav' for r in (
            'clean', 'mutated', 'acceptable', 'misleading_metadata')},
            dict(backend='constructed', voice='none'), 17)

    def observation(self, probe, target='contradicted'):
        return dict(receipt=dict(inference_calls=1), output=dict(findings=[dict(
            unit_id=r['unit_id'], feature='category_probe',
            status=target if r['role'] == 'mutated' else 'contradicted',
            reason='Constructed full form is heard; that alone does not establish a mistake.')
            for r in probe['withheld']]))

    def test_ambiguous_fixture_positive(self):
        probe = self.probe()
        self.assertEqual('uncertain', next(r for r in probe['withheld'] if r['role'] == 'mutated')['expected'])
        self.assertNotIn('expectation_note', json.dumps(blind_input(probe)))
        actual = compare_probe(probe, self.observation(probe))
        self.assertEqual(('uncertain', True, 0),
                         (actual['audio_confirmation'], actual['controls_passed'], actual['false_alarms']))
        target = next(r for r in actual['cases'] if r['role'] == 'mutated')
        self.assertEqual(('contradicted', 'uncertain'), (target['actual'], target['outcome']))

    def test_judge_support_cannot_resolve_ambiguous_fixture_negative(self):
        probe = self.probe()
        original = self.observation(probe, 'supported'); before = copy.deepcopy(original)
        actual = compare_probe(probe, original)
        self.assertEqual('uncertain', actual['audio_confirmation'])
        self.assertEqual(before, original)
        self.assertEqual('supported', next(r for r in actual['cases'] if r['role'] == 'mutated')['actual'])

    def test_correct_variants_positive(self):
        for context in [
            'Full TO is used for contrastive emphasis; the strong form is correct.',
            'Ordinary neutral careful speech permits a full vowel; reduction is optional.',
            'Careful word boundaries and smooth linking are both acceptable.',
            'This is a confirmation question; declarative word order and a rise are permitted.',
            'A falling wh-question and a rise requesting repetition are both permitted by this context.',
            'The declared British or American accent is permitted; accent alone is not a defect.',
        ]:
            with self.subTest(context=context):
                fixture = {**self.fixture(), 'context': context, 'control': True}
                fixture.pop('expected_by_role')
                probe = make_probe(fixture, {r:r+'.wav' for r in (
                    'clean','mutated','acceptable','misleading_metadata')}, {}, 17)
                self.assertTrue(all(r['expected']=='contradicted' for r in probe['withheld']))
                self.assertEqual('confirmed', compare_probe(probe, self.observation(probe))['audio_confirmation'])

    def test_valid_question_false_alarm_negative(self):
        probe = self.probe(); observation = self.observation(probe)
        control = next(r for r in probe['withheld'] if r['role']=='acceptable')
        finding = next(r for r in observation['output']['findings'] if r['unit_id']==control['unit_id'])
        finding.update(status='supported', reason='Constructed false alarm: every question must rise.')
        actual = compare_probe(probe, observation)
        self.assertEqual(('uncertain', False, 1),
                         (actual['audio_confirmation'], actual['controls_passed'], actual['false_alarms']))

    def test_failed_observation_cannot_confirm_negative(self):
        fixture = self.fixture(); fixture.pop('expected_by_role')
        probe = make_probe(fixture, {r:r+'.wav' for r in (
            'clean','mutated','acceptable','misleading_metadata')}, {}, 17)
        result = self.observation(probe, 'supported')
        result.update(error='DIAGNOSTIC_PROVIDER_FAILED', wire=dict(http_status=503))
        original = copy.deepcopy(result)
        compared = compare_probe(probe, result)
        self.assertEqual(('uncertain', 'failed'),
                         (compared['audio_confirmation'], compared['dispatch_status']))
        self.assertEqual(original, result)

    def test_physical_change_does_not_make_valid_contour_wrong_negative(self):
        fixture = {**self.fixture(), 'control':True, 'requires_physical':True}
        fixture.pop('expected_by_role')
        probe = make_probe(fixture, {r:r+'.wav' for r in (
            'clean','mutated','acceptable','misleading_metadata')}, {}, 17)
        observation = self.observation(probe)
        observation['physical'] = dict(status='supported', observations=[dict(
            actual_semitone_windows=[2,4,6], origin='constructed rising valid-question control')])
        actual = compare_probe(probe,observation)
        self.assertEqual('confirmed',actual['audio_confirmation'])
        self.assertFalse(actual['physical_auditory_conflict'])


class RetainedAudioDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('saved_audio_reconciliation',
            ROOT/'audit/iteration-33-diagnostics-20261027/reconcile.py')
        cls.owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.owner)
        cls.result = cls.owner.build()
        cls.rows = {r['id']:r for r in cls.result['sets']}

    def test_original_context_and_three_controls_positive(self):
        self.assertEqual(['linking','assimilation','weak-form','thought-group','intonation-function'],
                         list(self.rows))
        for row in self.rows.values():
            with self.subTest(case=row['id']):
                self.assertEqual({'clean','mutated','acceptable','misleading_metadata'},
                                 {c['role'] for c in row['clips']})
                self.assertEqual(3, row['original_comparison']['correct_controls'])
                response = self.owner.read(ROOT/row['original_response'])
                self.assertEqual(row['original_input'], json.loads(response['wire']['request']['input'][0]['text']))
                wave_parts = [p for p in response['wire']['request']['input'] if p['type']=='audio']
                for clip, part in zip(row['clips'], wave_parts, strict=True):
                    self.assertEqual((ROOT/clip['audio_path']).read_bytes(), base64.b64decode(part['data']))
                    self.assertEqual([f for f in response['output']['findings'] if f['unit_id']==clip['unit_id']],
                                     clip['original_findings'])

    def test_pause_actual_samples_positive(self):
        actual = self.rows['thought-group']['physical_observation']
        self.assertEqual((14400, 24000, dict(start=9000,end=23400)),
                         (actual['additional_samples'], actual['sample_rate_hz'], actual['inserted_interval']))
        self.assertTrue(actual['all_inserted_samples_zero'])
        self.assertTrue(actual['prefix_outside_120_sample_fade_unchanged'])
        self.assertTrue(actual['suffix_outside_120_sample_fade_unchanged'])
        row = self.rows['thought-group']
        self.assertEqual('contradicted', next(c for c in row['clips'] if c['role']=='mutated')['original_findings'][0]['status'])

    def test_requested_pause_cannot_replace_missing_samples_negative(self):
        reference = ROOT/'data/connected-speech-20261023/output/chunking-reference.wav'
        actual = self.owner.pause_observation(reference, reference, 9000, 14400)
        self.assertEqual(0, actual['additional_samples'])
        self.assertFalse(actual['all_inserted_samples_zero'])
        self.assertFalse(actual['suffix_outside_120_sample_fade_unchanged'])

    def test_retained_f0_and_valid_question_positive(self):
        row = self.rows['intonation-function']
        contours = {(c['case_id'],c['variant']):c['actual_semitone_windows']
                    for c in row['physical_observation']['contours']}
        for case,variant,direction in [('statement','reference',-1),('statement','candidate',1),
                                       ('question','reference',1),('question','candidate',-1),
                                       ('wh_question','reference',-1),('wh_question','candidate',1)]:
            with self.subTest(case=case,variant=variant):
                windows = contours[(case,variant)]
                self.assertTrue(all((b-a)*direction>0 for a,b in zip(windows,windows[1:])))
        self.assertEqual(1, row['original_comparison']['false_alarms'])
        control = next(c for c in row['clips'] if c['role']=='acceptable')
        self.assertIn('confirmation', control['public_context'])
        self.assertEqual('supported', control['original_findings'][0]['status'])

    def test_fixed_context_is_not_a_new_observation_negative(self):
        row = self.rows['intonation-function']
        self.assertEqual('You have car insurance.',row['recording_text'])
        self.assertTrue(all('You have car insurance' not in c['public_context'] for c in row['clips']))
        repair = row['fixture_repair']
        self.assertTrue(all('You have car insurance' in c['public_context'] for c in repair['input']['clips']))
        self.assertEqual(('not_run',0),(repair['observation'], repair['new_model_calls']))
        self.assertEqual('uncertain',row['original_comparison']['audio_confirmation'])

    def test_full_form_is_not_absent_or_wrong_by_definition_negative(self):
        row = self.rows['weak-form']
        target = next(c for c in row['clips'] if c['role']=='mutated')
        self.assertEqual('supported',target['expected'])  # Original expectation stays historical.
        self.assertEqual('contradicted',target['original_findings'][0]['status'])
        self.assertIn('full',target['original_findings'][0]['reason'])
        current = row['fixture_repair']
        self.assertEqual('uncertain', next(c for c in current['withheld_expectations'] if c['role']=='mutated')['expected'])
        self.assertEqual(('not_run',0),(current['observation'],current['new_model_calls']))

    def test_repair_preserves_audio_and_narrow_linking_positive(self):
        observer = self.owner.load_observer()
        for case in ['weak-form','intonation-function']:
            old = self.rows[case]
            fresh = observer.prepare(case)
            for clip, encoded in zip(old['clips'],[fresh['packet']['audio_base64']]+fresh['packet']['additional_audio_base64'],strict=True):
                self.assertEqual((ROOT/clip['audio_path']).read_bytes(),base64.b64decode(encoded))
        linking = self.rows['linking']
        self.assertEqual(('confirmed',0), (linking['original_comparison']['audio_confirmation'],linking['original_comparison']['false_alarms']))
        control = next(c for c in linking['clips'] if c['role']=='acceptable')
        self.assertIn('careful',control['public_context'])
        self.assertEqual('contradicted',control['original_findings'][0]['status'])

    def test_saved_reconciliation_dispatches_nothing_positive(self):
        with patch.object(models.urllib.request,'build_opener',side_effect=AssertionError('No provider call')):
            result = self.owner.build()
        self.assertEqual((0,0,0),(result['actual_new_model_calls'],result['actual_new_synthesis_calls'],result['score_or_key_changes']))
        self.assertEqual(self.result,result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
