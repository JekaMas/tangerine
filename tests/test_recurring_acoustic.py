"""Constructed compiler inputs, independent literal outputs; no model claims."""
from pathlib import Path
import copy,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'services/speech'))
from acoustic_alignment import compile_scopes
class RecurringAcoustic(unittest.TestCase):
 def compile(self,grouped,changed='bæn'):
  piece={'operations':[{'text':'pan pan pan pan'}],'g2p_tokens':[{'text':'pan','phonemes':'pæn','whitespace':' ' if i<3 else ''} for i in range(4)]}
  if grouped:piece['recurring_unit_ids']=['habit']
  edits=[{'unit_id':'habit','scope':{'start':i*4,'end':i*4+3},'controller':'phone_pair','parameters':{'reference_ipa':'pæn','mutated_ipa':changed}} for i in [0,1,3]]
  compile_scopes(piece,edits,0,set('pænbə '));return piece
 def test_group_positive(self):
  p=self.compile(True);self.assertEqual(list(p['phone_variants']),['habit']);self.assertEqual(p['phone_variants']['habit']['compiled_phonemes'],'bæn bæn pæn bæn');self.assertEqual(len(p['acoustic_token_scopes']),3)
  p=self.compile(True,'bəæn');self.assertEqual(p['phone_variants']['habit']['compiled_phonemes'],'bəæn bəæn pæn bəæn');self.assertEqual([(s['phone_start'],s['phone_end']) for s in p['phone_variants']['habit']['scopes']],[(0,4),(5,9),(14,18)])
 def test_independent_negative(self):
  p=self.compile(False);self.assertEqual(len(p['phone_variants']),3);self.assertEqual(set(v['compiled_phonemes'] for v in p['phone_variants'].values()),{'bæn pæn pæn pæn','pæn bæn pæn pæn','pæn pæn pæn bæn'})
if __name__=='__main__':unittest.main()
