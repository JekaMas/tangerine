"""Owned minimal PostgreSQL/MinIO and installed-local Go owners; never pull."""
from pathlib import Path
import json, os, secrets, subprocess, threading, time, urllib.request, uuid
import argparse

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-34-local-generation-20261027'

def call(args, check=True):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    with (OUT/'setup.log').open('a') as f:f.write(p.stdout+p.stderr)
    if check and p.returncode:raise RuntimeError('Owned native command failed; see setup.log')
    return p.stdout.strip()

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['baseline','repair','final','repaired','deadline-profile','qwen-repaired','projection-replay','controlled','controlled-deadline'],default='baseline');args=parser.parse_args()
    if args.variant!='baseline':OUT=OUT/args.variant
    OUT.mkdir(exist_ok=True,parents=True)
    if (OUT/'observations.json').exists():raise RuntimeError('Retain existing observations; no accidental redispatch')
    name='tangerine-i34-'+uuid.uuid4().hex[:8]
    for image in ['tangerine-i28-go','tangerine-i28-media','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826']:
        call(['docker','image','inspect',image,'--format','{{.Id}}'])
    password=secrets.token_hex(24);env=OUT/'private-runtime.env'
    env.write_text('POSTGRES_DB=tangerine\nPOSTGRES_USER=tangerine\nPOSTGRES_PASSWORD='+password+'\nDATABASE_URL=postgres://tangerine:'+password+'@postgres:5432/tangerine?sslmode=disable\nMINIO_ROOT_USER=i34-local\nMINIO_ROOT_PASSWORD='+password+'\nMINIO_ENDPOINT=minio:9000\nMINIO_ACCESS_KEY=i34-local\nMINIO_SECRET_KEY='+password+'\nMINIO_BUCKET=regressions\nTANGERINE_GEMINI_EVIDENCE=/evidence\nTANGERINE_LOCAL_LIVE=1\nGOWORK=off\n');env.chmod(0o600)
    (OUT/'stack.json').write_text(json.dumps({'name':name,'origin':'owned disposable test dependencies; no ports or persistent user volumes'},indent=2)+'\n')
    stop=threading.Event()
    def sample():
        with (OUT/'resources.jsonl').open('a') as f:
            while not stop.is_set():
                row={'time':time.time()}
                try:
                    with urllib.request.urlopen('http://127.0.0.1:11434/api/ps',timeout=3) as r:row['ollama']=json.load(r)
                    ps=subprocess.run(['ps','-axo','pid,rss,pcpu,comm'],capture_output=True,text=True,timeout=3)
                    row['processes']=[s for s in ps.stdout.splitlines() if 'ollama' in s.lower() or 'mlx' in s.lower()]
                except Exception as e:row['observation_error']=type(e).__name__
                f.write(json.dumps(row)+'\n');f.flush();stop.wait(2)
    thread=threading.Thread(target=sample,daemon=True)
    try:
        call(['docker','network','create',name])
        for kind,image,alias in [('postgres','postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826','postgres'),('media','tangerine-i28-media','minio')]:
            call(['docker','run','--pull=never','-d','--name',name+'-'+kind,'--network',name,'--network-alias',alias,'--env-file',str(env),image])
            for _ in range(100):
                probe=['pg_isready','-h','127.0.0.1','-U','tangerine','-d','tangerine'] if kind=='postgres' else ['/usr/local/bin/probe','http://127.0.0.1:9000/minio/health/ready']
                if subprocess.run(['docker','exec',name+'-'+kind,*probe],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
                time.sleep(.2)
            else:raise RuntimeError('Owned dependency unavailable')
        call(['docker','run','--pull=never','--rm','--network',name,'--env-file',str(env),'--entrypoint','/tangerine','tangerine-i28-go','initialize'])
        plan={'repair':'REPAIR-PLAN.json','final':'FINAL-PLAN.json','repaired':'REPAIRED-PLAN.json','deadline-profile':'DEADLINE-PROFILE-PLAN.json','qwen-repaired':'QWEN-REPAIRED-PLAN.json','projection-replay':'QWEN-REPAIRED-PLAN.json'}.get(args.variant,'PLAN.json')
        test='^TestNativeLocalGenerationComparison$' if not args.variant.startswith('controlled') else '^TestNativeLocalGenerationFailureModes$'
        if args.variant=='controlled-deadline':test='^TestNativeLocalGenerationFailureModes$/^deadline$'
        if args.variant=='projection-replay':test='^TestNativeLocalGenerationProjectionReplay$'
        copies='native_gemini_test.go native_local_generation_test.go'
        if args.variant.startswith('controlled'):copies+=' native_preparation_test.go native_mutation_test.go native_local_generation_failures_test.go'
        if args.variant=='projection-replay':copies+=' native_local_generation_replay_test.go'
        command='cp -R /checked-src/. /src/ && '+''.join('cp /fixtures/'+f+' /src/internal/app/ && ' for f in copies.split())+'exec go test -json -race -count=1 -timeout=23m -run '+test+' ./internal/app'
        command_args=['docker','run','--pull=never','--rm','--name',name+'-api','--network',name,'--add-host','ollama:host-gateway','--env-file',str(env),'-v',str(OUT)+':/evidence','-v',str(ROOT/'data/iteration-34-local-generation-20261027')+':/recorded:ro','-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(Path(__file__).parent/plan)+':/plan/PLAN.json:ro','--entrypoint','sh','tangerine-i28-go','-c',command]
        (OUT/'native-command.json').write_text(json.dumps(command_args,indent=2)+'\n')
        thread.start()
        with (OUT/'native.jsonl').open('w') as stdout,(OUT/'native.stderr').open('w') as stderr:
            code=subprocess.run(command_args,cwd=ROOT,stdout=stdout,stderr=stderr).returncode
        (OUT/'native-exit-code').write_text(str(code))
        if code:raise RuntimeError('Actual native owner harness failed; see native output')
    finally:
        stop.set()
        if thread.is_alive():thread.join(timeout=5)
        for kind in ['api','postgres','media']:call(['docker','rm','-f','-v',name+'-'+kind],False)
        call(['docker','network','rm',name],False)
        (OUT/'cleanup.json').write_text(json.dumps({'owned_stack':name,'remaining':call(['docker','ps','-aq','--filter','name='+name])})+'\n')

if __name__=='__main__':main()
