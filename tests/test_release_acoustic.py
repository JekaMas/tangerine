"""Literal independent I8 regressions, real Praat/native PCM, no inference."""
import base64,copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
from test_acoustic_controls import tone,step
from acoustic_controls import encode,samples,resolve_parameters,transform
from acoustic_alignment import project_native,resolve
import numpy as np
class ReleaseAcoustic(unittest.TestCase):
 def test_rate_gap_positive(self):
  audio=encode(np.concatenate([tone(4800),np.zeros(4800),tone(4800)]))
  words=[dict(text='one',phonemes='wʌn',start_sample=0,end_sample=4800),dict(text='two',phonemes='tu',start_sample=9600,end_sample=14400)]
  op=step(a=0,b=14400);op['taxonomy_id']='fluency.speech_rate'
  resolved,_=resolve_parameters(op,audio,words,target_wpm=120)
  actual=transform(audio,resolved);pcm=samples(base64.b64decode(actual['audio_base64']))
  self.assertAlmostEqual(2*60*24000/len(pcm),120,delta=.02)
  self.assertTrue(np.all(pcm[9600:14400]==0),'original internal4800samples must remain unchanged')
  self.assertTrue(any(r['source_start']==4800 and r['source_end']==9600 and r['final_end']-r['final_start']==4800 for r in actual['clock_mapping']))
 def test_vot_clock_positive(self):
  source=encode(np.concatenate([tone(600),np.zeros(1800),tone(21600)]))
  op=step('vot_edit',a=0,b=24000,vot_ms=0);op['landmarks']=dict(burst_end_sample=600,voicing_onset_sample=2400)
  r=transform(source,op);native=dict(decoder=[],acoustic_scopes=[dict(unit_id='vowel',start=2400,end=4800,phone_intervals=[dict(start=2400,end=4800)])])
  p=project_native(native,r['clock_mapping'],r['sample_count'])
  self.assertEqual((p['acoustic_scopes'][0]['start'],p['acoustic_scopes'][0]['end']),(600,3000))
  self.assertTrue(np.array_equal(samples(base64.b64decode(r['audio_base64']))[600:],samples(source)[2400:]))
 def test_repeated_scope_positive(self):
  edits=[dict(unit_id='u',controller='pitch_duration',scope=dict(start=a,end=b),parameters=dict(phone_start=None,phone_end=None)) for a,b in [(0,3),(7,12)]]
  n=dict(acoustic_scopes=[dict(unit_id='u',surface_scope=dict(start=0,end=3),start=0,end=600,phone_intervals=[]),dict(unit_id='u',surface_scope=dict(start=7,end=12),start=1200,end=2400,phone_intervals=[])])
  r=resolve(dict(acoustic_edits=edits),n,3000,'piece')
  self.assertEqual([x['source_interval'] for x in r],[dict(start=0,end=600),dict(start=1200,end=2400)])
 def test_rate_crossfade_positive(self):
  audio=encode(np.concatenate([tone(4800),np.zeros(4800),tone(4800)]))
  words=[dict(text='one',phonemes='wʌn',start_sample=0,end_sample=4800),dict(text='two',phonemes='tu',start_sample=9600,end_sample=14400)]
  op=step(a=0,b=14400);op['taxonomy_id']='fluency.speech_rate';resolved,_=resolve_parameters(op,audio,words,target_wpm=120)
  actual=transform(audio,resolved)
  rows=[r for r in actual['sample_rows'] if r['final_start']==0 and r['final_end']==120]
  self.assertEqual(len(rows),2,'both actual crossfade sources must remain represented')
  self.assertEqual({r['source_end'] for r in rows},{60,120})
  self.assertEqual(len({r['crossfade_group_id'] for r in rows}),1)
  self.assertIsNotNone(rows[0]['crossfade_group_id'])
 def test_rate_unreachable_negative(self):
  from acoustic_controls import duration_ratio_for_rate
  with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):
   duration_ratio_for_rate([dict(start_sample=0,end_sample=4800),dict(start_sample=9600,end_sample=14400)],600)
 def test_vot_outside_negative(self):
  raw=encode(tone(24000));op=step('vot_edit',a=2400,b=16800,vot_ms=0);op['landmarks']=dict(burst_end_sample=600,voicing_onset_sample=2400)
  r=transform(raw,op);pcm=samples(base64.b64decode(r['audio_base64']));self.assertTrue(np.array_equal(pcm[:2400],samples(raw)[:2400]));self.assertTrue(np.array_equal(pcm[-7200:],samples(raw)[-7200:]))
 def test_pair_scopes_positive(self):
  from acoustic_alignment import compile_scopes
  from test_acoustic_controls import edit
  piece=dict(operations=[dict(text='pan ready')],g2p_tokens=[dict(text='pan',phonemes='pæn',whitespace=' '),dict(text='ready',phonemes='ɹɛdi',whitespace='')])
  edits=[edit('phone_pair',0,3,reference_ipa='pæn',mutated_ipa='bæn'),edit('phone_pair',4,9,reference_ipa='ɹɛdi',mutated_ipa='lɛdi')]
  compile_scopes(piece,edits,0,set('pænb ɹɛdil'))
  self.assertEqual(len(piece['phone_variants']),2)
  self.assertEqual({v['compiled_phonemes'] for v in piece['phone_variants'].values()},{'bæn ɹɛdi','pæn lɛdi'})
 def test_duplicate_same_scope_negative(self):
  from acoustic_alignment import compile_scopes
  from test_acoustic_controls import edit
  piece=dict(operations=[dict(text='pan')],g2p_tokens=[dict(text='pan',phonemes='pæn',whitespace='')])
  compile_scopes(piece,[edit('pitch_duration',0,3,gain_db=2),edit('pause_insert',0,3,pause_ms=100)],0,set('pæn'))
  self.assertEqual(len(piece['acoustic_token_scopes']),1,'one actual target must not become two key intervals')
if __name__=='__main__':unittest.main()
