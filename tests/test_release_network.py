"""Exact bytes through the test-owned local-model/dependency bridge framing."""
import json,socket,threading,unittest
from release_network import Bridge,read_job

class BridgeFramingTests(unittest.TestCase):
 def frame(self,metadata,payload):
  return b'HTTP/1.1 101 Switching Protocols\r\nX-Tangerine-Target: '+json.dumps(metadata).encode().hex().encode()+b'\r\n\r\n'+payload
 def read(self,data):
  left,right=socket.socketpair()
  def send():
   with right:
    for i in range(0,len(data),1031):right.sendall(data[i:i+1031])
  worker=threading.Thread(target=send);worker.start()
  try:
   with left:return read_job(left)
  finally:worker.join()
 def test_large_request_prefix_positive(self):
  # Independent literal payload includes non-ASCII UTF-8 and binary header edges.
  body=('The café opens tomorrow. '*12000).encode();request=b'POST /v1/responses HTTP/1.1\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body
  meta={'kind':'local_model','host':'127.0.0.1','port':11434,'prefix_length':len(request)}
  actual,raw=self.read(self.frame(meta,request));self.assertEqual(actual,meta);self.assertEqual(raw,request)
 def test_dependency_initial_tls_positive(self):
  # CONNECT has no prefix; any bytes already after the framing stay intact.
  expected=b'\x16\x03\x01\x00\x04TLS!';meta={'kind':'dependency','prefix_length':0}
  actual,raw=self.read(self.frame(meta,expected));self.assertEqual(actual,meta);self.assertEqual(raw,expected)
 def test_incomplete_prefix_negative(self):
  with self.assertRaisesRegex(OSError,'bridge prefix incomplete'):self.read(self.frame({'prefix_length':99},b'only-five'))
 def test_closed_header_negative(self):
  with self.assertRaisesRegex(OSError,'bridge closed'):self.read(b'HTTP/1.1 101')
 def test_no_job_negative(self):
  self.assertEqual(self.read(b'HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n'),(None,b''))
 def connect(self,path):
  handler=Bridge.__new__(Bridge);handler.path=path;events=[]
  handler.send_error=lambda code:events.append(('rejected',code))
  handler.transfer=lambda target:events.append(('tunnel',target))
  handler.do_CONNECT();return events
 def test_authorized_gemini_tunnel_positive(self):
  self.assertEqual(self.connect('generativelanguage.googleapis.com:443'),[('tunnel',{'host':'generativelanguage.googleapis.com','port':443,'kind':'dependency'})])
 def test_authorized_openai_tunnel_positive(self):
  for host in ('auth.openai.com','api.openai.com'):
   self.assertEqual(self.connect(host+':443'),[('tunnel',{'host':host,'port':443,'kind':'dependency'})])
 def test_unapproved_host_or_port_negative(self):
  self.assertEqual(self.connect('unapproved.example:443'),[('rejected',403)])
  self.assertEqual(self.connect('api.openai.com:80'),[('rejected',403)])
  self.assertEqual(self.connect('api.openai.com.unapproved.example:443'),[('rejected',403)])
  self.assertEqual(self.connect('generativelanguage.googleapis.com:80'),[('rejected',403)])

if __name__=='__main__':unittest.main()
