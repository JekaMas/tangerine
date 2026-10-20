"""Real private HTTP server and actual subprocess groups; no subprocess replacement."""
import json,os,pathlib,sys,time,threading,unittest,urllib.request,urllib.error,socket
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
import server
class SpeechServer(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.environment=patch.dict(os.environ,{'SPEECH_INTERNAL_TOKEN':'owned-token','TANGERINE_MODEL_DIR':'/models'});cls.environment.start()
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);cls.url='http://127.0.0.1:'+str(cls.http.server_port);cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join();cls.environment.stop()
 def request(self,path,packet=None,token='owned-token'):
  data=None if packet is None else json.dumps(packet).encode();r=urllib.request.Request(self.url+path,data=data,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(r,timeout=15) as response:return response.status,json.load(response)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def slow_packet(self):
  return {'timeout_seconds':1,'profile':{'id':'qwen-custom-v1','adapter_version':'qwen-custom-v1','provider':'local_qwen3_tts','model':'Qwen3-TTS-12Hz-0.6B-CustomVoice','billing_mode':'local','voices':[{'id':'Ryan','locale':'en-US'}]},'turn':{'voice_id':'Ryan','locale':'en-US','operations':[{'kind':'text','text':'The café open tomorrow.'}]}}
 def test_ready_positive(self):self.assertEqual(self.request('/health/ready'),(200,{'status':'ready'}))
 def test_models_positive(self):
  status,data=self.request('/internal/v1/models');self.assertEqual(status,200);self.assertEqual(len(data['profiles']),5);self.assertTrue(data['espeak_ng']);controlled=next(p for p in data['profiles'] if p['profile_id']=='kokoro-controlled-v1');self.assertEqual(controlled['status'],'ready');self.assertEqual(controlled['praat_version'],'6.1.38')
 def test_unauthorized_negative(self):self.assertEqual(self.request('/internal/v1/models',token='wrong'),(403,{'error':'internal_access_required'}))
 def test_malformed_negative(self):self.assertEqual(self.request('/internal/v1/plan',{}),(422,{'error':'SYNTHESIS_FAILED'}))
 def watch(self):
  processes=[];native=server.subprocess.Popen
  def observe(*args,**kwargs):
   p=native(*args,**kwargs);processes.append(p);return p
  return processes,patch.object(server.subprocess,'Popen',side_effect=observe)
 def test_worker_success_positive(self):
  processes,observation=self.watch()
  with observation:status,data=self.request('/internal/v1/plan',{'profile':{'provider':'local_espeak_ng','billing_mode':'local','voices':[{'id':'en-us','locale':'en-US'}]},'plan':{'turns':[{'voice_id':'en-us','locale':'en-US','operations':[{'kind':'text','text':'Literal café.'}],'gap_after_ms':0}]}})
  self.assertEqual(status,200);self.assertEqual(data['pieces'][0]['operations'][0]['text'],'Literal café.');self.assertEqual(len(processes),1);self.assertEqual(processes[0].wait(timeout=5),0)
 def test_worker_failure_positive(self):
  processes,observation=self.watch()
  with observation:status,data=self.request('/internal/v1/piece',{'profile':{'provider':'elevenlabs','billing_mode':'metered'},'turn':{}})
  self.assertEqual((status,data),(422,{'error':'PAID_USE_FORBIDDEN'}));self.assertEqual(len(processes),1);self.assertNotEqual(processes[0].wait(timeout=5),0)
 def test_deadline_negative(self):
  processes,observation=self.watch()
  with observation:status,data=self.request('/internal/v1/piece',self.slow_packet())
  self.assertEqual((status,data),(504,{'error':'SPEECH_TIMEOUT'}));self.assertEqual(len(processes),1);self.assertEqual(processes[0].wait(timeout=5),-9)
 def test_disconnect_negative(self):
  processes,observation=self.watch();packet=self.slow_packet();packet['timeout_seconds']=260;data=json.dumps(packet).encode()
  with observation:
   connection=socket.create_connection(('127.0.0.1',self.http.server_port));connection.sendall(b'POST /internal/v1/piece HTTP/1.1\r\nHost: local\r\nAuthorization: Bearer owned-token\r\nContent-Type: application/json\r\nContent-Length: '+str(len(data)).encode()+b'\r\n\r\n'+data)
   for n in range(100):
    if processes:break
    time.sleep(.01)
   self.assertEqual(len(processes),1);connection.close();self.assertEqual(processes[0].wait(timeout=5),-9)
if __name__=='__main__':unittest.main()
