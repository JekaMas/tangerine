"""Actual native included-plan/local-speech observations; export is zero-call."""
from pathlib import Path
import json,unittest,wave
R=Path(__file__).resolve().parents[1];O=R/'data/ux-controls-20261023'
class UXModel(unittest.TestCase):
 def observation(self,label,count):
  p=O/'flow'/label
  key=json.loads((p/'ground-truth.json').read_text());binding=json.loads((p/'binding.json').read_text());request=json.loads((p/'blueprint.json').read_text())['exercise_request']
  self.assertEqual(request['category_ids'],['lexis.collocation']);self.assertEqual(request['severity_levels'],['minor']);self.assertEqual(request['mutation_count'],count);self.assertEqual(len(key['units']),count)
  rendered=json.loads((p/'render.json').read_text());self.assertEqual(rendered['phase_states'],{'canonical_text':'complete','mutation':'complete','render':'complete'})
  with wave.open(str(p/'actual.wav'),'rb') as w:self.assertEqual([w.getnchannels(),w.getsampwidth(),w.getframerate()],[1,2,24000]);self.assertGreater(w.getnframes(),24000)
  index=json.loads((O/'native-diagnostics.json').read_text());self.assertGreaterEqual(len(index['asset_ids']),4);self.assertEqual(index['readback_inference_calls'],0)
  packets=[(O/'native-diagnostics'/(x+'.json')).read_text() for x in index['asset_ids']];self.assertGreaterEqual(sum(binding['preparation_id'] in x for x in packets),2)
  receipt=json.loads((O/'mlflow.json').read_text());self.assertEqual(receipt['export_inference_calls'],0);self.assertEqual(receipt['flow_readback'],['minor','zero'])
  return p,key
 def test_minor_actual_positive(self):
  p,key=self.observation('minor',1);u=key['units'][0];self.assertEqual([u['primary_taxonomy_id'],u['severity'],u['weight']],['lexis.collocation','minor',1]);self.assertIn('I made a mistake',u['realization']['canonical_text']);self.assertIn('I did a mistake',u['realization']['surface_text'])
 def test_zero_actual_negative(self):
  p,_=self.observation('zero',0);clean=json.loads((p/'canonical_asset_id.json').read_text());mut=json.loads((p/'mutated_asset_id.json').read_text());self.assertEqual(clean['utterances'],mut['utterances']);self.assertEqual(mut['planned_units'],[]);self.assertEqual(mut['acoustic_edits'],[])
if __name__=='__main__':unittest.main()
