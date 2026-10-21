"""Literal diagnostic clocks/populations and explicit model-boundary fixtures."""
import base64,io,json,pathlib,sys,types,unittest,wave
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
from diagnostic_audio import lexical,wer,clip_windows,judge_measurements,complete_judge_measurements,transcribe_complete
class AudioDiagnosticTests(unittest.TestCase):
 def test_wer_positive(self):
  r=wer('The café opens at nine.','The café open at ten.')
  self.assertEqual((r['substitutions'],r['deletions'],r['insertions'],r['reference_count']),(2,0,0,5))
  self.assertEqual(r['exact_ratio'],{'numerator':'2','denominator':'5'})
 def test_lexical_positive(self):self.assertEqual(lexical("  ‘Café’ don't well-known — 42. "),['café',"don't",'well-known','42'])
 def test_no_reference_negative(self):self.assertIsNone(wer('','invented words')['exact_ratio'])
 def test_hypothesis_not_replaced_negative(self):
  r=wer('opens','open extra');self.assertEqual(r['hypothesis_tokens'],['open','extra']);self.assertEqual(r['substitutions']+r['insertions'],2)
 def test_windows_positive(self):
  r=clip_windows([(48000,72000),(90000,120000),(300000,480000)],600000,240000)
  self.assertEqual(r,[(24000,144000),(276000,504000)])
 def test_large_window_negative(self):
  r=clip_windows([(0,480000)],480000,240000)
  self.assertEqual(r,[(0,240000),(240000,480000)])
 def test_judge_projection_positive(self):
  row={'unit_id':'u','feature':'lexical_stress','status':'supported','clip_interval':{'start':240,'end':480},'reason':'Actual model finding','description':'First syllable','proposed_ipa':None}
  r=judge_measurements({'findings':[row]},'a'*64,'qwen25-omni-audio-v1','v1',{'start':24000,'end':48000},['raw'])
  self.assertEqual(r[0]['interval'],{'start':24240,'end':24480,'sample_rate_hz':24000});self.assertEqual(r[0]['categorical_value'],'model_supported');self.assertIsNone(r[0]['numeric_value'])
 def test_judge_uncertain_negative(self):
  row={'unit_id':'u','feature':'stress','status':'uncertain','clip_interval':None,'reason':'Cannot hear enough','description':'uncertain','proposed_ipa':None}
  r=judge_measurements({'findings':[row]},'b'*64,'qwen25-omni-audio-v1','v1',{'start':0,'end':24000},[])
  self.assertEqual(r[0]['status'],'not_measurable');self.assertIsNone(r[0]['categorical_value']);self.assertEqual(r[0]['reason'],'Cannot hear enough')
 def test_transcription_completion_positive(self):
  calls=[];consumed=[]
  class Model:
   def transcribe(self,path,**kwargs):
    calls.append((path,kwargs))
    def generator():
     consumed.append(True);yield types.SimpleNamespace(id=0,start=0.,end=1.,text=' open ',avg_logprob=-.1,words=[types.SimpleNamespace(start=0.,end=.5,word=' open',probability=.9)])
    return generator(),types.SimpleNamespace(language='en',language_probability=.99,duration=1.)
  r=transcribe_complete(Model(),'actual-private.wav')
  self.assertEqual(consumed,[True]);self.assertEqual(r['hypothesis'],' open ');self.assertEqual(r['segments'][0]['words'][0]['word'],' open')
  self.assertEqual(calls,[('actual-private.wav',dict(language='en',task='transcribe',beam_size=5,temperature=0,word_timestamps=True,initial_prompt=None,condition_on_previous_text=False,vad_filter=False))])
 def test_incomplete_generator_negative(self):
  class Model:
   def transcribe(self,*args,**kwargs):
    def generator():raise RuntimeError('decoder interrupted');yield None
    return generator(),types.SimpleNamespace(language='en',language_probability=1,duration=1)
  with self.assertRaisesRegex(RuntimeError,'interrupted'):transcribe_complete(Model(),'actual-private.wav')
 def test_judge_target_preservation_positive(self):
  finding=dict(unit_id='u1',feature='speech_realization',status='supported',clip_interval=None,reason='Audible changed vowel.',description='The vowel differs.',proposed_ipa='pɛn')
  request=dict(audio_sha256='a'*64,source_interval=dict(start=24000,end=48000),planned_units=[dict(id='u1',realization=dict(prosody=[]))])
  rows=complete_judge_measurements({'findings':[finding]},request,'qwen25-omni-audio-v1')
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['target_unit_id'],'u1');self.assertEqual(rows[0]['auditory_finding'],finding);self.assertEqual(rows[0]['categorical_value'],'model_supported')
 def test_judge_omitted_targets_negative(self):
  output={'findings':[]};request=dict(audio_sha256='a'*64,source_interval=dict(start=0,end=24000),planned_units=[dict(id='u1',realization=dict(prosody=[])),dict(id='u2',realization=dict(prosody=[dict(feature='lexical_stress')]))])
  rows=complete_judge_measurements(output,request,'qwen25-omni-audio-v1')
  self.assertEqual([(r['target_unit_id'],r['feature']) for r in rows],[('u1','speech_realization'),('u2','lexical_stress')]);self.assertEqual(output,{'findings':[]})
  self.assertTrue(all(r['status']=='not_measurable' and r['numeric_value'] is None and r['categorical_value'] is None and r['reason']=='model_omitted_target' and 'auditory_finding' not in r for r in rows))
 def test_judge_extra_findings_positive(self):
  requested=dict(unit_id='e1',feature='pause_insert',status='supported',description='Intrusive pause before opens.',reason='Audible pause.',clip_interval=None,proposed_ipa=None)
  auxiliary=dict(unit_id='e1',feature='phoneme',status='not_applicable',description='None.',reason='Not applicable.',clip_interval=None,proposed_ipa=None)
  output=dict(findings=[requested,auxiliary]);request=dict(audio_sha256='a'*64,source_interval=dict(start=0,end=96000),planned_units=[dict(id='e1',realization=dict(prosody=[]))],acoustic_edits=[dict(unit_id='e1',controller='pause_insert')])
  rows=complete_judge_measurements(output,request,'qwen25-omni-audio-v1')
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['auditory_finding'],requested);self.assertEqual(rows[0]['target_unit_id'],'e1');self.assertEqual(rows[0]['categorical_value'],'model_supported');self.assertEqual(output['findings'],[requested,auxiliary])
 def test_judge_unrequested_only_negative(self):
  auxiliary=dict(unit_id='other',feature='pause_insert',status='supported',description='Another target.',reason='Unrequested.',clip_interval=None,proposed_ipa=None)
  output=dict(findings=[auxiliary]);request=dict(audio_sha256='a'*64,source_interval=dict(start=0,end=96000),planned_units=[dict(id='e1',realization=dict(prosody=[dict(feature='pause_insert')]))])
  rows=complete_judge_measurements(output,request,'qwen25-omni-audio-v1')
  self.assertEqual(len(rows),1);self.assertEqual((rows[0]['target_unit_id'],rows[0]['feature'],rows[0]['status'],rows[0]['reason']),('e1','pause_insert','not_measurable','model_omitted_target'));self.assertIsNone(rows[0]['categorical_value']);self.assertNotIn('auditory_finding',rows[0]);self.assertEqual(output,dict(findings=[auxiliary]))
if __name__=='__main__':unittest.main()
