"""Constructed Gemini transport boundary; zero network/provider/model calls."""
import io,json,pathlib,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
import diagnostic_models as models
class AuditoryProtocolTests(unittest.TestCase):
 def profile(self,mode='free_tier'):return dict(provider='gemini_interactions',model='configured-available-model',billing_mode=mode,max_output_tokens=512)
 def result(self,status='completed'):
  return dict(status=status,steps=[dict(type='model_output',content=[dict(type='text',text=json.dumps(dict(findings=[dict(unit_id='u1',feature='speech_realization',status='uncertain',description='Cannot establish realization.',reason='Insufficient detail.')],summary='Uncertain.')))])])
 def invoke(self,body,status=200):
  received=[];capture=[]
  class Response(io.BytesIO):pass
  response=Response(body);response.status=status
  class Opener:
   def open(self,request,timeout):received.append(request);return response
  self.handlers=[]
  with patch.dict(models.os.environ,{'GEMINI_API_KEY':'test-owned-canary'}),patch.object(models.urllib.request,'build_opener',side_effect=lambda *handlers:self.handlers.extend(handlers) or Opener()):
   result=models.auditory(self.profile(),'Trusted prompt',{'units':['u1'],'features':['speech_realization']},[b'actual-fixture-audio',b'reference-fixture-audio'],capture=capture.append)
  return result,received,capture
 def test_completed_request_positive(self):
  result,received,capture=self.invoke(json.dumps(self.result()).encode());self.assertEqual(len(received),1);request=received[0];self.assertEqual(request.full_url,'https://generativelanguage.googleapis.com/v1beta/interactions');body=json.loads(request.data);self.assertEqual({k:body[k] for k in ['store','stream','background','tools']},dict(store=False,stream=False,background=False,tools=[]));self.assertEqual(body['generation_config'],dict(max_output_tokens=512));self.assertEqual(result['output']['findings'][0]['status'],'uncertain');self.assertEqual(capture[-1]['http_status'],200);self.assertNotIn('test-owned-canary',json.dumps(capture))
 def test_incomplete_status_negative(self):
  result,received,capture=self.invoke(json.dumps(self.result('in_progress')).encode());self.assertEqual(result['error'],'DIAGNOSTIC_PROVIDER_FAILED');self.assertEqual(result['wire']['response']['status'],'in_progress');self.assertEqual(len(received),1)
 def test_non_json_response_negative(self):
  result,_,capture=self.invoke(b'upstream unavailable',503);self.assertEqual(result['error'],'DIAGNOSTIC_PROVIDER_FAILED');self.assertEqual(result['wire']['response_text'],'upstream unavailable');self.assertEqual(capture[-1]['http_status'],503)
 def test_invalid_model_text_retained_negative(self):
  body=self.result();body['steps'][0]['content'][0]['text']='No structured findings were supplied.';result,_,capture=self.invoke(json.dumps(body).encode());self.assertEqual(result['error'],'DIAGNOSTIC_OUTPUT_INVALID');self.assertEqual(capture[-1]['response'],body);self.assertEqual(result['wire']['response'],body)
 def test_paid_before_transport_negative(self):
  with patch.object(models.urllib.request,'build_opener') as network,self.assertRaisesRegex(ValueError,'PAID_USE_FORBIDDEN'):models.auditory(self.profile('metered'),'prompt',{},[b'audio'])
  network.assert_not_called()
 def test_missing_key_negative(self):
  with patch.dict(models.os.environ,{},clear=True),patch.object(models.urllib.request,'build_opener') as network,self.assertRaisesRegex(ValueError,'MISSING_CREDENTIALS'):models.auditory(self.profile(),'prompt',{},[b'audio'])
  network.assert_not_called()
 def test_configured_proxy_positive(self):
  with patch.object(models.urllib.request,'getproxies',return_value={'https':'http://test-owned-proxy.invalid:3128'}):
   result,received,capture=self.invoke(json.dumps(self.result()).encode())
  handler=next(h for h in self.handlers if isinstance(h,models.urllib.request.ProxyHandler))
  self.assertEqual(handler.proxies,{'https':'http://test-owned-proxy.invalid:3128'});self.assertEqual(len(received),1);self.assertEqual(result['output']['findings'][0]['status'],'uncertain');self.assertNotIn('test-owned-proxy.invalid',json.dumps(capture))
 def test_redirect_credential_negative(self):
  _,received,_=self.invoke(json.dumps(self.result()).encode())
  handler=next(h for h in self.handlers if isinstance(h,models.urllib.request.HTTPRedirectHandler))
  self.assertIsNone(handler.redirect_request(received[0],None,302,'Redirected',{},'https://unapproved.example/receive-key'))
if __name__=='__main__':unittest.main()
