"""Reconcile retained actual browser/HTTP observations, not a new browser run.

These controlled PCM observations prove saved-media recovery/layout only. They
do not establish Azure speech, audible mutations or unobserved user activation.
"""
import json,unittest
from pathlib import Path
AUDIT=Path(__file__).resolve().parents[1]/'audit/iteration-24-azure-20261026'

class AzurePlayerObservations(unittest.TestCase):
 def facts(self):return json.loads((AUDIT/'browser-observations.json').read_text())
 def state(self,name):return next(x['observation'] for x in self.facts()['states'] if x['state']==name)
 def test_player_media_retry_positive(self):
  http=json.loads((AUDIT/'media-http-observations.json').read_text())
  self.assertEqual(0,http['actual_model_calls'])
  for name in ['azure-clean.wav','azure-mistakes.wav']:self.assertEqual(2,http['transient_recovery']['counts']['/'+name])
  state=self.state('media_transient_recovered');self.assertEqual(['',''],state['messages'])
  self.assertEqual(2,len(state['audio']))
  for audio in state['audio']:self.assertEqual(4,audio['readyState']);self.assertTrue(audio['paused']);self.assertEqual(6,audio['duration']);self.assertIsNone(audio.get('error'))
 def test_player_persistent_media_failure_negative(self):
  http=json.loads((AUDIT/'media-http-observations.json').read_text())
  for name in ['azure-clean.wav','azure-mistakes.wav']:self.assertEqual(2,http['persistent_failure']['counts']['/'+name])
  state=self.state('media_failure_after_retry');self.assertEqual(2,len(state['messages']))
  for message in state['messages']:
   self.assertEqual('The saved recording could not be played. Refresh saved recordings and try again. No new audio is generated.',message)
  partial=self.state('partial');self.assertEqual(1,len(partial['audio']));self.assertEqual('/azure-clean.wav',partial['audio'][0]['src']);self.assertTrue(all(not b['disabled'] for b in partial['buttons']))
 def test_player_controlled_layout_positive(self):
  layouts=self.facts()['layouts'];self.assertEqual([1280,390,320],[x['width'] for x in layouts])
  for layout in layouts:
   self.assertEqual(layout['width'],layout['pageWidth']);self.assertTrue(layout['fontLoaded']);self.assertEqual('17px',layout['size']);self.assertEqual('24.65px',layout['line']);self.assertTrue(all(a['paused'] for a in layout['audio']))

if __name__=='__main__':unittest.main(verbosity=2)
