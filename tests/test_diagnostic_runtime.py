"""Real WAV/ffmpeg/Praat and new model-response admission; no hosted call."""
import base64,hashlib,io,json,pathlib,sys,tempfile,types,unittest,wave
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
from audio import wav_bytes
import diagnostic_runtime as runtime
from diagnostic_models import decode_findings,derivative,processor_audio_options,auditory_conversation
import model_setup
from inference_capture import DiagnosticTokenCapture
class DiagnosticRuntimeTests(unittest.TestCase):
 def audio(self):
  import math,struct
  return wav_bytes(b''.join(struct.pack('<h',int(6000*math.sin(2*math.pi*180*i/24000))) for i in range(24000)))
 def packet(self,method):
  raw=self.audio();return dict(method_id=method,audio_base64=base64.b64encode(raw).decode(),audio_sha256=hashlib.sha256(raw).hexdigest())
 def test_native_measurements_positive(self):
  loud=runtime.execute(self.packet('ffmpeg-ebur128-v1'));self.assertEqual([r['feature'] for r in loud['measurements']],['integrated_lufs','true_peak_dbtp']);self.assertTrue(all(r['status']=='observed' for r in loud['measurements']));self.assertEqual(loud['receipt']['inference_calls'],0);self.assertIn('Summary:',loud['native']['method']['stderr']);self.assertEqual(loud['native']['method']['exit_code'],0)
 def test_native_unknown_negative(self):
  pitch=runtime.execute(self.packet('praat-ac-v1'));rows={r['feature']:r for r in pitch['measurements']};self.assertEqual(rows['lexical_stress']['status'],'not_measurable');self.assertIsNone(rows['lexical_stress']['numeric_value']);self.assertEqual(rows['lexical_stress']['reason'],'requires_auditory_or_native_annotation');self.assertEqual(pitch['receipt']['inference_calls'],0)
 def test_clip_plan_positive(self):
  p=self.packet('unused');p['intervals']=[dict(start=2000,end=4000)];r=runtime.plan(p);self.assertEqual(r['sample_count'],24000);self.assertEqual(r['clips'][0]['source_interval'],dict(start=0,end=24000));self.assertEqual(base64.b64decode(r['clips'][0]['audio_base64']),self.audio())
 def test_clip_outside_negative(self):
  p=self.packet('unused');p['intervals']=[dict(start=2000,end=24001)]
  with self.assertRaisesRegex(ValueError,'INVALID_AUDIO_INTERVAL'):runtime.plan(p)
 def test_derivative_positive(self):
  raw=derivative(self.audio(),16000)
  with wave.open(io.BytesIO(raw)) as w:self.assertEqual((w.getframerate(),w.getnchannels(),w.getnframes()),(16000,1,16000))
 def test_judge_prose_positive(self):self.assertEqual(decode_findings('Auditory report: ```json\n{"findings":[]}\n```')['findings'],[])
 def test_judge_non_object_negative(self):
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('I cannot hear anything.')
 def test_unknown_method_negative(self):
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):runtime.execute(self.packet('invented'))
 def test_asr_reference_not_sent_positive(self):
  # Explicit recognizer boundary fixture: actual WER owner independently checks
  # two substitutions in five words; it cannot change the received hypothesis.
  p=self.packet('faster-whisper-local-en-v1');p['reference_text']='The café opens at nine.';received=[]
  def recognize(audio,capture):received.append(audio);return dict(hypothesis='The café open at ten.',library_version='fixture',model_manifest={'repo':'constructed-recognizer'})
  with patch.object(runtime,'recognize',recognize):r=runtime.execute(p)
  self.assertEqual(received,[self.audio()]);self.assertEqual(r['native']['comparison']['exact_ratio'],{'numerator':'2','denominator':'5'});self.assertEqual(r['measurements'][0]['numeric_value'],'0.4');self.assertEqual(r['native']['hypothesis'],'The café open at ten.')
 def test_processor_padding_complete_positive(self):
  target=[0]*16000;reference=[0]*8000
  self.assertEqual(processor_audio_options([target,reference],160),dict(max_length=16000,truncation=False))
  self.assertEqual((len(target),len(reference)),(16000,8000))
 def test_processor_partial_frame_not_truncated_negative(self):
  target=[0]*16000+[1,2,3];reference=[0]*8000
  self.assertEqual(processor_audio_options([target,reference],160),dict(max_length=16160,truncation=False))
  self.assertEqual(target[-3:],[1,2,3]);self.assertEqual(len(target),16003)
 def test_generation_token_capture_positive(self):
  import torch
  with tempfile.TemporaryDirectory() as directory:
   path=pathlib.Path(directory)/'tokens.json';capture=DiagnosticTokenCapture(path)
   capture.put(torch.tensor([[10,20,30]]));capture.put(torch.tensor([41]));capture.put(torch.tensor([42]));capture.end()
   self.assertEqual(json.loads(path.read_text()),dict(method='generate',prompt_token_ids=[10,20,30],output_token_ids=[41,42],complete=True))
 def test_interrupted_token_capture_negative(self):
  import torch
  with tempfile.TemporaryDirectory() as directory:
   path=pathlib.Path(directory)/'tokens.json';capture=DiagnosticTokenCapture(path)
   capture.put(torch.tensor([[10,20]]));capture.put(torch.tensor([71]))
   self.assertEqual(json.loads(path.read_text()),dict(method='generate',prompt_token_ids=[10,20],output_token_ids=[71],complete=False))
 def test_judge_single_finding_positive(self):
  row=dict(unit_id='e1',feature='pause_insert',status='contradicted',description='The pause differs.',reason='The actual model reports a contrast.',proposed_ipa=None)
  actual=decode_findings(json.dumps(row));self.assertEqual(actual['findings'],[{**row,'clip_interval':None}]);self.assertEqual(actual['summary'],row['reason']);self.assertEqual(actual['findings'][0]['status'],'contradicted')
 def test_judge_unrelated_object_negative(self):
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('{"message":"An unrelated object is not a finding."}')
 def test_auditory_task_after_audio_positive(self):
  prompt='Compare target and reference.';content='{"targets":["e1"]}'
  result=auditory_conversation(prompt,content,['target.wav','reference.wav'])
  self.assertEqual(result,[dict(role='user',content=[dict(type='text',text=content),dict(type='text',text='Target audio'),dict(type='audio',audio='target.wav'),dict(type='text',text='Reference audio'),dict(type='audio',audio='reference.wav'),dict(type='text',text=prompt)])])
 def test_auditory_no_reference_negative(self):
  result=auditory_conversation('Judge only actual audio.','{}',['target.wav'])
  self.assertEqual([p['audio'] for p in result[0]['content'] if p['type']=='audio'],['target.wav']);self.assertEqual(result[0]['content'][-1],dict(type='text',text='Judge only actual audio.'));self.assertNotIn('Reference audio',str(result))
 def test_judge_array_reason_positive(self):
  first=dict(unit_id='e1',feature='pause_insert',status='supported',reason='Intrusive pause removed in reference.')
  second=dict(unit_id='e1',feature='pause_insert',status='not_applicable',reason='No pause in target.')
  out=decode_findings('```json\n'+json.dumps([first,second])+'\n```')
  self.assertEqual(out['findings'],[{**first,'description':first['reason'],'clip_interval':None,'proposed_ipa':None},{**second,'description':second['reason'],'clip_interval':None,'proposed_ipa':None}]);self.assertEqual([r['status'] for r in out['findings']],['supported','not_applicable'])
 def test_judge_array_transcription_negative(self):
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('["The café opens tomorrow."]')
 def test_download_incomplete_negative(self):
  class Response:
   status=200;headers={'Content-Length':'6'}
   def __enter__(self):return self
   def __exit__(self,*a):pass
   chunks=iter([b'abc',b''])
   def read(self,n):return next(self.chunks)
  with tempfile.TemporaryDirectory() as d,patch.object(model_setup.urllib.request,'urlopen',return_value=Response()):
   path=pathlib.Path(d)/'model';
   with self.assertRaisesRegex(ValueError,'MODEL_DOWNLOAD_INCOMPLETE'):model_setup.download('https://public.invalid/model',path)
   self.assertFalse(path.exists());self.assertEqual(path.with_name('model.partial').read_bytes(),b'abc')
 def test_download_resume_positive(self):
  class Response:
   status=206;headers={'Content-Length':'3','Content-Range':'bytes 3-5/6'}
   def __enter__(self):return self
   def __exit__(self,*a):pass
   chunks=iter([b'def',b''])
   def read(self,n):return next(self.chunks)
  received=[]
  def response(request,timeout):received.append(request.get_header('Range'));return Response()
  with tempfile.TemporaryDirectory() as d,patch.object(model_setup.urllib.request,'urlopen',side_effect=response):
   path=pathlib.Path(d)/'model';path.with_name('model.partial').write_bytes(b'abc');r=model_setup.download('https://public.invalid/model',path,hashlib.sha256(b'abcdef').hexdigest());self.assertEqual(path.read_bytes(),b'abcdef');self.assertEqual(received,['bytes=3-']);self.assertEqual(r['size'],6)
if __name__=='__main__':unittest.main()
