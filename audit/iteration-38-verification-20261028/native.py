"""Focused I38 HTTP validation/recovery through private real storage; no models."""
import argparse,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-38-verification-20261028'
STORE=ROOT/'data/iteration-38-empirical-20261027'

def main():
    p=argparse.ArgumentParser();p.add_argument('phase');p.add_argument('--select',default='^TestImportedHTTP(ValidationNegative|RecoveryPositive)$');args=p.parse_args()
    name=json.loads((STORE/'stack.json').read_text())['name']
    subprocess.run(['docker','start',name+'-postgres',name+'-media'],check=True,capture_output=True)
    selected=args.select
    shell='mkdir /i38-verify && cp -R /checked/. /i38-verify/ && cp /fixtures/native_source_test.go /fixtures/native_imported_reports_test.go /fixtures/native_imported_reports_verification_test.go /i38-verify/internal/app/ && cd /i38-verify && exec go test -race -json -count=1 -timeout=240s -run '+shlex.quote(selected)+' ./internal/app'
    command=['docker','run','--pull=never','--rm','--name',name+'-verification-'+args.phase,'--network',name,'--env-file',str(STORE/'private-runtime.env'),'-v',str(ROOT/'services/api')+':/checked:ro','-v',str(ROOT/'tests')+':/fixtures:ro','--entrypoint','sh','tangerine-i28-go','-c',shell]
    (OUT/(args.phase+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
    with (OUT/(args.phase+'.jsonl')).open('w') as stdout,(OUT/(args.phase+'.stderr')).open('w') as stderr:
        result=subprocess.run(command,stdout=stdout,stderr=stderr)
    (OUT/(args.phase+'-exit-code')).write_text(str(result.returncode)+'\n')
    print(json.dumps({'phase':args.phase,'exit_code':result.returncode}))
    return result.returncode

if __name__=='__main__':raise SystemExit(main())
