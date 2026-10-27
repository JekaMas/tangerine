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
VERIFY = ROOT/'data/iteration-33-verification-20261027'
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))


class SavedAudioAcceptance(unittest.TestCase):
    def observed_cases(self, names):
        sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
        from requirement_tests import parse_unittest_events
        observed = {r['test_id']:r['status'] for r in self.native_owner().observations()}
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

    def verification_cases(self,names):
        from requirement_tests import parse_unittest_events
        packet=json.loads((VERIFY/'directed.json').read_text())
        # The actual command ran once; these are its literal native assertions.
        apply=self.native_owner().apply
        self.assertEqual([],apply.errors(packet))
        observed=parse_unittest_events((ROOT/packet['stdout']).read_text())
        for name in names:
            self.assertEqual('pass',observed['unittest::tests.test_saved_audio_verification.SavedAudioVerification.'+name])

    def test_verification_fixture_positive(self):
        self.verification_cases(['test_correct_controls_and_supported_candidate_positive',
                                 'test_valid_variant_candidate_stays_correct_positive'])

    def test_verification_fixture_negative(self):
        self.verification_cases(['test_correct_controls_cannot_be_relabelled_negative',
                                 'test_unknown_judgment_is_uncertain_negative',
                                 'test_valid_variant_candidate_false_alarm_negative'])

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
        result = json.loads((VERIFY/'lab-readback.json').read_text())
        self.assertEqual(('FINISHED',0,0,0),(result['status'],result['actual_new_model_calls'],
                         result['actual_new_synthesis_calls'],result['export_inference_calls']))
        self.assertEqual(12,len(result['checked']))
        for name in result['checked']:
            with self.subTest(name=name):
                self.assertEqual((VERIFY/'lab-export'/name).read_bytes(),
                                 (VERIFY/'lab-readback'/name).read_bytes())
        for path in ['services/speech/category_validation.py',
                     'audit/iteration-26-acoustic-20261026/listening.py']:
            self.assertEqual((ROOT/path).read_bytes(),
                             (VERIFY/'lab-readback/source'/path).read_bytes())

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
        current=module.observations()
        self.assertEqual(580,len(current))
        self.assertTrue(all(r['status']=='pass' for r in current))
        self.assertEqual((532,48),(sum(r['disposition']=='reobserved_changed_owner' for r in current),
                                  sum(r['disposition']=='retained_unchanged_dependency' for r in current)))

    def native_owner(self):
        spec = importlib.util.spec_from_file_location('i33_native_cases',
            ROOT/'audit/iteration-33-diagnostics-20261027/verification_native.py')
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

    def test_listening_browser_positive(self):
        browser=VERIFY/'browser'
        load=lambda name:json.loads((browser/name).read_text())
        initial=load('initial.json');final=load('recovered.json')
        self.assertEqual((20,False),(initial['players'],initial['hasPrivate']))
        self.assertEqual(('17px','24.65px',True),
                         (initial['fontSize'],initial['lineHeight'],initial['fontLoaded']))
        self.assertEqual((20,20,False,False),
                         (final['players'],final['ready'],final['hasUnavailable'],final['hasErrorText']))
        self.assertEqual(['Confirmed in this model check','Confirmed in this model check',
                          'The model did not confirm this target',
                          'Uncertain · keep the observations separate',
                          'Uncertain · keep the observations separate'],final['statuses'])
        playback=load('exclusive-play.json')
        self.assertEqual(['Linking · Valid contextual variant'],playback['playing'])
        self.assertTrue(playback['states'][0]['paused']);self.assertGreater(playback['states'][0]['time'],0)
        self.assertFalse(playback['states'][2]['paused'])
        for name,width in [('narrow390.json',390),('narrow320.json',320)]:
            layout=load(name)
            self.assertEqual((width,width),(layout['width'],layout['scrollWidth']))
        keyboard=load('keyboard.json')
        self.assertEqual(('Linking','A','solid','3px'),
                         (keyboard['focused'],keyboard['tag'],keyboard['outline'],keyboard['width']))
        media=load('media-final.json');self.assertEqual(20,len(media))
        self.assertTrue(all(m['readyState']==4 and m['error'] is None for m in media))
        self.assertEqual(20,len({m['src'] for m in media}))
        for case in ['linking','assimilation','weak-form','thought-group','intonation-function']:
            self.assertTrue(all('/audio/'+case+'/'+role+'.wav' in {m['src'] for m in media}
                                for role in ['clean','mutated','acceptable','misleading_metadata']))
        probe=json.loads((VERIFY/'video-probe.json').read_text())
        self.assertEqual(('h264',1280,800),(probe['streams'][0]['codec_name'],
                         probe['streams'][0]['width'],probe['streams'][0]['height']))
        self.assertGreater(float(probe['format']['duration']),70)
        self.assertTrue((browser/'saved-listening-review.mp4').read_bytes()[4:8]==b'ftyp')
        self.verification_cases(['test_candidate_label_does_not_assert_realization_positive',
                                 'test_saved_comparison_refresh_recovers_positive'])

    def test_listening_browser_negative(self):
        browser=VERIFY/'browser';initial=json.loads((browser/'initial.json').read_text())
        self.assertEqual('Saved listening observation unavailable',initial['statuses'][0])
        self.assertEqual((4,0),(initial['media'][0]['ready'],initial['media'][1]['ready']))
        events=json.loads((browser/'http-observations.json').read_text())
        for path in ['/audio/linking/clean.wav','/audio/linking/mutated.wav']:
            statuses=[e['status'] for e in events if e['path']==path]
            self.assertEqual(503,statuses[0]);self.assertEqual(200,statuses[-1])
        self.assertEqual(2,(VERIFY/'browser-server.log').read_text().count('Saved comparison read failed:'))
        tone=(browser/'intonation-visible.txt').read_text()
        self.assertIn('incorrectly flagged 1 correct control',tone)
        self.assertIn('corrected context has not been judged again',tone)
        self.assertNotIn('PRIVATE_BACKEND_CANARY',tone)
        for name in ['desktop-initial.jpg','desktop-recovery.jpg','desktop-recovered.jpg',
                     'weak-form-valid-variant.jpg','intonation-honest-context.jpg',
                     'mobile390.jpg','mobile320.jpg','encoded-video-check.jpg']:
            self.assertTrue((browser/'screenshots'/name).read_bytes().startswith(b'\xff\xd8'))
        self.verification_cases(['test_saved_comparison_shapes_do_not_hide_players_negative'])
