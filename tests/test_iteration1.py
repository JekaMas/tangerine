"""Real extracted-source foundation acceptance. No database, media or HTTP test doubles.

Host Python/Chrome are test tools, never application prerequisites. Each run owns
one fresh Compose project and destroys only its own fixtures on final cleanup.
"""
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

def restore_fixture_file(path, data):
    # Publish restored fault inputs atomically across the Docker directory mount.
    # Ordinary configuration already uses atomic publication; cleanup must not
    # expose a truncated predecessor to the next independent startup case.
    temporary=path.with_name(path.name+'.fixture-restore')
    temporary.write_bytes(data)
    temporary.chmod(path.stat().st_mode & 0o777)
    temporary.replace(path)

class Iteration1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path(tempfile.mkdtemp(prefix='tangerine-i1-'))
        cls.extract = cls.sandbox / 'source'
        cls.extract.mkdir()
        cls.project = 'tangerine-i1-test-' + str(os.getpid())
        cls.env = {**os.environ, 'COMPOSE_PROJECT_NAME': cls.project}
        for key in ('DATABASE_URL','POSTGRES_PASSWORD','MINIO_ROOT_USER','MINIO_ROOT_PASSWORD','API_INTERNAL_TOKEN','SPEECH_INTERNAL_TOKEN','DEEPSEEK_API_KEY','OPENAI_API_KEY','AZURE_SPEECH_KEY','AZURE_SPEECH_REGION','ELEVENLABS_API_KEY'): cls.env.pop(key,None)
        cls.receipts = ROOT / 'data' / ('iteration1-native-' + str(os.getpid()))
        cls.receipts.mkdir(parents=True)
        paths = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'], cwd=ROOT, text=True).splitlines()
        with zipfile.ZipFile(cls.sandbox/'source.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for name in paths:
                p=ROOT/name
                if p.is_file() and not name.startswith(('.agents/','.claude/','audit/','research/','data/')):
                    archive.write(p,name)
        with zipfile.ZipFile(cls.sandbox/'source.zip') as archive:
            archive.extractall(cls.extract)
            manifest={'archive_sha256':hashlib.sha256((cls.sandbox/'source.zip').read_bytes()).hexdigest(),'entries':[{'path':x.filename,'sha256':hashlib.sha256(archive.read(x.filename)).hexdigest()} for x in archive.infolist()],'excluded_git_and_workflow':True}
            (cls.receipts/'source-archive.json').write_text(json.dumps(manifest,indent=2)+'\n')
        # Actual OS utilities and Docker only: no host Git, Go, Node or Python on launcher PATH.
        tools=cls.sandbox/'tools';tools.mkdir()
        for utility in ('docker','sh','dirname','sed','id','cp','chmod','mkdir','rm'):
            located=shutil.which(utility)
            if not located: raise AssertionError('Test OS utility missing: '+utility)
            (tools/utility).symlink_to(located)
        cls.env['PATH']=str(tools)
        (cls.receipts/'launcher-path.json').write_text(json.dumps({'available_tools':sorted(p.name for p in tools.iterdir()),'host_language_runtimes':[],'git':False}))
        cls.counter = 0
        # Setup failure still triggers cleanup; no orphan test project.
        cls.addClassCleanup(cls.cleanup)
        cls.initial = cls.launch('start', timeout=900)
        if cls.initial.returncode: raise AssertionError('ZIP startup failed; inspect '+str(cls.receipts))

    @classmethod
    def cleanup(cls):
        if (cls.extract/'data/config/runtime.env').exists():
            cls.compose('down','--volumes','--remove-orphans',check=False)
        shutil.rmtree(cls.sandbox)

    @classmethod
    def execute(cls, argv, cwd=None, env=None, timeout=60, input_text=None):
        result = subprocess.run(argv,cwd=cwd or cls.extract,env=env or cls.env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout,input=input_text)
        cls.counter+=1
        # Launcher/config never prints credentials; retain exact command output.
        (cls.receipts/f'{cls.counter:03d}.log').write_text(result.stdout)
        return result

    @classmethod
    def launch(cls, command, **kw): return cls.execute(['sh','scripts/tangerine',command],**kw)

    @classmethod
    def compose(cls,*args,check=True):
        r=cls.execute(['docker','compose','--env-file',str(cls.extract/'.env'),'--env-file',str(cls.extract/'data/config/runtime.env'),'-f',str(cls.extract/'deploy/local/compose.yaml'),*args],timeout=120)
        if check and r.returncode: raise AssertionError('Compose failed; inspect '+str(cls.receipts))
        return r

    @classmethod
    def sql(cls,text):
        return cls.compose('exec','-T','postgres','psql','-X','-v','ON_ERROR_STOP=1','-U','tangerine','-d','tangerine','-At','-c',text).stdout.strip()

    @classmethod
    def http(cls,path='/api/v1/library',headers=None,method='GET'):
        req=urllib.request.Request('http://localhost:3000'+path,headers=headers or {},method=method)
        try:
            with urllib.request.urlopen(req,timeout=15) as r:return r.status,r.read(),dict(r.headers)
        except urllib.error.HTTPError as e:
            with e: return e.code,e.read(),dict(e.headers)

    @classmethod
    def internal(cls,path,token=True):
        code="import os,urllib.request,urllib.error,json; h={'Authorization':'Bearer '+os.environ['API_INTERNAL_TOKEN']} if "+repr(token)+" else {}; r=urllib.request.Request('http://127.0.0.1:8080"+path+"',headers=h);\ntry:\n s=urllib.request.urlopen(r,timeout=10); print(json.dumps({'status':s.status,'body':s.read().decode()}))\nexcept urllib.error.HTTPError as e: print(json.dumps({'status':e.code,'body':e.read().decode()}))"
        # API image has no Python; actual speech container reaches API through its private network.
        code=code.replace("os.environ['API_INTERNAL_TOKEN']",repr(cls.config()['API_INTERNAL_TOKEN'])).replace('127.0.0.1:8080','api:8080')
        r=cls.compose('exec','-T','speech','python','-c',code)
        return json.loads(r.stdout)

    @classmethod
    def config(cls): return dict(line.split('=',1) for line in (cls.extract/'data/config/runtime.env').read_text().splitlines())

    @classmethod
    def media(cls,operation):
        r=cls.execute(['docker','run','--rm','--network',cls.project+'_private','--env-file',str(cls.extract/'data/config/runtime.env'),'-v',str(ROOT/'tests/iteration1_media.cjs')+':/probe.cjs:ro','--entrypoint','node',cls.project+'-web:local','/probe.cjs',operation])
        if r.returncode: raise AssertionError('Native S3 fixture failed; inspect '+str(cls.receipts))
        return json.loads(r.stdout)

    def test_delivery_zip_start_positive(self):
        self.assertEqual(self.initial.returncode,0)
        self.assertFalse((self.extract/'.git').exists());self.assertFalse((self.extract/'.agents').exists())
        self.assertEqual(self.http('/health/ready')[0],200)
        with urllib.request.urlopen('http://localhost:3000/health/ready',timeout=10) as response:
            self.assertEqual(response.headers['X-Tangerine-Instance'],hashlib.sha256(self.config()['API_INTERNAL_TOKEN'].encode()).hexdigest())
    def test_delivery_repeat_start_positive(self):
        before=self.sql('SELECT id FROM workspaces');self.assertEqual(self.launch('start',timeout=900).returncode,0)
        self.assertEqual(self.sql('SELECT id FROM workspaces'),before)
    def test_delivery_missing_source_negative(self):
        p=self.extract/'services/web/package-lock.json';saved=p.read_bytes();p.unlink()
        try:r=self.launch('start');self.assertNotEqual(r.returncode,0);self.assertIn('SOURCE_INCOMPLETE',r.stdout)
        finally:restore_fixture_file(p,saved)
    def test_delivery_no_docker_negative(self):
        r=self.execute(['/bin/sh','scripts/tangerine','start'],env={**self.env,'PATH':'/nonexistent'})
        self.assertNotEqual(r.returncode,0);self.assertIn('DOCKER_REQUIRED',r.stdout)

    def test_config_durable_positive(self):
        p=self.extract/'data/config/runtime.env';before=p.read_bytes();self.assertEqual(self.launch('start',timeout=900).returncode,0)
        self.assertEqual(p.read_bytes(),before);self.assertEqual(p.stat().st_mode & 0o777,0o600)
    def test_config_no_keys_positive(self):
        # Ambient shell keys and storage secrets must not override this installation.
        r=self.launch('start',env={**self.env,'OPENAI_API_KEY':'sentinel-not-an-operator-key','POSTGRES_PASSWORD':'wrong-ambient-password'},timeout=900)
        self.assertEqual(r.returncode,0)
        self.assertTrue(all(not line.split('=',1)[1] for line in (self.extract/'.env').read_text().splitlines() if line and not line.startswith('#')))
        health=json.loads(self.http('/api/v1/health')[1]);self.assertEqual(health['provider_configuration'],'missing_credentials');self.assertEqual(health['status'],'ok')
    def test_config_unknown_negative(self):
        p=self.extract/'.env';saved=p.read_bytes();p.write_text('UNKNOWN_OPERATOR=value\n')
        try:r=self.launch('start',timeout=900);self.assertNotEqual(r.returncode,0);self.assertIn('CONFIG_INVALID',r.stdout)
        finally:restore_fixture_file(p,saved)
    def test_config_damaged_negative(self):
        p=self.extract/'data/config/runtime.env';saved=p.read_bytes();p.write_text('damaged\n')
        try:r=self.launch('start',timeout=900);self.assertNotEqual(r.returncode,0);self.assertIn('CONFIG_DAMAGED',r.stdout);self.assertEqual(p.read_text(),'damaged\n')
        finally:restore_fixture_file(p,saved)

    def test_init_workspace_positive(self):
        self.assertEqual(self.sql('SELECT count(*) FROM workspaces'), '1')
        self.assertEqual(self.sql('SELECT count(*) FROM legacy_accounts'), '0');self.assertEqual(self.sql('SELECT count(*) FROM legacy_sessions'),'0')
        self.assertEqual(self.sql('SELECT count(*) FROM schema_migrations'),'3')
    def test_init_idempotent_positive(self):
        before=self.sql('SELECT version,sha256,applied_at FROM schema_migrations ORDER BY version');self.compose('run','--rm','initialize')
        self.assertEqual(self.sql('SELECT version,sha256,applied_at FROM schema_migrations ORDER BY version'),before)
    def test_init_checksum_negative(self):
        saved=self.sql("SELECT sha256 FROM schema_migrations WHERE version='001_foundation.sql'")
        self.sql("UPDATE schema_migrations SET sha256=repeat('0',64) WHERE version='001_foundation.sql'")
        try:r=self.compose('run','--rm','initialize',check=False);self.assertEqual(r.returncode,0);self.assertEqual(self.sql("SELECT sha256 FROM schema_migrations WHERE version='001_foundation.sql'"),'0'*64)
        finally:self.sql("UPDATE schema_migrations SET sha256='"+saved+"' WHERE version='001_foundation.sql'")
    def test_init_public_bucket_negative(self):
        self.media('public')
        try:r=self.compose('run','--rm','initialize',check=False);self.assertNotEqual(r.returncode,0);self.assertIn('MEDIA_INIT_FAILED',r.stdout);self.assertEqual(self.http('/health/ready')[0],200)
        finally:self.media('private')

    def test_library_empty_positive(self):
        self.assertEqual(self.http()[0],200);self.assertEqual(json.loads(self.http()[1]),[]);self.assertEqual(self.sql('SELECT count(*) FROM exercise_catalog'),'0')
    def test_library_projection_positive(self):
        identity='00000000-0000-4000-8000-000000000001'
        self.sql("INSERT INTO exercise_catalog(id,title,published_at,source_revision,audio_sha256,public_context,duration_ms,format,difficulty,availability) VALUES ('"+identity+"','Fixture title',now(),'private-key-marker',repeat('a',64),'Public context',1000,'monologue','unrated','published')")
        try:self.assertEqual(json.loads(self.http()[1]),[{'id':identity,'title':'Fixture title','public_context':'Public context','duration_ms':1000,'format':'monologue','difficulty':'unrated','availability':'published'}])
        finally:self.sql("DELETE FROM exercise_catalog WHERE id='"+identity+"'")
    def test_library_legacy_incomplete_negative(self):
        self.sql("INSERT INTO exercise_catalog(title,published_at,source_revision,audio_sha256) VALUES ('Historical incomplete',now(),'legacy',repeat('b',64))")
        try:self.assertEqual(json.loads(self.http()[1]),[]);self.assertEqual(self.sql("SELECT count(*) FROM exercise_catalog WHERE source_revision='legacy'"),'1')
        finally:self.sql("DELETE FROM exercise_catalog WHERE source_revision='legacy'")
    def test_library_storage_failure_negative(self):
        self.compose('stop','postgres')
        try:self.assertEqual(self.http()[0],503);self.assertEqual(json.loads(self.http()[1]),{'error':'storage_unavailable'})
        finally:self.compose('start','--wait','postgres')

    def test_transport_no_session_positive(self):
        code,_,headers=self.http(headers={'Cookie':'tangerine_session=invalid','Authorization':'Bearer ignored-user-token'})
        self.assertEqual(code,200);self.assertNotIn('Set-Cookie',headers)
    def test_transport_public_browser_positive(self):
        self.assertTrue(CHROME.is_file(),'Actual Chrome browser test prerequisite missing')
        from browser_probe import Browser
        browser=Browser(self.sandbox/'chrome')
        self.addCleanup(browser.close)
        browser.wait('No exercises yet')
        output=browser.evaluate('document.documentElement.outerHTML')
        (self.receipts/'browser-dom.log').write_text(output)
        (self.receipts/'browser-driver.json').write_text(json.dumps({'driver':'native Playwright/Chrome','version':browser.driver_version,'complete_dom':'</html>' in output}))
        self.assertIn('</html>',output,'Browser never produced a complete native DOM')
        self.assertIn('No exercises yet',output);self.assertNotIn('type="password"',output);self.assertNotIn('Sign in to your workspace',output)
        for secret in self.config().values():self.assertNotIn(secret,output)

    def test_transport_foreign_origin_negative(self):
        for method in ('POST','PUT','PATCH','DELETE'):
            self.assertEqual(self.http('/api/v1/library',{'Origin':'http://foreign.invalid'},method)[0],403)
        self.assertEqual(self.http(headers={'Host':'foreign.invalid:3000'})[0],403)
    def test_transport_internal_token_negative(self):
        r=self.internal('/api/v1/library',False);self.assertEqual(r['status'],403)
        self.assertEqual(self.http('/api/auth/login',{'Origin':'http://localhost:3000'},'POST')[0],404)

    def test_health_dependencies_positive(self):
        h=json.loads(self.http('/api/v1/health')[1]);self.assertEqual({k:h[k] for k in ('status','database','storage','speech')},{'status':'ok','database':'ready','storage':'ready','speech':'ready'})
        self.assertEqual(h['release_id'],'0.1.0-foundation')
    def test_health_liveness_positive(self):
        self.assertEqual(self.internal('/health/live')['status'],200)
        r=self.execute(['docker','image','inspect',self.project+'-api:local','--format','{{index .Config.Labels "org.opencontainers.image.version"}}']);self.assertEqual(r.stdout.strip(),'0.1.0-foundation')
    def test_health_speech_failure_negative(self):
        self.compose('stop','speech')
        try:self.assertEqual(self.http('/health/ready')[0],503);self.assertEqual(json.loads(self.http('/api/v1/health')[1])['speech'],'unavailable')
        finally:self.compose('start','--wait','speech')
    def test_health_media_failure_negative(self):
        self.compose('stop','minio')
        try:
            self.assertEqual(self.http('/health/ready')[0],503)
            h=json.loads(self.http('/api/v1/health')[1]);self.assertEqual(h['storage'],'unavailable');self.assertEqual(h['database'],'ready');self.assertEqual(h['speech'],'ready')
            self.assertEqual(self.internal('/health/live')['status'],200)
        finally:self.compose('start','--wait','minio')

    def test_restart_database_positive(self):
        before=self.sql('SELECT id,created_at FROM workspaces');self.assertEqual(self.launch('stop').returncode,0);self.assertEqual(self.launch('start',timeout=900).returncode,0)
        self.assertEqual(self.sql('SELECT id,created_at FROM workspaces'),before)
    def test_restart_media_positive(self):
        self.media('put');before=self.media('get');self.assertEqual(before['sha256'],hashlib.sha256(b'native-iteration1-object\n').hexdigest())
        self.assertEqual(self.launch('stop').returncode,0);self.assertEqual(self.launch('start',timeout=900).returncode,0);self.assertEqual(self.media('get'),before)
    def test_restart_missing_config_negative(self):
        p=self.extract/'data/config/runtime.env';saved=p.read_bytes();p.unlink()
        try:r=self.launch('start');self.assertNotEqual(r.returncode,0);self.assertIn('CONFIG_MISSING',r.stdout);self.assertFalse(p.exists())
        finally:restore_fixture_file(p,saved);p.chmod(0o600)
    def test_restart_unknown_command_negative(self):
        before=self.sql('SELECT id FROM workspaces');r=self.launch('invalid-command');self.assertNotEqual(r.returncode,0);self.assertIn('UNKNOWN_COMMAND',r.stdout);self.assertEqual(self.sql('SELECT id FROM workspaces'),before)

    def test_operations_status_positive(self):
        r=self.launch('status');self.assertEqual(r.returncode,0)
        for service in ('postgres','minio','api','web','speech'):self.assertIn(service,r.stdout)
        r=self.compose('ps','--format','json');rows=[json.loads(line) for line in r.stdout.splitlines()]
        publishers=[p for row in rows for p in (row.get('Publishers') or []) if p['PublishedPort']>0];self.assertEqual([(p['URL'],p['PublishedPort']) for p in publishers],[('127.0.0.1',3000)])
    def test_operations_logs_positive(self):
        r=self.launch('logs');self.assertEqual(r.returncode,0)
        for value in self.config().values():self.assertNotIn(value,r.stdout)
    def test_operations_build_failure_negative(self):
        p=self.extract/'services/api/Dockerfile';saved=p.read_bytes();p.write_text('FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587\nRUN exit 17\n')
        try:r=self.launch('start',timeout=900);self.assertNotEqual(r.returncode,0);self.assertIn('BUILD_FAILED',r.stdout);self.assertEqual(self.http('/health/ready')[0],200)
        finally:restore_fixture_file(p,saved)
    def test_operations_occupied_port_negative(self):
        self.assertEqual(self.launch('stop').returncode,0)
        received=[]
        class ForeignReady(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(dict(self.headers));self.send_response(200);self.send_header('X-Tangerine-Instance','foreign-installation');self.end_headers();self.wfile.write(b'{"status":"ready"}')
            def log_message(self,*args):pass
        listener=http.server.ThreadingHTTPServer(('127.0.0.1',3000),ForeignReady)
        worker=threading.Thread(target=listener.serve_forever,daemon=True);worker.start()
        try:
            r=self.launch('start',timeout=900);self.assertNotEqual(r.returncode,0);self.assertIn('START_FAILED',r.stdout);self.assertNotIn('Tangerine is ready',r.stdout)
            for headers in received:self.assertNotIn('Authorization',headers);self.assertNotIn(self.config()['API_INTERNAL_TOKEN'],str(headers))
        finally:listener.shutdown();listener.server_close();worker.join();self.assertEqual(self.launch('start',timeout=900).returncode,0)

if __name__=='__main__': unittest.main()
