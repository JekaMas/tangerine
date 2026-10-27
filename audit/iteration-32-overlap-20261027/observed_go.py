"""Reuse exact observed Go output on unchanged semantic inputs.

This development adapter dispatches no Go/model/speech command. The original
JSON stream and actual exit observation remain visible; no pass is fabricated
from an audit status. Current DAG assertions consume the retained outputs explicitly; they do not impersonate a newly executed Go test.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-32-overlap-20261027'
def receipt_errors(cohort):
 errors=[]
 if cohort['exit_code']!=0:errors.append('nonzero actual command exit')
 path=ROOT/cohort['stdout'];raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=cohort['stdout_sha256']:errors.append('changed original output')
 events=[json.loads(line) for line in raw.decode().splitlines() if line.startswith('{')]
 if any(e['Action'] in ['fail','skip'] for e in events):errors.append('failed or skipped native case')
 observed={e['Package']+'::'+e['Test'] for e in events if e.get('Test') and e['Action']=='pass'}
 if set(cohort['test_ids'])!=observed:errors.append('incomplete exact native population')
 for name,digest in cohort['source_sha256'].items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:errors.append('changed semantic source: '+name)
 return errors
if __name__=='__main__':
 packet=json.loads((OUT/'OBSERVATIONS.json').read_text())
 for cohort in packet['cohorts']:
  errors=receipt_errors(cohort)
  if errors:raise SystemExit('\n'.join(errors))
 print(json.dumps(dict(status='passed',scope='Retained exact native observations; no Go/model/speech command executed',observations=sum(len(c['test_ids']) for c in packet['cohorts']))))
