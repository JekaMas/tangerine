"""Authorized main publication and actual Docker-only GitHub source ZIP proof.

Current source and original historical counterexamples remain distinct. This is
source distribution and disposable local qualification, never app deployment.
"""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/completion-leftovers-20261028/release';OLD=ROOT/'data/iteration-30-release-20261027';CANONICAL=Path('/Users/jekamas/projects/0xatelerix/tangerine');GAPS='audit/spec-fullness-20261008/GAPS.md'
CLIENT=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def call(args,cwd=ROOT):
 r=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=240)
 if r.returncode:raise RuntimeError('Release command failed: '+r.stderr[:500])
 return r.stdout.strip()
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def preserve(before):
 status=call(['git','status','--porcelain'],CANONICAL);assert status.strip()=='M '+GAPS,status
 file=(CANONICAL/GAPS).read_bytes();diff=call(['git','diff','--binary','--',GAPS],CANONICAL).encode()
 data=dict(protected_file_sha256=hashlib.sha256(file).hexdigest(),protected_diff_sha256=hashlib.sha256(diff).hexdigest())
 containers=call(['docker','ps','--format','{{.Names}}']).splitlines()
 if before:
  data.update(canonical_status_before=status,user_containers=sorted(n for n in containers if n.startswith('tangerine-local-')))
  (OUT/'protected-GAPS-before').write_bytes(file);(OUT/'protected-GAPS-diff-before').write_bytes(diff)
 else:data.update(canonical_status_after=status,running_containers=sorted(containers))
 write('preservation-before.json' if before else 'preservation-after.json',data)
def publish():
 OUT.mkdir(parents=True,exist_ok=True);preserve(True)
 target=call(['git','rev-parse','HEAD']);assert not call(['git','status','--porcelain']),'Commit reviewed changes before publication'
 call(['git','fetch','origin','main']);call(['git','merge-base','--is-ancestor','origin/main',target]);call(['git','merge-base','--is-ancestor','main',target])
 assert not call(['git','diff','main',target,'--',GAPS]),'Protected path overlaps release'
 call(['git','merge','--ff-only',target],CANONICAL)
 with (OUT/'push.log').open('w') as log:
  result=subprocess.run(['git','push','origin','main:main'],cwd=CANONICAL,stdout=log,stderr=log,timeout=240)
 if result.returncode:raise RuntimeError('Publication failed; inspect retained push log')
 remote=call(['git','ls-remote','origin','refs/heads/main']).split()[0];github=call(['gh','api','repos/JekaMas/tangerine/commits/main','--jq','.sha'])
 repo=json.loads(call(['gh','repo','view','JekaMas/tangerine','--json','nameWithOwner,isPrivate,defaultBranchRef,url']));assert remote==github==target and not repo['isPrivate']
 url='https://api.github.com/repos/JekaMas/tangerine/zipball/'+target;destination=OUT/'published-source.zip'
 with CLIENT.open(urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'Tangerine-source-acceptance'}),timeout=120) as response,destination.open('wb') as output:shutil.copyfileobj(response,output)
 public='https://github.com/JekaMas/tangerine/archive/refs/heads/main.zip'
 with CLIENT.open(urllib.request.Request(public,headers={'User-Agent':'Tangerine-source-acceptance'}),timeout=120) as response,(OUT/'public-main.zip').open('wb') as output:shutil.copyfileobj(response,output)
 write('publication.json',dict(repository=repo['nameWithOwner'],visibility='PUBLIC',default_branch=repo['defaultBranchRef']['name'],repository_url=repo['url'],published_revision=target,remote_main=remote,github_main=github,archive_revision=target,archive_file=destination.name,archive_url=url,archive_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),push_exit=0,unauthenticated_archive_url=public))
 for name in ['launcher-negative.json','native-origin-fixture-failure.json','native-header-fixture-failure.json','readiness-header-discriminator.json']:
  shutil.copy2(OLD/name,OUT/name)
 write('REUSE.json',dict(historical_directory=str(OLD.relative_to(ROOT)),files=['launcher-negative.json','native-origin-fixture-failure.json','native-header-fixture-failure.json','readiness-header-discriminator.json'],boundary='Original literal damaged-source, wrong-origin and missing-response-header failures retain their original date/source. Launcher and response-identity semantics are unchanged. New origin-case HTTP regressions and current ZIP startup/UI are observed separately.',new_inference=0))
 preserve(False);print(json.dumps(dict(published_revision=target,repository=repo['url'],archives='Actual immutable and unauthenticated main ZIPs downloaded')))
def native_owner():
 spec=importlib.util.spec_from_file_location('retained_i30_native_release',ROOT/'audit/iteration-30-release-20261027/native_release.py');owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner);owner.DATA=OUT;return owner
def observe_identity():
 state=json.loads((OUT/'stack.json').read_text());native=json.loads((OUT/'native.json').read_text());source=Path(state['source_root']);values=dict(line.split('=',1) for line in (source/'data/config/runtime.env').read_text().splitlines() if '=' in line)
 with CLIENT.open(state['origin_url']+'/health/ready',timeout=15) as response:observed=response.headers.get('X-Tangerine-Instance')
 native['public_identity_matches']=observed==hashlib.sha256(values['API_INTERNAL_TOKEN'].encode()).hexdigest()
 env=call(['docker','inspect','--format','{{range .Config.Env}}{{println .}}{{end}}',state['project']+'-api-1']);native['actual_api_origin']=next(line.split('=',1)[1] for line in env.splitlines() if line.startswith('APP_ORIGIN='))
 assert native['public_identity_matches'] and native['actual_api_origin']=='http://localhost:3000';write('native.json',native)
def browser():
 state=json.loads((OUT/'stack.json').read_text());node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
 env={**os.environ,'I30_URL':state['origin_url'],'I30_OUTPUT':str(OUT),'TANGERINE_PLAYWRIGHT_MODULE':str(node.parent.parent/'node_modules/playwright')}
 with (OUT/'browser.log').open('w') as log:r=subprocess.run([str(node),str(ROOT/'tests/completion_leftovers_i30.cjs')],cwd=ROOT,env=env,stdout=log,stderr=log,timeout=240)
 (OUT/'browser-exit-code').write_text(str(r.returncode)+'\n')
 if r.returncode:raise RuntimeError('Published ZIP UI failed; inspect retained browser log')
 # Save through the same production owner for the retained stop/start contract.
 request=urllib.request.Request(state['origin_url']+'/api/v1/configuration')
 with CLIENT.open(request,timeout=15) as response:current=json.load(response)['configuration'];etag=response.headers.get('ETag')
 for key in ['workspace_id','configuration_sha256','provider_access_policy']:current.pop(key,None)
 current['speech_profile']='kokoro-controlled-v1'
 import uuid
 request=urllib.request.Request(state['origin_url']+'/api/v1/configuration',method='PUT',data=json.dumps(current).encode(),headers={'Origin':state['origin_url'],'Content-Type':'application/json','If-Match':etag,'Idempotency-Key':str(uuid.uuid4())})
 with CLIENT.open(request,timeout=15) as response:assert response.status==200
 print('Current downloaded source UI passed; test-owned configuration saved for restart')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['publish','start','browser','restart','cleanup','preserve']);action=parser.parse_args().action
 if action=='publish':publish()
 elif action=='start':native_owner().start();observe_identity()
 elif action=='browser':browser()
 elif action=='restart':native_owner().restart();observe_identity();preserve(False)
 elif action=='cleanup':native_owner().cleanup()
 else:preserve(False)
if __name__=='__main__':main()
