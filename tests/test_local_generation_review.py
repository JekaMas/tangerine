"""Independent review counterexamples; no model or product gate is introduced."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'audit/iteration-34-local-generation-20261027'
spec = importlib.util.spec_from_file_location('i34_review_comparison', HERE / 'compare.py')
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


class LocalGenerationReview(unittest.TestCase):
    def review_data(self):
        return ROOT/'data/iteration-34-verification-20261027'

    def packet(self, text=None):
        case = json.loads((HERE / 'PLAN.json').read_text())['cases'][1]
        text = text or 'I have two books. We make a decision for a book swap. Please help with the event.'
        candidate = dict(utterances=[dict(id='u1', canonical_text=text, surface_text=text)], planned_units=[])
        return case, candidate, text

    def claim(self, candidate, text, quote, occurrence=0, utterance='u1', judgment='true_error'):
        start = text.index(quote, occurrence)
        candidate['planned_units'].append(dict(id='false-control', expected_judgment=judgment,
            primary_taxonomy_id='lexis.collocation', realization=dict(surface_text=text),
            text_spans=[dict(utterance_id=utterance, span=dict(start_cp=start, end_cp=start+len(quote), exact_text=quote))], corrections=[]))

    def test_control_claim_siblings_negative(self):
        for quote in ['help with the event', 'help', 'Please help with the event.']:
            with self.subTest(quote=quote):
                case, candidate, text = self.packet()
                self.claim(candidate, text, quote)
                assessed = compare.quality(case, candidate, candidate)
                self.assertEqual((assessed['FP'], assessed['TN'], assessed['accuracy']), (1, 3, .75))
                self.assertFalse(assessed['qualified'])
                self.assertIn('Correct control missing, changed or claimed: help with the event', assessed['findings'])
        case, candidate, text = self.packet('I have two books. We make a decision for a book swap. Please help with the event. We help with the event.')
        self.claim(candidate, text, 'help', text.index('We help'))
        assessed = compare.quality(case, candidate, candidate)
        self.assertEqual((assessed['FP'], assessed['TN']), (1, 3))
        self.assertEqual(len(assessed['construction_deviations']), 1)

    def test_unclaimed_correct_controls_positive(self):
        case, candidate, text = self.packet()
        assessed = compare.quality(case, candidate, candidate)
        self.assertTrue(assessed['qualified'])
        self.assertEqual((assessed['FP'], assessed['TN'], assessed['accuracy']), (0, 4, 1))
        # Same quote in a different turn and an accepted control are not claims
        # against this occurrence. A neighboring non-overlapping span is not one.
        for utterance, judgment, quote in [('other', 'true_error', 'help'), ('u1', 'acceptable_variant', 'help'), ('u1', 'true_error', 'Please ')]:
            with self.subTest(utterance=utterance, judgment=judgment, quote=quote):
                c = copy.deepcopy(candidate)
                self.claim(c, text, quote, utterance=utterance, judgment=judgment)
                self.assertEqual(compare.quality(case, candidate, c)['TN'], 4)

    def test_selected_alternative_positive(self):
        result=json.loads((compare.OUT/'comparison.json').read_text())
        # The frozen rule is correctness on BOTH common requests, not a raw
        # protocol pass or an unmeasured global model leaderboard.
        qualified=[a for a in result['alternatives'] if a['qualified']]
        self.assertEqual([a['id'] for a in qualified],['projection-replay'])
        self.assertEqual(result['selected'],qualified[0]['id'])
        q=qualified[0]
        self.assertEqual(q['quality'],dict(TP=2,FP=0,FN=0,TN=6,precision=1,recall=1,accuracy=1))
        self.assertEqual(q['measured']['dispatches'],0)
        for row in result['rows']:
            case=next(c for c in json.loads((HERE/'PLAN.json').read_text())['cases'] if c['id']==row['case'])
            d=ROOT/row['directory'];prefix=row['id']+'-'
            clean=d/(prefix+'canonical_asset_id.json');candidate=d/(prefix+'mutated_asset_id.json')
            assessed=compare.quality(case,json.loads(clean.read_text()) if clean.exists() else None,
                                     json.loads(candidate.read_text()) if candidate.exists() else None)
            self.assertEqual(assessed,row['quality'])
        self.assertEqual(result['dispatch_count'],30)
        self.assertEqual(result['api_charge_usd'],0)

    def test_unqualified_alternatives_negative(self):
        result=json.loads((compare.OUT/'comparison.json').read_text())
        a={a['id']:a for a in result['alternatives']}
        self.assertFalse(a['schema']['qualified']);self.assertEqual(a['schema']['admitted'],0)
        self.assertIsNone(a['schema']['quality']['accuracy'])
        self.assertFalse(a['repaired-plain']['qualified'])
        self.assertEqual(a['repaired-plain']['admitted'],2)
        self.assertEqual(a['repaired-plain']['quality']['precision'],.5)
        self.assertFalse(a['deadline-profile-plain']['qualified'])
        self.assertEqual(a['deadline-profile-plain']['admitted'],1)
        self.assertFalse(a['qwen-repaired-plain']['qualified'])
        self.assertEqual(a['qwen-repaired-plain']['quality']['precision'],.5)
        replay=[r for r in result['rows'] if r['alternative']=='projection-replay']
        self.assertTrue(all(r['actual_inference'] is False for r in replay))
        zero=next(r for r in replay if r['case']=='zero-errors')
        self.assertEqual(zero['quality']['construction_deviations'],[dict(control='help with the event',requested_occurrences=1,actual_clean_occurrences=2)])

    def browser(self):
        d=self.review_data()/'browser'
        return json.loads((d/'observations.json').read_text()),[json.loads(s) for s in (d/'requests.jsonl').read_text().splitlines()]

    def test_ui_failure_and_resume_positive(self):
        v,events=self.browser()
        for key in ['generation-failed-1280','refreshed-failure-1280','generation-failed-390','resumed-ui-only-390']:
            row=v[key]
            self.assertEqual(row['topic'],'Two friends plan a neighbourhood book swap.')
            self.assertTrue(row['generateEnabled']);self.assertTrue(row['topicEnabled'])
        self.assertIn('resume this exercise explicitly',v['generation-failed-1280']['body'])
        self.assertIn('Resume exercise',v['generation-failed-390']['body'])
        self.assertIn('Exercise saved. Open the Library',v['resumed-ui-only-390']['body'])
        self.assertEqual(v['resumed-ui-only-390']['alerts'],[])
        self.assertEqual(v['busyNative'],dict(topicDisabled=True,generateDisabled=True,status=['Generating clean text, mutations and audio…']))
        self.assertEqual(v['keyboardNative'],dict(focus='Refresh',outline='3px',style='solid'))
        post=[e for e in events if e['scenario']=='empty' and e['method']=='POST']
        self.assertEqual([e['path'] for e in post],['/api/v1/blueprints','/api/v1/candidates:generate','/api/v1/preparations/5a3ff6e5-3aae-4864-be0e-fe4af335e7e3:resume'])
        request=post[0]['body']['exercise_request']
        self.assertEqual({k:request[k] for k in ['speaker_count','text_length_words','english_level','mutation_count','category_families','severity_levels']},dict(speaker_count=2,text_length_words=90,english_level='B1',mutation_count=2,category_families=['grammar','lexis'],severity_levels=['minor']))
        self.assertEqual(len({e['idempotency_key'] for e in post}),3)

    def test_ui_technical_error_and_implicit_writes_negative(self):
        v,events=self.browser()
        for row in v.values():
            if 'body' not in row:continue
            for private in ['PRIVATE_BACKEND_CANARY','SQL','password','private trace']:
                self.assertNotIn(private,row['body'])
        self.assertIn('local service returned an unreadable response',v['malformed-response-390']['body'])
        self.assertEqual(v['malformed-response-390']['topic'],'Retain this request while the local service recovers.')
        self.assertTrue(all(e['forwarded'] is False for e in events))
        for scenario in ['transient-read','unavailable-read','explicit-read-recovery']:
            self.assertEqual([e for e in events if e['scenario']==scenario and e['method']!='GET'],[])
        for scenario in ['malformed-write','busy-check']:
            self.assertEqual([e['path'] for e in events if e['scenario']==scenario and e['method']=='POST'],['/api/v1/blueprints','/api/v1/candidates:generate'])

    def test_ui_read_recovery_positive(self):
        v,events=self.browser()
        for path in ['/api/v1/preparations','/api/v1/preparation-options']:
            transient=[e for e in events if e['scenario']=='transient-read' and e['path']==path]
            self.assertEqual([e['status'] for e in transient],[503,200])
            exhausted=[e for e in events if e['scenario']=='unavailable-read' and e['path']==path]
            self.assertEqual([e['status'] for e in exhausted],[503,503,503])
            recovered=[e for e in events if e['scenario']=='explicit-read-recovery' and e['path']==path]
            self.assertEqual([e['status'] for e in recovered],[200])
        self.assertIn('Retry categories',v['catalogue-exhausted-390']['body'])
        self.assertTrue(v['catalogue-exhausted-390']['generateEnabled'])
        self.assertEqual(v['read-recovered-settled-390']['alerts'],[])
        self.assertEqual(v['read-recovered-settled-390']['topic'],'Retain this request while the local service recovers.')

    def test_ui_typography_and_reflow_negative(self):
        v,_=self.browser()
        self.assertEqual({row['width'] for row in v.values() if 'width' in row},{1280,390,320})
        for row in v.values():
            if 'width' not in row:continue
            self.assertFalse(row['overflow'])
            self.assertTrue(row['fontLoaded']);self.assertEqual(row['fontStatus'],'loaded')
            self.assertEqual(row['bodyStyle']['size'],'17px');self.assertEqual(row['bodyStyle']['line'],'24.65px')
        for key in ['customize-1280','customize-320']:
            self.assertEqual(len(v[key]['captions']),9)
            for caption in v[key]['captions']:
                self.assertEqual(caption['size'],'14px')
                self.assertLessEqual(caption['scrollWidth'],caption['width']+1)
        self.assertIn('Workspace',v['navigation-320']['body'])
        video=json.loads((self.review_data()/'browser/video-probe.json').read_text())
        self.assertEqual(video['new_model_calls'],0);self.assertTrue(video['silent'])
        self.assertGreater(float(video['probe']['format']['duration']),20)
        self.assertEqual([s['codec_type'] for s in video['probe']['streams']],['video'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
