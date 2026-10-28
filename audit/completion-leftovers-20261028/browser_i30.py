"""Actual workspace frontend with the owned I30 API/store and controlled GET faults."""
import json,os,shutil,socket,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/completion-leftovers-20261028/i30'
OLD=ROOT/'data/iteration-30-release-20261027'
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
PREFIX='tangerine-completion-20261028'
def call(args):return subprocess.run(args,capture_output=True,text=True,check=True).stdout.strip()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'audit/iteration-30-release-20261027/readiness_forwarder.py',OLD/'fixtures/readiness_forwarder.py')
    state=json.loads((OLD/'stack.json').read_text());source=Path(state['source_root'])
    network=state['project']+'_egress'
    web=PREFIX+'-web';gateway=PREFIX+'-gateway'
    for name in [web,gateway]:
        subprocess.run(['docker','stop',name],capture_output=True)
        subprocess.run(['docker','rm',name],capture_output=True)
    call(['docker','run','--pull=never','-d','--name',web,'--network',network,'--env-file',str(source/'.env'),'--env-file',str(source/'data/config/runtime.env'),'-e','API_INTERNAL_URL=http://api:8080','-e','APP_ORIGIN=http://localhost:3000','-p','127.0.0.1::3000','tangerine-completion-web'])
    call(['docker','network','connect',state['project']+'_private',web])
    port=int(call(['docker','inspect','--format','{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}',web]))
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));browser_port=probe.getsockname()[1]
    url='http://localhost:'+str(browser_port)
    image=call(['docker','inspect','--format','{{.Config.Image}}',state['gateway']])
    call(['docker','run','--pull=never','-d','--name',gateway,'-v',str(OLD/'fixtures')+':/i30:ro','-e','I30_WEB_PORT='+str(port),'-e','I30_BROWSER_GATEWAY=1','-e','I30_BROWSER_ORIGIN='+url,'-p','127.0.0.1:'+str(browser_port)+':8088',image,'python','-B','/i30/readiness_forwarder.py'])
    (OUT/'source.json').write_text(json.dumps({'frontend':'Current workspace build, same native Settings/API owner contract','backend_archive_revision':state['archive_revision'],'test_store':state['project'],'user_app_untouched':True},indent=2)+'\n')
    try:
        env={**os.environ,'TANGERINE_PLAYWRIGHT_MODULE':str(NODE.parent.parent/'node_modules/playwright'),'I30_URL':url,'I30_OUTPUT':str(OUT)}
        with (OUT/'browser.log').open('w') as log:r=subprocess.run([str(NODE),str(ROOT/'tests/completion_leftovers_i30.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=240)
        (OUT/'exit-code').write_text(str(r.returncode)+'\n');return r.returncode
    finally:
        for name in [gateway,web]:call(['docker','stop',name])

if __name__=='__main__':raise SystemExit(main())
