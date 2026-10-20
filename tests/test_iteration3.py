"""Native MLflow registry, PostgreSQL/MinIO activation and export recovery.
Constructed diagnostics are not LLM/provider observations. Actual SDK/server,
immutable native storage and independent artifact byte readbacks are exercised.
"""
import socket,base64,hashlib,json,os,shutil,subprocess,tempfile,time,unittest,uuid,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
class Iteration3Tests(unittest.TestCase):
 @classmethod
 def call(cls,args,input=None,ok=True):
  p=subprocess.run(args,cwd=cls.root,env=cls.env,input=input,text=True,capture_output=True,timeout=240)
  if ok and p.returncode:raise AssertionError('native command failed: '+p.stdout+p.stderr)
  return p
 @classmethod
 def compose(cls,*args,input=None,ok=True):return cls.call(['docker','compose','--env-file',str(cls.root/'.env'),'--env-file',str(cls.root/'data/config/runtime.env'),'-f',str(cls.root/'deploy/local/compose.yaml'),'--profile','llm-lab',*args],input,ok)
 @classmethod
 def sdk(cls,action,packet=None,ok=True):return cls.compose('exec','-T','llm-lab','python','/tangerine/lab.py',action,input=json.dumps(packet,ensure_ascii=False) if packet is not None else None,ok=ok)
 @classmethod
 def native(cls,packet,ok=True):
  return cls.compose('run','--rm','--no-deps','-T','api','lab',input=json.dumps(packet,ensure_ascii=False),ok=ok)
 @classmethod
 def setup(cls):
  (ROOT/'data/iteration3').mkdir(parents=True,exist_ok=True)
  cls.project='tangerine-i3-'+uuid.uuid4().hex[:10];cls.tmp=tempfile.TemporaryDirectory(prefix='stack-',dir=ROOT/'data/iteration3');cls.root=Path(cls.tmp.name)
  for name in ['scripts','deploy/local','services/api','services/speech','specification/v2']:
   shutil.copytree(ROOT/name,cls.root/name)
  shutil.copyfile(ROOT/'.env.example',cls.root/'.env');(cls.root/'data/config').mkdir(parents=True)
  with socket.socket() as listener:
   listener.bind(('127.0.0.1',0));cls.lab_port=str(listener.getsockname()[1])
  cls.env={**os.environ,'COMPOSE_PROJECT_NAME':cls.project,'TANGERINE_LAB_IMAGE':'tangerine-mlflow-upstream:3.17.0','TANGERINE_LAB_PORT':cls.lab_port}
  image=json.loads(cls.call(['docker','image','inspect','tangerine-mlflow-upstream:3.17.0']).stdout)[0]
  assert image['Architecture']=='arm64' and image['Id']=='sha256:21d98f3ca5b8a7e229bb4e11df7cc87306ecb5e5a90af231e009e01d8b7525ad','native fixture image must match the verified official arm64 manifest configuration'
  host_os=cls.call(['docker','version','--format','{{.Client.Os}}']).stdout.strip();host_arch=cls.call(['docker','version','--format','{{.Client.Arch}}']).stdout.strip()
  cls.call(['docker','build','-f',str(ROOT/'services/api/Dockerfile'),'-t',cls.project+'-api:local',str(ROOT)])
  cls.call(['docker','build','-f',str(ROOT/'deploy/local/minio.Dockerfile'),'-t',cls.project+'-minio:local',str(ROOT)])
  cls.call(['docker','run','--rm','--user',str(os.getuid())+':'+str(os.getgid()),'-v',str(cls.root/'.env')+':/operator.env:ro','-v',str(cls.root/'data/config')+':/runtime','-e','TANGERINE_OPERATOR_FILE=/operator.env','-e','TANGERINE_RUNTIME_DIR=/runtime',cls.project+'-api:local','configure'])
  cls.compose('up','-d','--no-build','--wait','postgres','minio')
  cls.compose('run','--rm','--no-deps','-T','initialize')
  cls.call(['sh','scripts/tangerine','lab'])
  cls.receipts=ROOT/'data/iteration3/native';cls.receipts.mkdir(exist_ok=True)
  cls.builtin=json.loads(cls.sdk('export-command-placeholder',ok=False).stdout or '{}') if False else json.loads(cls.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input='{"action":"builtins"}').stdout)
 @classmethod
 def setUpClass(cls):
  try:cls.setup()
  except BaseException:
   cls.cleanup();raise
  cls.addClassCleanup(cls.cleanup)
 @classmethod
 def cleanup(cls):
  if hasattr(cls,'root') and (cls.root/'data/config/runtime.env').exists():
   try:
    if hasattr(cls,'receipts'):
     p=cls.compose('exec','-T','llm-lab','python','/tangerine/lab.py','snapshot','/lab/retained-native.db',ok=False)
     if p.returncode==0:
      cid=cls.compose('ps','-q','llm-lab').stdout.strip();cls.call(['docker','cp',cid+':/lab/retained-native.db',str(cls.receipts/'actual-mlflow.db')]);cls.call(['docker','cp',cid+':/lab/artifacts',str(cls.receipts/'actual-artifacts')])
    cls.compose('down','-v','--remove-orphans',ok=False)
   except Exception:pass
  if hasattr(cls,'tmp'):cls.tmp.cleanup()
 def good(self,p):self.assertEqual(p.returncode,0,p.stdout+p.stderr);return json.loads(p.stdout)
 def active(self):return self.good(self.native({'action':'active'}))
 def activate(self,b):
  c=self.good(self.sdk('activation-packet',b));return self.good(self.native(c))
 def selection(self):
  return {'bindings':[{'stage':b['stage'],'phase':b['phase'],'prompt_name':'tangerine-'+b['prompt_id'],'prompt_version':1,'context_name':'tangerine-context-'+b['prompt_id'],'context_version':1} for b in self.builtin['bindings']]}
 def export(self,s):
  rows=self.good(self.sdk('export',s));b={**self.builtin,'id':str(uuid.uuid4()),'origin':'registry_export','bindings':rows}
  return self.good(self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'seal','bundle':b})))
 def packet(self,body=None,capture=True):
  body=json.dumps(body or {'origin':'constructed_native_tooling_fixture','planned_cases':['positive','negative'],'provider_calls':0},ensure_ascii=False,separators=(',',':'))
  return {'operation':str(uuid.uuid4()),'origin':'constructed_native_tooling_fixture','capture':capture,'artifacts':[{'name':'cases.json','body':body,'sha256':sha(body.encode())}]}
 def test_lab_start_positive(self):
  version=self.good(self.compose('exec','-T','llm-lab','python','-c','import mlflow,json;print(json.dumps(mlflow.__version__))'))
  self.assertEqual(version,'3.17.0')
  with urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:'+self.lab_port+'/health',timeout=10) as r:self.assertEqual(r.status,200)
  services=self.compose('config','--services').stdout.splitlines();self.assertIn('llm-lab',services)
  from browser_probe import Browser
  browser=Browser(self.root/'lab-browser',initial_url='http://127.0.0.1:'+self.lab_port+'/')
  try:
   browser.wait('Experiments')
   href=browser.evaluate("Array.from(document.querySelectorAll('a')).find(a=>a.innerText.trim()==='Prompts')?.href");self.assertTrue(href)
   browser.call('Page.navigate',{'url':href});browser.wait('tangerine-adjudication-v1');text=browser.evaluate('document.body.innerText');self.assertIn('tangerine-adjudication-v1',text)
   (self.receipts/'actual-lab-browser.txt').write_text(text)
   (self.receipts/'actual-lab-browser.png').write_bytes(base64.b64decode(browser.call('Page.captureScreenshot',{'format':'png'})['data']))
  finally:browser.close()
 def test_lab_restart_positive(self):
  first=self.good(self.sdk('seed'));self.call(['sh','scripts/tangerine','lab','stop']);network=self.call(['docker','network','ls','-q','--filter','label=com.docker.compose.project='+self.project,'--filter','label=com.docker.compose.network=egress']).stdout.strip();self.assertTrue(network);self.call(['docker','network','rm',network]);self.call(['sh','scripts/tangerine','lab']);second=self.good(self.sdk('seed'));self.assertEqual(first,second);self.assertEqual(len(first),18)
 def test_lab_isolation_negative(self):
  self.call(['sh','scripts/tangerine','lab','stop']);b=self.active();self.assertEqual(len(b['bindings']),9);self.compose('run','--rm','--no-deps','-T','api','initialize');self.call(['sh','scripts/tangerine','lab'])
 def test_lab_host_denied_negative(self):
  req=urllib.request.Request('http://127.0.0.1:'+self.lab_port+'/',headers={'Host':'evil.example'})
  with self.assertRaises(urllib.error.HTTPError) as c:urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=10)
  self.assertEqual(c.exception.code,403)
 def test_registry_exact_positive(self):
  b=self.export(self.selection());self.assertEqual(len(b['bindings']),9);self.assertTrue(all(v['registry_version']==1 and v['context_registry_version']==1 for v in b['bindings']));self.assertEqual(b['bindings'][4]['template'],self.builtin['bindings'][4]['template'])
 def test_registry_edit_freeze_positive(self):
  b=self.export(self.selection());saved=self.activate(b)
  script="import mlflow,json; mlflow.set_tracking_uri('http://llm-lab:5000');p=mlflow.genai.register_prompt('tangerine-map-v1','New literal mapping prompt.');print(json.dumps(int(p.version)))"
  v=self.good(self.compose('exec','-T','llm-lab','python','-c',script));self.assertEqual(v,2);self.assertEqual(self.active()['bundle_sha256'],b['bundle_sha256']);s=self.selection();s['bindings'][4]['prompt_version']=2;new=self.export(s);self.assertEqual(new['bindings'][4]['template'],'New literal mapping prompt.');self.assertNotEqual(new['bundle_sha256'],b['bundle_sha256'])
 def test_registry_missing_negative(self):
  s=self.selection();s['bindings'][0]['prompt_version']=987654;self.assertNotEqual(self.sdk('export',s,ok=False).returncode,0)
 def test_registry_alias_negative(self):
  s=self.selection();s['bindings'][0]['prompt_version']='production';self.assertNotEqual(self.sdk('export',s,ok=False).returncode,0)
 def test_activation_revert_positive(self):
  a=self.export(self.selection());self.activate(a);b=self.export(self.selection());b['bindings'][0]['template']+=' changed';b['bindings'][0]['prompt_sha256']=sha(b['bindings'][0]['template'].encode());b['origin']='local_import';b=self.good(self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'seal','bundle':b})));self.activate(b);self.assertEqual(self.active()['bundle_sha256'],b['bundle_sha256']);self.activate(a);self.assertEqual(self.active()['bundle_sha256'],a['bundle_sha256'])
 def test_activation_readback_positive(self):
  b=self.export(self.selection());saved=self.activate(b);old=self.good(self.native({'action':'read','id':b['id']}));self.assertEqual(old['payload'],b);self.assertEqual(self.active()['id'],b['id']);self.assertEqual(saved[0]['kind'],'prompt-bundle')
 def test_activation_invalid_negative(self):
  old=self.active();b=self.export(self.selection());b['bindings'].pop();p=self.native({'action':'activate','bundle':b},ok=False);self.assertNotEqual(p.returncode,0);self.assertEqual(self.active()['bundle_sha256'],old['bundle_sha256'])
  duplicated=self.compose('run','--rm','--no-deps','-T','api','lab',input='{"action":"activate","action":"active"}',ok=False);self.assertNotEqual(duplicated.returncode,0);self.assertEqual(self.active()['bundle_sha256'],old['bundle_sha256'])
 def test_activation_corrupt_negative(self):
  old=self.active();b=self.export(self.selection());b['bindings'][0]['template']+=' unsealed';self.assertNotEqual(self.native({'action':'activate','bundle':b},ok=False).returncode,0);self.assertEqual(self.active()['bundle_sha256'],old['bundle_sha256'])
 def test_export_native_positive(self):
  p=self.packet();asset=self.good(self.native({'action':'diagnostic-save','payload':p}));self.assertEqual(asset['state'],'linked');read=self.good(self.native({'action':'diagnostic-read','id':asset['id']}));self.assertEqual(read,p);export=self.good(self.sdk('sync',read));self.assertEqual(export['provider_calls'],0);self.assertEqual(self.good(self.sdk('sync',read))['run'],export['run']);self.assertEqual(self.good(self.sdk('verify',export))['status'],'observed');(self.receipts/'actual-mlflow-export.json').write_text(json.dumps(export,indent=2));(self.receipts/'native-diagnostic.json').write_text(json.dumps({'asset':asset,'packet':p},indent=2))
 def test_export_privacy_positive(self):
  p=self.packet({'answer':'legitimate answer','Authorization':'CANARY','url':'https://example/?key=CANARY','personal_metadata':{'name':'private'}});p['secrets']=['CANARY'];export=self.good(self.sdk('sync',p));a=export['artifacts'][0];self.assertNotEqual(a['sha256'],a['original_sha256']);self.assertTrue(a['redaction_reasons']);self.assertEqual(self.good(self.sdk('verify',export))['status'],'observed')
 def test_export_outage_recovery_negative(self):
  p=self.packet();a=self.good(self.native({'action':'diagnostic-save','payload':p}));self.call(['sh','scripts/tangerine','lab','stop']);self.assertNotEqual(self.sdk('sync',p,ok=False).returncode,0);self.assertEqual(self.good(self.native({'action':'diagnostic-read','id':a['id']})),p);self.call(['sh','scripts/tangerine','lab']);e=self.good(self.sdk('sync',self.good(self.native({'action':'diagnostic-read','id':a['id']}))));self.assertEqual(e['provider_calls'],0);self.assertEqual(self.good(self.sdk('verify',e))['status'],'observed')
 def test_export_hash_negative(self):
  malformed=self.packet({'answer':'private'});malformed['capture']='false';self.assertNotEqual(self.sdk('sync',malformed,ok=False).returncode,0)
  p=self.packet();p['artifacts'][0]['sha256']='0'*64;self.assertNotEqual(self.sdk('sync',p,ok=False).returncode,0)
  first=self.packet();e=self.good(self.sdk('sync',first));second=self.packet();second['run']=e['run'];self.assertNotEqual(self.sdk('sync',second,ok=False).returncode,0);self.assertEqual(self.good(self.sdk('verify',e))['status'],'observed')
  upper=self.packet();upper['operation']=upper['operation'].upper();a=self.good(self.sdk('sync',upper));self.assertEqual(self.good(self.sdk('sync',upper))['run'],a['run'])
 def test_verify_exact_positive(self):
  e=self.good(self.sdk('sync',self.packet()));self.assertEqual(self.good(self.sdk('verify',e)),{'status':'observed','discrepancies':[],'provider_calls':0})
 def test_verify_zero_capture_positive(self):
  e=self.good(self.sdk('sync',self.packet({'answer':'private'},capture=False)));self.assertTrue(e['artifacts'][0]['redaction_reasons']);self.assertEqual(self.good(self.sdk('verify',e))['status'],'observed')
 def test_verify_missing_negative(self):
  e=self.good(self.sdk('sync',self.packet()));e['artifacts'][0]['artifact']='native/nonexistent.json';self.assertEqual(self.good(self.sdk('verify',e))['status'],'incomplete')
 def test_verify_mismatch_negative(self):
  e=self.good(self.sdk('sync',self.packet()));e['artifacts'][0]['sha256']='0'*64;self.assertEqual(self.good(self.sdk('verify',e))['status'],'incomplete')
 def test_snapshot_consistent_positive(self):
  self.good(self.sdk('sync',self.packet()));r=self.good(self.compose('exec','-T','llm-lab','python','/tangerine/lab.py','snapshot','/lab/native-backup.db'));self.assertEqual(r['provider_calls'],0)
  p=self.compose('exec','-T','llm-lab','python','-c',"import sqlite3; d=sqlite3.connect('/lab/native-backup.db');print(d.execute('PRAGMA integrity_check').fetchone()[0])");self.assertEqual(p.stdout.strip(),'ok')
 def test_snapshot_persistent_positive(self):
  first=self.good(self.sdk('seed'));self.compose('restart','llm-lab');self.compose('up','-d','--wait','llm-lab');self.assertEqual(self.good(self.sdk('seed')),first)
 def test_snapshot_failure_negative(self):
  p=self.compose('exec','-T','llm-lab','python','/tangerine/lab.py','snapshot','/nonexistent/db',ok=False);self.assertNotEqual(p.returncode,0);self.assertEqual(len(self.good(self.sdk('seed'))),18)
 def test_snapshot_no_host_network_negative(self):
  p=self.compose('ps','--format','json','llm-lab');v=json.loads(p.stdout);ports=v['Publishers'];self.assertTrue(all(x['URL']=='127.0.0.1' for x in ports if x['PublishedPort']>0));self.assertNotIn('web',self.compose('ps','--services','--status','running').stdout.splitlines())
 def test_trace_ingest_positive(self):
  script="""import base64,json,urllib.request,mlflow,uuid,subprocess,time
mlflow.set_tracking_uri('http://llm-lab:5000')
eid=mlflow.create_experiment('native-trace-'+uuid.uuid4().hex)
trace=uuid.uuid4().hex; span=uuid.uuid4().hex[:16]
p={'action':'otlp','trace':{'Trace':trace,'Span':span,'Name':'native-tooling-fixture','Start':'2026-10-10T12:00:00Z','End':'2026-10-10T12:00:01Z','Attributes':{'stage':'tooling','receipt_id':'constructed-no-provider-call'}}}
r=subprocess.run(['/tangerine/native','lab-json'],input=json.dumps(p).encode(),capture_output=True,check=True)
b=base64.b64decode(json.loads(r.stdout))
req=urllib.request.Request('http://llm-lab:5000/v1/traces',data=b,headers={'Content-Type':'application/x-protobuf','x-mlflow-experiment-id':eid})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req) as res: status=res.status
rows=mlflow.search_traces(experiment_ids=[eid],return_type='list')
import sqlite3
with sqlite3.connect('/lab/mlflow.db') as db: observed=db.execute('SELECT trace_id,span_id,name,start_time_unix_nano,end_time_unix_nano,content FROM spans WHERE span_id=?',(span,)).fetchone()
assert observed is not None and observed[1]==span and observed[2]=='native-tooling-fixture'
assert observed[3]==1791633600000000000 and observed[4]==1791633601000000000
content=json.loads(observed[5]);assert base64.b64decode(content['trace_id']).hex()==trace
assert json.loads(content['attributes']['stage'])=='tooling'
assert json.loads(content['attributes']['receipt_id'])=='constructed-no-provider-call'
print(json.dumps({'status':status,'traces':len(rows),'provider_calls':0,'requested':p,'otlp_base64':base64.b64encode(b).decode(),'native_sha256':__import__('hashlib').sha256(b).hexdigest(),'server_span':dict(trace_id=observed[0],span_id=observed[1],name=observed[2],start_ns=observed[3],end_ns=observed[4],content=content)}))
"""
  r=self.good(self.compose('exec','-T','llm-lab','python','-c',script));self.assertEqual({k:r[k] for k in ['status','traces','provider_calls']},{'status':200,'traces':1,'provider_calls':0});(self.receipts/'actual-otlp-trace.json').write_text(json.dumps(r,indent=2))
 def test_trace_disabled_positive(self):
  native=self.packet({'status':'disabled','dispatches':[],'zero_call_reason':'diagnostic metadata only'});e=self.good(self.sdk('sync',native));self.assertEqual(e['provider_calls'],0);self.assertEqual(self.good(self.sdk('verify',e))['status'],'observed')
 def test_trace_malformed_negative(self):
  req=urllib.request.Request('http://127.0.0.1:'+self.lab_port+'/v1/traces',data=b'not protobuf',headers={'Content-Type':'application/x-protobuf','x-mlflow-experiment-id':'0'})
  with self.assertRaises(urllib.error.HTTPError) as c:urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=10)
  self.assertGreaterEqual(c.exception.code,400)
 def test_trace_invalid_context_negative(self):
  p={'action':'otlp','trace':{'Trace':'invalid','Span':'invalid','Name':'invalid'}};r=self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps(p),ok=False);self.assertNotEqual(r.returncode,0)
 def retain(self,body):
  a=self.good(self.native({'action':'diagnostic-save','key':str(uuid.uuid4()),'payload':body}));return {'asset_id':a['id'],'sha256':a['sha256']}
 def development(self,mutate_inventory=None):
  revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
  inv=self.good(self.compose('exec','-T','llm-lab','python','/tangerine/lab.py','inventory',revision))
  self.assertEqual(len(inv['entries']),25);self.assertEqual(sum(x['implementation_state']=='planned' for x in inv['entries']),14);self.assertEqual(sum(x['implementation_state']=='implemented' for x in inv['entries']),11)
  self.assertTrue({'services/api/internal/app/provider_configuration.go','services/api/internal/app/provider_connections.go','services/api/internal/app/provider-default.json','services/api/internal/app/provider_command.go'}.issubset({d['path'] for d in inv['dependencies']}))
  canonical=next(x for x in inv['entries'] if x['id']=='generation.canonical');self.assertEqual(canonical['implementation_state'],'implemented');self.assertEqual(canonical['owner_symbols'],['Server.PrepareCanonical']);self.assertEqual(canonical['owner_paths'],['services/api/internal/app/preparation.go','services/api/internal/app/provider_inference.go','services/api/internal/app/preparation_content.go','services/api/internal/app/mutation_diagnostics.go']);self.assertTrue({'services/api/internal/app/preparation.go','services/api/internal/app/preparation_content.go'}.issubset({d['path'] for d in inv['dependencies']}))
  speech=next(x for x in inv['entries'] if x['id']=='speech.kokoro');self.assertEqual(speech['kind'],'tts');self.assertEqual(speech['owner_symbols'],['Server.RenderPreparation','render']);self.assertEqual(speech['adapter_paths'],['services/speech/backends.py']);self.assertTrue({'services/speech/backends.py','services/speech/inference_capture.py','services/api/internal/app/speech_plan.go'}.issubset({d['path'] for d in inv['dependencies']}))
  mutation=next(x for x in inv['entries'] if x['id']=='generation.mutation');self.assertEqual(mutation['implementation_state'],'implemented');self.assertEqual(mutation['owner_symbols'],['Server.PrepareMutation']);self.assertTrue({'services/api/internal/app/mutation.go','services/api/internal/app/mutation_content.go','services/api/internal/app/generationdata/error-taxonomy.v1.yaml'}.issubset({d['path'] for d in inv['dependencies']}))
  b=self.builtin;valid=self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'validate','bundle':b}));self.assertEqual(valid.returncode,0)
  bad={**b,'bindings':[]};invalid=self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'validate','bundle':bad}),ok=False);self.assertNotEqual(invalid.returncode,0)
  duplicate={**b,'bindings':[b['bindings'][0]]*9};repeated=self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'validate','bundle':duplicate}),ok=False);self.assertNotEqual(repeated.returncode,0)
  case_results={'origin':'constructed_native_command_fixtures_not_workflow_test_receipts','cases':[{'case_id':'I3-01.P1.S1.POSITIVE','property_id':'I3-01.P1','status':'passed','action':'validate complete builtin bundle','expected_exit':'zero','observed_exit':valid.returncode},{'case_id':'I3-01.P1.S1.NEGATIVE','property_id':'I3-01.P1','status':'passed','action':'validate missing and duplicate bindings','expected_exit':'nonzero','observed_exits':[invalid.returncode,repeated.returncode]}],'provider_calls':0}
  if mutate_inventory:
   mutate_inventory(inv);inv['inventory_sha256']=sha(json.dumps({k:v for k,v in inv.items() if k!='inventory_sha256'},sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
  invref=self.retain(inv);caseref=self.retain(case_results);observer=[];observerref=self.retain(observer)
  packet=self.packet(capture=True);packet['artifacts']=[]
  for name,body in [('inventory.json',inv),('cases.json',case_results),('dispatches.json',observer)]:
   text=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(',',':'));packet['artifacts'].append({'name':name,'body':text,'sha256':sha(text.encode())})
  export=self.good(self.sdk('sync',packet));(self.receipts/'development-lab-export.json').write_text(json.dumps(export,indent=2))
  coverage={k:{'matched':0,'observed':0,'missing_reason':'zero provider calls in deterministic tooling'} for k in ['dispatch','snapshot','export']}
  run=dict(schema_version='2.0.0',id=str(uuid.uuid4()),change_id='implement-teacher-error-trainer',source_revision=revision,inventory_asset=invref,dependencies=inv['dependencies'],affected_property_ids=['I3-01.P1'],selected_case_ids=['I3-01.P1.S1.POSITIVE','I3-01.P1.S1.NEGATIVE'],required_surface_ids=[],experiment_ids=[],lab_tracking_uri='http://llm-lab:5000',status='observed',observations=[],dispatch_observer_asset=observerref,coverage=coverage,discrepancies=[],comparison_asset=None,actual_case_result_asset=caseref,zero_call_reason='deterministic tooling;14 pipeline owners remain planned;shared provider adapter is unexercised by this zero-call run',created_at='2026-10-10T07:00:00Z',mlflow_run_ids=[export['run']],mlflow_artifact_refs=['runs:/'+a['run']+'/'+a['artifact'] for a in export['artifacts']])
  return run
 def development_verify(self,run,ok=True):
  packet=self.good(self.native({'action':'development-prepare','payload':run}));return self.sdk('development-verify',packet,ok=ok)
 def test_development_zero_positive(self):
  run=self.development();out=self.good(self.development_verify(run));self.assertEqual(out['status'],'observed');self.assertIsNone(out['ratio']);self.assertEqual(out['observed'],0);(self.receipts/'ai-development-run.json').write_text(json.dumps(run,indent=2));(self.receipts/'development-verification.json').write_text(json.dumps(out,indent=2))
 def test_development_recheck_positive(self):
  run=self.development();self.assertEqual(self.good(self.development_verify(run))['status'],'observed');self.assertEqual(self.good(self.development_verify(run))['status'],'observed');self.assertEqual(len(run['observations']),0)
 def test_development_missing_negative(self):
  run=self.development();run['mlflow_artifact_refs'].pop();out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertEqual(json.loads(out.stdout)['status'],'incomplete')
  run=self.development();run['selected_case_ids']=['unobserved-case'];out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertTrue(any('missing/unperformed selected case' in x for x in json.loads(out.stdout)['discrepancies']))
 def test_development_false_surface_negative(self):
  run=self.development();run['required_surface_ids']=['claim_mapping'];out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertTrue(any('unexercised' in x for x in json.loads(out.stdout)['discrepancies']))
  run=self.development();run['dependencies'][0]['sha256']='0'*64;out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertTrue(any('dependency mismatch' in x for x in json.loads(out.stdout)['discrepancies']))
  run=self.development();dependency=next(d for d in run['dependencies'] if d['path'].startswith('specification/v2/prompts/'));path=self.root/dependency['path'];before=path.read_bytes()
  try:
   path.write_bytes(before+b'\nchanged after snapshot');out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertIn('inventory source/dependency verification failed',json.loads(out.stdout)['discrepancies'])
  finally:path.write_bytes(before)
  run=self.development(lambda inv:inv['entries'].pop());out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertIn('inventory source/dependency verification failed',json.loads(out.stdout)['discrepancies'])
  run=self.development(lambda inv:inv['dependencies'].__setitem__(slice(None),[d for d in inv['dependencies'] if d['path']!='services/api/internal/app/provider-default.json']));out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertIn('inventory source/dependency verification failed',json.loads(out.stdout)['discrepancies'])
  run=self.development(lambda inv:inv['dependencies'].__setitem__(slice(None),[d for d in inv['dependencies'] if d['path']!='services/api/internal/app/preparation.go']));out=self.development_verify(run,ok=False);self.assertNotEqual(out.returncode,0);self.assertIn('inventory source/dependency verification failed',json.loads(out.stdout)['discrepancies'])
 def test_lab_port_selected_positive(self):
  self.assertEqual((self.root/'data/config/lab-port').read_text().strip(),self.lab_port);p=self.call(['sh','scripts/tangerine','lab']);self.assertIn('http://localhost:'+self.lab_port,p.stdout)
 def test_lab_port_readback_positive(self):
  with urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:'+self.lab_port+'/version',timeout=10) as r:self.assertEqual(r.read(),b'3.17.0')
 def test_lab_port_invalid_negative(self):
  p=self.call(['sh','scripts/tangerine','lab','--port','not-a-port'],ok=False);self.assertNotEqual(p.returncode,0);self.assertIn('LAB_PORT_INVALID',p.stderr);self.assertEqual(len(self.good(self.sdk('seed'))),18)
 def test_lab_port_occupied_negative(self):
  import socket
  self.call(['sh','scripts/tangerine','lab','stop']);old=self.env
  with socket.socket() as listener:
   listener.bind(('127.0.0.1',0));listener.listen();port=listener.getsockname()[1]
   try:
    type(self).env={**old,'TANGERINE_LAB_PORT':str(port)};p=self.call(['sh','scripts/tangerine','lab'],ok=False);self.assertNotEqual(p.returncode,0);self.assertIn('LAB_PORT_OCCUPIED',p.stderr)
   finally:type(self).env=old
  self.call(['sh','scripts/tangerine','lab']);self.assertEqual(len(self.good(self.sdk('seed'))),18)
