"""Inspect actual saved tests/Lab bytes and original scope; no new AI calls."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/iteration-33-diagnostics-20261027'


class SavedAudioAcceptance(unittest.TestCase):
    def observed_cases(self, names):
        sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
        from requirement_tests import parse_unittest_events
        packet = json.loads((OUT/'native/diagnostic.json').read_text())
        self.assertEqual([],self.native_owner().errors(packet))
        observed = parse_unittest_events((ROOT/packet['stdout']).read_text())
        for name in names:
            self.assertEqual('pass',observed.get('unittest::'+name),name)

    def test_context_native_positive(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_native_diagnostic_context_positive',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_gemini_projected_context_positive',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_blind_context_and_audio_order_positive',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_completed_request_positive',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_configured_proxy_positive',
            'tests.test_audio_diagnostics.AudioDiagnosticTests.test_controlled_context_projection_positive'])

    def test_context_native_negative(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_private_key_cannot_bias_context_negative',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_paid_before_transport_negative',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_missing_key_negative',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_non_json_response_negative',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_invalid_model_text_retained_negative',
            'tests.test_auditory_protocol.AuditoryProtocolTests.test_redirect_credential_negative',
            'tests.test_audio_diagnostics.AudioDiagnosticTests.test_judge_omitted_targets_negative'])

    def test_fixture_native_positive(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_ambiguous_fixture_positive',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_correct_variants_positive',
            'tests.test_selected_acoustic.SelectedAcoustic.test_correct_control_projection_positive',
            'tests.test_selected_acoustic.SelectedAcoustic.test_boundary_context_repair_positive'])

    def test_fixture_native_negative(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_judge_support_cannot_resolve_ambiguous_fixture_negative',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_valid_question_false_alarm_negative',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_failed_observation_cannot_confirm_negative',
            'tests.test_saved_audio_diagnostics.SavedAudioDiagnostics.test_physical_change_does_not_make_valid_contour_wrong_negative',
            'tests.test_selected_acoustic.SelectedAcoustic.test_blind_public_context_negative',
            'tests.test_selected_acoustic.SelectedAcoustic.test_correct_variant_false_alarm_negative'])

    def test_saved_physical_native_positive(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_original_context_and_three_controls_positive',
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_pause_actual_samples_positive',
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_retained_f0_and_valid_question_positive',
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_repair_preserves_audio_and_narrow_linking_positive',
            'tests.test_completion_i26.CompletionI26.test_acoustic_positive'])

    def test_saved_physical_native_negative(self):
        self.observed_cases([
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_requested_pause_cannot_replace_missing_samples_negative',
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_fixed_context_is_not_a_new_observation_negative',
            'tests.test_saved_audio_diagnostics.RetainedAudioDiagnostics.test_full_form_is_not_absent_or_wrong_by_definition_negative',
            'tests.test_completion_i26.CompletionI26.test_acoustic_negative'])

    def test_original_scope_preserved_positive(self):
        paths = ['specification/v2/domain/error-taxonomy.v1.yaml',
                 'specification/v2/domain/mutation-recipes.v1.json',
                 'specification/v2/domain/metrics.v1.yaml',
                 'specification/v2/domain/providers.v1.yaml',
                 'specification/v2/language/source-lock.json']
        for path in paths:
            with self.subTest(path=path):
                original = subprocess.run(['git','show','60bb692:'+path],cwd=ROOT,
                                          check=True,capture_output=True).stdout
                self.assertEqual(original,(ROOT/path).read_bytes())

    def test_actual_lab_bytes_positive(self):
        result = json.loads((OUT/'lab-readback.json').read_text())
        self.assertEqual(('FINISHED',0,0,0),(result['status'],result['actual_new_model_calls'],
                         result['actual_new_synthesis_calls'],result['export_inference_calls']))
        self.assertEqual(9,len(result['checked']))
        for name in result['checked']:
            with self.subTest(name=name):
                self.assertEqual((OUT/'lab-export'/name).read_bytes(),
                                 (OUT/'lab-readback'/name).read_bytes())
        source = 'source/services/speech/diagnostic_models.py'
        self.assertEqual((ROOT/'services/speech/diagnostic_models.py').read_bytes(),
                         (OUT/'lab-readback'/source).read_bytes())

    def test_retained_native_cases_positive(self):
        sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
        from requirement_tests import parse_unittest_events
        module = self.native_owner()
        for suite in ['category','category-evidence','diagnostic']:
            packet = json.loads((OUT/'native'/(suite+'.json')).read_text())
            self.assertEqual([],module.errors(packet))
            self.assertEqual(packet['tests_run'],len(set(packet['test_ids'])))
            self.assertEqual((0,0),(packet['new_inference_calls'],packet['new_synthesis_calls']))
            observed = parse_unittest_events((ROOT/packet['stdout']).read_text())
            self.assertEqual(set(packet['test_ids']),set(observed))
            self.assertTrue(all(s=='pass' for s in observed.values()))

    def native_owner(self):
        spec = importlib.util.spec_from_file_location('i33_native_cases',
            ROOT/'audit/iteration-33-diagnostics-20261027/native_cases.py')
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module

    def test_stale_or_failed_receipt_cannot_be_reused_negative(self):
        module = self.native_owner()
        original = json.loads((OUT/'native/diagnostic.json').read_text())
        changed = copy.deepcopy(original);changed['source_sha256']['services/speech/diagnostic_models.py']='0'*64
        self.assertIn('Changed semantic input: services/speech/diagnostic_models.py',module.errors(changed))
        changed = copy.deepcopy(original);changed['failures']=1
        self.assertIn('Original native run failed or skipped cases',module.errors(changed))
        changed = copy.deepcopy(original);changed['tests_run']-=1
        self.assertIn('Original native run omitted an exact selected test',module.errors(changed))
