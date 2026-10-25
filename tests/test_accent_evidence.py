"""Independent readback of actual local synthesis/browser/demo artifacts."""
from pathlib import Path
import hashlib,json,unittest,wave,urllib.request
R=Path(__file__).resolve().parents[1];O=R/'data/accents-20261025'
class AccentEvidence(unittest.TestCase):
 def ui(self):return json.loads((O/'browser.json').read_text())
 def test_controls_positive(self):
  v=self.ui();self.assertEqual(v['controls']['choices'],['melo_en_au','melo_en_in']);self.assertTrue(v['controls']['restore']);self.assertEqual(v['controls']['saved'],['melo_en_au','melo_en_in']);self.assertTrue(v['controls']['narrow_no_overflow'])
 def test_voice_failure_negative(self):
  v=self.ui()['failure'];self.assertTrue(v['catalogue_retained']);self.assertTrue(v['preview_retained']);self.assertEqual(v['llm_requests'],0)
 def voice(self,name,locale,speaker):
  d=O/'speech'/name;v=json.loads((d/'preview.json').read_text());self.assertEqual([v['receipt']['provider'],v['receipt']['locale'],v['receipt']['native']['speaker_id']],['local_melo',locale,speaker]);self.assertIsNone(v['receipt']['observed_accent']);self.assertTrue(v['receipt']['native']['model_visible_calls']);
  with wave.open(str(d/'preview.wav')) as w:self.assertEqual([w.getnchannels(),w.getframerate()],[1,24000]);self.assertGreater(w.getnframes(),24000);self.assertTrue(any(w.readframes(w.getnframes())))
 def test_australian_positive(self):self.voice('melo_en_au','en-AU',3)
 def test_indian_positive(self):self.voice('melo_en_in','en-IN',2)
 def test_acoustic_pair_positive(self):
  for name in ['melo_en_au','melo_en_in']:
   d=O/'speech'/name;native=json.loads((d/'acoustic-response.json').read_text())['receipt']['native'];pair=native['paired_mutations']['target']['native'];refs=next(r for r in native['acoustic_scopes'] if r['unit_id']=='target');changed=next(r for r in pair['acoustic_scopes'] if r['unit_id']=='target');self.assertEqual(refs['phonemes'],['th','ih','ng','k']);self.assertEqual(changed['phonemes'],['s','ih','ng','k']);self.assertEqual(native['speaker_id'],pair['speaker_id']);self.assertLess(refs['start'],refs['end']);self.assertNotEqual(hashlib.sha256((d/'reference.wav').read_bytes()).digest(),hashlib.sha256((d/'mutated.wav').read_bytes()).digest());self.assertEqual(json.loads((d/'transformed.json').read_text())['receipt']['model_calls'],0)
 def test_preview_replay_negative(self):self.assertEqual(self.ui()['preview'],{'plays':2,'synthesis_requests':0,'same_audio':True})
 def test_actual_demo_positive(self):
  v=json.loads((O/'demo.json').read_text());self.assertTrue(v['actual_generation']);self.assertTrue(v['actual_playback']);self.assertTrue(v['actual_answer']);self.assertTrue(v['score_and_feedback']);self.assertFalse(v['network_substitution']);self.assertTrue(Path(v['video_path']).is_file());self.assertGreater(Path(v['video_path']).stat().st_size,100000)
  prep=json.loads((O/'demo-preparation.json').read_text());self.assertEqual(prep['phase_states'],{'canonical_text':'complete','mutation':'complete','render':'complete'});self.assertEqual(prep['render_progress_summary']['complete_pieces'],4);self.assertEqual(prep['exercise_request']['speaker_voice_ids'],['melo_en_au','melo_en_in'])
  attempt=json.loads((O/'demo-attempt.json').read_text());result=json.loads((O/'demo-results.json').read_text());self.assertEqual(attempt['state'],'completed');self.assertEqual(result['status'],'complete');self.assertEqual(result['feedback_status'],'complete');self.assertEqual(result['score']['counts']['tp'],1);self.assertEqual(result['score']['counts']['fn'],1);self.assertEqual(result['score']['counts']['fp'],0);self.assertEqual(result['score']['composite']['exact_value_0_100'],{'denominator':'1','numerator':'60'});self.assertTrue(result['feedback']['items'])
  recording=json.loads((O/'demo-frames.json').read_text());self.assertTrue(recording['dialoguePlayback']['ended']);self.assertEqual(recording['dialoguePlayback']['time'],recording['dialoguePlayback']['duration']);self.assertGreater(len(recording['frames']),100)
 def test_preserved_work_negative(self):
  old=json.loads((O/'attempt-before.json').read_text());new=json.load(urllib.request.urlopen('http://localhost:3000/api/v1/attempts/'+old['attempt_id'],timeout=10));self.assertEqual(old,new);before=json.loads((O/'configuration-before.json').read_text());after=json.load(urllib.request.urlopen('http://localhost:3000/api/v1/configuration',timeout=10));self.assertEqual(before['configuration'],after['configuration']);self.assertEqual([(x['name'],x['present']) for x in before['credentials']],[(x['name'],x['present']) for x in after['credentials']]);self.assertEqual(json.loads((O/'demo.json').read_text())['paid_dispatches'],0)
if __name__=='__main__':unittest.main()
