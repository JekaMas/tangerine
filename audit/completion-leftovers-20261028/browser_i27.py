"""Fresh tiny lineage fixture through native storage/HTTP, then actual Chrome.

Uses only the retained disposable I30 stores; no corpus reimport or model call.
The Go fixture owns and removes its newly created private SQL schema.
"""
import importlib.util,json,os,subprocess,threading,time
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/completion-leftovers-20261028/i27';OLD=ROOT/'data/iteration-30-release-20261027'
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
def call(args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()
def main():
 OUT.mkdir(parents=True,exist_ok=True);state=json.loads((OLD/'stack.json').read_text());source=Path(state['source_root']);prefix='tangerine-completion-i27';worker=None
 for suffix in ['native','web']:
  subprocess.run(['docker','rm',prefix+'-'+suffix],capture_output=True)
 envargs=['--env-file',str(source/'.env'),'--env-file',str(source/'data/config/runtime.env')]
 # Compose defines storage URLs/aliases inline. Reuse the owned API's resolved
 # storage environment, never assume the launcher secrets file includes them.
 resolved=call(['docker','inspect','--format','{{range .Config.Env}}{{println .}}{{end}}',state['project']+'-api-1'])
 storage_keys={'DATABASE_URL','MINIO_ENDPOINT','MINIO_ACCESS_KEY','MINIO_SECRET_KEY','MINIO_BUCKET'}
 private=OUT/'private-storage.env';private.write_text('\n'.join(line for line in resolved.splitlines() if line.split('=',1)[0] in storage_keys)+'\n');private.chmod(0o600)
 shell='mkdir /native-src && cp -R /checked-src/. /native-src/ && cp /fixtures/native_source_test.go /fixtures/source_completion_browser_fixture_test.go /native-src/internal/app/ && cd /native-src && exec go test -race -json -count=1 -timeout=600s -run ^TestSourceCompletionBrowserFixture$ ./internal/app'
 command=['docker','run','--rm','--pull=never','--name',prefix+'-native','--network',state['project']+'_private','--network-alias','completion-source-fixture','--env-file',str(private),'-e','GOWORK=off','-e','GOTOOLCHAIN=local','-e','GOPROXY=off','-e','GOSUMDB=off','-e','TANGERINE_SOURCE_EVIDENCE=/evidence','-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','--entrypoint','sh','tangerine-i28-go','-c',shell]
 (OUT/'native-command.json').write_text(json.dumps(command,indent=2)+'\n')
 with (OUT/'native.jsonl').open('w') as stdout,(OUT/'native.stderr').open('w') as stderr:
  worker=subprocess.Popen(command,stdout=stdout,stderr=stderr)
 try:
  for _ in range(1200):
   if (OUT/'fixture.json').exists():break
   if worker.poll() is not None:raise RuntimeError('Native Sources fixture failed; inspect private log')
   time.sleep(.1)
  else:raise RuntimeError('Native Sources fixture startup deadline')
  call(['docker','run','--pull=never','-d','--name',prefix+'-web','--network',state['project']+'_egress',*envargs,'-e','API_INTERNAL_URL=http://completion-source-fixture:8080','-e','API_INTERNAL_TOKEN=source-owned-token','-p','127.0.0.1::3000','tangerine-completion-web'])
  call(['docker','network','connect',state['project']+'_private',prefix+'-web'])
  port=call(['docker','inspect','--format','{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}',prefix+'-web'])
  spec=importlib.util.spec_from_file_location('source_browser_forwarder',ROOT/'audit/iteration-30-release-20261027/readiness_forwarder.py');forwarder=importlib.util.module_from_spec(spec)
  with patch.dict(os.environ,dict(I30_WEB_PORT=port)):spec.loader.exec_module(forwarder)
  forwarder.TARGET='http://127.0.0.1:'+port;forwarder.BROWSER=True
  gateway=ThreadingHTTPServer(('127.0.0.1',0),forwarder.Forward);url='http://127.0.0.1:'+str(gateway.server_port);forwarder.BROWSER_ORIGIN=url
  thread=threading.Thread(target=gateway.serve_forever,daemon=True);thread.start()
  env={**os.environ,'I27_URL':url,'I27_OUTPUT':str(OUT),'TANGERINE_PLAYWRIGHT_MODULE':str(NODE.parent.parent/'node_modules/playwright')}
  try:
   with (OUT/'browser.log').open('w') as log:r=subprocess.run([str(NODE),str(ROOT/'tests/completion_leftovers_i27.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=180)
  finally:gateway.shutdown();gateway.server_close();thread.join(timeout=5)
  (OUT/'exit-code').write_text(str(r.returncode)+'\n');return r.returncode
 finally:
  (OUT/'done').write_text('done\n')
  if worker:
   try:code=worker.wait(timeout=30);(OUT/'native-exit-code').write_text(str(code)+'\n')
   except subprocess.TimeoutExpired:subprocess.run(['docker','stop',prefix+'-native'],capture_output=True);worker.wait(timeout=15)
  subprocess.run(['docker','stop',prefix+'-web'],capture_output=True)
if __name__=='__main__':raise SystemExit(main())
