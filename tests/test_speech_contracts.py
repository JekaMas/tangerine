"""Literal independent speech contracts; remote transport fixtures are explicit."""
import base64, io, json, os, pathlib, struct, sys, tempfile, unittest, wave
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/speech'))
import audio,backends,model_setup,voice_setup
from inference_capture import observe_method

def profile(provider='local_espeak_ng',mode='local'):
 return {'id':'test','provider':provider,'billing_mode':mode,'overage_disabled':True,'model':'fixture-model','voices':[{'id':'en-us','locale':'en-US','accent_description':None}],'voice_settings':{}}
def turn(text='The café open tomorrow.'):
 return {'id':'u1','utterance_id':'u1','speaker_id':'s1','voice_id':'en-us','locale':'en-US','gap_after_ms':250,'operations':[{'kind':'text','text':text}]}
class SpeechContracts(unittest.TestCase):
 def test_admission_once_positive(self):
  from unittest.mock import Mock
  sample=audio.wav_bytes(b'\x07\x00'*2400);admission=Mock(wraps=audio.admit)
  with patch.object(audio,'admit',admission),patch.object(backends,'admit',admission),patch.object(backends,'espeak',side_effect=lambda p,t:(audio.normalize(sample),{},None)):
   result=backends.render(profile(),turn())
  self.assertEqual(admission.call_count,1);self.assertEqual(result['sample_count'],2400)
 def test_normalize_conversion_positive(self):
  sample=audio.wav_bytes(b'\x07\x00'*2400)
  with patch.object(audio,'admit',side_effect=AssertionError('normalization must not repeat owning admission')):converted=audio.normalize(sample)
  self.assertEqual(converted[44:],sample[44:]);self.assertEqual(converted[:4],b'RIFF')
 def test_admission_silent_negative(self):
  with patch.object(backends,'espeak',return_value=(audio.wav_bytes(b'\0\0'*2400),{},None)),self.assertRaisesRegex(ValueError,'AUDIO_SILENT'):backends.render(profile(),turn())
 def test_advisory_timeout_negative(self):
  import subprocess
  with patch.object(audio.subprocess,'run',side_effect=subprocess.TimeoutExpired('ffmpeg',60)):result=audio.measure(b'\x07\x00'*12000)
  self.assertEqual(result['loudness_state'],'not_measurable');self.assertIsNone(result['integrated_lufs']);self.assertIn('loudness_not_measurable',result['warnings'])
 def test_download_complete_positive(self):
  import hashlib
  with tempfile.TemporaryDirectory() as tmp:
   dest=pathlib.Path(tmp)/'model';response=io.BytesIO(b'abcd');response.status=200;response.headers={}
   with patch.object(model_setup.urllib.request,'urlopen',return_value=response):row=model_setup.download('https://fixture.invalid/model',dest,hashlib.sha256(b'abcd').hexdigest())
   self.assertEqual(dest.read_bytes(),b'abcd');self.assertEqual(row['size'],4)
 def test_download_resume_positive(self):
  import hashlib
  for status,body,headers in [(206,b'cd',{'Content-Range':'bytes 2-3/4'}),(200,b'abcd',{})]:
   with self.subTest(status=status),tempfile.TemporaryDirectory() as tmp:
    dest=pathlib.Path(tmp)/'model';dest.with_name('model.partial').write_bytes(b'ab');response=io.BytesIO(body);response.status=status;response.headers=headers
    with patch.object(model_setup.urllib.request,'urlopen',return_value=response) as request:row=model_setup.download('https://fixture.invalid/model',dest,hashlib.sha256(b'abcd').hexdigest())
    self.assertEqual(request.call_args.args[0].get_header('Range'),'bytes=2-');self.assertEqual(dest.read_bytes(),b'abcd');self.assertEqual(row['size'],4)
 def test_download_range_negative(self):
  with tempfile.TemporaryDirectory() as tmp:
   dest=pathlib.Path(tmp)/'model';partial=dest.with_name('model.partial');partial.write_bytes(b'ab');response=io.BytesIO(b'cd');response.status=206;response.headers={'Content-Range':'bytes 1-2/4'}
   with patch.object(model_setup.urllib.request,'urlopen',return_value=response),self.assertRaisesRegex(ValueError,'MODEL_DOWNLOAD_INVALID'):model_setup.download('https://fixture.invalid/model',dest)
   self.assertFalse(dest.exists());self.assertEqual(partial.read_bytes(),b'ab')
 def test_download_hash_negative(self):
  with tempfile.TemporaryDirectory() as tmp:
   dest=pathlib.Path(tmp)/'model';response=io.BytesIO(b'abcd');response.status=200;response.headers={}
   with patch.object(model_setup.urllib.request,'urlopen',return_value=response),self.assertRaisesRegex(ValueError,'MODEL_DOWNLOAD_INVALID'):model_setup.download('https://fixture.invalid/model',dest,'0'*64)
   self.assertFalse(dest.exists());self.assertFalse(dest.with_name('model.partial').exists())
 def voice_request(self):
  return {'profile_id':'qwen-base-v1','voice_id':'saved-test','mode':'local_reference','reference_text':'Hello.','locale':'en-US','reference_path':'source.wav'}
 def test_voice_setup_reference_positive(self):
  from qwen_tts import Qwen3TTSModel
  import torch
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'source.wav').write_bytes(audio.wav_bytes(b'\x07\x00'*2400));request=self.voice_request()
   with patch.object(voice_setup,'ROOT',root),patch.object(voice_setup,'installed',return_value=(root,{'repo':'constructed-base'})),patch.object(Qwen3TTSModel,'from_pretrained') as factory:
    factory.return_value.create_voice_clone_prompt.return_value=[{'speaker':torch.tensor([.25,.5])}];manifest=voice_setup.setup(request)
   self.assertEqual(manifest['request'],request);self.assertEqual(manifest['origin'],'local_reference');self.assertEqual({v['path'] for v in manifest['files']},{'reference.wav','reference.txt','conditioning.pt'});self.assertEqual(factory.call_count,1);self.assertEqual(factory.return_value.create_voice_clone_prompt.call_args.kwargs['ref_text'],'Hello.');self.assertTrue((root/'voices/qwen-base-v1/saved-test/conditioning.pt').exists())
 def test_voice_setup_replay_positive(self):
  from qwen_tts import Qwen3TTSModel
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);request=self.voice_request();dest=root/'voices/qwen-base-v1/saved-test';dest.mkdir(parents=True);manifest={'request':request,'origin':'accepted-saved-fixture'};(dest/'manifest.json').write_text(json.dumps(manifest))
   with patch.object(voice_setup,'ROOT',root),patch.object(Qwen3TTSModel,'from_pretrained',side_effect=AssertionError('unexpected inference')):self.assertEqual(voice_setup.setup(request),manifest)
 def test_voice_setup_conflict_negative(self):
  from qwen_tts import Qwen3TTSModel
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);request=self.voice_request();dest=root/'voices/qwen-base-v1/saved-test';dest.mkdir(parents=True);(dest/'manifest.json').write_text(json.dumps({'request':{**request,'reference_text':'Different.'}}))
   with patch.object(voice_setup,'ROOT',root),patch.object(Qwen3TTSModel,'from_pretrained',side_effect=AssertionError('unexpected inference')),self.assertRaisesRegex(ValueError,'VOICE_ID_CONFLICT'):voice_setup.setup(request)
 def test_voice_setup_missing_negative(self):
  from qwen_tts import Qwen3TTSModel
  with tempfile.TemporaryDirectory() as tmp:
   with patch.object(voice_setup,'ROOT',pathlib.Path(tmp)),patch.object(Qwen3TTSModel,'from_pretrained',side_effect=AssertionError('unexpected inference')),self.assertRaises(FileNotFoundError):voice_setup.setup(self.voice_request())
 def test_token_capture_positive(self):
  class Tokenizer:
   def tokenize(self,text):return [17,23]
  owner=Tokenizer();events=[]
  with observe_method(owner,'tokenize',events):result=owner.tokenize('<assistant>café</assistant>')
  self.assertEqual(result,[17,23]);self.assertEqual(events,[{'method':'tokenize','args':['<assistant>café</assistant>'],'kwargs':{},'outcome':'complete','result':[17,23]}])
 def test_decoder_capture_positive(self):
  class Decoder:
   def generate(self,**kwargs):return marker
  owner=Decoder();events=[];marker=object()
  with observe_method(owner,'generate',events,capture_result=False):result=owner.generate(input_ids=[[17,23]],temperature=.9,speakers=['Ryan'])
  self.assertIs(result,marker);self.assertEqual(events,[{'method':'generate','args':[],'kwargs':{'input_ids':[[17,23]],'temperature':.9,'speakers':['Ryan']},'outcome':'complete'}])
 def test_capture_failure_negative(self):
  class Decoder:
   def generate(self):raise ValueError('private-canary')
  owner=Decoder();original=owner.generate;events=[]
  with self.assertRaisesRegex(ValueError,'private-canary'):
   with observe_method(owner,'generate',events):owner.generate()
  self.assertEqual(owner.generate,original);self.assertNotIn('private-canary',json.dumps(events));self.assertEqual(events[0]['exception_type'],'ValueError')
 def test_capture_no_call_negative(self):
  class Decoder:
   def generate(self):raise AssertionError('unexpected inference')
  owner=Decoder();original=owner.generate;events=[]
  with observe_method(owner,'generate',events):pass
  self.assertEqual(events,[]);self.assertEqual(owner.generate,original)
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
