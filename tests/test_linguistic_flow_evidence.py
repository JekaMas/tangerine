"""Readback of actual on-demand native observations; never dispatch a model."""
import json
from pathlib import Path
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/linguistic-fullness-20261023/flow'


def read(name):
    return json.loads((D/name).read_text())


class LinguisticFlowEvidence(unittest.TestCase):
    def test_generated_preparation_positive(self):
        clean=read('canonical_asset_id.json')['utterances']
        changed=read('mutated_asset_id.json')
        self.assertEqual(len(clean),3)
        self.assertEqual(len(changed['planned_units']),1)
        self.assertEqual(clean[0]['canonical_text'],'Shall I book two tickets to York for our meeting on Friday?')
        self.assertEqual(changed['utterances'][0]['surface_text'],'Shall I book two ticket to York for our meeting on Friday?')
        for a,b in zip(clean,changed['utterances']):
            self.assertEqual(a['canonical_text'],b['canonical_text'])
            self.assertEqual(a['speaker_id'],b['speaker_id'])
            if a['id']!='u1':self.assertEqual(a,b)
        key=read('published-ground-truth.json')
        self.assertEqual(key['status'],'published')
        self.assertEqual(key['units'][0]['primary_taxonomy_id'],'grammar.nouns.number')
        with wave.open(str(D/'actual-flow.wav'),'rb') as audio:
            self.assertEqual((audio.getnchannels(),audio.getsampwidth(),audio.getframerate()),(1,2,24000))
            self.assertGreater(audio.getnframes(),0)
            self.assertTrue(any(audio.readframes(audio.getnframes())))

    def test_correct_repair_false_claims_negative(self):
        actual=read('actual-score-feedback.json')
        self.assertEqual(actual['feedback_status'],'complete')
        counts=actual['score']['counts']
        self.assertEqual((counts['tp'],counts['fp'],counts['fn']),(1,1,0))
        for metric,n,d in [('detection.precision','1','2'),('correction.strict_accuracy','1','1'),('explanation.graded_accuracy','0','1')]:
            self.assertEqual((actual['score']['metrics'][metric]['numerator'],actual['score']['metrics'][metric]['denominator']),(n,d))
        text=' '.join(x['text'] for x in actual['feedback']['items'])
        self.assertIn('children',text)
        self.assertIn('Shall I',text)
        self.assertTrue(any(x['kind']=='false_positive' for x in actual['feedback']['items']))
        self.assertTrue(any(x['kind']=='recommendation' for x in actual['feedback']['items']))

    def test_optional_case_review_positive(self):
        r=read('case_review-stage.json')
        self.assertEqual(r['error'],'<nil>')
        self.assertEqual(r['output']['resolution'],'supported')
        self.assertTrue(r['result']['receipt_ids'])
        self.assertTrue(r['result']['context_snapshot_ids'])
        supplied=read('case_review-input.json')['input']
        self.assertIsNone(supplied['answer'])
        self.assertEqual(supplied['ground_truth']['units'][0]['realization']['surface_text'],'two ticket')

    def test_optional_reconsideration_negative(self):
        r=read('adjudication-stage.json')
        self.assertEqual(r['error'],'<nil>')
        self.assertEqual(r['output']['resolution'],'supported')
        self.assertTrue(r['result']['receipt_ids'])
        decisions=r['output']['decisions']['decisions']
        self.assertTrue(any(x['decision']=='matched_error' for x in decisions))
        self.assertTrue(any(x['decision']=='false_positive' for x in decisions))
        unsupported=[a for x in decisions for a in x['explanation']['additional_assertions'] if a['judgment']=='unsupported']
        self.assertGreaterEqual(len(unsupported),2)


if __name__=='__main__':unittest.main(verbosity=2)
