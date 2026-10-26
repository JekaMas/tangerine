"""Literal I23 oracles over actual retained native/Free/CUA/Lab observations.

No inference is repeated for acceptance. Controlled failure/repair packets prove
their actual native boundary; a prior uncertain result and panic remain failures.
"""
import copy,hashlib,importlib.util,json,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/iteration-23-gemini-20261026'
spec=importlib.util.spec_from_file_location('i23_review',ROOT/'audit/iteration-23-gemini-20261026/review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
def read(name):return json.loads((DATA/name).read_text())
def output(dispatch):
 return json.loads(''.join(p.get('text','') for s in dispatch['response'].get('steps',[]) if s['type']=='model_output' for p in s.get('content',[]) if p['type']=='text'))
def passed(file,name):
 rows=[json.loads(x) for x in (DATA/file).read_text().splitlines()]
 return any(r.get('Action')=='pass' and r.get('Test')==name for r in rows) and not any(r.get('Action')=='fail' for r in rows)

class CompletionI23(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.fixture=read('resume/fixture.json');cls.result=read('resume/result.json');cls.facts=read('observations.json');cls.packet=read('REVIEW.json')

 def test_gemini_positive(self):
  p=read('live/preparation.json');self.assertEqual({'canonical_text':'complete','mutation':'complete','render':'complete'},p['phase_states'])
  assets=DATA/'live/assets';settings=json.loads((assets/(p['settings_asset_id']+'.json')).read_text());request=settings['blueprint']['exercise_request']
  self.assertEqual('Planning a community garden',request['topic']);self.assertEqual((2,90,'B1',1),(request['speaker_count'],request['text_length_words'],request['english_level'],request['mutation_count']))
  self.assertEqual(['grammar'],request['category_families'])
  key=read('live/key.json');self.assertEqual(1,len(key['units']));self.assertEqual({'s1','s2'},{u['speaker_id'] for u in key['utterances']})
  unit=key['units'][0];self.assertEqual('grammar.determiners.article_omission',unit['primary_taxonomy_id']);self.assertEqual('the',unit['corrections'][0]['text'])
  self.assertIn('ideas for the layout',key['utterances'][0]['canonical_text']);self.assertIn('ideas for layout',key['utterances'][0]['surface_text'])
  self.assertEqual(hashlib.sha256((DATA/'live/exercise.wav').read_bytes()).hexdigest(),key['audio']['sha256'])
  with wave.open(str(DATA/'live/exercise.wav')) as audio:self.assertEqual((1,24000,693000),(audio.getnchannels(),audio.getframerate(),audio.getnframes()))
  playback=read('playback.json');self.assertFalse(playback['paused']);self.assertGreater(playback['currentTime'],0);self.assertEqual(28.875,playback['duration'])
  # Listening owns its immutable projection/version; the generator's key has
  # its own identity. Join them through the saved native source-key relation.
  relationship=read('native-relationship.json');self.assertEqual(self.fixture['case_id'],relationship['case_version_id']);self.assertEqual(p['key_id'],relationship['source_key_id'])
  self.assertEqual(self.fixture['preparation_id'],p['id']);self.assertEqual(self.fixture['audio_asset_id'],key['audio']['asset_id']);self.assertEqual(key['audio']['sha256'],read('resume/attempt.json')['Context']['audio_sha256'])
  self.assertEqual({'tp':1,'fn':0,'fp':0},{k:self.result['score']['counts'][k] for k in ['tp','fn','fp']});self.assertEqual('100.0',self.result['score']['composite']['display']);self.assertEqual('complete',self.result['feedback_status'])
  self.assertEqual(read('answer-expectation.json')['answer'],read('resume/attempt.json')['Attempt']['answer_text'])
  for folder in ['live','repair','resume']:
   for d in read(folder+'/dispatches.json'):
    self.assertEqual('gemini-3.1-flash-lite',d['request']['model']);self.assertEqual('https://generativelanguage.googleapis.com/v1beta/interactions',d['url']);self.assertTrue(d['credential_header_present']);self.assertFalse(d['authorization_header_present']);self.assertFalse(d['request']['store']);self.assertFalse(d['request']['stream'])
  self.assertIn('No billing account',(DATA/'account-billing.txt').read_text());self.assertIn('Free tier',(DATA/'account-api-keys.txt').read_text())
  ledger=read('candidate-reconciliation.json');self.assertEqual([],ledger['discrepancies']);self.assertEqual(ledger['independent_dispatches'],ledger['native_receipts']);self.assertEqual(ledger['native_receipts'],ledger['native_snapshots'])
  lab=read('lab-readback.json');self.assertTrue(lab['readback']);self.assertEqual('FINISHED',lab['status']);self.assertEqual(0,lab['export_inference_calls'])
  self.assertTrue(passed('resume/native.jsonl','TestNativeGeminiResume'))

 def test_gemini_negative(self):
  for name,calls,code in [('quota',1,'LOCAL_BUDGET_EXCEEDED'),('denied',1,'PROVIDER_FAILURE'),('credentials',1,'MISSING_CREDENTIALS'),('unavailable',2,'PROVIDER_FAILURE')]:
   row=read('controlled/error-'+name+'.json');self.assertEqual((calls,code),(row['calls'],row['code']));before,after=row['before'],row['after']
   self.assertIsNotNone(before['canonical_asset_id']);self.assertEqual(before['canonical_asset_id'],after['canonical_asset_id']);self.assertEqual(before['settings_asset_id'],after['settings_asset_id']);self.assertIsNone(after['audio_asset_id']);self.assertEqual('complete',after['phase_states']['canonical_text']);self.assertEqual('failed',after['phase_states']['mutation'])
   self.assertTrue(passed('controlled/native.jsonl','TestNativeGeminiErrors/'+name))
  self.assertEqual(2,read('controlled/recovery.json')['calls']);self.assertTrue(passed('controlled/native.jsonl','TestNativeGeminiUnavailableRecovery'))
  live=read('live/dispatches.json');self.assertEqual([503,200],[x['http_status'] for x in live[1:3]]);self.assertEqual(live[1]['request'],live[2]['request'])

 def test_attribution_positive(self):
  repaired=read('resume/dispatches.json');extractions=[output(d) for d in repaired if d['http_status']==200 and 'clauses' in output(d)]
  self.assertTrue(extractions);accepted=extractions[-1];self.assertEqual([],accepted['unparsed_spans']);self.assertEqual(0,accepted['clauses'][0]['claim_span']['start_cp']);self.assertTrue(accepted['clauses'][0]['claim_span']['exact_text'].startswith('Speaker 1 says'))
  self.assertIn("Include a claim's speaker attribution",repaired[0]['request']['system_instruction'])
  self.assertTrue(passed('extraction-siblings.jsonl','TestInterpretationAttributionPositive'))
  self.assertTrue(passed('context/native.jsonl','TestNativeGeminiRepairContext'))
  context=read('context/repair-context.json');self.assertEqual(3,context['calls']);self.assertEqual(2,len(context['snapshots']))
  for test in ['TestGeminiRepairContextPositive','TestProviderRepairRetryContextPositive','TestProviderNoRepairContextNegative']:self.assertTrue(passed('repair-protocol.jsonl',test))

 def test_unparsed_negative(self):
  baseline=read('live/result.json');self.assertEqual('review_required',baseline['score']['status']);self.assertIsNone(baseline['score']['composite']['exact_value_0_100'])
  first=output(read('live/dispatches.json')[3]);self.assertEqual('Speaker 1 says ',first['unparsed_spans'][0]['exact_text'])
  self.assertTrue(passed('extraction-siblings.jsonl','TestInterpretationGenuineUnparsedNegative'))
  failure=''.join(json.loads(x).get('Output','') for x in (DATA/'repair/native.jsonl').read_text().splitlines());self.assertIn('index out of range [-1]',failure)
  self.assertEqual('1',(DATA/'repair/exit-code').read_text());self.assertEqual('0',(DATA/'resume/exit-code').read_text())

 def test_review_positive(self):self.assertEqual([],review.review_errors(self.packet,self.facts,self.fixture,self.result))
 def test_ux_omission_negative(self):
  p=copy.deepcopy(self.packet);p.pop('ui_ux');self.assertIn('ui_ux omitted',review.review_errors(p,self.facts,self.fixture,self.result))
 def test_typography_omission_negative(self):
  facts=copy.deepcopy(self.facts);facts['layouts'][0]['body']='10px';self.assertIn('readability',review.review_errors(self.packet,facts,self.fixture,self.result))
  p=copy.deepcopy(self.packet);p.pop('typography');self.assertIn('typography omitted',review.review_errors(p,self.facts,self.fixture,self.result))
 def test_evidence_mismatch_negative(self):
  for field,value,error in [('attempt_id',read('live/fixture.json')['attempt_id'],'attempt mismatch'),('reference_origin','candidate-generated labels','reference origin'),('requested_benchmark_calls',50,'excluded performance campaign'),('unexecuted_cases',['planned'],'unexecuted claimed green')]:
   p=copy.deepcopy(self.packet);p[field]=value;self.assertIn(error,review.review_errors(p,self.facts,self.fixture,self.result))

if __name__=='__main__':unittest.main()
