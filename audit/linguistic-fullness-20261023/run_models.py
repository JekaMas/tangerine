"""Explicit finite included-plan experiment. No SDK, retries or paid fallback.

Build the test against this checkout, invoke its actual production owners inside
the existing local API environment, and retain native readback. This adds only
development observations; it does not activate a bundle or change Settings.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[2]
OUT=R/'data/linguistic-fullness-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
API='tangerine-local-api-1'
REMOTE='/tmp/tangerine-linguistic-20261023'
IMAGE='tangerine-linguistic-observer:local'


def docker(*args,timeout=300):
    return subprocess.run(['docker',*args],cwd=R,env=ENV,capture_output=True,timeout=timeout)


def require(p,name):
    (OUT/(name+'.log')).write_bytes(p.stdout+p.stderr)
    if p.returncode:
        raise SystemExit(name+' failed; inspect private log')


def build():
    require(docker('build','--target','build','-t',IMAGE,'-f','services/api/Dockerfile','.'),'observer-build')
    require(docker('run','--rm','-e','CGO_ENABLED=0','-v',str(OUT)+':/observer','--entrypoint','go',IMAGE,'test','-c','-o','/observer/linguistic.test','./internal/app'),'observer-compile')
    require(docker('exec',API,'mkdir','-p',REMOTE),'observer-directory')
    require(docker('cp',str(OUT/'linguistic.test'),API+':'+REMOTE+'/linguistic.test'),'observer-copy')
    image=docker('image','inspect',IMAGE,'--format','{{.Id}}').stdout.decode().strip()
    (OUT/'observer-binding.json').write_text(json.dumps(dict(image=image,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),source_diff=subprocess.check_output(['git','diff','--stat'],cwd=R,text=True),credentials='existing native connection; never copied into the harness',billing='included_subscription only',workspace_activation=False),indent=2)+'\n')


def run(batch):
    dest=OUT/f'model-{batch:02}'
    if (dest/'native-result.json').exists():
        print(json.dumps(dict(batch=batch,status='retained',path=str(dest.relative_to(R)))),flush=True)
        return
    source=OUT/f'batch-{batch:02}.json'
    require(docker('cp',str(source),API+':'+REMOTE+f'/batch-{batch:02}.json'),f'model-{batch:02}-copy')
    dest.mkdir(parents=True,exist_ok=True)
    p=docker('exec','-e',f'TANGERINE_LINGUISTIC_BATCH={REMOTE}/batch-{batch:02}.json','-e',f'TANGERINE_LINGUISTIC_OUTPUT={REMOTE}/model-{batch:02}',API,REMOTE+'/linguistic.test','-test.v','-test.run','^TestLinguisticIncludedModel$','-test.timeout','270s',timeout=280)
    (dest/'test.log').write_bytes(p.stdout+p.stderr)
    copy=docker('cp',API+':'+REMOTE+f'/model-{batch:02}/.',str(dest))
    if copy.returncode:
        (dest/'copy-failure.log').write_bytes(copy.stdout+copy.stderr)
    summary=dict(batch=batch,exit_code=p.returncode,status='passed' if p.returncode==0 else 'failed',paid_fallback=False)
    if (dest/'observed-labels.json').exists():
        observed=json.loads((dest/'observed-labels.json').read_text())
        expected=json.loads((dest/'withheld-expectations.json').read_text())
        summary.update(total=len(expected),matched=sum(observed.get(k)==v for k,v in expected.items()),mismatches=[k for k,v in expected.items() if observed.get(k)!=v])
    (dest/'receipt.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    # A failed verdict is useful evidence. An unavailable transport/allowance
    # stops the finite run; do not spend more calls against the same failure.
    if not (dest/'observed-labels.json').exists():
        raise SystemExit('Model/transport admission unavailable; retained native result; no retry/fallback')


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',action='store_true',required=True)
    ap.add_argument('--build',action='store_true')
    ap.add_argument('--batches',default=','.join(map(str,range(17))))
    args=ap.parse_args()
    if args.build:build()
    for b in args.batches.split(','):run(int(b))
