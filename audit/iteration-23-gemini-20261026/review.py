"""Selected evidence relations only. Never a runtime gate or an aesthetic oracle."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def review_errors(packet,facts,fixture,result):
 errors=[]
 for name in ['ui_ux','typography','evidence']:
  part=packet.get(name,{})
  if not part.get('observations') or not part.get('references'):errors.append(name+' omitted')
  for ref in part.get('references',[]):
   if not (ROOT/ref).is_file():errors.append('missing '+ref)
 if packet.get('attempt_id')!=fixture['attempt_id'] or result.get('attempt_id')!=fixture['attempt_id']:errors.append('attempt mismatch')
 if result['score']['case_version_id']!=fixture['case_id']:errors.append('case mismatch')
 if facts.get('reopened_url','').split('attempt=')[-1]!=fixture['attempt_id']:errors.append('browser mismatch')
 if {r['width'] for r in facts.get('layouts',[])}!={320,390,1280}:errors.append('layout observations missing')
 for row in facts.get('layouts',[]):
  if row['overflow'] or row['body']!='17px' or row['lineHeight']!='24.65px' or not row['loaded']:errors.append('readability')
 if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
 if packet.get('unexecuted_cases')!=[]:errors.append('unexecuted claimed green')
 if packet.get('requested_benchmark_calls',0)!=0 or packet.get('performance_campaigns')!='excluded':errors.append('excluded performance campaign')
 return errors
