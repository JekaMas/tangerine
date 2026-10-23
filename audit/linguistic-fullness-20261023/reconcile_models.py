"""Match current literal inputs to retained native observations; no inference.

Changed inputs get a new finite batch. Old failures/results stay intact. A wrong
verdict on an unchanged input remains failed; this tool never hides it by retry.
"""
import argparse
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]
O=R/'data/linguistic-fullness-20261023'
CASES=json.loads((R/'audit/linguistic-fullness-20261023/MODEL-CASES.json').read_text())['cases']
ap=argparse.ArgumentParser()
ap.add_argument('--prepare',action='store_true')
a=ap.parse_args()
index={};missing=[];failed=[];historical=[]
for case in CASES:
    matches=[]
    for path in sorted(O.glob('model-*/candidate-input.json')):
        values=json.loads(path.read_text())
        if case['id'] not in values:
            continue
        result_path=path.parent/'native-result.json'
        if not result_path.exists():
            continue
        result=json.loads(result_path.read_text())
        if result.get('error')!='<nil>' or not result.get('judgment'):
            continue
        verdicts=[v for v in result['judgment'].get('verdicts',[]) if v['proposition_id']==case['id']]
        if len(verdicts)!=1:
            continue
        observation=dict(directory=str(path.parent.relative_to(R)),input_matches=values[case['id']]==case['input'],verdict=verdicts[0]['verdict'],reason=verdicts[0]['reason'])
        if observation['input_matches']:
            matches.append(observation)
        else:
            historical.append(dict(case_id=case['id'],**observation))
    if not matches:
        missing.append(case)
        continue
    # Latest matching input observation; never silently choose a favorable
    # duplicate. There are no unchanged-input retries in this experiment.
    chosen=matches[-1]
    index[case['id']]=chosen
    if chosen['verdict']!=case['expected']:
        failed.append(dict(case_id=case['id'],expected=case['expected'],**chosen))
(O/'model-observation-index.json').write_text(json.dumps(index,indent=2)+'\n')
summary=dict(total=len(CASES),current_observed=len(index),current_matched=len(index)-len(failed),missing=[x['id'] for x in missing],failed=failed,superseded_input_observations=historical,paid_fallback=False)
(O/'model-reconciliation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='superseded_input_observations'}))
if a.prepare and missing:
    existing=[int(p.stem.split('-')[1]) for p in O.glob('batch-*.json')]
    start=max(existing+[19])+1
    for n,i in enumerate(range(0,len(missing),24),start):
        (O/f'batch-{n:02}.json').write_text(json.dumps(dict(batch=n,cases=missing[i:i+24]),ensure_ascii=False,indent=2)+'\n')
        print('new changed/unobserved-input batch',n,'cases',len(missing[i:i+24]))
