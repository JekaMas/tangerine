"""Explicit ordered opt-in stage observation; no hidden deployment or fallback."""
import argparse
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[2]
O=R/'data/linguistic-fullness-20261023'
ENV={**os.environ,'DOCKER_HOST':'unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock','DOCKER_CONFIG':str(R/'data/local-preview/docker-config')}
ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true',required=True)
ap.add_argument('--stages',default='PreparationPositive,AnswerNegative,ReviewPositive,AdjudicationNegative')
args=ap.parse_args()
for stage in args.stages.split(','):
    with (O/('flow-'+stage+'.log')).open('wb') as log:
        p=subprocess.run(['docker','exec','-e','TANGERINE_LINGUISTIC_FLOW=/tmp/tangerine-linguistic-20261023/flow','tangerine-local-api-1','/tmp/tangerine-linguistic-20261023/flow-current.test','-test.v','-test.run','^TestLinguisticAffected'+stage+'$','-test.timeout','600s'],cwd=R,env=ENV,stdout=log,stderr=subprocess.STDOUT,timeout=610)
    if p.returncode:raise SystemExit('Failed '+stage+'; retained native state. Inspect before an explicit continuation.')
subprocess.run(['docker','cp','tangerine-local-api-1:/tmp/tangerine-linguistic-20261023/flow/.',str(O/'flow')],cwd=R,env=ENV,check=True,capture_output=True)
