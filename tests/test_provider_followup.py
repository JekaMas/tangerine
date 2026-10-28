"""Exact retained request/PCM/browser/Lab expectations; no model dispatch.

Native provider speech is an external input to normalization, not linguistic
correctness gold. The same explicit Free model/configuration serves both variants.
"""
import base64,io,json,sys,wave
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/completion-leftovers-20261028';PAIR=DATA/'gemini-current-api';sys.path.insert(0,str(ROOT/'services/speech'));from audio import admit

def read(name):return json.loads((PAIR/name).read_text())
def audio_output(value):
 if isinstance(value,dict):
  if value.get('type')=='audio' and value.get('data'):return base64.b64decode(value['data'])
  return next((a for x in value.values() if (a:=audio_output(x))),None)
 if isinstance(value,list):return next((a for x in value if (a:=audio_output(x))),None)

class ProviderFollowup(unittest.TestCase):
 def test_context_positive(self):
  original=json.loads((ROOT/'data/pronunciation-all-20261023/output/shared-material.json').read_text());plan=read('plan.json')
  self.assertEqual(original,plan['source_material']);self.assertEqual((20,26),(len(original['turns']),len(original['targets'])))
  voices=[dict(speaker='s1',voice='Kore'),dict(speaker='s2',voice='Puck')]
  for variant in ['clean','mistakes']:
   request=read('gemini-'+variant+'-request.json');body=request['body'];self.assertEqual('https://generativelanguage.googleapis.com/v1beta/interactions',request['url'])
   self.assertEqual('gemini-3.8-flash-lite-tts',body['model']);self.assertEqual(dict(speakers=voices),body['generation_config']['speech_config'])
   turns=body['input'][0]['content'];self.assertEqual([t['canonical_text'] for t in original['turns']],[t['text'] for t in turns])
   self.assertEqual([t['speaker_id'] for t in original['turns']],[t['annotations'][0]['speaker'] for t in turns])
   if variant=='mistakes':
    for turn,source in zip(turns,original['turns']):
     for target in source['targets']:self.assertIn(target['provider_hint'],turn['annotations'][0]['style'])
   else:self.assertFalse(any('deliberate acoustic deviations' in t['annotations'][0]['style'] for t in turns))
   response=read('gemini-'+variant+'.raw');self.assertEqual(('completed','gemini-3.8-flash-lite-tts'),(response['status'],response['model']));self.assertGreater(response['usage']['total_output_tokens'],0)
   self.assertEqual(200,read('gemini-'+variant+'-receipt.json')['http_status'])
  lab=json.loads((DATA/'gemini-lab-readback.json').read_text());self.assertTrue(lab['readback']);self.assertEqual((2,1,0),(lab['matched_successful_model_calls'],lab['failed_contract_requests'],lab['export_inference_calls']))
 def test_audio_and_playback_positive(self):
  for variant in ['clean','mistakes']:
   with wave.open(io.BytesIO(audio_output(read('gemini-'+variant+'.raw')))) as native:
    self.assertEqual((1,2,24000),(native.getnchannels(),native.getsampwidth(),native.getframerate()));expected=native.readframes(native.getnframes())
   projected=(PAIR/('gemini-'+variant+'.wav')).read_bytes();self.assertEqual(expected,admit(projected))
   with wave.open(io.BytesIO(projected)) as audio:self.assertEqual(len(expected)//2,audio.getnframes())
  facts=json.loads((DATA/'gemini-browser/browser-observations.json').read_text())
  self.assertTrue(facts['actual_pair_playback_observed'] and facts['activation_observed'] and facts['keyboard_observed'] and facts['refresh_observed'] and facts['single_player_observed'])
  self.assertEqual(26,facts['requested_targets']);self.assertEqual(['/gemini-clean.wav','/gemini-mistakes.wav'],[a['src'] for a in facts['audio']]);self.assertTrue(all(a['advanced_time']>0 and a['error'] is None for a in facts['audio']))
  self.assertEqual([1280,390,320],[v['width'] for v in facts['layouts']]);self.assertTrue(all(v['width']==v['pageWidth'] and v['fontLoaded'] and v['size']=='17px' for v in facts['layouts']))
  requests=json.loads((DATA/'gemini-browser/requests.json').read_text());self.assertTrue(all(r['method']=='GET' for r in requests))
 def test_legacy_mode_negative(self):
  legacy=DATA/'gemini-resume';response=json.loads((legacy/'gemini-mistakes-3.raw').read_text());receipt=json.loads((legacy/'gemini-mistakes-3-receipt.json').read_text());request=json.loads((legacy/'gemini-mistakes-3-request.json').read_text())
  self.assertEqual(400,receipt['http_status']);self.assertIn("Unknown parameter 'mode'",response['error']['message']);self.assertEqual('conversational',request['body']['generation_config']['speech_config']['mode'])
  old=json.loads((ROOT/'data/pronunciation-all-20261023/output/gemini-mistakes-3-receipt.json').read_text());self.assertEqual(429,old['http_status'])
  for variant in ['clean','mistakes']:self.assertNotIn('mode',read('gemini-'+variant+'-request.json')['body']['generation_config']['speech_config'])
 def test_streaming_container_negative(self):
  for variant in ['clean','mistakes']:
   bad=(PAIR/'container-projection-failure'/('gemini-'+variant+'.wav')).read_bytes()
   with self.assertRaisesRegex(ValueError,'AUDIO_FORMAT_INVALID'):admit(bad)
   # The provider reply and PCM are preserved. Fixing a container projection
   # must not request a new generation or accept the false24-hour duration.
   self.assertGreater(len(admit((PAIR/('gemini-'+variant+'.wav')).read_bytes())),0)
  calls=read('dispatches.json');self.assertEqual(2,len(calls));self.assertTrue(all(c['outcome']=='complete' and c['http_status']==200 for c in calls))

if __name__=='__main__':unittest.main(verbosity=2)
