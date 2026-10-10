"""Native Settings, persisted provider configuration and actual MLflow readback.
Remote protocol fixtures are explicit substitutes; no hosted model quality claim.
"""
import base64,copy,hashlib,json,os,socket,subprocess,time,unittest,uuid,urllib.request,urllib.error
from pathlib import Path
import test_iteration1 as foundation
import test_iteration2 as storage
from browser_probe import Browser
ROOT=foundation.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
class Iteration4Tests(unittest.TestCase):
 cleanup=classmethod(foundation.Iteration1Tests.cleanup.__func__)
 execute=classmethod(foundation.Iteration1Tests.execute.__func__)
 launch=classmethod(foundation.Iteration1Tests.launch.__func__)
 compose=classmethod(foundation.Iteration1Tests.compose.__func__)
 sql=classmethod(foundation.Iteration1Tests.sql.__func__)
 http=classmethod(foundation.Iteration1Tests.http.__func__)
 config=classmethod(foundation.Iteration1Tests.config.__func__)
 media=classmethod(foundation.Iteration1Tests.media.__func__)
 cli=storage.Iteration2Tests.cli
 good=storage.Iteration2Tests.good
 write=storage.Iteration2Tests.write
 linked=storage.Iteration2Tests.linked
 reserve=storage.Iteration2Tests.reserve
 upload=storage.Iteration2Tests.upload
 op=storage.Iteration2Tests.op
 @classmethod
 def setUpClass(cls):
  project=os.getenv('TANGERINE_TEST_PAUSE_PROJECT','');cls.preview_web=''
  if project:
   q=subprocess.run(['docker','ps','-q','--filter','label=com.docker.compose.project='+project,'--filter','label=com.docker.compose.service=web'],capture_output=True,text=True,check=True);cls.preview_web=q.stdout.strip()
   if '\n' in cls.preview_web:raise AssertionError('Ambiguous preview')
   if cls.preview_web:subprocess.run(['docker','stop',cls.preview_web],check=True,capture_output=True)
   cls.addClassCleanup(lambda:subprocess.run(['docker','start',cls.preview_web],check=True,capture_output=True) if cls.preview_web else None)
  foundation.Iteration1Tests.setUpClass.__func__(cls)
  sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
  cls.env.update(TANGERINE_LAB_IMAGE='tangerine-mlflow-upstream:3.17.0',TANGERINE_LAB_PORT=str(port))
  r=cls.launch('lab',timeout=240)
  if r.returncode:raise AssertionError(r.stdout)
 @classmethod
 def sdk(cls,action,packet):
  p=subprocess.run(['docker','compose','--env-file',str(cls.extract/'.env'),'--env-file',str(cls.extract/'data/config/runtime.env'),'-f',str(cls.extract/'deploy/local/compose.yaml'),'--profile','llm-lab','exec','-T','llm-lab','python','/tangerine/lab.py',action],input=json.dumps(packet),timeout=120,cwd=cls.extract,env=cls.env,text=True,capture_output=True)
  (cls.receipts/('sdk-'+uuid.uuid4().hex+'.log')).write_text(p.stdout+p.stderr)
  return p
 def browser(self):
  b=Browser(self.receipts/('browser-'+uuid.uuid4().hex));self.addCleanup(b.close);b.call('Page.navigate',{'url':'http://localhost:3000/settings'});b.wait('Your LLM connection');b.wait('chatgpt-plan-responses-v1');return b
 def capture(self,b,name):
  (self.receipts/(name+'.txt')).write_text(b.evaluate('document.body.innerText'))
  (self.receipts/(name+'.png')).write_bytes(base64.b64decode(b.call('Page.captureScreenshot',{'format':'png'})['data']))
 def cfg(self):
  code,raw,headers=self.http('/api/v1/configuration');self.assertEqual(code,200);v=json.loads(raw);return v['configuration'],{k.lower():v for k,v in headers.items()}.get('etag')
 def put(self,c,etag=None,key=None):
  c=copy.deepcopy(c)
  for k in ('workspace_id','configuration_sha256','provider_access_policy'):c.pop(k,None)
  headers={'Content-Type':'application/json','Origin':'http://localhost:3000','If-Match':etag or self.cfg()[1],'Idempotency-Key':key or str(uuid.uuid4())}
  req=urllib.request.Request('http://localhost:3000/api/v1/configuration',data=json.dumps(c).encode(),headers=headers,method='PUT')
  try:
   with urllib.request.urlopen(req,timeout=15) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_settings_initial_positive(self):
  b=self.browser();self.assertIn('No provider connections yet.',b.evaluate('document.body.innerText'));self.assertEqual(len(self.cfg()[0]['llm_profiles']),3);self.capture(b,'settings-initial')
 def test_settings_saved_positive(self):
  c,tag=self.cfg();c['feedback_language']='en';code,v=self.put(c,tag);self.assertEqual(code,200)
  b=self.browser();b.evaluate("document.querySelector('summary').click()");value=b.evaluate("document.querySelector('textarea').value");self.assertEqual(json.loads(value)['llm_profiles'],c['llm_profiles']);self.capture(b,'settings-saved')
 def test_settings_failure_negative(self):
  b=self.browser();self.compose('stop','api')
  try:
   b.evaluate("Array.from(document.querySelectorAll('button')).find(x=>x.innerText==='Refresh').click()");b.wait('Provider settings are unavailable. Saved content is retained.');self.capture(b,'settings-outage')
  finally:self.compose('start','api')
  for _ in range(60):
   if self.http('/api/v1/configuration')[0]==200:break
   time.sleep(.5)
  b.evaluate("Array.from(document.querySelectorAll('button')).find(x=>x.innerText==='Refresh').click()");b.wait('No provider connections yet.');
  for _ in range(100):
   if b.evaluate("document.querySelector('[role=alert]')?.innerText") is None:break
   time.sleep(.1)
  self.assertIsNone(b.evaluate("document.querySelector('[role=alert]')?.innerText"));self.capture(b,'settings-recovered')
 def test_settings_invalid_negative(self):
  b=self.browser();before=self.cfg()[0]['configuration_sha256'];b.evaluate("document.querySelector('summary').click()");b.evaluate("const a=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(a,'{}');a.dispatchEvent(new Event('input',{bubbles:true}));");b.evaluate("Array.from(document.querySelectorAll('button')).find(x=>x.innerText==='Save configuration').click()");b.wait('Settings were not saved.');self.assertEqual(self.cfg()[0]['configuration_sha256'],before);self.capture(b,'settings-rejected')
 def test_connection_metadata_positive(self):
  ident=str(uuid.uuid4());d={'id':str(uuid.uuid4()),'kind':'provider-connection','version':'2.0.0','scope':'local','nodes':[],'references':[],'head':{'id':'provider:'+ident,'expected_revision':None,'state':'saved'},'payload':dict(id=ident,provider='openai_chatgpt',client_id='oaiapp_test_owned',ext_agent_host_id='urn:uuid:'+str(uuid.uuid4()),subject='fixture-subject',account_label='Stored fixture registration',state='disconnected',scopes=[],credential_ref=None,expires_at=None,credits_after_plan_limit_disabled=None,models_asset_id=None,last_error_code=None,updated_at='2026-10-10T10:00:00Z')}
  self.good(self.write(d));b=self.browser();b.wait('Stored fixture registration');self.capture(b,'settings-metadata');
  # Keep immutable saved history, but remove the fixture head from live selection.
  self.sql("DELETE FROM entity_head WHERE id='provider:"+ident+"'")
 def test_configuration_local_positive(self):
  c,tag=self.cfg();p=c['llm_profiles'][0];p.update(provider='local_responses',endpoint='http://ollama:11434/v1/responses',model='test-owned-local',credential_ref='local-none',auth_method='local_none',billing_mode='local',stream=False);self.assertEqual(self.put(c,tag)[0],200);self.assertEqual(json.loads(self.http('/api/v1/health')[1])['provider_configuration'],'ready');self.assertEqual(self.cfg()[0]['llm_profiles'][0]['model'],'test-owned-local')
 def test_configuration_stale_negative(self):
  c,tag=self.cfg();self.assertEqual(self.put(c,tag)[0],200);before=self.cfg()[0]['configuration_sha256'];c['feedback_language']='ru';code,v=self.put(c,tag);self.assertEqual(code,412);self.assertEqual(v['code'],'REVISION_STALE');self.assertEqual(self.cfg()[0]['configuration_sha256'],before)
 def test_connection_unknown_negative(self):
  req=urllib.request.Request('http://localhost:3000/api/v1/provider-connections:action',data=json.dumps({'action':'select','connection_id':str(uuid.uuid4()),'credits_after_plan_limit_disabled':None}).encode(),headers={'Content-Type':'application/json','Origin':'http://localhost:3000'},method='POST')
  with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(req,timeout=15)
  self.assertEqual(e.exception.code,422)
 def packet(self,name):return json.loads((ROOT/'data/iteration4/native'/name).read_text())
 def export(self,name):
  packet=self.packet(name);p=self.sdk('sync',packet);self.assertEqual(p.returncode,0,p.stdout);out=json.loads(p.stdout);self.assertEqual(out['provider_calls'],0);self.assertEqual(json.loads(self.sdk('verify',out).stdout)['status'],'observed');self.actual_span(packet,out) if packet['trace_enabled'] else self.assertEqual(out['trace_exports'],[]);(self.receipts/(name+'-lab-export.json')).write_text(json.dumps(out,indent=2));return packet,out
 def join(self,packet):
  v=json.loads(packet['artifacts'][0]['body']);self.assertEqual(v['transport_attempt_count'],1)
  receipts=[d['payload'] for d in v['documents'] if d['kind']=='provider-receipt'];contexts=[d['payload'] for d in v['documents'] if d['kind']=='llm-context-snapshot'];bindings=[d['payload'] for d in v['documents'] if d['kind']=='effective-binding'];self.assertEqual(len(receipts),1);self.assertEqual(len(contexts),1);self.assertEqual(len(bindings),1)
  r=receipts[0];events=[json.loads(x) for x in (ROOT/'data/iteration4/native/dispatch-observations.jsonl').read_text().splitlines()];events=[x for x in events if x['request_id']==r['provider_request_id']];self.assertEqual(len(events),1);event=events[0]
  wire={a['asset_id']:a for a in v['wire_assets']};self.assertEqual(event['wire_request_sha256'],wire[r['wire_request_asset_id']]['sha256']);self.assertEqual(event['wire_response_sha256'],wire[r['wire_response_asset_id']]['sha256']);self.assertEqual(event['http_status'],r['http_status']);self.assertEqual(contexts[0]['receipt_id'],r['id']);self.assertEqual(r['binding_sha256'],bindings[0]['binding_sha256'])
  for a in v['wire_assets']:self.assertEqual(sha(a['body'].encode()),a['sha256'])
 def test_lab_transport_positive(self):
  packet,out=self.export('positive-diagnostic.json');self.join(packet)
 def test_lab_failed_call_positive(self):
  packet,out=self.export('negative-diagnostic.json');self.join(packet);v=json.loads(packet['artifacts'][0]['body']);r=next(d['payload'] for d in v['documents'] if d['kind']=='provider-receipt');self.assertEqual(r['http_status'],429);self.assertIsNone(r['cost_micro_usd'])
 def test_lab_missing_negative(self):
  packet,out=self.export('positive-diagnostic.json');out['artifacts'][0]['artifact']='native/never-created.json';self.assertEqual(json.loads(self.sdk('verify',out).stdout)['status'],'incomplete')
 def test_lab_mismatch_negative(self):
  packet,out=self.export('canary-diagnostic.json');self.assertNotIn('OWNED_PROVIDER_CREDENTIAL_CANARY',json.dumps(packet));self.assertNotEqual(out['artifacts'][0]['original_sha256'],out['artifacts'][0]['sha256']);out['artifacts'][0]['sha256']='0'*64;self.assertEqual(json.loads(self.sdk('verify',out).stdout)['status'],'incomplete')
 def catalogue(self):
  ident=str(uuid.uuid4());raw=json.dumps({'models':[{'slug':'fixture-alpha','display_name':'Fixture Alpha','visibility':'list'},{'slug':'fixture-hidden','display_name':'Hidden fixture','visibility':'hide'},{'slug':'fixture-beta','display_name':'Fixture Beta','visibility':'list'}]},separators=(',',':')).encode();a,req,payload=self.linked(raw)
  d={'id':str(uuid.uuid4()),'kind':'provider-connection','version':'2.0.0','scope':'local','nodes':[],'references':[{'pointer':'/models_asset_id','id':a['id'],'scope':a['id'],'kind':'asset-bytes','sha256':sha(raw),'relation':'provider-model-catalogue'}],'head':{'id':'provider:'+ident,'expected_revision':None,'state':'active'},'payload':dict(id=ident,provider='openai_chatgpt',client_id='oaiapp_owned_catalogue',ext_agent_host_id='urn:uuid:'+str(uuid.uuid4()),subject='fixture-subject',account_label='Catalogue fixture',state='connected_no_usage',scopes=['chatgpt.tokens.use.direct'],credential_ref=None,expires_at=None,credits_after_plan_limit_disabled=None,models_asset_id=a['id'],last_error_code=None,updated_at='2026-10-10T10:00:00Z')}
  self.good(self.write(d));self.addCleanup(lambda:self.sql("DELETE FROM entity_head WHERE id='provider:"+ident+"'"));return ident,a,raw
 def test_models_selected_positive(self):
  c=json.loads((ROOT/'services/api/internal/app/provider-default.json').read_text());self.assertEqual(self.put(c)[0],200);ident,a,raw=self.catalogue();b=self.browser();b.wait('Fixture Alpha');b.evaluate("const s=document.querySelector('select');s.value='fixture-beta';s.dispatchEvent(new Event('change',{bubbles:true}));");b.wait('Settings saved.');saved=self.cfg()[0];self.assertEqual(saved['llm_profiles'][0]['model'],'fixture-beta');self.assertEqual(saved['llm_profiles'][0]['credential_ref'],ident);self.assertEqual(saved['stage_profiles'],c['stage_profiles']);self.capture(b,'models-selected')
 def test_models_readback_positive(self):
  ident,a,raw=self.catalogue();code,body,_=self.http('/api/v1/prepare/assets/'+a['id']+'/bytes');self.assertEqual(code,200);self.assertEqual(body,raw);b=self.browser();b.wait('Fixture Beta');self.assertEqual(b.evaluate("Array.from(document.querySelector('select').options).map(x=>x.textContent)"),['Choose an available model','Fixture Alpha','Fixture Beta']);self.capture(b,'models-catalogue')
 def test_models_unlinked_negative(self):
  a,req,raw=self.linked(b'Unrelated saved private bytes');self.assertEqual(self.http('/api/v1/prepare/assets/'+a['id']+'/bytes')[0],404)
 def test_models_unknown_negative(self):
  self.assertEqual(self.http('/api/v1/prepare/assets/'+str(uuid.uuid4())+'/bytes')[0],404);c,tag=self.cfg();before=c['configuration_sha256'];c['llm_profile']='absent-profile';code,v=self.put(c,tag);self.assertEqual(code,422);self.assertEqual(v['code'],'SCHEMA_INVALID');self.assertEqual(self.cfg()[0]['configuration_sha256'],before)

 def actual_span(self,packet,out):
  self.assertTrue(packet['trace_enabled']);self.assertEqual(len(out['trace_exports']),1);row=out['trace_exports'][0];self.assertEqual(row['state'],'exported')
  code="import sqlite3,json;db=sqlite3.connect('/lab/mlflow.db');r=db.execute('SELECT span_id,name,content FROM spans WHERE span_id=?',(\""+row['span_id']+"\",)).fetchone();print(json.dumps(r))"
  p=subprocess.run(['docker','compose','--env-file',str(self.extract/'.env'),'--env-file',str(self.extract/'data/config/runtime.env'),'-f',str(self.extract/'deploy/local/compose.yaml'),'exec','-T','llm-lab','python','-c',code],cwd=self.extract,env=self.env,text=True,capture_output=True,timeout=30);self.assertEqual(p.returncode,0,p.stderr);observed=json.loads(p.stdout);self.assertEqual(observed[0],row['span_id']);content=json.loads(observed[2]);self.assertEqual(base64.b64decode(content['trace_id']).hex(),row['trace_id']);self.assertEqual(json.loads(content['attributes']['receipt_id']),row['receipt_id']);(self.receipts/('actual-span-'+row['span_id']+'.json')).write_text(p.stdout)
