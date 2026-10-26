"""Current I22 literal oracles, with bounded reuse of actual native/CUA/Lab data.

Local negative protocol cases execute the real dictionary owner. The live and
browser cases inspect actual retained inputs/results independently; no hosted
synthesis/judgment is repeated by acceptance. Text/semantic replies are constructed.
"""
import base64,copy,hashlib,importlib.util,json,subprocess,unittest,wave
from pathlib import Path
from tests import test_elevenlabs as protocol
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-22-elevenlabs-20261026'
LIVE=DATA/'live'
SPEC=importlib.util.spec_from_file_location('i22_review',ROOT/'audit/iteration-22-elevenlabs-20261026/review.py')
review=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(review)
ANSWER="The second think in speaker one's turn uses /s/; use /θɪŋk/."

def read(name):return json.loads((DATA/name).read_text())

def observed_protocol(method):
    result=unittest.TestResult()
    protocol.ElevenLabsDictionary(method).run(result)
    if not result.wasSuccessful():raise AssertionError(result.errors+result.failures)
    if result.testsRun!=1 or result.skipped:raise AssertionError('missing exact local protocol case')

class CompletionI22(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts=read('observations.json');cls.fixture=read('live/native-fixture.json')
        cls.frozen=read('live/frozen-plan.json');cls.progress=read('live/progress.json')
        cls.key=read('live/key.json');cls.result=read('live/result.json')
        cls.docs=read('live/native-documents.json');cls.packet=read('REVIEW.json')
        cls.events=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]

    def hosted(self):
        out=[]
        for r in self.docs:
            id=r.get('wire_response_asset_id')
            if not id:continue
            p=LIVE/'assets'/(id+'.json')
            if not p.is_file():continue
            native=json.loads(p.read_text()).get('receipt',{}).get('native',{})
            for n in [native,native.get('paired_mutation',{}).get('native',{})]:
                if n.get('url'):out.append((n['url'],json.loads(base64.b64decode(n['body_base64']))))
        return out

    def test_dictionary_positive(self):
        pieces=self.frozen['pieces'];target=pieces[1]
        self.assertEqual(['I think we should ','think',' again.','I think so.'],[p['operations'][0]['text'] for p in pieces])
        self.assertEqual('eleven_flash_v2',self.frozen['profile']['model'])
        rules=target['pronunciation_dictionary_bindings']
        calls=self.hosted();self.assertEqual(5,len(calls))
        for url,body in calls:self.assertEqual('eleven_flash_v2',body['model_id'])
        target_calls=[b for _,b in calls if b['text']=='think'];self.assertEqual(2,len(target_calls))
        for b,name,ipa in zip(target_calls,['reference','mutated'],['θɪŋk','sɪŋk']):
            self.assertEqual([rules[name]['locator']],b['pronunciation_dictionary_locators'])
            self.assertIn(('<phoneme>'+ipa+'</phoneme>').encode(),base64.b64decode(rules[name]['pls_base64']))
            self.assertEqual(200,rules[name]['http_status'])
        heard=read('live/auditory-response.json')['output']['findings']
        self.assertEqual({'A':'sɪŋk','B':'θɪŋk'},{h['unit_id']:h['proposed_ipa'] for h in heard})
        self.assertTrue(all(h['status']=='supported' for h in heard))

    def test_scope_negative(self):
        observed_protocol('test_scope_positive')
        observed_protocol('test_phone_pair_coordinates_positive')
        calls=self.hosted()
        for url,b in calls:
            if b['text']!='think':self.assertNotIn('pronunciation_dictionary_locators',b)
        voices={b['text']:url.split('/v1/text-to-speech/')[1].split('?')[0] for url,b in calls}
        self.assertEqual('EXAVITQu4vr4xnSDxMaL',voices['I think we should '])
        self.assertEqual('JBFqnCBsd6RMkjVDRZzb',voices['I think so.'])
        self.assertEqual(dict(start=18,end=23),self.frozen['pieces'][1]['surface_scope'])

    def test_dictionary_admission_negative(self):
        observed_protocol('test_dictionary_admission_negative')
        # Native public outcome remains the existing mapping; no fabricated ID.
        self.assertEqual('LOCAL_BUDGET_EXCEEDED',read('live/failed-preparation.json')['last_failure']['code'])

    def test_quota_negative(self):
        observed_protocol('test_quota_negative')
        observed_protocol('test_unsupported_model_negative')
        receipts=[d for d in self.docs if d.get('http_status')==429]
        self.assertEqual(1,len(receipts));self.assertEqual('PROVIDER_QUOTA',receipts[0]['error_code'])
        self.assertEqual('transport_error',receipts[0]['outcome'])
        before,after=read('live/subscription-before.json'),read('live/subscription-after.json')
        self.assertEqual(['free','free'],[x['tier'] for x in [before,after]])
        self.assertEqual(22,after['character_count']-before['character_count'])
        for x in [before,after]:
            self.assertFalse(x['can_extend_character_limit']);self.assertEqual(0,x['max_credit_limit_extension'])
            self.assertEqual('0',x['current_overage']['amount'])

    def test_resume_positive(self):
        before=read('live/failed-progress.json')['pieces'];after=self.progress['pieces']
        self.assertEqual('complete',before[0]['state']);self.assertEqual('failed',before[1]['state'])
        self.assertEqual(before[0]['asset_id'],after[0]['asset_id'])
        self.assertTrue(all(p['state']=='complete' for p in after))
        self.assertEqual(read('live/failed-preparation.json')['render_plan_asset_id'],read('live/preparation.json')['render_plan_asset_id'])
        self.assertEqual(4,len(after));self.assertEqual(5,len(self.hosted()))
        self.assertEqual('complete',read('live/preparation.json')['phase_states']['render'])

    def test_ordinary_flow_positive(self):
        score=self.result['score'];counts=score['counts']
        self.assertEqual((1,0,0),(counts['tp'],counts['fn'],counts['fp']))
        self.assertEqual('100.0',score['composite']['display'])
        self.assertEqual(dict(numerator='100',denominator='1'),score['composite']['exact_value_0_100'])
        metric=score['metrics']['correction.graded_accuracy'];self.assertEqual(('1','1'),(metric['numerator'],metric['denominator']))
        self.assertEqual('not_applicable',score['optional_explanation']['status'])
        self.assertEqual('complete',self.result['feedback_status'])
        self.assertEqual(self.fixture['attempt_id'],self.result['attempt_id'])
        self.assertEqual(self.fixture['case_id'],score['case_version_id'])
        self.assertEqual(hashlib.sha256((LIVE/'exercise.wav').read_bytes()).hexdigest(),self.key['audio']['sha256'])
        c=self.facts['cases'];self.assertEqual(ANSWER,c['savedDraft']['answer']);self.assertEqual(ANSWER,c['reopenedDraft']['answer'])
        self.assertIn('100.0 / 100',c['reopenedResults']['main']);self.assertIn('0 missed',c['reopenedResults']['main'])
        self.assertTrue(c['desktopResults']['readOnly']);self.assertEqual(ANSWER,c['desktopResults']['answer'])
        media=c['playing']['media'][0];self.assertFalse(media['paused']);self.assertEqual(4,media['readyState']);self.assertIsNone(media['error'])
        with wave.open(str(LIVE/'exercise.wav'),'rb') as w:
            self.assertEqual((24000,1,2),(w.getframerate(),w.getnchannels(),w.getsampwidth()))
            self.assertAlmostEqual(media['duration'],w.getnframes()/24000,places=5)
        self.assertIn(self.fixture['case_id'],str(c['library']['links']))
        self.assertIn(self.fixture['attempt_id'],str(c['history']['links']))
        self.assertIn('Audio complete',' '.join(c['preparationReadback']['main'].split()))

    def test_safe_recovery_positive(self):
        c=self.facts['cases']
        self.assertEqual([],c['readRecovered']['alerts']);self.assertEqual(ANSWER,c['readRecovered']['answer'])
        row=c['fixedReadFailure'];self.assertEqual([],row['statuses']);self.assertEqual(ANSWER,row['answer'])
        self.assertEqual(['Saved attempt is unavailable. Your text is retained. Refresh to retry.'],row['alerts'])
        self.assertTrue(all(not b['disabled'] for b in row['buttons']))
        self.assertNotIn('PRIVATE_',row['main'])
        events=[e for e in self.events if e.get('event')=='response' and e.get('scenario')=='fixed-read-failure']
        self.assertEqual([503,503,503],[e['status'] for e in events])
        row=c['submitUnavailable'];self.assertEqual(ANSWER,row['answer']);self.assertNotIn('PRIVATE_',row['main'])
        self.assertTrue(all(not b['disabled'] for b in row['buttons']))
        sent=[e for e in self.events if e.get('event')=='request' and e.get('scenario')=='controlled-submit-unavailable' and e.get('method')=='POST' and e.get('path','').endswith(':submit')]
        self.assertEqual(1,len(sent));self.assertEqual(ANSWER,sent[0]['body']['answer_text'])
        self.assertEqual('true',c['mobileMenu']['expanded']);self.assertEqual('Toggle navigation',c['mobileMenu']['focus'])

    def test_native_interval_positive(self):
        out=read('live/resolved-after-label-repair.json')
        self.assertEqual('generated_piece_interval_24000',out['alignment_basis'])
        self.assertNotIn('kokoro',out['alignment_basis'])
        key_interval=self.key['units'][0]['audio_intervals'][0]
        first,target=self.progress['pieces'][:2]
        self.assertEqual(dict(start_ms=first['sample_count']//24,end_ms=(first['sample_count']+target['sample_count']+23)//24),key_interval)
        replay=self.facts['cases']['replayStopped']
        self.assertTrue(replay['paused']);self.assertLess(replay['time'],replay['duration'])
        self.assertGreaterEqual(replay['time'],key_interval['end_ms']/1000)
        self.assertLess(replay['time']-key_interval['end_ms']/1000,.5)

    def test_review_positive(self):
        self.assertEqual([],review.review_errors(self.packet,self.facts,self.fixture,self.result))
        lab=read('lab-readback.json');self.assertEqual('FINISHED',lab['status'])
        self.assertEqual(self.fixture['attempt_id'],lab['attempt_id']);self.assertEqual('observed',lab['readback'])
        self.assertEqual(0,lab['export_inference_calls'])
        self.assertIn('ordinary-flow/exercise.wav',lab['files'])
        self.assertIn('ordinary-flow/constructed-wires.json',lab['files'])

    def test_ux_omission_negative(self):
        invalid=copy.deepcopy(self.packet);invalid.pop('ui_ux')
        self.assertIn('ui_ux unsupported',review.review_errors(invalid,self.facts,self.fixture,self.result))
        invalid['ui_ux']=dict(observations=['web build succeeded'],references=[])
        self.assertIn('ui_ux unsupported',review.review_errors(invalid,self.facts,self.fixture,self.result))

    def test_typography_omission_negative(self):
        invalid=copy.deepcopy(self.packet);invalid.pop('typography')
        self.assertIn('typography unsupported',review.review_errors(invalid,self.facts,self.fixture,self.result))
        facts=copy.deepcopy(self.facts);facts['layouts'][0]['labels'][0]['size']='10px'
        self.assertIn('label readability',review.review_errors(self.packet,facts,self.fixture,self.result))

    def test_evidence_mismatch_negative(self):
        invalid=copy.deepcopy(self.packet);invalid['attempt_id']='different-attempt'
        self.assertIn('native identity',review.review_errors(invalid,self.facts,self.fixture,self.result))
        invalid=copy.deepcopy(self.packet);invalid['unexecuted_cases']=['planned']
        self.assertIn('unexecuted',review.review_errors(invalid,self.facts,self.fixture,self.result))
        invalid=copy.deepcopy(self.packet);invalid['reference_origin']='candidate-generated'
        self.assertIn('reference origin',review.review_errors(invalid,self.facts,self.fixture,self.result))
        invalid=copy.deepcopy(self.packet);invalid['requested_benchmark_calls']=50
        self.assertIn('performance scope',review.review_errors(invalid,self.facts,self.fixture,self.result))

    def test_limits_negative(self):
        observed_protocol('test_partial_word_negative')
        observed_protocol('test_unsupported_phone_timing_negative')
        observed_protocol('test_billing_negative')
        self.assertFalse(any(e.get('event')=='forbidden_execution' for e in self.events))

if __name__=='__main__':unittest.main()
