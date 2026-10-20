"""Literal independent speech contracts; remote transport fixtures are explicit."""
import base64, io, json, os, pathlib, struct, sys, tempfile, unittest, wave
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/speech'))
import audio,backends,model_setup

def profile(provider='local_espeak_ng',mode='local'):
 return {'id':'test','provider':provider,'billing_mode':mode,'overage_disabled':True,'model':'fixture-model','voices':[{'id':'en-us','locale':'en-US','accent_description':None}],'voice_settings':{}}
def turn(text='The café open tomorrow.'):
 return {'id':'u1','utterance_id':'u1','speaker_id':'s1','voice_id':'en-us','locale':'en-US','gap_after_ms':250,'operations':[{'kind':'text','text':text}]}
class SpeechContracts(unittest.TestCase):
 def test_wave_positive(self):
  b=audio.wav_bytes(b'\x07\x00\x08\x00');self.assertEqual(audio.admit(b),b'\x07\x00\x08\x00');self.assertEqual(struct.unpack_from('<I',b,24)[0],24000)
 def test_assembly_positive(self):
  b,m=audio.assemble([{'id':'p1','audio':audio.wav_bytes(b'\x07\x00'),'gap_after_ms':1},{'id':'p2','audio':audio.wav_bytes(b'\x08\x00'),'gap_after_ms':0}]);self.assertEqual(len(b),96);self.assertEqual(m,[{'piece_id':'p1','start_sample':0,'end_sample':1,'gap_end_sample':25},{'piece_id':'p2','start_sample':25,'end_sample':26,'gap_end_sample':26}]);self.assertEqual(b[44:],b'\x07\x00'+b'\0\0'*24+b'\x08\x00')
 def test_silent_negative(self):
  with self.assertRaisesRegex(ValueError,'AUDIO_SILENT'):audio.admit(audio.wav_bytes(b'\0\0'))
 def test_invalid_format_negative(self):
  with self.assertRaises((ValueError,wave.Error,EOFError)):audio.admit(b'not audio')
 def test_local_policy_positive(self):backends.billing(profile())
 def test_included_policy_positive(self):backends.billing(profile('elevenlabs','included_subscription'))
 def test_metered_negative(self):
  with self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):backends.billing(profile('elevenlabs','metered'))
 def test_overage_negative(self):
  p=profile('azure_speech','free_tier');p['account_tier']='S0'
  with self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):backends.billing(p)
  p=profile('openai_tts','included_subscription')
  with self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):backends.billing(p)
 def test_split_positive(self):
  t=turn('word '*900);d=backends.plan(profile(),{'turns':[t]});pieces=d['pieces'];self.assertEqual(''.join(x['operations'][0]['text'] for x in pieces),t['operations'][0]['text']);self.assertEqual([x['gap_after_ms'] for x in pieces],[0,0,250]);self.assertTrue(all(x['voice_id']=='en-us' and x['speaker_id']=='s1' for x in pieces))
 def test_unicode_positive(self):
  d=backends.plan(profile(),{'turns':[turn('The café says <speak> literally & clearly.')]});self.assertEqual(d['pieces'][0]['operations'][0]['text'],'The café says <speak> literally & clearly.')
 def test_indivisible_negative(self):
  with self.assertRaisesRegex(ValueError,'INPUT_CAPACITY_EXCEEDED'):backends.plan(profile(),{'turns':[turn('a'*2001)]})
 def test_voice_negative(self):
  t=turn();t['voice_id']='invented'
  with self.assertRaisesRegex(ValueError,'VOICE_UNAVAILABLE'):backends.plan(profile(),{'turns':[t]})
 def test_ssml_positive(self):
  out=backends.ssml(turn('<speak> & café')).decode();self.assertIn('&lt;speak&gt; &amp; café',out);self.assertIn('name="en-us"',out)
 def test_hosted_request_positive(self):
  p=profile('elevenlabs','free_tier');p['model']='eleven_v3';sample=audio.wav_bytes(b'\x07\x00')
  with patch.dict(os.environ,{'ELEVENLABS_API_KEY':'fixture-secret'}),patch.object(backends,'transport',return_value=(sample,200)) as transport,patch.object(backends,'normalize',return_value=sample):
   b,native,raw=backends.hosted(p,turn(),1)
  args=transport.call_args.args;self.assertEqual(json.loads(args[1]),{'inputs':[{'text':'The café open tomorrow.','voice_id':'en-us'}],'model_id':'eleven_v3'});self.assertEqual(args[2]['xi-api-key'],'fixture-secret');self.assertEqual(native['http_status'],200);self.assertEqual(b,sample)
 def test_no_credentials_negative(self):
  with patch.dict(os.environ,{},clear=True),self.assertRaisesRegex(ValueError,'MISSING_CREDENTIALS'):backends.hosted(profile('elevenlabs','free_tier'),turn(),1)
 def test_unsupported_operation_negative(self):
  t=turn();t['operations']=[{'kind':'arbitrary_xml','text':'<audio src="remote"/>'}]
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):backends.ssml(t)
 def test_quality_positive(self):
  d=audio.quality(b'\xff\x7f\x00\x10');self.assertEqual(d['warnings'],['clipping_risk']);self.assertIsNone(d['observed_accent']);self.assertIsNone(d['speech_intelligibility'])
 def test_accepted_cache_positive(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(model_setup,'ROOT',pathlib.Path(tmp)):
   d=pathlib.Path(tmp)/'kokoro-local-en-v1';d.mkdir();(d/'manifest.json').write_text(json.dumps({'complete':True,'revision':'accepted','files':[]}))
   with patch.object(model_setup,'fetch',side_effect=AssertionError('repeat network audit')):self.assertEqual(model_setup.installed('kokoro-local-en-v1')[1]['revision'],'accepted')
 def test_missing_setup_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(model_setup,'ROOT',pathlib.Path(tmp)),self.assertRaisesRegex(ValueError,'MODEL_SETUP_REQUIRED'):model_setup.installed('kokoro-local-en-v1')
 def test_incomplete_setup_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(model_setup,'ROOT',pathlib.Path(tmp)):
   d=pathlib.Path(tmp)/'kokoro-local-en-v1';d.mkdir();(d/'manifest.json').write_text('{"complete":false}')
   with self.assertRaisesRegex(ValueError,'MODEL_SETUP_REQUIRED'):model_setup.installed('kokoro-local-en-v1')
 def test_short_measure_positive(self):
  d=audio.measure(b'\x07\x00'*100);self.assertEqual(d['sample_count'],100);self.assertIsNone(d['integrated_lufs']);self.assertEqual(d['loudness_state'],'not_measurable');self.assertIn('loudness_not_measurable',d['warnings'])
 def test_planned_pause_positive(self):
  pcm=b'\0\0'*60000+b'\x00\x20'*12000
  d=audio.measure(pcm,[[0,60000]]);self.assertNotIn('unwanted_silence',d['warnings']);self.assertEqual(d['planned_pause_intervals'],[[0,60000]]);self.assertEqual(d['sample_count'],72000)
 def test_unwanted_silence_negative(self):
  pcm=b'\0\0'*60000+b'\x00\x20'*12000;d=audio.measure(pcm);self.assertIn('unwanted_silence',d['warnings']);self.assertIsNone(d['observed_accent'])
 def test_clipping_warning_negative(self):
  d=audio.measure(b'\xff\x7f'*12000);self.assertIn('clipping_risk',d['warnings']);self.assertEqual(d['sample_count'],12000)
if __name__=='__main__':unittest.main()
