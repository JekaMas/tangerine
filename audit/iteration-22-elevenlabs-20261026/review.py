"""Scoped evidence review. Never runs in the product or dispatches inference."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREFIX='data/iteration-22-elevenlabs-20261026/'

def review_errors(packet, facts, fixture, result):
    errors=[]
    for name in ['ui_ux','typography','evidence']:
        part=packet.get(name,{})
        if not part.get('observations') or PREFIX+'observations.json' not in part.get('references',[]):
            errors.append(name+' unsupported')
        for ref in part.get('references',[]):
            if not (ROOT/ref).is_file():errors.append('missing '+ref)
    if {x['width'] for x in facts.get('layouts',[])}!={320,390,1280}:errors.append('layout scope')
    for row in facts.get('layouts',[]):
        if row['overflow'] or row['body']!='17px' or row['lineHeight']!='24.65px' or not row['loaded'] or row['fontStatus']!='loaded':errors.append('readability')
        if any(float(x['size'].removesuffix('px'))<13 for x in row['labels']):errors.append('label readability')
    expected=fixture['attempt_id']
    if packet.get('attempt_id')!=expected or result['attempt_id']!=expected or result['score']['case_version_id']!=fixture['case_id']:errors.append('native identity')
    if not facts['cases']['reopenedResults']['url'].endswith('attempt='+expected):errors.append('browser identity')
    if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
    if packet.get('unexecuted_cases')!=[]:errors.append('unexecuted')
    if packet.get('performance_campaigns')!='excluded' or packet.get('requested_benchmark_calls',0)!=0:errors.append('performance scope')
    return errors
