"""I24 exact completion oracles. Missing real Azure evidence never becomes green."""
import base64,copy,json,unittest,wave
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/iteration-24-azure-20261026'
SOURCE='9dbf8c95-51a3-4c0f-9395-b3a77a824d22'
def target_errors(rows):
 expected={('u1','s1','choices'),('u2','s2','companies'),('u3','s1','another'),('u4','s2','Collision')}
 if len(rows)!=4 or {(r.get('turn_id'),r.get('speaker_id'),r.get('word')) for r in rows}!=expected:return ['target observations missing or mismatched']
 if any(r.get('reference_file')!='azure-clean.wav' or r.get('mutated_file')!='azure-mistakes.wav' or r.get('outcome') not in ['realized','partly_realized','not_realized','uncertain'] or not r.get('observation','').strip() for r in rows):return ['target observations missing or mismatched']
 return []
def review_errors(packet):
 errors=[]
 for field in ['ui_ux','typography','evidence']:
  if not packet.get(field,{}).get('observations'):errors.append(field+' omitted')
 if packet.get('source_preparation')!=SOURCE:errors.append('source mismatch')
 if packet.get('requested_benchmark_calls',0):errors.append('excluded performance campaign')
 if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
 if packet.get('claims_full_completion') and packet.get('missing_inputs'):errors.append('missing evidence claimed green')
 if packet.get('claims_full_completion'):errors.extend(target_errors(packet.get('target_observations',[])))
 return errors
def packet():return dict(source_preparation=SOURCE,reference_origin='independently authored literal expectations',requested_benchmark_calls=0,claims_full_completion=False,missing_inputs=['Microsoft passkey; actual F0 resource/key/region and recordings'],ui_ux=dict(observations='Actual waiting view inspected; interactions and real playback incomplete.'),typography=dict(observations='Actual loaded Source Sans3,17px body and24.65px line height at1280/390/320, no overflow.'),evidence=dict(observations='Native controlled compilation/policy/resume; actual Azure synthesis not performed.'))

class CompletionI24(unittest.TestCase):
 def test_azure_positive(self):
  out=DATA/'live'
  if not (out/'result.json').exists():self.skipTest('Actual Azure F0 resource/key/region unavailable; Microsoft passkey handoff pending. No real Azure recordings.')
  result=json.loads((out/'result.json').read_text());plan=json.loads((out/'plan.json').read_text())
  self.assertEqual('complete',result['status']);self.assertEqual(SOURCE,plan['source_preparation']);self.assertEqual('F0',plan['resource']['sku']['name']);self.assertEqual(8,len(plan['turns']))
  original=json.loads((ROOT/'audit/iteration-24-azure-20261026/material.json').read_text());self.assertEqual(original,plan['source_material'])
  calls=json.loads((out/'dispatches.json').read_text());completed=[d for d in calls if d.get('http_status')==200];self.assertEqual(8,len(completed))
  expected=[(variant,t) for variant in ['clean','mistakes'] for t in original['turns']];ns={'s':'http://www.w3.org/2001/10/synthesis'}
  for row,(variant,t) in zip(completed,expected):
   self.assertEqual('actual Azure HTTP transport',row['origin']);self.assertTrue(row['credential_header_present']);self.assertTrue(row['raw_response_base64']);self.assertEqual(plan['profile']['endpoint'],row['url'])
   tree=ET.fromstring(base64.b64decode(row['body_base64']));voice=tree.find('s:voice',ns);phoneme=voice.find('s:phoneme',ns)
   self.assertEqual(t['canonical_text'],''.join(voice.itertext()));self.assertEqual('en-US-JennyNeural' if t['speaker_id']=='s1' else 'en-GB-RyanNeural',voice.attrib['name']);self.assertEqual(t['target']['word'],phoneme.text);self.assertEqual(t['target']['reference_ipa' if variant=='clean' else 'mutated_ipa'],phoneme.attrib['ph'])
   native=json.loads((out/(variant+'-'+t['id']+'-response.json')).read_text());self.assertEqual(row['body_base64'],native['receipt']['native']['body_base64'])
  for variant in ['clean','mistakes']:
   with wave.open(str(out/('azure-'+variant+'.wav'))) as audio:
    self.assertEqual((1,2,24000),(audio.getnchannels(),audio.getsampwidth(),audio.getframerate()));frames=audio.getnframes();pcm=audio.readframes(frames)
   parts=0;expected_pcm=[]
   for t in plan['turns']:
    if t['variant']==variant:
     with wave.open(str(out/(variant+'-'+t['id']+'.wav'))) as audio:parts+=audio.getnframes()+7200;expected_pcm.append(audio.readframes(audio.getnframes())+b'\0\0'*7200)
   self.assertEqual(parts,frames);self.assertEqual(b''.join(expected_pcm),pcm)
 def test_review_positive(self):
  self.assertEqual([],review_errors(packet()))
  if not (DATA/'live/result.json').exists():self.skipTest('No actual Azure pair/player playback to verify; only waiting-state visual observations are available.')
  facts=json.loads((DATA/'live/browser-facts.json').read_text());self.assertTrue(facts['playback_observed']);self.assertEqual(SOURCE,facts['source_preparation'])
  self.assertEqual([],target_errors(facts['target_observations']))
 def test_ux_omission_negative(self):
  p=packet();p.pop('ui_ux');self.assertIn('ui_ux omitted',review_errors(p))
 def test_typography_omission_negative(self):
  p=packet();p.pop('typography');self.assertIn('typography omitted',review_errors(p))
 def test_evidence_mismatch_negative(self):
  for change,error in [({'source_preparation':'wrong'},'source mismatch'),({'claims_full_completion':True},'missing evidence claimed green'),({'requested_benchmark_calls':50},'excluded performance campaign'),({'reference_origin':'candidate-generated'},'reference origin')]:
   p=packet();p.update(change);self.assertIn(error,review_errors(p))
  rows=[dict(turn_id=u,speaker_id=s,word=w,reference_file='azure-clean.wav',mutated_file='azure-mistakes.wav',outcome='uncertain',observation='Constructed review fixture; no Azure audio claim.') for u,s,w in [('u1','s1','choices'),('u2','s2','companies'),('u3','s1','another'),('u4','s2','Collision')]]
  self.assertEqual([],target_errors(rows))
  for invalid in [rows[:3],[{**r,'word':'wrong'} if r['turn_id']=='u1' else r for r in rows],[{**r,'observation':''} for r in rows],[{**r,'reference_file':'another-exercise.wav'} for r in rows]]:
   self.assertEqual(['target observations missing or mismatched'],target_errors(invalid))

if __name__=='__main__':unittest.main(verbosity=2)
