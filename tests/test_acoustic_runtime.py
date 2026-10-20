"""Actual installed Kokoro planner/compiler and private controller protocol."""
import copy,json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
from backends import plan,resolve_acoustic,transform_acoustic
from test_acoustic_controls import edit,step,parameters,tone

class AcousticRuntime(unittest.TestCase):
 def profile(self):
  return dict(id='kokoro-controlled-v1',provider='local_kokoro',adapter_version='kokoro-controlled-v1',model='Kokoro-82M',billing_mode='local',voices=[dict(id='af_heart',locale='en-US')])
 def turn(self,edits=None,text='The pan is ready.'):
  return dict(id='u1',utterance_id='u1',speaker_id='s1',voice_id='af_heart',locale='en-US',operations=[dict(kind='text',text=text)],gap_after_ms=250,acoustic_edits=edits or [])
 def test_plan_pair_positive(self):
  result=plan(self.profile(),dict(turns=[self.turn([edit('phone_pair',4,7,reference_ipa='pæn',mutated_ipa='bæn')])]))
  piece=result['pieces'][0];self.assertEqual(len(result['pieces']),1);self.assertIn('pæn',piece['compiled_phonemes']);self.assertIn('bæn',piece['phone_variants']['e1']['compiled_phonemes']);self.assertEqual(piece['gap_after_ms'],250);self.assertEqual(piece['operations'][0]['text'],'The pan is ready.');self.assertTrue(piece['compiled_phonemes'].startswith('ð'));self.assertTrue(piece['phone_variants']['e1']['compiled_phonemes'].endswith(piece['compiled_phonemes'].split('pæn')[1]))
  currency=self.turn([edit('phone_pair',0,1,reference_ipa='dɑləɹ',mutated_ipa='tɑləɹ')],text='$');currency_result=plan(self.profile(),dict(turns=[currency]));self.assertEqual(currency_result['pieces'][0]['operations'][0]['text'],'$');self.assertEqual(currency_result['pieces'][0]['compiled_phonemes'],'dɑləɹ')

 def test_plan_phrases_positive(self):
  text='The pan is ready.';ops=[edit('pause_insert',4,7,pause_ms=100),dict(edit('pitch_duration',11,16,gain_db=2),unit_id='e2')]
  result=plan(self.profile(),dict(turns=[self.turn(ops)]));self.assertEqual(''.join(x['operations'][0]['text'] for x in result['pieces']),text);self.assertEqual(sum(bool(x.get('acoustic_edits')) for x in result['pieces']),1);self.assertEqual(len(result['pieces'][0]['acoustic_token_scopes']),2)
 def test_plan_unknown_phones_negative(self):
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):plan(self.profile(),dict(turns=[self.turn([edit('phone_pair',4,7,reference_ipa='pæn',mutated_ipa='∅')])]))
 def test_plan_capacity_negative(self):
  with self.assertRaisesRegex(ValueError,'INPUT_CAPACITY_EXCEEDED'):plan(self.profile(),dict(turns=[self.turn([edit('phone_pair',4,7,reference_ipa='p'*511,mutated_ipa='bæn')])]))
 def test_plan_word_tokens_positive(self):
  result=plan(self.profile(),dict(turns=[self.turn([edit('pause_insert',4,7,pause_ms=500)])]));target=result['pieces'][0];self.assertIn('pan',[t['text'] for t in target['g2p_tokens']]);self.assertTrue(target['compiled_phonemes']);self.assertEqual(target['surface_scope'],dict(start=0,end=17))
 def test_plan_dialogue_positive(self):
  a=self.turn([edit('pause_insert',4,7,pause_ms=1)]);b=self.turn([],text='Yes.');b['id']=b['utterance_id']='u2';result=plan(self.profile(),dict(turns=[a,b]));self.assertEqual(result['pieces'][-1]['utterance_id'],'u2');self.assertEqual(result['pieces'][-1]['operations'][0]['text'],'Yes.')
 def test_plan_wrong_adapter_negative(self):
  p=self.profile();p['adapter_version']='kokoro-local-en-v1'
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):plan(p,dict(turns=[self.turn([edit('pause_insert',4,7,pause_ms=1)])]))
 def test_plan_overlap_negative(self):
  with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):plan(self.profile(),dict(turns=[self.turn([edit('pitch_duration',0,16,gain_db=1),edit('pause_insert',4,7,pause_ms=1)])]))

class AcousticHosted(unittest.TestCase):
 def profile(self):return dict(id='azure-free',provider='azure_speech',adapter_version='azure-standard-v1',model='neural',endpoint='https://fixture.invalid/tts',voices=[dict(id='en-US-Voice',locale='en-US')],billing_mode='free_tier',account_tier='F0',overage_disabled=True,capabilities=['plain_text','ipa'])
 def turn(self,op):return dict(id='u1',utterance_id='u1',speaker_id='s1',voice_id='en-US-Voice',locale='en-US',operations=[dict(kind='text',text='pan')],gap_after_ms=0,acoustic_edits=[op])
 def test_hosted_pair_positive(self):
  from unittest.mock import patch
  import os,backends
  from acoustic_controls import encode
  requests=[]
  def send(url,body,headers,timeout):requests.append(body);return encode(tone()),200
  p=self.profile();turn=self.turn(edit('phone_pair',0,3,reference_ipa='pæn',mutated_ipa='bæn'))
  with patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=send):result=backends.render(p,turn)
  self.assertEqual(len(requests),2);self.assertIn('pæn'.encode(),requests[0]);self.assertIn('bæn'.encode(),requests[1]);self.assertIn('paired_mutation',result['receipt']['native']);self.assertIsNone(result['receipt']['observed_accent'])
 def test_hosted_plan_positive(self):
  result=plan(self.profile(),dict(turns=[self.turn(edit('pause_insert',0,3,pause_ms=500))]));self.assertEqual(result['pieces'][0]['operations'][0]['text'],'pan');self.assertEqual(len(result['pieces']),1)
 def test_hosted_fine_alignment_negative(self):
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):plan(self.profile(),dict(turns=[self.turn(edit('vowel_duration',0,3,duration_ratio=.5,phone_start=1,phone_end=2))]))
 def test_hosted_paid_negative(self):
  import backends
  p=self.profile();p['account_tier']='S0'
  with self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):backends.render(p,self.turn(edit('phone_pair',0,3,reference_ipa='pæn',mutated_ipa='bæn')))
