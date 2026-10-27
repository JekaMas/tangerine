"""Private durable native import runner, cached dependencies, no provider keys."""
import argparse,json,secrets,subprocess,sys,time,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-36-jfleg-20261027'
PG='postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826'

def call(args):
    result=subprocess.run(args,capture_output=True,text=True,check=True)
    return result.stdout.strip()

def setup():
    name='tangerine-i36-'+uuid.uuid4().hex[:8];secret=secrets.token_hex(24)
    env=OUT/'private-runtime.env'
    env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+secret+'\nDATABASE_URL=postgres://tangerine:'+secret+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=i36-local\nMINIO_ROOT_PASSWORD='+secret+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=i36-local\nMINIO_SECRET_KEY='+secret+'\nMINIO_BUCKET=jfleg\nAPI_INTERNAL_TOKEN=i36-local-test-token\nAPP_ORIGIN=http://localhost:3000\nGOWORK=off\nGOTOOLCHAIN=local\nGOPROXY=off\nGOSUMDB=off\n');env.chmod(0o600)
    (OUT/'stack.json').write_text(json.dumps(dict(name=name,scope='Private disposable JFLEG only; no user data/ports or provider credentials.'),indent=2)+'\n')
    for image in [PG,'tangerine-i28-media','tangerine-i28-go']:call(['docker','image','inspect',image,'--format','{{.Id}}'])
    call(['docker','network','create','--internal',name])
    for suffix,image,alias in [('postgres',PG,'postgres'),('media','tangerine-i28-media','minio')]:
        call(['docker','run','--pull=never','-d','--name',name+'-'+suffix,'--network',name,'--network-alias',alias,'--env-file',str(env),image])
        probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if suffix=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
        for _ in range(120):
            result=subprocess.run(['docker','exec',name+'-'+suffix,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if result.returncode==0:break
            time.sleep(.1)
        else:raise RuntimeError('Owned dependency unavailable')
    print('Owned private JFLEG dependencies ready',flush=True)

def run(action):
    name=json.loads((OUT/'stack.json').read_text())['name']
    selected={'metadata':'^TestNativeJFLEGConsumerPositive$','partial':'^TestNativeJFLEGPartialNegative$','completeness':'^TestNativeJFLEGCompleteness','evaluation':'^TestNativeJFLEGLab','status':'^TestNativeSourceSourcesPositive$','full':'^TestNativeJFLEGFull$','consumers':'^TestNativeJFLEG(Consumer|Reference|Cursor|Lab)','regression':'^(TestNativeSourceSources|TestNativeSourceNativeImport|TestNativeSourceResume|TestNativeSourceRights|TestNativeSourceAdmitted|TestNativeSourceMappingCursor)'}[action]
    shell='mkdir /native-src && cp -R /checked-src/. /native-src/ && cp /fixtures/native_source_test.go /fixtures/native_source_admitted_test.go /fixtures/native_source_mapping_cursor_test.go /fixtures/native_jfleg_test.go /fixtures/native_jfleg_consumers_test.go /native-src/internal/app/ && cd /native-src && exec go test -race -json -count=1 -timeout=240s -run '+shlex.quote(selected)+' ./internal/app'
    argv=['docker','run','--pull=never','--rm','--name',name+'-'+action,'--network',name,'--env-file',str(OUT/'private-runtime.env'),'-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','-v','/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/jfleg:/corpus:ro','--entrypoint','sh','tangerine-i28-go','-c',shell]
    for suffix in ['.jsonl','.stderr','-exit-code','-command.json']:
        p=OUT/(action+suffix)
        if p.exists():p.rename(p.with_name(p.name+'.'+str(time.time_ns())))
    (OUT/(action+'-command.json')).write_text(json.dumps(argv,indent=2)+'\n')
    with (OUT/(action+'.jsonl')).open('w') as stdout,(OUT/(action+'.stderr')).open('w') as stderr:result=subprocess.run(argv,stdout=stdout,stderr=stderr)
    (OUT/(action+'-exit-code')).write_text(str(result.returncode));print(json.dumps(dict(action=action,exit_code=result.returncode)),flush=True)
    return result.returncode

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['setup','full','consumers','regression','status','evaluation','completeness','partial','metadata','stop']);args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if args.action=='setup':
        if (OUT/'stack.json').exists():raise RuntimeError('Owned stack already recorded; reuse it')
        setup();return 0
    if args.action=='stop':
        name=json.loads((OUT/'stack.json').read_text())['name'];call(['docker','stop',name+'-postgres',name+'-media']);return 0
    return run(args.action)
if __name__=='__main__':sys.exit(main())
