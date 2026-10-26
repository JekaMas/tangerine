"""Disposable I22 native owner fixture. Explicit live flag uses existing Free only."""
from pathlib import Path
import os,secrets,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
MODE=sys.argv[1] if len(sys.argv)>1 else 'controlled'
LIVE=MODE=='live'
OUT=ROOT/'data/iteration-22-elevenlabs-20261026'/MODE
OUT.mkdir(parents=True,exist_ok=True)
NAME='tangerine-i22-'+MODE

def call(args, check=True):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError('I22 owned setup failed; see '+str(OUT/'setup.log'))
 return p.stdout.strip()

password=secrets.token_hex(24)
config=OUT/'private-runtime.env'
config.write_text(f'POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD={password}\nDATABASE_URL=postgres://tangerine:{password}@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=elevenlabs-fixture\nMINIO_ROOT_PASSWORD={password}\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=elevenlabs-fixture\nMINIO_SECRET_KEY={password}\nMINIO_BUCKET=regressions\nAPI_INTERNAL_TOKEN=listening-owned-token\nSPEECH_INTERNAL_TOKEN=actual-local-speech-test\nTANGERINE_ELEVENLABS_EVIDENCE=/evidence\nTANGERINE_SPEECH_TEST_URL=http://speech:8090\nTANGERINE_ELEVENLABS_ENDPOINT={"https://api.elevenlabs.io" if LIVE else "http://provider:8092"}\nTANGERINE_ELEVENLABS_LIVE={"1" if LIVE else "0"}\nTANGERINE_ELEVENLABS_BROWSER={"1" if LIVE else "0"}\n')
config.chmod(0o600)
if LIVE:
 # Admission is explicit test setup; production has no repeated stored-data checks.
 import json,urllib.request
 key=(ROOT/'data/speech-comparison-20261022/private/elevenlabs.key').read_text().strip()
 req=urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':key})
 with urllib.request.urlopen(req,timeout=30) as response:sub=json.load(response)
 (OUT/'subscription-before.json').write_text(json.dumps(sub))
 if not (sub['tier']=='free' and not sub['can_extend_character_limit'] and not sub['allowed_to_extend_character_limit'] and sub.get('max_credit_limit_extension')==0 and sub['character_limit']-sub['character_count']>=300):raise RuntimeError('Live Free allowance/overage admission unavailable')
 with config.open('a') as f:f.write('ELEVENLABS_API_KEY='+key+'\n')
else:
 with config.open('a') as f:f.write('ELEVENLABS_API_KEY=controlled-provider-key\n')
call(['docker','network','create',NAME])
for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i21-guided-media','minio')]:
 call(['docker','run','-d','--name',NAME+'-'+kind,'--network',NAME,'--network-alias',alias,'--env-file',str(config),image])
 for _ in range(90):
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  if subprocess.run(['docker','exec',NAME+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(.2)
 else:raise RuntimeError('Owned '+kind+' unavailable')
call(['docker','run','--rm','--network',NAME,'--env-file',str(config),'--entrypoint','/tangerine','tangerine-i22-go','initialize'])
common=['--network',NAME,'--env-file',str(config),'-v',str(ROOT/'services/speech')+':/app:ro','-v',str(OUT)+':/evidence']
if not LIVE:call(['docker','run','-d','--name',NAME+'-provider','--network-alias','provider',*common,'-v',str(ROOT/'data/iteration-22-elevenlabs-20261026/controlled-provider.py')+':/controlled-provider.py:ro','--entrypoint','python','tangerine-local-speech:local','/controlled-provider.py'])
call(['docker','run','-d','--name',NAME+'-speech','--network-alias','speech',*common,'tangerine-local-speech:local'])
args=['docker','run','--rm','--name',NAME+'-api','--network',NAME,'--env-file',str(config),'-p','127.0.0.1:3389:8080','-v',str(OUT)+':/evidence']
for source in ['native_preparation_test.go','native_mutation_test.go','native_speech_test.go','native_listening_test.go','native_interpretation_test.go','native_elevenlabs_test.go']:
 args+=['-v',str(ROOT/'tests'/source)+':/src/internal/app/'+source+':ro']
p=subprocess.Popen(args+['--entrypoint','go','tangerine-i22-go','test','-json','-race','-count=1','-timeout=2h','-run','^TestNativeElevenLabsFlow$','./internal/app'],cwd=ROOT,stdout=(OUT/'native.jsonl').open('w'),stderr=(OUT/'native.stderr.log').open('w'))
(OUT/'process.pid').write_text(str(p.pid))
code=p.wait();(OUT/'exit-code').write_text(str(code))
if not LIVE:
 for kind in ['api','speech','provider','postgres','media']:call(['docker','rm','-f','-v',NAME+'-'+kind],check=False)
 call(['docker','network','rm',NAME],check=False)
raise SystemExit(code)
