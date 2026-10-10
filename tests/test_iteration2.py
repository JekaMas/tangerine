"""Domain-storage acceptance through real Go owner, PostgreSQL, MinIO and Chrome.
Every expectation is literal or derived from test-owned bytes, not the production writer.
"""
import base64, concurrent.futures, hashlib, io, json, subprocess, tarfile, time, unittest, uuid
from pathlib import Path
import test_iteration1 as foundation
from browser_probe import Browser
ROOT=foundation.ROOT
uid=lambda:str(uuid.uuid4())
sha=lambda b:hashlib.sha256(b).hexdigest()
class Iteration2Tests(unittest.TestCase):
 # Reuse infrastructure only; do not inherit or execute the old test methods twice.
 setUpClass=classmethod(foundation.Iteration1Tests.setUpClass.__func__)
 cleanup=classmethod(foundation.Iteration1Tests.cleanup.__func__)
 execute=classmethod(foundation.Iteration1Tests.execute.__func__)
 launch=classmethod(foundation.Iteration1Tests.launch.__func__)
 compose=classmethod(foundation.Iteration1Tests.compose.__func__)
 sql=classmethod(foundation.Iteration1Tests.sql.__func__)
 http=classmethod(foundation.Iteration1Tests.http.__func__)
 config=classmethod(foundation.Iteration1Tests.config.__func__)
 media=classmethod(foundation.Iteration1Tests.media.__func__)
 def cli(self,request,db=None):
  args=['docker','compose','--env-file',str(self.extract/'.env'),'--env-file',str(self.extract/'data/config/runtime.env'),'-f',str(self.extract/'deploy/local/compose.yaml'),'exec','-T']
  if db:args+=['-e','DATABASE_URL='+db]
  args+=['api','tangerine','storage'];r=subprocess.run(args,cwd=self.extract,env=self.env,input=json.dumps(request,ensure_ascii=False),text=True,capture_output=True,timeout=30)
  self.assertEqual(r.returncode,0,r.stdout+r.stderr);response=json.loads(r.stdout);(self.receipts/('storage-'+uid()+'.json')).write_text(json.dumps({'input':request,'output':response},ensure_ascii=False,indent=2));return response
 def write(self,*documents):return self.cli({'action':'write','documents':documents})
 def doc(self,text='Literal answer',head=None,expected=None):
  id=uid();d={'id':id,'kind':'answer-write','version':'2.0.0','scope':id,'payload':{'answer_text':text,'requested_language':'en'},'nodes':[],'references':[]}
  if head:d['head']={'id':head,'expected_revision':expected,'state':'draft'}
  return d
 def good(self,r):self.assertTrue(r['ok'],r);return r['result']
 def bad(self,r,error=None):self.assertFalse(r['ok'],r);self.assertEqual(r['error'],error) if error else None
 def head(self):h=uid();d=self.doc(head=h);self.good(self.write(d));return h,d
 def op(self):return {'operation_name':'save-source','idempotency_key':uid(),'path':'/local/source/'+uid(),'query':{},'if_match':None,'body':{'a':1}}
 def reserve(self,data=b'Exact native private bytes\n',owner=None):
  req={'operation':self.op(),'sha256':sha(data),'byte_count':len(data),'purpose':'provider_input','mime_type':'text/plain'}
  if owner:req['owner']={'id':owner,'expected_revision':0,'state':'draft'}
  a=self.good(self.cli({'action':'reserve','asset':req}));return a,req,data
 def upload(self,a,data):return self.cli({'action':'upload','id':a['id'],'data_base64':base64.b64encode(data).decode()})
 def linked(self,data=b'Stored text'):
  a,r,b=self.reserve(data);self.good(self.upload(a,b));self.good(self.cli({'action':'link','id':a['id']}));return a,r,b
 def refdoc(self,a,text='private ref'):
  d=self.doc(text);d['kind']='case-head';d['payload']={'id':d['id'],'revision':0,'status':'draft','candidate_id':a['id'],'parent_case_version_id':None,'ground_truth_id':None,'delivery_asset_id':None,'created_at':'2026-10-10T10:00:00Z','quarantine_open':False};d['references']=[{'pointer':'/candidate_id','id':a['id'],'scope':a['scope'],'kind':a['kind'],'sha256':a['sha256'],'relation':'candidate'}];return d
 def native_get(self,key):
  script=(ROOT/'tests/iteration1_media.cjs').read_text().replace("const operation = process.argv[2]","const operation = 'get'").replace("'/tangerine-audio/iteration1-fixture.bin'",json.dumps('/tangerine-audio/'+key)).replace("const text=await response.text()","const text=Buffer.from(await response.arrayBuffer())").replace("size:Buffer.byteLength(text)","size:Buffer.byteLength(text),data_base64:text.toString('base64')")
  r=self.execute(['docker','run','--rm','-i','--network',self.project+'_private','--env-file',str(self.extract/'data/config/runtime.env'),'--entrypoint','node',self.project+'-web:local','-'],input_text=script);self.assertEqual(r.returncode,0);return base64.b64decode(json.loads(r.stdout)['data_base64'])
 def native_put(self,key,data):
  # Copy bytes into an existing test S3 fixture via its signed native request code.
  script=(ROOT/'tests/iteration1_media.cjs').read_text().replace("const operation = process.argv[2]","const operation = 'put'").replace("'/tangerine-audio/iteration1-fixture.bin'",json.dumps('/tangerine-audio/'+key)).replace("'native-iteration1-object\\n'",json.dumps(data.decode()))
  self.assertEqual(self.execute(['docker','run','--rm','-i','--network',self.project+'_private','--env-file',str(self.extract/'data/config/runtime.env'),'--entrypoint','node',self.project+'-web:local','-'],input_text=script).returncode,0)

 def test_registry_exact_positive(self):
  files=list((ROOT/'specification/v2/contracts').glob('*.schema.json'));self.assertEqual(int(self.sql('SELECT count(*) FROM schema_registry')),len(files))
  for p in files:self.assertEqual(self.sql("SELECT sha256 FROM schema_registry WHERE kind='"+p.name.removesuffix('.schema.json')+"'"),sha(p.read_bytes()))
 def test_registry_readback_positive(self):
  d=self.doc('A complete literal payload');saved=self.good(self.write(d))[0];self.assertEqual(saved['schema_sha256'],sha((ROOT/'specification/v2/contracts/answer-write.schema.json').read_bytes()));self.assertEqual(self.good(self.cli({'action':'read','id':d['id']}))['payload'],d['payload'])
 def test_registry_extra_negative(self):
  d=self.doc();d['payload']['unlisted']='no';self.bad(self.write(d));self.assertEqual(self.sql("SELECT count(*) FROM document WHERE id='"+d['id']+"'"),'0')
 def test_registry_missing_negative(self):
  d=self.doc();del d['payload']['requested_language'];self.bad(self.write(d));d['version']='99.0';self.bad(self.write(d));bundle=self.doc();bundle['kind']='prompt-bundle';bundle['payload']={'schema_version':'2.0.0','id':bundle['id'],'origin':'builtin','created_at':'2026-10-10T10:00:00Z','bindings':[],'bundle_sha256':'0'*64};self.bad(self.write(bundle))

 def test_unicode_exact_positive(self):
  text='e\u0301 / é / 😀 / Русский\r\n\t';d=self.doc(text);self.good(self.write(d));self.assertEqual(self.good(self.cli({'action':'read','id':d['id']}))['payload']['answer_text'],text)
 def test_unicode_jcs_positive(self):
  r=self.good(self.cli({'action':'canonical','raw_json':'{"z":2,"a":1}'}));self.assertEqual(r,{'canonical':'{"a":1,"z":2}','sha256':sha(b'{"a":1,"z":2}')})
 def test_unicode_duplicates_negative(self):
  self.bad(self.cli({'action':'canonical','raw_json':'{"a":1,"a":2}'}));self.bad(self.cli({'action':'canonical','raw_json':'{"a":{"x":1,"x":2}}'}))
 def test_unicode_surrogate_negative(self):
  for raw in ['{"a":"\\ud800"}','{"a":"\\udc00"}','{"a":9007199254740992}','{"a":1e999}']:self.bad(self.cli({'action':'canonical','raw_json':raw}))

 def test_immutable_read_positive(self):
  d=self.doc();self.good(self.write(d));first=self.good(self.cli({'action':'read','id':d['id']}));self.assertEqual(self.good(self.cli({'action':'read','id':d['id']})),first)
 def test_immutable_versions_positive(self):
  h,old=self.head();new=self.doc('Updated',h,0);self.good(self.write(new));asset,request,payload=self.linked(b'Frozen preparation bytes');self.assertEqual(self.launch('stop').returncode,0);self.assertEqual(self.launch('start',timeout=900).returncode,0);self.assertEqual(self.good(self.cli({'action':'asset-read','id':asset['id']}))['sha256'],sha(payload));self.assertEqual(self.good(self.cli({'action':'read','id':old['id']}))['payload']['answer_text'],'Literal answer');self.assertEqual(self.sql("SELECT revision FROM entity_head WHERE id='"+h+"'"),'1')
 def test_immutable_update_negative(self):
  d=self.doc();self.good(self.write(d));r=self.compose('exec','-T','postgres','psql','-U','tangerine','-d','tangerine','-v','ON_ERROR_STOP=1','-c',"UPDATE document SET payload='{}' WHERE id='"+d['id']+"'",check=False);self.assertNotEqual(r.returncode,0);self.assertEqual(self.good(self.cli({'action':'read','id':d['id']}))['payload'],d['payload'])
 def test_immutable_delete_negative(self):
  d=self.doc();self.good(self.write(d));r=self.compose('exec','-T','postgres','psql','-U','tangerine','-d','tangerine','-v','ON_ERROR_STOP=1','-c',"DELETE FROM document WHERE id='"+d['id']+"'",check=False);self.assertNotEqual(r.returncode,0)

 def target(self):
  d=self.doc();r=self.good(self.write(d))[0];return {'id':d['id'],'scope':d['scope'],'kind':d['kind'],'sha256':r['sha256']}
 def test_batch_forward_positive(self):
  target=self.doc('Forward');b=json.dumps(target['payload'],sort_keys=True,separators=(',',':')).encode();source=self.refdoc({'id':target['id'],'scope':target['scope'],'kind':target['kind'],'sha256':sha(b)});self.good(self.write(source,target));self.assertEqual(self.sql("SELECT count(*) FROM object_reference WHERE source_document_id='"+source['id']+"'"),'1')
 def test_batch_audit_positive(self):
  a,b=self.doc('One'),self.doc('Two');self.good(self.write(a,b));self.assertEqual(self.sql("SELECT count(*) FROM audit_event WHERE subject_document_id IN('"+a['id']+"','"+b['id']+"')"),'2')
 def test_batch_dangling_negative(self):
  a=self.doc();b=self.refdoc({'id':uid(),'scope':uid(),'kind':'answer-write','sha256':'0'*64});self.bad(self.write(a,b));self.assertEqual(self.sql("SELECT count(*) FROM document WHERE id IN('"+a['id']+"','"+b['id']+"')"),'0')
 def test_batch_duplicate_negative(self):
  d=self.doc();self.bad(self.write(d,d));self.assertEqual(self.sql("SELECT count(*) FROM document WHERE id='"+d['id']+"'"),'0')

 def test_refs_scoped_positive(self):
  target=self.target();d=self.refdoc(target);self.good(self.write(d));self.assertEqual(self.sql("SELECT target_scope_id FROM object_reference WHERE source_document_id='"+d['id']+"'"),target['scope'])
 def test_refs_digest_positive(self):
  target=self.target();d=self.refdoc(target);self.good(self.write(d));self.assertEqual(self.sql("SELECT expected_sha256 FROM object_reference WHERE source_document_id='"+d['id']+"'"),target['sha256'])
 def test_refs_wrong_scope_negative(self):
  target=self.target();target['scope']=uid();self.bad(self.write(self.refdoc(target)));d=self.refdoc(target);d['references']=[];self.bad(self.write(d),'reference_error')
  target=self.target();a,b=self.refdoc(target),self.refdoc(target);a['payload']['parent_case_version_id']=b['id'];b['payload']['parent_case_version_id']=a['id'];ah=sha(json.dumps(a['payload'],sort_keys=True,separators=(',',':')).encode());bh=sha(json.dumps(b['payload'],sort_keys=True,separators=(',',':')).encode());a['references'].append({'pointer':'/parent_case_version_id','id':b['id'],'scope':b['scope'],'kind':'case-head','sha256':bh,'relation':'parent-evidence'});b['references'].append({'pointer':'/parent_case_version_id','id':a['id'],'scope':a['scope'],'kind':'case-head','sha256':ah,'relation':'parent-evidence'});self.bad(self.write(a,b),'reference_error')
 def test_refs_wrong_digest_negative(self):
  target=self.target();target['sha256']='0'*64;self.bad(self.write(self.refdoc(target)));target=self.target();target['kind']='ground-truth';self.bad(self.write(self.refdoc(target)))

 def test_cas_create_positive(self):
  h,d=self.head();self.assertEqual(self.sql("SELECT revision FROM entity_head WHERE id='"+h+"'"),'0')
 def test_cas_advance_positive(self):
  h,d=self.head();new=self.doc('Next',h,0);self.good(self.write(new));self.assertEqual(self.sql("SELECT revision,document_id FROM entity_head WHERE id='"+h+"'"),'1|'+new['id'])
 def test_cas_stale_negative(self):
  h,d=self.head();self.good(self.write(self.doc('Next',h,0)));old=self.doc('Stale',h,0);self.bad(self.write(old),'revision_conflict');self.assertEqual(self.sql("SELECT count(*) FROM document WHERE id='"+old['id']+"'"),'0')
 def test_cas_concurrent_negative(self):
  h,d=self.head();a,b=self.doc('A',h,0),self.doc('B',h,0)
  with concurrent.futures.ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda d:self.write(d),[a,b]))
  self.assertEqual(sorted(r['ok'] for r in results),[False,True]);self.assertEqual(self.sql("SELECT revision FROM entity_head WHERE id='"+h+"'"),'1')

 def test_operation_retry_positive(self):
  r=self.op();first=self.good(self.cli({'action':'operation','operation':r}));self.assertEqual(self.good(self.cli({'action':'operation','operation':r})),first)
 def test_operation_completed_positive(self):
  a,r,b=self.linked();self.assertEqual(self.good(self.cli({'action':'reserve','asset':r}))['id'],a['id']);self.assertEqual(self.sql("SELECT state FROM operation WHERE id='"+a['operation_id']+"'"),'complete');r['operation']['body']={'a':2};self.bad(self.cli({'action':'reserve','asset':r}),'conflict')
 def test_operation_body_negative(self):
  r=self.op();self.good(self.cli({'action':'operation','operation':r}));r['body']={'a':2};self.bad(self.cli({'action':'operation','operation':r}),'conflict')
 def test_operation_target_negative(self):
  for field,value in [('path','/local/other'),('query',{'variant':'changed'}),('if_match',1)]:
   r=self.op();self.good(self.cli({'action':'operation','operation':r}));r[field]=value;self.bad(self.cli({'action':'operation','operation':r}),'conflict')

 def test_asset_verified_positive(self):
  a,r,b=self.reserve();verified=self.good(self.upload(a,b));self.assertEqual(verified['state'],'bytes_verified');self.assertEqual(self.sql("SELECT sha256,byte_count FROM asset_location WHERE asset_id='"+a['id']+"'"),sha(b)+'|'+str(len(b)))
 def test_asset_delivery_positive(self):
  a,r,b=self.linked();self.assertEqual(self.good(self.cli({'action':'asset-read','id':a['id']})),{'data_base64':base64.b64encode(b).decode(),'sha256':sha(b)})
 def test_asset_wrong_input_negative(self):
  a,r,b=self.reserve();self.bad(self.upload(a,b+'x'.encode()));self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),'reserved');self.native_put(a['storage_key'],b);self.good(self.cli({'action':'upload-stream','id':a['id'],'data_base64':base64.b64encode(b'changed').decode()}));self.good(self.cli({'action':'link','id':a['id']}));self.assertEqual(self.good(self.cli({'action':'asset-read','id':a['id']}))['sha256'],sha(b))
 def test_asset_unlinked_negative(self):
  a,r,b=self.reserve();self.good(self.upload(a,b));self.bad(self.cli({'action':'asset-read','id':a['id']}),'asset_unavailable');self.native_put(a['storage_key'],b'changed-after-verification');self.bad(self.cli({'action':'link','id':a['id']}));self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),'orphaned')

 def test_recovery_upload_positive(self):
  a,r,b=self.reserve(b'large-object'*600000);self.good(self.cli({'action':'upload-stream','id':a['id'],'data_base64':base64.b64encode(b).decode()}));self.good(self.cli({'action':'recover','id':a['id']}));self.good(self.cli({'action':'link','id':a['id']}));self.assertEqual(self.good(self.cli({'action':'asset-read','id':a['id']}))['sha256'],sha(b))
 def test_recovery_link_positive(self):
  a,r,b=self.reserve();self.good(self.upload(a,b));self.good(self.cli({'action':'link','id':a['id']}));first=self.sql("SELECT result_document_id FROM operation WHERE id='"+a['operation_id']+"'");self.good(self.cli({'action':'link','id':a['id']}));self.assertEqual(self.sql("SELECT result_document_id FROM operation WHERE id='"+a['operation_id']+"'"),first)
 def test_recovery_corrupt_negative(self):
  a,r,b=self.reserve();self.native_put(a['storage_key'],b'corrupt');self.bad(self.cli({'action':'verify','id':a['id']}));self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),'orphaned')
 def test_recovery_terminal_negative(self):
  partial,request,payload=self.reserve();self.good(self.cli({'action':'begin-upload','id':partial['id']}));self.assertEqual(self.good(self.cli({'action':'recover','id':partial['id']}))['state'],'orphaned');self.assertEqual(self.sql("SELECT state,error_document_id IS NOT NULL,result_document_id IS NOT NULL FROM operation WHERE id='"+partial['operation_id']+"'"),'failed|t|t');self.bad(self.upload(partial,payload),'asset_unavailable');request['operation']['idempotency_key']=uid();retry=self.good(self.cli({'action':'retry-asset','id':partial['id'],'asset':request}));self.good(self.upload(retry,payload));self.good(self.cli({'action':'link','id':retry['id']}));self.assertEqual(self.sql("SELECT state FROM operation WHERE id='"+partial['operation_id']+"'"),'failed');self.assertEqual(self.sql("SELECT multipart_upload_id IS NULL FROM asset_location WHERE asset_id='"+partial['id']+"'"),'t');a,r,b=self.reserve();self.native_put(a['storage_key'],b'bad');self.bad(self.cli({'action':'verify','id':a['id']}));self.bad(self.cli({'action':'link','id':a['id']}),'asset_unavailable');self.bad(self.upload(a,b),'asset_unavailable')

 def owner_doc(self,a,h):
  d=self.refdoc({'id':a['id'],'scope':a['id'],'kind':'asset-bytes','sha256':a['sha256']});d['head']={'id':h,'expected_revision':0,'state':'draft'};return d
 def owner_head(self):
  target=self.target();d=self.refdoc(target);h=uid();d['head']={'id':h,'expected_revision':None,'state':'draft'};self.good(self.write(d));return h
 def test_owner_link_positive(self):
  h=self.owner_head();a,r,b=self.reserve(owner=h);self.good(self.upload(a,b));d=self.owner_doc(a,h);self.good(self.cli({'action':'link','id':a['id'],'owner':d}));self.assertEqual(self.sql("SELECT revision,document_id FROM entity_head WHERE id='"+h+"'"),'1|'+d['id'])
 def test_owner_snapshot_positive(self):
  h=self.owner_head();a,r,b=self.reserve(owner=h);self.assertEqual(self.sql("SELECT owner_head_id,owner_revision FROM asset_location WHERE asset_id='"+a['id']+"'"),h+'|0')
 def test_owner_stale_negative(self):
  h=self.owner_head();a,r,b=self.reserve(owner=h);self.good(self.upload(a,b));target=self.target();d=self.refdoc(target);d['head']={'id':h,'expected_revision':0,'state':'draft'};self.good(self.write(d));self.bad(self.cli({'action':'link','id':a['id'],'owner':self.owner_doc(a,h)}),'revision_conflict');self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),'orphaned')
 def test_owner_bad_document_negative(self):
  h=self.owner_head();a,r,b=self.reserve(owner=h);self.good(self.upload(a,b));d=self.owner_doc(a,h);d['references']=[];self.bad(self.cli({'action':'link','id':a['id'],'owner':d}),'reference_error');self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),'bytes_verified');self.assertEqual(self.sql("SELECT revision FROM entity_head WHERE id='"+h+"'"),'0')

 def orphan(self):
  a,r,b=self.reserve();self.native_put(a['storage_key'],b'wrong');self.bad(self.cli({'action':'verify','id':a['id']}));return a
 def test_orphan_old_positive(self):
  a=self.orphan();self.sql("UPDATE asset_location SET reserved_at=clock_timestamp()-interval '31 days' WHERE asset_id='"+a['id']+"'");self.assertIn(a['id'],self.good(self.cli({'action':'orphans'})))
 def test_orphan_preview_positive(self):
  a=self.orphan();self.sql("UPDATE asset_location SET reserved_at=clock_timestamp()-interval '31 days' WHERE asset_id='"+a['id']+"'");before=self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'");self.good(self.cli({'action':'orphans'}));self.assertEqual(self.sql("SELECT state FROM asset_location WHERE asset_id='"+a['id']+"'"),before)
 def test_orphan_recent_negative(self):
  a=self.orphan();self.assertNotIn(a['id'],self.good(self.cli({'action':'orphans'})))
 def test_orphan_referenced_negative(self):
  # A frozen historical reference excludes an old orphan; no reference is repointed.
  a=self.orphan();self.sql("UPDATE asset_location SET reserved_at=clock_timestamp()-interval '31 days' WHERE asset_id='"+a['id']+"'");node=self.sql("SELECT document_id FROM entity_head WHERE id='"+a['id']+"'");self.sql("INSERT INTO object_node(node_id,scope_id,kind,document_id,json_pointer,content_sha256) VALUES('"+a['id']+"','"+a['id']+"','asset-bytes','"+node+"','/sha256','"+a['sha256']+"')");d=self.refdoc({'id':a['id'],'scope':a['id'],'kind':'asset-bytes','sha256':a['sha256']});self.good(self.write(d));self.assertNotIn(a['id'],self.good(self.cli({'action':'orphans'})))

 def test_migration_fresh_positive(self):
  self.assertEqual(self.sql('SELECT count(*) FROM migration_receipt'),'1');self.assertEqual(self.sql('SELECT count(*) FROM migration_backup'),'0');self.assertEqual(self.sql("SELECT count(*) FROM workspace w JOIN workspaces f ON f.id=w.foundation_workspace_id"),'1')
 def test_migration_upgrade_positive(self):
  name='upgrade_'+uuid.uuid4().hex;self.sql('CREATE DATABASE '+name);db='postgres://tangerine:'+self.config()['POSTGRES_PASSWORD']+'@postgres:5432/'+name+'?sslmode=disable'
  def oldsql(text):
   args=['docker','compose','--env-file',str(self.extract/'.env'),'--env-file',str(self.extract/'data/config/runtime.env'),'-f',str(self.extract/'deploy/local/compose.yaml'),'exec','-T','postgres','psql','-X','-v','ON_ERROR_STOP=1','-U','tangerine','-d',name,'-At'];r=subprocess.run(args,cwd=self.extract,env=self.env,input=text,text=True,capture_output=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr);return r.stdout.strip()
  try:
   oldsql('CREATE TABLE schema_migrations(version text PRIMARY KEY,sha256 char(64),applied_at timestamptz DEFAULT now());')
   for file in sorted((ROOT/'services/api/internal/app/migrations').glob('00[12]*')):oldsql(file.read_text()+"\nINSERT INTO schema_migrations(version,sha256) VALUES('"+file.name+"','"+sha(file.read_bytes())+"');")
   oldsql("INSERT INTO exercise_catalog(id,title,published_at,source_revision,audio_sha256) VALUES('00000000-0000-4000-8000-000000000099','Unchanged legacy','2026-10-10T00:00:00Z','original','0000000000000000000000000000000000000000000000000000000000000000');");oldsql("INSERT INTO legacy_accounts(email,password_hash) VALUES('fixture@example.invalid','unusable-old-hash');");before=oldsql('SELECT id,created_at FROM workspaces');self.media('put')
   r=self.compose('exec','-T','-e','DATABASE_URL='+db,'api','tangerine','migrate');self.assertEqual(r.returncode,0);self.assertEqual(oldsql('SELECT id,created_at FROM workspaces'),before);self.assertEqual(oldsql('SELECT title,source_revision FROM exercise_catalog'),'Unchanged legacy|original');self.assertEqual(oldsql('SELECT count(*) FROM migration_backup'),'1');self.assertEqual(oldsql('SELECT email,password_hash FROM legacy_accounts'),'fixture@example.invalid|unusable-old-hash');manifest=json.loads(oldsql('SELECT manifest FROM migration_backup'));self.assertIn('database.dump',[x['path'] for x in manifest]);self.assertIn('objects/iteration1-fixture.bin',[x['path'] for x in manifest])
   key,digest=oldsql('SELECT storage_key,sha256 FROM migration_backup').split('|');backup=self.native_get(key);self.assertEqual(sha(backup),digest)
   with tarfile.open(fileobj=io.BytesIO(backup)) as archive:
    for entry in manifest:self.assertEqual(sha(archive.extractfile(entry['path']).read()),entry['sha256'])
    self.assertEqual(archive.extractfile('objects/iteration1-fixture.bin').read(),b'native-iteration1-object\n');dump=archive.extractfile('database.dump').read()
   restored='restore_'+uuid.uuid4().hex;self.sql('CREATE DATABASE '+restored)
   try:
    args=['docker','compose','--env-file',str(self.extract/'.env'),'--env-file',str(self.extract/'data/config/runtime.env'),'-f',str(self.extract/'deploy/local/compose.yaml'),'exec','-T','postgres','pg_restore','--no-owner','--no-privileges','--exit-on-error','-U','tangerine','-d',restored];restore=subprocess.run(args,cwd=self.extract,env=self.env,input=dump,capture_output=True,timeout=30);self.assertEqual(restore.returncode,0,restore.stderr.decode());result=self.compose('exec','-T','postgres','psql','-U','tangerine','-d',restored,'-At','-c','SELECT title,source_revision FROM exercise_catalog');self.assertEqual(result.stdout.strip(),'Unchanged legacy|original')
   finally:self.sql('DROP DATABASE '+restored+' WITH (FORCE)')
   # Backup dump is native pg_restore-readable. The migration owner already verified all entry hashes and remote bytes.
   self.assertEqual(oldsql("SELECT jsonb_array_length(table_inventory)>0 AND sha256 ~ '^[0-9a-f]{64}$' FROM migration_backup"),'t')
  finally:self.sql('DROP DATABASE '+name+' WITH (FORCE)')
 def test_migration_unknown_negative(self):
  before=self.sql('SELECT count(*) FROM migration_backup');self.sql("INSERT INTO schema_migrations(version,sha256) VALUES('999_unknown.sql','"+'0'*64+"')")
  try:self.assertNotEqual(self.compose('run','--rm','--no-deps','initialize',check=False).returncode,0);self.assertEqual(self.http('/health/ready')[0],503);self.assertEqual(self.sql('SELECT count(*) FROM migration_backup'),before)
  finally:self.sql("DELETE FROM schema_migrations WHERE version='999_unknown.sql'")
 def test_migration_readiness_negative(self):
  original=self.sql("SELECT sha256 FROM schema_migrations WHERE version='001_foundation.sql'");self.sql("UPDATE schema_migrations SET sha256='"+'0'*64+"' WHERE version='001_foundation.sql'")
  try:self.assertNotEqual(self.compose('run','--rm','--no-deps','initialize',check=False).returncode,0);self.assertEqual(self.http('/health/ready')[0],503);self.assertEqual(foundation.Iteration1Tests.internal.__func__(type(self),'/health/live')['status'],200);self.assertEqual(self.http('/api/v1/library')[0],200)
  finally:self.sql("UPDATE schema_migrations SET sha256='"+original+"' WHERE version='001_foundation.sql'")
  self.sql('ALTER TABLE exercise_catalog RENAME COLUMN public_context TO missing_context')
  try:self.assertEqual(self.http('/health/ready')[0],503);self.assertEqual(foundation.Iteration1Tests.internal.__func__(type(self),'/health/live')['status'],200);self.assertEqual(self.http('/api/v1/library')[0],503)
  finally:self.sql('ALTER TABLE exercise_catalog RENAME COLUMN missing_context TO public_context')
  self.populated();self.sql('ALTER TABLE exercise_catalog ALTER COLUMN published_at TYPE text USING published_at::text')
  try:self.assertEqual(self.http('/health/ready')[0],503);self.assertEqual(foundation.Iteration1Tests.internal.__func__(type(self),'/health/live')['status'],200);self.assertEqual(self.http('/api/v1/library')[0],200)
  finally:self.sql('ALTER TABLE exercise_catalog ALTER COLUMN published_at TYPE timestamptz USING published_at::timestamptz')
  self.assertEqual(self.http('/health/ready')[0],200)

 def browser(self):b=Browser(self.sandbox/('chrome-'+uid()));self.addCleanup(b.close);return b
 def populated(self):
  id=uid();self.sql("INSERT INTO exercise_catalog(id,title,public_context,duration_ms,format,difficulty,availability,published_at,audio_sha256,source_revision) VALUES('"+id+"','Browser fixture','Audible public topic',1000,'monologue','unrated','published','2026-10-10T00:00:00Z','0000000000000000000000000000000000000000000000000000000000000000','private-hidden-key')");self.addCleanup(lambda:self.sql("DELETE FROM exercise_catalog WHERE id='"+id+"'"));return id
 def test_browser_populated_positive(self):
  self.populated();b=self.browser();dom=b.wait('Browser fixture');self.assertIn('Audible public topic',dom);self.assertNotIn('private-hidden-key',dom);(self.receipts/'browser-populated.html').write_text(dom)
 def test_browser_refresh_positive(self):
  b=self.browser();b.wait('No exercises yet');self.populated();b.refresh();dom=b.wait('Browser fixture');self.assertNotIn('No exercises yet',dom);(self.receipts/'browser-refresh.html').write_text(dom)
 def test_browser_failure_negative(self):
  self.sql('ALTER TABLE exercise_catalog RENAME COLUMN public_context TO unavailable_context')
  try:b=self.browser();dom=b.wait('The Library is unavailable');self.assertIn('role="alert"',dom);self.assertNotIn('No exercises yet',dom);(self.receipts/'browser-error.html').write_text(dom)
  finally:self.sql('ALTER TABLE exercise_catalog RENAME COLUMN unavailable_context TO public_context')
 def test_browser_recovery_negative(self):
  b=self.browser();b.wait('No exercises yet');self.sql('ALTER TABLE exercise_catalog RENAME COLUMN public_context TO recovering_context')
  try:b.refresh();b.wait('The Library is unavailable')
  finally:self.sql('ALTER TABLE exercise_catalog RENAME COLUMN recovering_context TO public_context')
  b.refresh();dom=b.wait('No exercises yet');self.assertNotIn('role="alert"',dom);(self.receipts/'browser-recovery.html').write_text(dom)
