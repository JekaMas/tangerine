"""I33 counterexamples through the real comparison and saved HTTP owners.

All judgments/failures here are constructed. WAVs are original saved Kokoro
recordings. No synthesis or model transport is used.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'services/speech'))
from category_validation import ROLES, compare_probe, make_probe
from tests.test_selected_listening_recovery import application, get, saved_rows


def fixture(**options):
    return dict(taxonomy_id='pronunciation.suprasegmental.weak_forms',
                control=False, context='Neutral careful speech permits strong TO.',
                control_context='Contrastively emphasized strong TO is correct.',
                question='Is TO inappropriate for the stated context?',
                control_question='Is TO inappropriate for the stated context?',
                **options)


def probe(value):
    return make_probe(value, {r:r+'.wav' for r in ROLES}, {}, 17)


def observation(value, candidate='supported', controls='contradicted'):
    # Independent oracle by role: never copy the computed expected field.
    return dict(receipt=dict(inference_calls=1), output=dict(findings=[
        dict(unit_id=r['unit_id'], feature='category_probe',
             status=candidate if r['role']=='mutated' else controls,
             reason='Constructed judgment, not an actual model observation.')
        for r in value['withheld']]))


class SavedAudioVerification(unittest.TestCase):
    def test_correct_controls_and_supported_candidate_positive(self):
        value=probe(fixture())
        self.assertEqual({'clean':'contradicted','mutated':'supported',
                          'acceptable':'contradicted','misleading_metadata':'contradicted'},
                         {r['role']:r['expected'] for r in value['withheld']})
        result=compare_probe(value,observation(value))
        self.assertEqual(('confirmed',True,0),
                         (result['audio_confirmation'],result['controls_passed'],result['false_alarms']))

    def test_correct_controls_cannot_be_relabelled_negative(self):
        for override in ['supported','uncertain','not_applicable']:
            with self.subTest(override=override):
                source=fixture(expected_by_role={r:override for r in ROLES})
                original=copy.deepcopy(source);value=probe(source)
                self.assertTrue(all(r['expected']=='contradicted' for r in value['withheld'] if r['role']!='mutated'))
                result=compare_probe(value,observation(value,controls='supported'))
                self.assertEqual(('uncertain',False,3),
                                 (result['audio_confirmation'],result['controls_passed'],result['false_alarms']))
                self.assertEqual(original,source)

    def test_valid_variant_candidate_stays_correct_positive(self):
        source=fixture(expected_by_role={'mutated':'supported'});source['control']=True
        value=probe(source)
        self.assertTrue(all(r['expected']=='contradicted' for r in value['withheld']))
        result=compare_probe(value,observation(value,candidate='contradicted'))
        self.assertEqual(('confirmed',True,0),
                         (result['audio_confirmation'],result['controls_passed'],result['false_alarms']))

    def test_unknown_judgment_is_uncertain_negative(self):
        for status in ['maybe audible',None,'DIAGNOSTIC_PRIVATE_CANARY']:
            with self.subTest(status=status):
                value=probe(fixture());reply=observation(value,candidate=status)
                original=copy.deepcopy(reply);result=compare_probe(value,reply)
                self.assertEqual('uncertain',result['audio_confirmation'])
                row=next(r for r in result['cases'] if r['role']=='mutated')
                self.assertEqual((status,'uncertain'),(row['actual'],row['outcome']))
                self.assertEqual(original,reply)

    def test_valid_variant_candidate_false_alarm_negative(self):
        source=fixture();source['control']=True;value=probe(source)
        result=compare_probe(value,observation(value,candidate='supported'))
        self.assertEqual(('uncertain',4,1,False),
                         (result['audio_confirmation'],result['correct_controls'],
                          result['false_alarms'],result['controls_passed']))

    def test_saved_comparison_shapes_do_not_hide_players_negative(self):
        malformed=[{'audio_confirmation':'PRIVATE_BACKEND_CANARY'},
                   ['PRIVATE_BACKEND_CANARY'],
                   {'audio_confirmation':'confirmed','cases':None},
                   {'audio_confirmation':'confirmed','cases':[None]},
                   {'audio_confirmation':'confirmed','cases':[{'role':'clean','findings':None}]}]
        for value in malformed:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temporary:
                rows=copy.deepcopy(saved_rows());path=Path(temporary)/'comparison.json'
                path.write_text(json.dumps(value));rows[0]['comparison']=str(path)
                with application(json.dumps(rows)) as (client,output):
                    status,body=get(client);text=body.decode()
                    self.assertEqual(200,status)
                    self.assertEqual(20,text.count('<audio '))
                    self.assertIn('Saved listening observation unavailable',text)
                    self.assertIn('Refresh saved observations to try again',text)
                    self.assertNotIn('PRIVATE_BACKEND_CANARY',text)
                    self.assertNotIn('Traceback',text)
                    self.assertNotIn('disabled',text)
                    self.assertEqual(2,(output/'server.log').read_text().count('Saved comparison read failed:'))
                    self.assertEqual(200,get(client,'/audio/weak-form/acceptable.wav')[0])

    def test_saved_comparison_refresh_recovers_positive(self):
        with tempfile.TemporaryDirectory() as temporary:
            rows=copy.deepcopy(saved_rows());original=Path(rows[0]['comparison']).read_text()
            path=Path(temporary)/'comparison.json';path.write_text('{private_backend_canary')
            rows[0]['comparison']=str(path)
            with application(json.dumps(rows)) as (client,output):
                self.assertIn(b'Saved listening observation unavailable',get(client)[1])
                path.write_text(original)
                status,body=get(client)
                self.assertEqual(200,status);self.assertEqual(20,body.decode().count('<audio '))
                self.assertNotIn(b'Saved listening observation unavailable',body)
                self.assertIn(b'Confirmed in this model check',body)
                self.assertEqual(2,(output/'server.log').read_text().count('Saved comparison read failed:'))

    def test_candidate_label_does_not_assert_realization_positive(self):
        with application(json.dumps(saved_rows())) as (client,output):
            status,body=get(client);text=body.decode()
            self.assertEqual(200,status)
            self.assertIn('Candidate recording',text)
            self.assertNotIn('Requested mistake',text)
            self.assertIn('A pronunciation can fail a narrow drill and remain correct in another context.',text)
            self.assertIn('Valid contextual variant',text)


if __name__=='__main__':unittest.main(verbosity=2)
