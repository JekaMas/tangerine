"""Durable disposable real PostgreSQL/MinIO harness; cached images only."""
import argparse,json,secrets,subprocess,time,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-35-official-l2-20261027'
PG='postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826'

def call(args,check=True):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
    if check and p.returncode:raise RuntimeError('Owned command failed; see private setup.log')
    return p.stdout.strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['setup','regression','import','inspect','targeted','tiers','versions','counts','clock','repair-clock','cursor','multi','extent-unit','repair-extents','quality','cleanup']);args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    state=OUT/'stack.json';env=OUT/'private-runtime.env'
    if args.action=='setup':
        if state.exists():raise RuntimeError('Owned stack already recorded; resume it')
        for image in ['tangerine-i28-go','tangerine-i28-media',PG]:call(['docker','image','inspect',image,'--format','{{.Id}}'])
        name='tangerine-i35-'+uuid.uuid4().hex[:8];password=secrets.token_hex(24)
        env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+password+'\nDATABASE_URL=postgres://tangerine:'+password+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=i35-local\nMINIO_ROOT_PASSWORD='+password+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=i35-local\nMINIO_SECRET_KEY='+password+'\nMINIO_BUCKET=official-l2\nGOWORK=off\nGOTOOLCHAIN=local\nGOPROXY=off\nGOSUMDB=off\n');env.chmod(0o600)
        state.write_text(json.dumps(dict(name=name,scope='Disposable native import only. No user volumes/ports or hosted calls.'))+'\n')
        call(['docker','network','create',name])
        for kind,image,alias in [('postgres',PG,'postgres'),('media','tangerine-i28-media','minio')]:
            call(['docker','run','--pull=never','-d','--name',name+'-'+kind,'--network',name,'--network-alias',alias,'--env-file',str(env),image])
            for _ in range(100):
                probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
                if subprocess.run(['docker','exec',name+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
                time.sleep(.2)
            else:raise RuntimeError('Owned dependency not ready')
        call(['docker','run','--pull=never','--rm','--network',name,'--env-file',str(env),'--entrypoint','/tangerine','tangerine-i28-go','initialize'])
        print(json.dumps(dict(name=name,state='ready')));return
    name=json.loads(state.read_text())['name']
    if args.action=='cleanup':
        for suffix in ['import','regression','inspect','postgres','media']:call(['docker','rm','-f','-v',name+'-'+suffix],False)
        call(['docker','network','rm',name],False);(OUT/'cleanup.json').write_text(json.dumps(dict(owned_stack=name,remaining=call(['docker','ps','-aq','--filter','name='+name])))+'\n');return
    copies=['native_source_test.go','native_source_admitted_test.go','native_official_l2_test.go','native_source_l2_speakers_test.go','native_source_counts_recovery_test.go','native_source_mapping_cursor_test.go']
    selected={'import':'^TestNativeOfficialL2Full$','inspect':'^TestNativeOfficialL2Readback$','quality':'^TestNativeOfficialL2QualityReadback$', 'extent-unit':'^TestSource(AcousticBounds|L2AncillaryTier)', 'repair-extents':'^TestNativeOfficialL2RepairExtents$', 'multi':'^TestNativeSourceMappingMemberTablePositive$', 'cursor':'^TestNativeSourceMappingCursor', 'clock':'^TestSource(SerializedClock|AcousticBounds)', 'repair-clock':'^TestNativeOfficialL2RepairClock$', 'counts':'^TestNativeSourceCount', 'versions':'^(TestNativeSourceL2SpeakerMetadata|TestSourceCorpus)', 'tiers':'^TestSource(L2AncillaryTier|AcousticBounds)', 'targeted':'^(TestSourceL2SpeakerProjection|TestNativeSourceL2SpeakerMetadata|TestSourceL2AncillaryTier)', 'regression':'^(TestNativeSource(Admitted|Intake|NativeImport|Resume|Cancel|FullScope|L2)|TestSourceL2SpeakerProjection|TestL2SpeakerTable|TestSourceTextGrid)' }[args.action]
    command='cp -R /checked-src/. /src/ && '+''.join('cp /fixtures/'+f+' /src/internal/app/ && ' for f in copies)+'exec go test -json -race -count=1 -timeout=8h -run '+shlex.quote(selected)+' ./internal/app'+(' ./internal/source' if args.action=='regression' else '')
    argv=['docker','run','--pull=never','--rm','--name',name+'-'+args.action,'--network',name,'--env-file',str(env),'-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','-v',str(Path(__file__).parent/'PLAN.json')+':/plan/PLAN.json:ro','-v',str(ROOT/'data/iteration-27-sources-20261026/research/l2-official-members.json')+':/admission/members.json:ro','-v','/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/l2-arctic:/corpus:ro','--entrypoint','sh','tangerine-i28-go','-c',command]
    (OUT/(args.action+'-command.json')).write_text(json.dumps(argv,indent=2)+'\n')
    # Preserve failed observations when repairing. The database and accepted objects
    # survive test processes so a repair does not repeat admission/copy.
    log=OUT/(args.action+'.jsonl')
    if log.exists():log.rename(OUT/(args.action+'-previous-'+str(time.time_ns())+'.jsonl'))
    with log.open('w') as out,(OUT/(args.action+'.stderr')).open('w') as err:code=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err).returncode
    (OUT/(args.action+'-exit-code')).write_text(str(code));print(json.dumps(dict(action=args.action,exit_code=code)))
    if code:raise SystemExit(code)
if __name__=='__main__':main()
