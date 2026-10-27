"""Owned native supplement stack. Cached images, acquired bytes, no model access."""
import argparse,json,secrets,subprocess,sys,time,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027';CORPORA=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora');PG='postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826'
def call(args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()
def inputs():
 a=ROOT/'audit/corpus-acquisition-20261009';scopes=[]
 for name,id,version,receipt,origin in [
  ('edacc','EDACC','1.0-doi-7914','edacc-v10-current-receipt.json','https://doi.org/10.7488/ds/7914'),
  ('elrd','ELRD','7e4c8f377b8d5cedff7dd429eb2050084a6a1b08','elrd-owner-snapshot-receipt.json','https://github.com/uhh-lt/elrd'),
  ('dral-base','DRAL','16kHz-base','dral-16khz-receipt.json','https://www.cs.utep.edu/nigel/dral/'),
  ('dral-8','DRAL','8.0-fixes-plus-testdata','dral-latest-increment-receipt.json','https://www.cs.utep.edu/nigel/dral/')]:
  d=json.loads((OUT/(name+'-prepared.json')).read_text());r=json.loads((a/receipt).read_text());files=[dict(x,local='/members/'+name+'/'+x['path']) for x in d['files']]
  archive=Path(d['archive']);files.append(dict(path='original-containers/'+archive.name,local='/corpora/'+str(archive.relative_to(CORPORA)),bytes=archive.stat().st_size,sha256=r['sha256']))
  if name=='edacc':
   p=CORPORA/'edacc/CC_BY_SA_license_text.txt';r=json.loads((a/'edacc-current-license-receipt.json').read_text());files.append(dict(path='CC_BY_SA_license_text.txt',local='/corpora/edacc/'+p.name,bytes=p.stat().st_size,sha256=r['sha256']))
  scopes.append(dict(name=name,source_id=id,version=version,origin=origin,files=files))
 files=[]
 for p in sorted((CORPORA/'diplomat').rglob('*')):
  if p.is_file():
   relative=p.relative_to(CORPORA/'diplomat').as_posix();matches=[]
   for q in a.glob('diplomat-*-receipt.json'):
    r=json.loads(q.read_text())
    if r.get('path')==str(p) or r.get('local_path')==str(p) or r.get('destination')==str(p) or r.get('file')=='diplomat/'+relative:matches.append(r)
   files.append(dict(path=relative,local='/corpora/diplomat/'+relative,bytes=p.stat().st_size,sha256=matches[0]['sha256'] if len(matches)==1 else None))
 scopes.insert(2,dict(name='diplomat',source_id='DIPLOMAT',version='8fc673fd553378e3b34211820c3ebefdb892c67f',origin='https://huggingface.co/datasets/henry12348/DiPlomat/tree/8fc673fd553378e3b34211820c3ebefdb892c67f',files=files))
 (OUT/'admission-inputs.json').write_text(json.dumps(scopes,indent=2)+'\n')
def setup():
 name='tangerine-i37-'+uuid.uuid4().hex[:8];secret=secrets.token_hex(24);env=OUT/'private-runtime.env'
 env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+secret+'\nDATABASE_URL=postgres://tangerine:'+secret+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=i37-local\nMINIO_ROOT_PASSWORD='+secret+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=i37-local\nMINIO_SECRET_KEY='+secret+'\nMINIO_BUCKET=supplements\nAPI_INTERNAL_TOKEN=i37-local-test-token\nAPP_ORIGIN=http://localhost:3000\nGOWORK=off\nGOTOOLCHAIN=local\nGOPROXY=off\nGOSUMDB=off\n');env.chmod(0o600)
 (OUT/'stack.json').write_text(json.dumps(dict(name=name,scope='Owned supplement data only. No provider credentials or user ports.'),indent=2)+'\n')
 for image in [PG,'tangerine-i28-media','tangerine-i28-go']:call(['docker','image','inspect',image,'--format','{{.Id}}'])
 call(['docker','network','create','--internal',name])
 for suffix,image,alias in [('postgres',PG,'postgres'),('media','tangerine-i28-media','minio')]:
  call(['docker','run','--pull=never','-d','--name',name+'-'+suffix,'--network',name,'--network-alias',alias,'--env-file',str(env),image])
  probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if suffix=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
  for _ in range(120):
   if subprocess.run(['docker','exec',name+'-'+suffix,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
   time.sleep(.1)
  else:raise RuntimeError('Owned dependency unavailable')
 inputs();print('Owned supplement stack ready',flush=True)
def run(action):
 name=json.loads((OUT/'stack.json').read_text())['name']
 selected={'partitions':'^TestNativeSupplementPartitionPositive$','missing':'^TestNativeSupplementMissingNegative$','stale':'^TestNativeSupplementPersistenceNegative$','persistence':'^TestNativeSupplementPersistencePositive$','meaning':'^TestNativeSupplementReadbackPositive$','windows':'^TestNativeSupplementWindow','full':'^TestNativeSupplementFull','consumers':'^TestNativeSupplement(Consumer|Readback|Missing|Cursor|Views|Files|Persistence)','siblings':'^(TestNativeSourceSourcesPositive|TestNativeSource(?:Admitted|MappingCursor|Rights|NativeImport|Resume).*)$'}.get(action,'^TestNativeSupplementFull'+action.upper()+'$')
 shell='mkdir /native-src && cp -R /checked-src/. /native-src/ && cp /fixtures/native_source_test.go /fixtures/native_source_admitted_test.go /fixtures/native_source_mapping_cursor_test.go /fixtures/native_supplement_test.go /fixtures/native_supplement_consumers_test.go /native-src/internal/app/ && cd /native-src && exec go test -race -json -count=1 -timeout=2400s -run '+shlex.quote(selected)+' ./internal/app'
 argv=['docker','run','--pull=never','--rm','--name',name+'-'+action,'--network',name,'--env-file',str(OUT/'private-runtime.env'),'-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','-v',str(OUT/'members')+':/members:ro','-v',str(CORPORA)+':/corpora:ro','--entrypoint','sh','tangerine-i28-go','-c',shell]
 for suffix in ['.jsonl','.stderr','-exit-code','-command.json']:
  p=OUT/(action+suffix)
  if p.exists():p.rename(p.with_name(p.name+'.'+str(time.time_ns())))
 (OUT/(action+'-command.json')).write_text(json.dumps(argv,indent=2)+'\n')
 with (OUT/(action+'.jsonl')).open('w') as stdout,(OUT/(action+'.stderr')).open('w') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr)
 (OUT/(action+'-exit-code')).write_text(str(r.returncode));print(json.dumps(dict(action=action,exit_code=r.returncode)),flush=True);return r.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action');args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if args.action=='setup':
  if (OUT/'stack.json').exists():raise RuntimeError('Reuse recorded stack')
  setup()
 elif args.action=='inputs':inputs()
 elif args.action=='stop':
  name=json.loads((OUT/'stack.json').read_text())['name'];call(['docker','stop',name+'-postgres',name+'-media'])
 else:sys.exit(run(args.action))
