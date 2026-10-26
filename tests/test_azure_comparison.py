"""Literal Azure compilation/policy/recovery fixtures, never hosted voice proof."""
import base64,copy,importlib.util,json,os,tempfile,unittest,wave,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'services/speech'))
import audio,backends
spec=importlib.util.spec_from_file_location('azure_comparison',ROOT/'audit/iteration-24-azure-20261026/compare.py')
comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison)
spec_player=importlib.util.spec_from_file_location('azure_player',ROOT/'audit/iteration-24-azure-20261026/player.py')
player=importlib.util.module_from_spec(spec_player);spec_player.loader.exec_module(player)
from xml.etree import ElementTree as ET
NS={'s':'http://www.w3.org/2001/10/synthesis'}

class AzureComparison(unittest.TestCase):
 def plan(self):return comparison.build_plan(json.loads(comparison.SOURCE.read_text()),{'location':'eastus','sku':{'name':'F0'},'origin':'constructed resource metadata; no entitlement claim'})
 def test_ssml_continuity_negative(self):
  for turn in self.plan()['turns']:
   tree=ET.fromstring(backends.ssml(turn));voice=tree.find('s:voice',NS)
   self.assertEqual([],voice.findall('s:s',NS),'Text fragments must not become sentences around the selected word.')
   self.assertEqual(''.join(o['text'] for o in turn['operations']),''.join(voice.itertext()))
 def test_ssml_targets_positive(self):
  plan=self.plan();expected={'u1':('choices','tʃɔɪsɪz','ʃɔɪsɪz'),'u2':('companies','ˈkʌmpəniz','kəmˈpæniz'),'u3':('another','əˈnʌðɚ','əˈnʌzɚ'),'u4':('Collision','kəˈlɪʒən','ˈkɑlɪʒən')}
  self.assertEqual(8,len(plan['turns']))
  for t in plan['turns']:
   tree=ET.fromstring(backends.ssml(t));p=tree.find('s:voice/s:phoneme',NS);word,reference,changed=expected[t['id']]
   self.assertEqual(word,p.text);self.assertEqual('ipa',p.attrib['alphabet']);self.assertEqual(reference if t['variant']=='clean' else changed,p.attrib['ph'])
   self.assertEqual(('en-US-JennyNeural','en-US') if t['speaker_id']=='s1' else ('en-GB-RyanNeural','en-GB'),(t['voice_id'],t['locale']))
 def test_text_prosody_pause_siblings_positive(self):
  t=copy.deepcopy(self.plan()['turns'][0]);t['operations']=[{'kind':'text','text':'A <safe> & '},{'kind':'phoneme','text':'word','ipa':'wɜːd'},{'kind':'text','text':' in '},{'kind':'prosody','text':'context','pitch_semitones':2},{'kind':'pause','duration_ms':100},{'kind':'text','text':'.'}]
  tree=ET.fromstring(backends.ssml(t));v=tree.find('s:voice',NS)
  self.assertEqual('A <safe> & word in context.',''.join(v.itertext()));self.assertEqual(' in ',v[0].tail);self.assertEqual('.',v[-1].tail);self.assertEqual('+2st',v.find('s:prosody',NS).attrib['pitch']);self.assertEqual('100ms',v.find('s:break',NS).attrib['time'])
 def test_missing_key_negative(self):
  p=self.plan()
  with patch.dict(os.environ,{},clear=True),patch.object(backends,'transport') as transport:
   result,code=backends.execute_packet(dict(profile=p['profile'],turn=p['turns'][0]))
  self.assertEqual(({'error':'MISSING_CREDENTIALS'},1),(result,code));transport.assert_not_called()
 def test_non_f0_overage_negative(self):
  p=self.plan()
  for change in [dict(account_tier='S0'),dict(account_tier='trial'),dict(billing_mode='metered'),dict(overage_disabled=False)]:
   with self.subTest(change=change),patch.object(backends,'transport') as transport:
    result,code=backends.execute_packet(dict(profile={**p['profile'],**change},turn=p['turns'][0]))
   self.assertEqual(({'error':'PAID_USE_FORBIDDEN'},1),(result,code));transport.assert_not_called()
 def test_resource_tier_is_preserved_negative(self):
  p=comparison.build_plan(json.loads(comparison.SOURCE.read_text()),{'location':'westus','sku':{'name':'S0'}})
  self.assertEqual('S0',p['profile']['account_tier'])
  with patch.object(backends,'transport') as transport,self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):
   with tempfile.TemporaryDirectory() as tmp:comparison.execute(p,Path(tmp))
  transport.assert_not_called()
 def test_pair_native_transport_positive(self):
  p=self.plan();calls=[]
  def respond(url,body,headers,timeout):
   calls.append((url,body,headers,timeout));return audio.wav_bytes((len(calls)*1024).to_bytes(2,'little')*2400),200
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-private-key'}),patch.object(backends,'transport',side_effect=respond):
   result=comparison.execute(p,Path(tmp));self.assertEqual('complete',result['status']);self.assertEqual(8,len(calls))
   for variant in ['clean','mistakes']:
    with wave.open(str(Path(tmp)/('azure-'+variant+'.wav'))) as a:
     self.assertEqual((1,2,24000,38400),(a.getnchannels(),a.getsampwidth(),a.getframerate(),a.getnframes()))
     values=[1024,2048,3072,4096] if variant=='clean' else [5120,6144,7168,8192]
     self.assertEqual(b''.join(v.to_bytes(2,'little')*2400+b'\0\0'*7200 for v in values),a.readframes(a.getnframes()))
   for url,body,headers,timeout in calls:
    self.assertEqual(p['profile']['endpoint'],url);self.assertEqual('constructed-private-key',headers['Ocp-Apim-Subscription-Key']);self.assertNotIn(b'constructed-private-key',body);self.assertGreater(timeout,0)
 def test_resume_reuses_pieces_positive(self):
  p=self.plan();fixture=audio.wav_bytes(b'\x00\x10'*2400);calls=[]
  def respond(*args):
   calls.append(args)
   if len(calls)==3:raise ValueError('PROVIDER_QUOTA')
   return fixture,200
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-private-key'}),patch.object(backends,'transport',side_effect=respond):
   out=Path(tmp)
   with self.assertRaisesRegex(ValueError,'PROVIDER_QUOTA'):comparison.execute(p,out)
   self.assertEqual(2,len(list(out.glob('clean-u*.wav'))));self.assertFalse((out/'azure-clean.wav').exists())
   before=(out/'clean-u1.wav').read_bytes();comparison.execute(p,out)
   self.assertEqual(9,len(calls));self.assertEqual(before,(out/'clean-u1.wav').read_bytes())
   comparison.execute(p,out);self.assertEqual(9,len(calls))
 def test_saved_response_recovery_positive(self):
  p=self.plan();fixture=audio.wav_bytes(b'\x00\x10'*2400)
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-private-key'}),patch.object(backends,'transport',return_value=(fixture,200)) as transport:
   out=Path(tmp);comparison.execute(p,out);self.assertEqual(8,transport.call_count)
   original=(out/'clean-u1.wav').read_bytes();(out/'clean-u1.wav').unlink()
   comparison.execute(p,out);self.assertEqual(8,transport.call_count);self.assertEqual(original,(out/'clean-u1.wav').read_bytes());self.assertEqual([],list(out.glob('*.partial')))
 def test_cli_context_capture_positive(self):
  fixture=audio.wav_bytes(b'\x00\x10'*2400)
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-private-key'}),patch.object(backends,'transport',return_value=(fixture,200)):
   out=Path(tmp)/'out';resource=Path(tmp)/'resource.json';resource.write_text(json.dumps({'location':'eastus','sku':{'name':'F0'},'origin':'constructed metadata'}))
   with patch.object(sys,'argv',['compare','--out',str(out),'--resource',str(resource)]):comparison.main()
   dispatches=json.loads((out/'dispatches.json').read_text());self.assertEqual(8,len(dispatches));self.assertEqual(8,len(list(out.glob('*-response.json'))))
   for row in dispatches:
    self.assertTrue(row['credential_header_present']);self.assertEqual(200,row['http_status']);self.assertTrue(row['raw_response_base64']);self.assertNotIn('constructed-private-key',json.dumps(row));ET.fromstring(base64.b64decode(row['body_base64']))
 def test_cli_failure_capture_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-private-key'}),patch.object(backends,'transport',side_effect=ValueError('PROVIDER_QUOTA')):
   out=Path(tmp)/'out';resource=Path(tmp)/'resource.json';resource.write_text(json.dumps({'location':'eastus','sku':{'name':'F0'},'origin':'constructed metadata'}))
   with patch.object(sys,'argv',['compare','--out',str(out),'--resource',str(resource)]):self.assertEqual(1,comparison.main())
   dispatches=json.loads((out/'dispatches.json').read_text());self.assertEqual(1,len(dispatches));self.assertEqual('PROVIDER_QUOTA',dispatches[0]['error']);self.assertNotIn('raw_response_base64',dispatches[0]);self.assertFalse((out/'result.json').exists());self.assertEqual([],list(out.glob('azure-*.wav')))
 def test_player_unavailable_positive(self):
  with tempfile.TemporaryDirectory() as tmp:
   page=player.page(Path(tmp),'live')
  self.assertIn('Comparison incomplete',page);self.assertIn('existing Azure F0 Speech resource, key and region',page);self.assertNotIn('<audio ',page);self.assertIn('Refresh saved recordings',page);self.assertNotIn('AZURE_SPEECH_KEY',page)
 def test_player_private_routes_negative(self):
  from http.server import ThreadingHTTPServer
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'secret.env').write_text('private-key-sentinel')
   server=ThreadingHTTPServer(('127.0.0.1',0),player.handler(out,'live'));worker=threading.Thread(target=server.serve_forever);worker.start()
   try:
    base='http://127.0.0.1:'+str(server.server_address[1])
    for path in ['/secret.env','/plan.json','/azure-clean.wav/../secret.env']:
     with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+path)
     self.assertEqual(404,error.exception.code);self.assertNotIn(b'private-key-sentinel',error.exception.read())
    with urllib.request.urlopen(base+'/') as response:self.assertEqual(200,response.status)
   finally:server.shutdown();server.server_close();worker.join()

if __name__=='__main__':unittest.main(verbosity=2)
