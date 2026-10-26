"""Owned native fixture. Live is explicit, Free-project only; no paid fallback."""
from pathlib import Path
import json,os,secrets,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
MODE=sys.argv[1] if len(sys.argv)>1 else 'controlled'
LIVE=MODE in ('live','repair','resume'); REPAIR=MODE in ('repair','resume'); OUT=ROOT/'data/iteration-23-gemini-20261026'/MODE
OUT.mkdir(parents=True,exist_ok=True);NAME='tangerine-i23-'+MODE
def call(args,check=True):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError('I23 owned setup failed; see '+str(OUT/'setup.log'))
 return p.stdout.strip()
password=secrets.token_hex(24);config=OUT/'private-runtime.env'
config.write_text(f'POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD={password}\nDATABASE_URL=postgres://tangerine:{password}@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=gemini-fixture\nMINIO_ROOT_PASSWORD={password}\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=gemini-fixture\nMINIO_SECRET_KEY={password}\nMINIO_BUCKET=regressions\nAPI_INTERNAL_TOKEN=listening-owned-token\nSPEECH_INTERNAL_TOKEN=actual-local-speech-test\nTANGERINE_GEMINI_EVIDENCE=/evidence\nTANGERINE_SPEECH_TEST_URL=http://speech:8090\nTANGERINE_GEMINI_LIVE={int(LIVE)}\n')
config.chmod(0o600)
if LIVE:
 # Human-visible account observation, not a self-declared profile assertion.
 evidence=ROOT/'data/iteration-23-gemini-20261026'
 if 'No billing account' not in (evidence/'account-billing.txt').read_text() or 'Free tier' not in (evidence/'account-api-keys.txt').read_text():raise RuntimeError('Free-only admission observation missing')
 private=(ROOT/'data/iteration16/private/gemini.env').read_text().strip()
 with config.open('a') as f:f.write(private+'\n')
if REPAIR:
 # Reuse the admitted owned database/media and actual generated exercise.
 config.write_bytes((OUT.parent/'live/private-runtime.env').read_bytes());config.chmod(0o600)
 prior='repair' if MODE=='resume' else 'live';test='TestNativeGeminiResume' if MODE=='resume' else 'TestNativeGeminiAnswerRepair'
 args=['docker','run','--rm','--name',NAME+'-api','--network','tangerine-i23-live','--env-file',str(config),'-p','127.0.0.1:3423:8080','-v',str(OUT)+':/evidence','-v',str(OUT.parent/prior)+':/prior:ro','-v',str(ROOT/'tests/native_gemini_test.go')+':/src/internal/app/native_gemini_test.go:ro','--entrypoint','go','tangerine-i23-go','test','-json','-race','-count=1','-timeout=2h','-run','^'+test+'$','./internal/app']
 code=subprocess.run(args,cwd=ROOT,stdout=(OUT/'native.jsonl').open('w'),stderr=(OUT/'native.stderr.log').open('w')).returncode
 (OUT/'exit-code').write_text(str(code));raise SystemExit(code)
call(['docker','network','create',NAME])
for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i21-guided-media','minio')]:
 call(['docker','run','-d','--name',NAME+'-'+kind,'--network',NAME,'--network-alias',alias,'--env-file',str(config),image])
 for _ in range(100):
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  if subprocess.run(['docker','exec',NAME+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(.2)
 else:raise RuntimeError('Owned '+kind+' unavailable')
call(['docker','run','--rm','--network',NAME,'--env-file',str(config),'--entrypoint','/tangerine','tangerine-i23-go','initialize'])
if LIVE:call(['docker','run','-d','--name',NAME+'-speech','--network',NAME,'--network-alias','speech','--env-file',str(config),'-v',str(ROOT/'services/speech')+':/app:ro','-v','tangerine-local_speech-models:/models:ro','tangerine-local-speech:local'])
args=['docker','run','--rm','--name',NAME+'-api','--network',NAME,'--env-file',str(config),'-v',str(OUT)+':/evidence','-v',str(ROOT/'tests/native_gemini_test.go')+':/src/internal/app/native_gemini_test.go:ro']
if LIVE:args+=['-p','127.0.0.1:3423:8080']
pattern='^TestNativeGeminiFreeFlow$' if LIVE else '^TestNativeGemini(Errors|UnavailableRecovery|RepairContext)$'
if MODE=='context':pattern='^TestNativeGeminiRepairContext$'
code=subprocess.run(args+['--entrypoint','go','tangerine-i23-go','test','-json','-race','-count=1','-timeout=2h','-run',pattern,'./internal/app'],cwd=ROOT,stdout=(OUT/'native.jsonl').open('w'),stderr=(OUT/'native.stderr.log').open('w')).returncode
(OUT/'exit-code').write_text(str(code))
if not LIVE:
 for kind in ['api','postgres','media']:call(['docker','rm','-f','-v',NAME+'-'+kind],check=False)
 call(['docker','network','rm',NAME],check=False)
raise SystemExit(code)
