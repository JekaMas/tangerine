"""Owned empirical report observations; no providers, downloads or installations."""
import argparse,json,secrets,subprocess,sys,time,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-38-empirical-20261027'
PG='postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826'
def call(args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()
def setup():
    name='tangerine-i38-'+uuid.uuid4().hex[:8];secret=secrets.token_hex(24)
    env=OUT/'private-runtime.env'
    env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+secret+'\nDATABASE_URL=postgres://tangerine:'+secret+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=i38-local\nMINIO_ROOT_PASSWORD='+secret+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=i38-local\nMINIO_SECRET_KEY='+secret+'\nMINIO_BUCKET=empirical\nAPI_INTERNAL_TOKEN=i38-local-test-token\nAPP_ORIGIN=http://localhost:3000\nGOWORK=off\nGOTOOLCHAIN=local\nGOPROXY=off\nGOSUMDB=off\n');env.chmod(0o600)
    (OUT/'stack.json').write_text(json.dumps(dict(name=name,scope='Private disposable empirical report only; no user data/ports or provider credentials.'),indent=2)+'\n')
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
    print('Owned private empirical report dependencies ready',flush=True)

def run(action,which='38'):
 folder=ROOT/('data/iteration-'+which+'-'+{'38':'empirical','35':'official-l2','36':'jfleg','37':'supplements'}[which]+'-20261027')
 name=json.loads((folder/'stack.json').read_text())['name']
 call(['docker','start',name+'-postgres',name+'-media'])
 evidence=OUT/('native-'+which);evidence.mkdir(parents=True,exist_ok=True)
 selected='^TestImported'+('AcquireAvailable$' if action.startswith('acquire-') else 'ActualReports$' if action.startswith('actual') else '(Coverage|Speech|CataloguePositive)' if action=='final-consumers' else 'CataloguePositive$' if action=='catalogue' else 'PersistenceNegative$' if action=='missing' else '(Speech|PersistencePositive)' if action=='repair' else '(Catalogue|Writing|Persistence|Speech|Coverage)')
 race='' if action.startswith('acquire-') else '-race '
 shell='mkdir /i38-src && cp -R /checked/. /i38-src/ && cp /fixtures/native_source_test.go /fixtures/native_imported_reports_test.go /i38-src/internal/app/ && cd /i38-src && exec go test '+race+'-json -count=1 -timeout=2400s -run '+shlex.quote(selected)+' ./internal/app'
 source={'acquire-fce':'FCE-2.1','acquire-wi':'WILOCNESS-2.1','acquire-speech':'SPEECHOCEAN762','actual-fce':'FCE-2.1','actual-wi':'WILOCNESS-2.1','actual-speech':'SPEECHOCEAN762'}.get(action,'')
 argv=['docker','run','--pull=never','--rm','--name',name+'-i38-'+action,'--network',name,'--env-file',str(folder/'private-runtime.env'),'-e','I38_EVIDENCE=/evidence','-e','I38_SOURCE='+source,'-v',str(ROOT/'services/api')+':/checked:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(evidence)+':/evidence','-v','/Users/jekamas/projects/0xatelerix/tangerine/data/corpora:/corpora:ro','--entrypoint','sh','tangerine-i28-go','-c',shell]
 stem=action+'-'+which
 for ext in ['.jsonl','.stderr','-exit-code','-command.json']:
  p=OUT/(stem+ext)
  if p.exists():p.rename(p.with_name(p.name+'.'+str(time.time_ns())))
 (OUT/(stem+'-command.json')).write_text(json.dumps(argv,indent=2)+'\n')
 with (OUT/(stem+'.jsonl')).open('w') as stdout,(OUT/(stem+'.stderr')).open('w') as stderr:r=subprocess.run(argv,stdout=stdout,stderr=stderr)
 (OUT/(stem+'-exit-code')).write_text(str(r.returncode));print(json.dumps(dict(action=stem,exit_code=r.returncode)),flush=True);return r.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('--store',default='38');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.action=='setup':
  if (OUT/'stack.json').exists():raise RuntimeError('Reuse recorded owned storage')
  setup()
 else:sys.exit(run(a.action,a.store))
