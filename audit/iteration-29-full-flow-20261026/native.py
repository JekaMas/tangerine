"""Owned I29 native UI workspace. Model calls happen only through CUA actions.

Uses the selected API/web sources and installed local speech assets.
No host install, paid key/provider, ordinary workspace change or browser driver.
"""
from pathlib import Path
import json,os,secrets,subprocess,sys,time,uuid

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-29-full-flow-20261026'
OUT.mkdir(parents=True,exist_ok=True)

def call(args,check=True):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError('Owned setup failed; inspect setup.log')
 return p.stdout.strip()

def api_args(name,resume=False):
 args=['docker','run','--rm','--name',name+'-api','--network',name,'--network-alias','api','--env-file',str(OUT/'private-runtime.env')]
 if resume:args+=['-e','TANGERINE_I29_RESUME=1']
 return args+['-v',str(OUT)+':/evidence','-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','--entrypoint','sh','tangerine-i28-go','-c','cp -R /checked-src/. /src/ && cp /fixtures/native_gemini_test.go /fixtures/full_flow_browser_fixture_test.go /src/internal/app/ && exec go test -json -race -count=1 -timeout=190m -run ^TestNativeFullFlowBrowserFixture$ ./internal/app']

if len(sys.argv)>1 and sys.argv[1]=='cleanup':
 stack=json.loads((OUT/'stack.json').read_text());name=stack['name']
 for kind in ['web','api','speech','postgres','media']:call(['docker','rm','-f','-v',name+'-'+kind],False)
 call(['docker','network','rm',name],False)
 raise SystemExit(0)

if len(sys.argv)>1 and sys.argv[1]=='resume':
 # Keep the exact DB, media, configuration and saved attempt after an in-scope
 # repair. Only this owned API process is replaced; no preparation is rerun.
 stack=json.loads((OUT/'stack.json').read_text());name=stack['name']
 for kind in ['postgres','media','speech','web']:
  call(['docker','start',name+'-'+kind])
 for kind in ['postgres','media']:
  for _ in range(120):
   probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
   if subprocess.run(['docker','exec',name+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
   time.sleep(.2)
  else:raise RuntimeError('Retained owned dependency unavailable')
 (OUT/'done').unlink(missing_ok=True)
 args=api_args(name,resume=True)
 with (OUT/'native-repaired.jsonl').open('w') as stdout,(OUT/'native-repaired.stderr').open('w') as stderr:
  code=subprocess.run(args,cwd=ROOT,stdout=stdout,stderr=stderr).returncode
 (OUT/'native-repaired-exit-code').write_text(str(code))
 raise SystemExit(code)

assert 'No billing account' in (OUT/'account-billing.txt').read_text()
assert 'Free tier' in (OUT/'account-api-keys.txt').read_text()
key=next(line for line in (ROOT/'data/iteration16/private/gemini.env').read_text().splitlines() if line.startswith('GEMINI_API_KEY='))
assert key.rsplit('=',1)[1].strip().strip('"\'').endswith('ljSA'), 'The selected key must match the actually observed Free project'
NAME='tangerine-i29-'+uuid.uuid4().hex[:8]
password=secrets.token_hex(24)
private=OUT/'private-runtime.env'
private.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+password+'\nDATABASE_URL=postgres://tangerine:'+password+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=full-flow\nMINIO_ROOT_PASSWORD='+password+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=full-flow\nMINIO_SECRET_KEY='+password+'\nMINIO_BUCKET=regressions\nAPI_INTERNAL_TOKEN=listening-owned-token\nSPEECH_INTERNAL_TOKEN=actual-local-speech-test\nTANGERINE_GEMINI_EVIDENCE=/evidence\nTANGERINE_SPEECH_TEST_URL=http://speech:8090\nTANGERINE_GEMINI_LIVE=1\n'+key+'\n')
private.chmod(0o600)
web=OUT/'private-web.env';web.write_text('API_INTERNAL_URL=http://api:8080\nAPI_INTERNAL_TOKEN=listening-owned-token\n');web.chmod(0o600)
speech=OUT/'private-speech.env';speech.write_text('SPEECH_INTERNAL_TOKEN=actual-local-speech-test\n');speech.chmod(0o600)
call(['docker','network','create',NAME])
for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i28-media','minio')]:
 call(['docker','run','-d','--name',NAME+'-'+kind,'--network',NAME,'--network-alias',alias,'--env-file',str(private),image])
 for _ in range(120):
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  if subprocess.run(['docker','exec',NAME+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(.2)
 else:raise RuntimeError('Owned dependency unavailable')
call(['docker','run','--rm','--network',NAME,'--env-file',str(private),'--entrypoint','/tangerine','tangerine-i28-go','initialize'])
call(['docker','run','-d','--name',NAME+'-speech','--network',NAME,'--network-alias','speech','--env-file',str(speech),'-v',str(ROOT/'services/speech')+':/app:ro','-v','tangerine-local_speech-models:/models:ro','tangerine-local-speech:local'])
call(['docker','run','-d','--name',NAME+'-web','--network',NAME,'--env-file',str(web),'-p','127.0.0.1::3000','tangerine-i29-web'])
stack={'name':NAME,'web_port':call(['docker','port',NAME+'-web','3000/tcp']).rsplit(':',1)[1],'api_image':'tangerine-i28-go','web_image':'tangerine-i29-web','speech_image':'tangerine-local-speech:local','origin':'actual native disposable workspace; no pre-generated exercise or model reply fixture'}
(OUT/'stack.json').write_text(json.dumps(stack,indent=2)+'\n')
args=api_args(NAME)
with (OUT/'native.jsonl').open('w') as stdout,(OUT/'native.stderr').open('w') as stderr:
 code=subprocess.run(args,cwd=ROOT,stdout=stdout,stderr=stderr).returncode
(OUT/'native-exit-code').write_text(str(code))
# Keep this owned storage until explicit cleanup after evidence reconciliation.
# A failed observation never automatically erases its native checkpoint.
raise SystemExit(code)
