"""Constructed recovery counterexamples through the native comparison owner."""
import base64,contextlib,importlib.util,io,json,os,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'services/speech'))
import audio,backends
spec=importlib.util.spec_from_file_location('azure_recovery_comparison',ROOT/'audit/iteration-24-azure-20261026/compare.py')
comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(comparison)
spec=importlib.util.spec_from_file_location('azure_recovery_player',ROOT/'audit/iteration-24-azure-20261026/player.py')
player=importlib.util.module_from_spec(spec);spec.loader.exec_module(player)

class AzureRecovery(unittest.TestCase):
 def plan(self):return comparison.build_plan(json.loads(comparison.SOURCE.read_text()),{'location':'eastus','sku':{'name':'F0'},'origin':'constructed metadata'})
 def test_transport_failure_metadata_positive(self):
  for status in [401,403,429,503]:
   error=urllib.error.HTTPError('https://fixture.invalid/tts',status,'private-sentinel',{'Retry-After':'2'},io.BytesIO(b'private-sentinel'))
   with patch.object(backends.urllib.request,'build_opener') as factory:
    factory.return_value.open.side_effect=error
    with self.assertRaises(ValueError) as failed:backends.transport('https://fixture.invalid/tts',b'input',{},10)
   self.assertEqual(status,failed.exception.http_status);self.assertEqual(2,failed.exception.retry_after);self.assertNotIn('private-sentinel',str(failed.exception))
 def test_transient_retry_positive(self):
  for failure in [urllib.error.URLError('private-sentinel'),TimeoutError('private-sentinel'),self.http_failure(503)]:
   with self.subTest(failure=type(failure).__name__),tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=[failure]+[(audio.wav_bytes(b'\x00\x10'*2400),200)]*8) as send,patch.object(comparison,'sleep') as sleep:
    result=comparison.execute(self.plan(),Path(tmp))
    self.assertEqual('complete',result['status']);self.assertEqual(9,send.call_count);sleep.assert_called_once_with(1)
    state=json.loads((Path(tmp)/'state.json').read_text());self.assertEqual(('complete',8),(state['state'],state['completed_pieces']))
 def http_failure(self,status,retry_after=None):
  error=ValueError('PROVIDER_QUOTA' if status==429 else 'PROVIDER_FAILED');error.http_status=status;error.retry_after=retry_after;return error
 def test_known_rate_limit_recovery_positive(self):
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=[self.http_failure(429,2)]+[(audio.wav_bytes(b'\x00\x10'*2400),200)]*8) as send,patch.object(comparison,'sleep') as sleep:
   self.assertEqual('complete',comparison.execute(self.plan(),Path(tmp))['status']);self.assertEqual(9,send.call_count);sleep.assert_called_once_with(2)
 def test_terminal_failures_negative(self):
  for failure in [self.http_failure(401),self.http_failure(403),self.http_failure(400),self.http_failure(429),ValueError('PAID_USE_FORBIDDEN'),ValueError('AUDIO_SILENT')]:
   with self.subTest(failure=str(failure)),tempfile.TemporaryDirectory() as tmp,patch.object(backends,'render',side_effect=failure) as send,patch.object(comparison,'sleep') as sleep:
    with self.assertRaises(ValueError):comparison.execute(self.plan(),Path(tmp))
    self.assertEqual(1,send.call_count);sleep.assert_not_called()
    state=json.loads((Path(tmp)/'state.json').read_text());self.assertEqual('paused',state['state']);self.assertNotIn(str(failure),state['message'])
 def test_retry_deadline_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(backends,'render',side_effect=self.http_failure(503)) as send,patch.object(comparison,'sleep') as sleep:
   with self.assertRaises(ValueError):comparison.execute(self.plan(),Path(tmp),timeout=.01)
   self.assertEqual(1,send.call_count);sleep.assert_not_called()
 def test_completed_variant_survives_failure_positive(self):
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=[(audio.wav_bytes(b'\x00\x10'*2400),200)]*4+[self.http_failure(429)]) as send:
   out=Path(tmp)
   with self.assertRaises(ValueError):comparison.execute(self.plan(),out)
   self.assertEqual(5,send.call_count);self.assertTrue((out/'azure-clean.wav').exists());self.assertFalse((out/'azure-mistakes.wav').exists())
   page=player.page(out,'controlled');self.assertIn('src="/azure-clean.wav"',page);self.assertNotIn('src="/azure-mistakes.wav"',page);self.assertIn('allowance',page);self.assertNotIn('Complete Microsoft sign-in',page)
 def test_cli_exhaustion_is_human_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=urllib.error.URLError('private-sentinel')) as send,patch.object(comparison,'sleep') as sleep:
   resource=Path(tmp)/'resource.json';resource.write_text(json.dumps({'location':'eastus','sku':{'name':'F0'}}));output=Path(tmp)/'out';stdout=io.StringIO()
   with patch.object(sys,'argv',['compare','--resource',str(resource),'--out',str(output)]),contextlib.redirect_stdout(stdout):code=comparison.main()
   self.assertEqual(1,code);self.assertEqual(3,send.call_count);self.assertEqual(2,sleep.call_count)
   self.assertNotIn('private-sentinel',stdout.getvalue());self.assertNotIn('Traceback',stdout.getvalue());self.assertIn('retained',stdout.getvalue())
   dispatches=json.loads((output/'dispatches.json').read_text());self.assertEqual(3,len(dispatches));self.assertTrue(all(d['error_type']=='URLError' for d in dispatches));self.assertNotIn('private-sentinel',json.dumps(dispatches));self.assertFalse((output/'result.json').exists())
 def test_cli_cancel_retains_progress_negative(self):
  with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'AZURE_SPEECH_KEY':'constructed-key'}),patch.object(backends,'transport',side_effect=[(audio.wav_bytes(b'\x00\x10'*2400),200)]*2+[KeyboardInterrupt()]) as send,patch.object(comparison,'sleep') as sleep:
   resource=Path(tmp)/'resource.json';resource.write_text(json.dumps({'location':'eastus','sku':{'name':'F0'}}));out=Path(tmp)/'out';stdout=io.StringIO()
   with patch.object(sys,'argv',['compare','--resource',str(resource),'--out',str(out)]),contextlib.redirect_stdout(stdout):code=comparison.main()
   self.assertEqual(130,code);self.assertEqual(3,send.call_count);sleep.assert_not_called();self.assertEqual(2,len(list(out.glob('clean-u*.wav'))));self.assertIn('stopped',stdout.getvalue());self.assertNotIn('Traceback',stdout.getvalue())
   state=json.loads((out/'state.json').read_text());self.assertEqual(('paused',2),(state['state'],state['completed_pieces']));self.assertFalse((out/'result.json').exists())
 def test_player_progress_positive(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'state.json').write_text(json.dumps({'state':'retrying','message':'A temporary connection problem occurred. Retrying the current piece.','completed_pieces':2}))
   page=player.page(out,'controlled');self.assertIn('Retrying the current piece',page);self.assertIn('2 of 8 pieces saved',page);self.assertNotIn('Complete Microsoft sign-in',page);self.assertNotIn('disabled',page)

if __name__=='__main__':unittest.main(verbosity=2)
