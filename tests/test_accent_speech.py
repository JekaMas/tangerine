"""Pure native phone/routing and actual missing-model admission, no synthesis."""
from pathlib import Path
import sys,tempfile,unittest
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'services/speech'))
from accent_phones import ipa_phones,route_voice
class AccentSpeech(unittest.TestCase):
 def test_ipa_positive(self):self.assertEqual([ipa_phones('θɪŋk'),ipa_phones('sɪŋk'),ipa_phones('ʃɪp'),ipa_phones('ʃiːp'),ipa_phones('ˈfəʊtəɡræf')],[[('th',0),('ih',1),('ng',0),('k',0)],[('s',0),('ih',1),('ng',0),('k',0)],[('sh',0),('ih',1),('p',0)],[('sh',0),('iy',1),('p',0)],[('f',0),('ow',2),('t',0),('ah',1),('g',0),('r',0),('ae',1),('f',0)]])
 def test_unknown_phone_negative(self):
  with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):ipa_phones('qɪp')
 def test_routing_positive(self):self.assertEqual([route_voice(v) for v in ['melo_en_au','melo_en_in','af_heart','bm_george']],[('local_melo','en-AU',3),('local_melo','en-IN',2),('local_kokoro','en-US',None),('local_kokoro','en-GB',None)])
 def test_missing_model_negative(self):
  import model_setup
  before=model_setup.ROOT
  try:
   with tempfile.TemporaryDirectory() as path:
    model_setup.ROOT=Path(path)
    with self.assertRaisesRegex(ValueError,'MODEL_SETUP_REQUIRED'):model_setup.installed('melo-local-en-v1')
  finally:model_setup.ROOT=before
if __name__=='__main__':unittest.main()
