"""Separate installed-local full-flow workspace; no key, download or fallback."""
from pathlib import Path
import json,secrets,subprocess,time,uuid,sys,os

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/os.environ.get('TANGERINE_I29_LOCAL_DATA','data/iteration-29-local-full-flow-20261026')
OUT.mkdir(exist_ok=True)
def run_api(name,log='native'):
 args=['docker','run','--rm','--name',name+'-api','--network',name,'--network-alias','api','--add-host','ollama:host-gateway','--env-file',str(OUT/'private-runtime.env'),'-v',str(OUT)+':/evidence','-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','--entrypoint','sh','tangerine-i28-go','-c','cp -R /checked-src/. /src/ && cp /fixtures/native_gemini_test.go /fixtures/full_flow_browser_fixture_test.go /fixtures/full_flow_local_fixture_test.go /src/internal/app/ && exec go test -json -race -count=1 -timeout=190m -run ^TestNativeLocalFullFlowBrowserFixture$ ./internal/app']
 with (OUT/(log+'.jsonl')).open('w') as stdout,(OUT/(log+'.stderr')).open('w') as stderr:
  code=subprocess.run(args,cwd=ROOT,stdout=stdout,stderr=stderr).returncode
 (OUT/(log+'-exit-code')).write_text(str(code))
 return code

if len(sys.argv)>1 and sys.argv[1]=='resume':
 name=json.loads((OUT/'stack.json').read_text())['name'];(OUT/'done').unlink(missing_ok=True)
 raise SystemExit(run_api(name,sys.argv[2] if len(sys.argv)>2 else 'native-resumed'))

assert not (OUT/'stack.json').exists(), 'Retain existing local state instead of recreating it'
name='tangerine-i29-local-'+uuid.uuid4().hex[:8]
password=secrets.token_hex(24)
env=OUT/'private-runtime.env'
env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+password+'\nDATABASE_URL=postgres://tangerine:'+password+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=full-flow\nMINIO_ROOT_PASSWORD='+password+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=full-flow\nMINIO_SECRET_KEY='+password+'\nMINIO_BUCKET=regressions\nAPI_INTERNAL_TOKEN=listening-owned-token\nSPEECH_INTERNAL_TOKEN=actual-local-speech-test\nTANGERINE_GEMINI_EVIDENCE=/evidence\nTANGERINE_SPEECH_TEST_URL=http://speech:8090\nTANGERINE_LOCAL_LIVE=1\n');env.chmod(0o600)
web=OUT/'private-web.env';web.write_text('API_INTERNAL_URL=http://api:8080\nAPI_INTERNAL_TOKEN=listening-owned-token\n');web.chmod(0o600)
speech=OUT/'private-speech.env';speech.write_text('SPEECH_INTERNAL_TOKEN=actual-local-speech-test\n');speech.chmod(0o600)

def call(args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError('Owned local setup failed; inspect setup.log')
 return p.stdout.strip()

call(['docker','network','create',name])
for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i28-media','minio')]:
 call(['docker','run','-d','--name',name+'-'+kind,'--network',name,'--network-alias',alias,'--env-file',str(env),image])
 for _ in range(120):
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  if subprocess.run(['docker','exec',name+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(.2)
 else:raise RuntimeError('Owned local dependency unavailable')
call(['docker','run','--rm','--network',name,'--env-file',str(env),'--entrypoint','/tangerine','tangerine-i28-go','initialize'])
call(['docker','run','-d','--name',name+'-speech','--network',name,'--network-alias','speech','--env-file',str(speech),'-v',str(ROOT/'services/speech')+':/app:ro','-v','tangerine-local_speech-models:/models:ro','tangerine-local-speech:local'])
call(['docker','run','-d','--name',name+'-web','--network',name,'--env-file',str(web),'-p','127.0.0.1::3000','tangerine-i29-verify-web'])
port=call(['docker','port',name+'-web','3000/tcp']).rsplit(':',1)[1]
(OUT/'stack.json').write_text(json.dumps({'name':name,'web_port':port,'origin':'separate explicit local-only example; no cloud key or model download'},indent=2)+'\n')
raise SystemExit(run_api(name))
