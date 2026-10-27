"""New small native UI fixtures, against the retained owned I36 dependencies."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-36-verification-20261027';PRIOR=ROOT/'data/iteration-36-jfleg-20261027';phase='commit' if '--commit' in sys.argv else 'fixtures'
name=json.loads((PRIOR/'stack.json').read_text())['name'];OUT.mkdir(exist_ok=True)
selector='TestNativeJFLEGVerifyCommitFixtures' if phase=='commit' else 'TestNativeJFLEGVerifyUIFixtures'
shell='mkdir /native-src && cp -R /checked-src/. /native-src/ && cp /fixtures/native_source_test.go /fixtures/native_jfleg_test.go /fixtures/native_jfleg_verify_test.go /native-src/internal/app/ && cd /native-src && exec go test -race -json -count=1 -timeout=120s -run ^'+selector+'$ ./internal/app'
args=['docker','run','--pull=never','--rm','--network',name,'--env-file',str(PRIOR/'private-runtime.env'),'-v',str(ROOT/'services/api')+':/checked-src:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','--entrypoint','sh','tangerine-i28-go','-c',shell]
prefix='native-commit' if phase=='commit' else 'native'
(OUT/(prefix+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
with (OUT/(prefix+'.jsonl')).open('w') as stdout,(OUT/(prefix+'.stderr')).open('w') as stderr:result=subprocess.run(args,stdout=stdout,stderr=stderr)
(OUT/(prefix+'-exit-code')).write_text(str(result.returncode));print(json.dumps({'new_native_case_exit':result.returncode}));sys.exit(result.returncode)
