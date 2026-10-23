"""Native controls, independently specified contours and literal phone sequences.
Synthetic signals test acoustics; actual model recordings are a separate run.
"""
import base64, copy, pathlib, sys, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
import numpy as np
from acoustic_controls import encode,samples,resolve_parameters,transform,Unmeasurable
from acoustic_alignment import compile_scopes
from acoustic_plan import scopes

PATTERNS={
 'rise':[(0,0),(1,5)],
 'fall':[(0,0),(1,-5)],
 'fall_rise':[(0,0),(.5,-3),(1,3)],
 'rise_fall':[(0,0),(.5,3),(1,-3)],
}
def source(hz=160):
 x=np.arange(24000)/24000
 return encode(.16*np.sin(2*np.pi*hz*x)+.04*np.sin(4*np.pi*hz*x))
def intent(pattern,taxonomy='pronunciation.suprasegmental.intonation_function'):
 return dict(id='contour',unit_id='contrast',source_piece_id='actual-source',source_interval=dict(start=0,end=24000),controller='pitch_duration',taxonomy_id=taxonomy,parameters=dict(pitch_points=[dict(fraction=x,semitones=y) for x,y in PATTERNS[pattern]]))
class ConnectedSpeech(unittest.TestCase):
 def relative(self,pattern):
  resolved,observation=resolve_parameters(intent(pattern),source())
  points=resolved['parameters']['pitch_points']
  self.assertAlmostEqual(100*2**(points[0]['semitones']/12),160,delta=1)
  self.assertEqual([round(x['semitones']-points[0]['semitones'],6) for x in points],[y for _,y in PATTERNS[pattern]])
  self.assertNotIn('taxonomy_id',resolved)
 def unvoiced(self,pattern):
  with self.assertRaises(Unmeasurable):resolve_parameters(intent(pattern),encode(np.zeros(24000)))
 def test_rise_positive(self):self.relative('rise')
 def test_fall_positive(self):self.relative('fall')
 def test_fall_rise_positive(self):self.relative('fall_rise')
 def test_rise_fall_positive(self):self.relative('rise_fall')
 def test_rise_unvoiced_negative(self):self.unvoiced('rise')
 def test_fall_unvoiced_negative(self):self.unvoiced('fall')
 def test_fall_rise_unvoiced_negative(self):self.unvoiced('fall_rise')
 def test_rise_fall_unvoiced_negative(self):self.unvoiced('rise_fall')
 def test_voiced_interval_positive(self):
  raw=encode(np.concatenate([np.zeros(12000),samples(source()),np.zeros(12000)]));step=intent('fall_rise');step['source_interval']['end']=48000
  result,_=resolve_parameters(step,raw);points=result['parameters']['pitch_points'];self.assertGreaterEqual(points[0]['fraction'],.25-1e-12);self.assertLessEqual(points[-1]['fraction'],.75+1e-12);self.assertTrue(points[0]['fraction']<points[1]['fraction']<points[2]['fraction'])
 def test_unvoiced_tail_is_not_contour_endpoint_negative(self):
  raw=encode(np.concatenate([samples(source()),np.zeros(24000)]));step=intent('rise');step['source_interval']['end']=48000
  result,_=resolve_parameters(step,raw);self.assertLessEqual(result['parameters']['pitch_points'][-1]['fraction'],.5+1e-12)
 def test_other_pitch_category_is_not_relative_negative(self):
  original=intent('fall','pronunciation.suprasegmental.pitch_range')
  # This different category already owns source-derived pitch-range expansion;
  # test an explicitly absolute generic pitch operation instead.
  original.pop('taxonomy_id');result,_=resolve_parameters(original,source())
  self.assertEqual(result['parameters'],original['parameters'])
 def test_nullable_pitch_points_negative(self):
  original=intent('rise','pronunciation.suprasegmental.assimilation');original['controller']='phone_pair';original['parameters']=dict(reference_ipa='wʊd ju',mutated_ipa='wʊdʒə',pitch_points=None)
  result,_=resolve_parameters(original,source());self.assertIsNone(result['parameters']['pitch_points']);self.assertEqual(result['parameters'],original['parameters'])
 def test_custom_absolute_contour_preserved_negative(self):
  original=intent('fall');original['parameters']['pitch_points']=[dict(fraction=0,semitones=7),dict(fraction=1,semitones=2)]
  result,_=resolve_parameters(original,source());self.assertEqual(result['parameters'],original['parameters'])
 def test_resolved_contour_stays_resolved_positive(self):
  resolved,_=resolve_parameters(intent('fall'),source());again,_=resolve_parameters(resolved,source(210));self.assertEqual(again['parameters'],resolved['parameters'])
 def measured_change(self,pattern):
  raw=source();resolved,_=resolve_parameters(intent(pattern),raw);out=transform(raw,resolved);y=samples(base64.b64decode(out['audio_base64']))
  # Independent zero-crossing frequency estimator; no controller observations.
  def hz(a,b):
   values=y[round(a*len(y)):round(b*len(y))];cross=np.flatnonzero((values[:-1]<=0)&(values[1:]>0));return 24000*(len(cross)-1)/(cross[-1]-cross[0])
  return 12*np.log2(hz(.75,.95)/hz(.05,.25))
 def test_rising_wave_positive(self):self.assertGreater(self.measured_change('rise'),3)
 def test_falling_wave_positive(self):self.assertLess(self.measured_change('fall'),-3)
 def test_question_mark_does_not_force_rise_negative(self):
  # Same physical falling template is available to a WH-question; no punctuation
  # classifier is allowed to turn every question into the rising template.
  self.assertLess(self.measured_change('fall'),-3)
 def pair(self,reference,changed,kind='blending'):
  text='Would you compare the quotes?';op=dict(unit_id=kind,scope=dict(start=0,end=9),controller='phone_pair',parameters=dict(reference_ipa=reference,mutated_ipa=changed))
  turn=dict(operations=[dict(text=text)],acoustic_edits=[op]);scopes(turn)
  piece=dict(operations=[dict(text=text)],g2p_tokens=[dict(text='Would',phonemes='wʊd',whitespace=' '),dict(text='you',phonemes='ju',whitespace=' '),dict(text='compare',phonemes='kəmpɛɹ',whitespace=' '),dict(text='the',phonemes='ðə',whitespace=' '),dict(text='quotes',phonemes='kwəʊts',whitespace=''),dict(text='?',phonemes='?',whitespace='')])
  vocab={x:1 for x in reference+changed+'wʊdjukəmpɛɹðkwəʊts? '}
  compile_scopes(piece,[op],0,vocab);return piece
 def test_blended_phrase_compiles_positive(self):
  result=self.pair('wʊdʒə','wʊtʃə');self.assertTrue(result['compiled_phonemes'].startswith('wʊdʒə '));self.assertEqual(result['operations'][0]['text'],'Would you compare the quotes?');self.assertIn('wʊtʃə',result['phone_variants']['blending']['compiled_phonemes'])
 def test_unblended_variant_is_renderable_negative(self):
  # Unblended careful speech is a permitted control, not automatically an error.
  result=self.pair('wʊd ju','wʊdʒə');self.assertTrue(result['compiled_phonemes'].startswith('wʊd ju '));self.assertIn('wʊdʒə',result['phone_variants']['blending']['compiled_phonemes'])
 def test_rhythm_selected_interval_positive(self):
  raw=source();step=dict(id='rhythm',unit_id='rhythm',source_piece_id='rhythm-source',controller='pitch_duration',source_interval=dict(start=4800,end=16800),parameters=dict(duration_ratio=1.5))
  result=transform(raw,step);out=base64.b64decode(result['audio_base64']);self.assertLess(abs(result['sample_count']-30000),30);self.assertEqual(out[44:44+9600],raw[44:44+9600]);self.assertEqual(out[-14400:],raw[-14400:])
 def test_rhythm_not_global_slowdown_negative(self):
  raw=source();step=dict(id='rhythm',unit_id='rhythm',source_piece_id='rhythm-source',controller='pitch_duration',source_interval=dict(start=4800,end=16800),parameters=dict(duration_ratio=1))
  result=transform(raw,step);self.assertLess(abs(result['sample_count']-24000),30)
class AuditoryWrappers(unittest.TestCase):
 def test_results_wrapper_positive(self):
  from diagnostic_models import decode_findings
  out=decode_findings('{"results":[{"unit_id":"a","status":"uncertain","description":"Cannot distinguish phones"}],"summary":"actual opinion"}')
  self.assertEqual(len(out['findings']),1);self.assertEqual(out['findings'][0]['status'],'uncertain');self.assertEqual(out['summary'],'actual opinion')
 def test_keyed_wrapper_positive(self):
  from diagnostic_models import decode_findings
  out=decode_findings('{"clip-A":{"unit_id":"a","status":"supported","proposed_ipa":"wʊdʒə","description":"Voiced affricate"},"clip-B":{"unit_id":"b","status":"uncertain","description":"Indistinct"}}')
  self.assertEqual([x['unit_id'] for x in out['findings']],['a','b']);self.assertEqual(out['findings'][0]['proposed_ipa'],'wʊdʒə');self.assertEqual(out['findings'][1]['status'],'uncertain')
 def test_keyed_label_is_unit_id_positive(self):
  from diagnostic_models import decode_findings
  out=decode_findings('{"A":{"feature":"phones","status":"uncertain","description":"Indistinct"},"B":{"feature":"phones","status":"supported","proposed_ipa":"wʊtʃə","description":"Voiceless affricate"}}')
  self.assertEqual([r['unit_id'] for r in out['findings']],['A','B']);self.assertEqual(out['findings'][0]['status'],'uncertain');self.assertEqual(out['findings'][1]['proposed_ipa'],'wʊtʃə')
 def test_summary_status_is_not_unit_negative(self):
  from diagnostic_models import decode_findings
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('{"summary":{"status":"supported","description":"No acoustic feature or unit identity"}}')
 def test_malformed_results_negative(self):
  from diagnostic_models import decode_findings
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('{"results":"no observations"}')
 def test_unrelated_keyed_values_negative(self):
  from diagnostic_models import decode_findings
  with self.assertRaisesRegex(ValueError,'DIAGNOSTIC_OUTPUT_INVALID'):decode_findings('{"summary":{"description":"No identified unit"}}')
if __name__=='__main__':unittest.main()
