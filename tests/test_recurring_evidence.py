"""Read back this task's real synthetic observations with literal expectations.

No provider calls are made by this suite. Missing observations fail rather than
being silently substituted by fixtures. Generation and semantic decisions are
finite observations, not universal linguistic accuracy claims.
"""
from pathlib import Path
import json, re, unittest, wave

R = Path(__file__).resolve().parents[1]
O = R / 'data/recurring-errors-20261025'

def read(name):
    return json.loads((O / name).read_text())

def pcm(path):
    with wave.open(str(path)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
        return w.readframes(w.getnframes())

class RecurringEvidence(unittest.TestCase):
    def test_controls_positive(self):
        v = read('browser.json')
        self.assertEqual([r['target_percent'] for r in v['restored']], [85, 95])
        self.assertEqual(v['restored'][0]['instruction'], 'Drop plural endings after numbers')
        request = v['effective']['exercise_request']
        self.assertEqual(request['mutation_count'], 1)
        self.assertEqual(request['speaker_voice_ids'], ['melo_en_au', 'melo_en_in'])
        self.assertEqual(request['category_ids'], ['grammar.nouns.number'])
        self.assertEqual(request['recurring_errors'][0]['target_percent'], 85)
        blueprint = read('demo-blueprint.json')
        self.assertEqual({**request, 'audio_backend': None, 'mutation_seed': None}, blueprint['exercise_request'])

    def test_controls_negative(self):
        v = read('browser.json')
        self.assertEqual([r['speaker_number'] for r in v['one']], [1])
        self.assertEqual([r['speaker_number'] for r in v['effective']['exercise_request']['recurring_errors']], [1])
        self.assertTrue(v['failure_retained'])
        self.assertEqual(v['llm_dispatches_during_failure'], 0)
        self.assertEqual(v['viewport']['scrollWidth'], v['viewport']['width'])

    def test_acoustic_positive(self):
        for name in ['speech-grouped', 'speech-kokoro']:
            d = O / name
            native = read(name + '/response.json')['receipt']['native']
            self.assertEqual(list(native['paired_mutations']), ['habit'])
            pair = native['paired_mutations']['habit']['native']
            self.assertEqual(len(native['acoustic_scopes']), 3)
            self.assertEqual(len(pair['acoustic_scopes']), 3)
            for reference, changed in zip(native['acoustic_scopes'], pair['acoustic_scopes']):
                self.assertEqual(reference['surface_scope'], changed['surface_scope'])
                if name == 'speech-grouped':
                    self.assertEqual(reference['phonemes'], ['th', 'ih', 'ng', 'k'])
                    self.assertEqual(changed['phonemes'], ['s', 'ih', 'ng', 'k'])
                else:
                    self.assertEqual(reference['phonemes'], 'θɪŋk')
                    self.assertEqual(changed['phonemes'], 'sɪŋk')
            self.assertNotEqual(pcm(d / 'reference.wav'), pcm(d / 'mutated.wav'))
            for index in range(3):
                self.assertEqual(read(name + '/transform-' + str(index) + '.json')['receipt']['model_calls'], 0)

    def test_correct_exception_negative(self):
        for name in ['speech-grouped', 'speech-kokoro']:
            d = O / name
            observed = read(name + '/observation.json')
            a, b = observed['correct_before'], observed['correct_after']
            self.assertEqual(observed['eligible_opportunities'], 4)
            self.assertEqual(observed['mutated_opportunities'], 3)
            self.assertEqual(pcm(d / 'reference.wav')[a['start_sample']*2:a['end_sample']*2],
                             pcm(d / 'mutated.wav')[b['start_sample']*2:b['end_sample']*2])

    def test_generation_positive(self):
        candidate, key, p = read('demo-candidate.json'), read('demo-key.json'), read('demo-preparation-state.json')
        self.assertEqual(p['phase_states'], dict(canonical_text='complete', mutation='complete', render='complete'))
        self.assertEqual(len(candidate['planned_units']), 1)
        unit = candidate['planned_units'][0]
        self.assertEqual(unit['primary_taxonomy_id'], 'grammar.nouns.number')
        ledger = unit['recurrence']
        self.assertEqual([ledger['speaker_number'], ledger['target_percent']], [1, 85])
        actual = []
        for turn in candidate['utterances']:
            if turn['speaker_id'] == 's1':
                actual.extend((turn['id'], m.start(), m.end()) for m in re.finditer('two tickets', turn['canonical_text']))
            else:
                self.assertEqual(turn['surface_text'], turn['canonical_text'])
        self.assertEqual(len(actual), 7)
        self.assertEqual(sorted(actual), sorted((r['utterance_id'], r['canonical_span']['start_cp'], r['canonical_span']['end_cp']) for r in ledger['opportunities']))
        self.assertEqual(sum(r['mutated'] for r in ledger['opportunities']), 6)
        self.assertEqual(len(unit['text_spans']), 6)
        self.assertEqual(key['units'][0]['recurrence'], ledger)
        with wave.open(str(O / 'demo-dialogue.wav')) as audio:
            self.assertEqual(audio.getframerate(), 24000)
            self.assertGreater(audio.getnframes(), 240000)

    def test_answer_positive(self):
        v = read('positive-results.json')
        self.assertEqual([v['status'], v['feedback_status']], ['complete', 'complete'])
        self.assertEqual([v['score']['counts'][k] for k in ['tp', 'fn', 'fp', 'true_errors']], [1, 0, 0, 1])
        self.assertEqual(v['score']['composite']['exact_value_0_100'], dict(numerator='100', denominator='1'))
        self.assertEqual(v['score']['optional_explanation']['value'], 0)
        recurrence = v['score']['items'][0]['reference']['recurrence']
        self.assertEqual([recurrence['mutation_count'], recurrence['opportunity_count'], recurrence['realized_percent_display']], [6, 7, '85.7'])
        self.assertEqual(recurrence['correct_examples'], ['two tickets'])
        self.assertTrue(v['feedback']['items'])

    def test_correct_answer_negative(self):
        v = read('negative-results.json')
        self.assertEqual([v['status'], v['feedback_status']], ['complete', 'complete'])
        self.assertEqual([v['score']['counts'][k] for k in ['tp', 'fn', 'fp', 'true_errors']], [0, 1, 1, 1])
        self.assertEqual(v['score']['composite']['exact_value_0_100'], dict(numerator='0', denominator='1'))
        self.assertTrue(v['feedback']['items'])

    def test_preservation_negative(self):
        p = read('preservation.json')
        self.assertTrue(p['original_attempt_unchanged'])
        self.assertTrue(p['configuration_restored'])
        self.assertTrue(p['credential_presence_unchanged'])
        self.assertEqual(p['provider_bindings'], ['openai_chatgpt'])
        self.assertEqual(p['billing_modes'], ['included_subscription'])
        self.assertEqual(p['speech_providers'], ['local_melo'])

if __name__ == '__main__':
    unittest.main()
