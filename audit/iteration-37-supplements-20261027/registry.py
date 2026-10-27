"""Reobserve only the changed JFLEG registry assertion on retained private data."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027/jfleg-registry';OLD=ROOT/'data/iteration-36-jfleg-20261027'
name=json.loads((OLD/'stack.json').read_text())['name'];OUT.mkdir(parents=True,exist_ok=True)
for file in ['fixture.json','native-expected.json']:(OUT/file).write_bytes((OLD/file).read_bytes())
started=[]
for suffix in ['postgres','media']:
 container=name+'-'+suffix
 running=subprocess.check_output(['docker','inspect','--format','{{.State.Running}}',container],text=True).strip()=='true'
 if not running:subprocess.run(['docker','start',container],capture_output=True,check=True);started.append(container)
shell='mkdir /i37-registry-src && cp -R /checked/. /i37-registry-src/ && cp /fixtures/native_source_test.go /fixtures/native_jfleg_test.go /fixtures/native_jfleg_consumers_test.go /i37-registry-src/internal/app/ && cd /i37-registry-src && exec go test -race -json -count=1 -timeout=240s -run "^TestNativeJFLEGConsumerPositive$" ./internal/app'
args=['docker','run','--pull=never','--rm','--network',name,'--env-file',str(OLD/'private-runtime.env'),'-v',str(ROOT/'services/api')+':/checked:ro','-v',str(ROOT/'tests')+':/fixtures:ro','-v',str(OUT)+':/evidence','--entrypoint','sh','tangerine-i28-go','-c',shell]
for file in ['native.jsonl','native.stderr','exit-code','command.json']:
 p=OUT/file
 if p.exists():p.rename(p.with_name('initial-mkdir-failure-'+p.name))
(OUT/'command.json').write_text(json.dumps(args,indent=2)+'\n')
try:
 with (OUT/'native.jsonl').open('w') as so,(OUT/'native.stderr').open('w') as se:r=subprocess.run(args,stdout=so,stderr=se)
 (OUT/'exit-code').write_text(str(r.returncode));print('Affected retained JFLEG consumer exit',r.returncode,flush=True)
finally:
 if started:subprocess.run(['docker','stop',*started],capture_output=True,check=True)
