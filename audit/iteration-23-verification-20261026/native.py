"""Disposable native error/browser observations; all LLM replies are controlled."""
import json, os, secrets, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODE=sys.argv[1] if len(sys.argv)>1 else 'controlled'
if MODE not in ['controlled','browser']:raise SystemExit('controlled or browser only')
OUT=ROOT/'data/iteration-23-verification-20261026'/MODE
OUT.mkdir(parents=True,exist_ok=True)
NAME='tangerine-i23-verify-'+MODE
def call(args,check=True):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError('Owned setup failed; see '+str(OUT/'setup.log'))
 return p.stdout.strip()
password=secrets.token_hex(24);env=OUT/'private-runtime.env'
env.write_text(f'POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD={password}\nDATABASE_URL=postgres://tangerine:{password}@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=gemini-fixture\nMINIO_ROOT_PASSWORD={password}\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=gemini-fixture\nMINIO_SECRET_KEY={password}\nMINIO_BUCKET=regressions\nAPI_INTERNAL_TOKEN=listening-owned-token\nSPEECH_INTERNAL_TOKEN=actual-local-speech-test\nTANGERINE_GEMINI_EVIDENCE=/evidence\nTANGERINE_SPEECH_TEST_URL=http://speech:8090\nGEMINI_API_KEY=controlled-gemini-key\n')
env.chmod(0o600)
call(['docker','network','create',NAME])
for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i21-guided-media','minio')]:
 call(['docker','run','-d','--name',NAME+'-'+kind,'--network',NAME,'--network-alias',alias,'--env-file',str(env),image])
 for _ in range(100):
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  if subprocess.run(['docker','exec',NAME+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(.2)
 else:raise RuntimeError('Owned dependency unavailable: '+kind)
call(['docker','run','--rm','--network',NAME,'--env-file',str(env),'--entrypoint','/tangerine','tangerine-i23-verify-go','initialize'])
if MODE=='browser':
 (OUT/'provider-state').write_text('denied\n')
 call(['docker','run','-d','--name',NAME+'-speech','--network',NAME,'--network-alias','speech','--env-file',str(env),'-v',str(ROOT/'services/speech')+':/app:ro','-v','tangerine-local_speech-models:/models:ro','tangerine-local-speech:local'])
args=['docker','run','--rm','--name',NAME+'-api','--network',NAME,'--env-file',str(env),'-v',str(OUT)+':/evidence','-v',str(ROOT/'tests/native_gemini_test.go')+':/src/internal/app/native_gemini_test.go:ro','-v',str(ROOT/'tests/native_gemini_recovery_test.go')+':/src/internal/app/native_gemini_recovery_test.go:ro','-v',str(ROOT/'data/iteration-23-gemini-20261026/live')+':/reference:ro']
if MODE=='browser':args+=['-p','127.0.0.1:3523:8080']
pattern='^TestNativeGeminiBrowserRecovery$' if MODE=='browser' else '^TestNativeGeminiErrors$'
code=subprocess.run(args+['--entrypoint','go','tangerine-i23-verify-go','test','-json','-race','-count=1','-timeout=2h','-run',pattern,'./internal/app'],cwd=ROOT,stdout=(OUT/'native.jsonl').open('w'),stderr=(OUT/'native.stderr.log').open('w')).returncode
(OUT/'exit-code').write_text(str(code))
if MODE=='controlled':
 for kind in ['api','postgres','media']:call(['docker','rm','-f','-v',NAME+'-'+kind],check=False)
 call(['docker','network','rm',NAME],check=False)
raise SystemExit(code)
