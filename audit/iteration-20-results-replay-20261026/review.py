"""Review evidence relations; actual visual inspection remains self-review."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREFIX='data/iteration-20-results-replay-20261026/'
def review_errors(packet,facts,native):
 errors=[]
 for name in ['ui_ux','typography','evidence']:
  part=packet.get(name,{})
  if not part.get('observations') or PREFIX+'observations.json' not in part.get('references',[]):errors.append(name+' unsupported')
  for ref in part.get('references',[]):
   if not (ROOT/ref).is_file():errors.append('missing '+ref)
 rows=facts['cases']['layouts']
 if {(x['state'],x['width']) for x in rows}!={(s,w) for s in ['completed','uncertain','draft','checking'] for w in [1280,390,320]}:errors.append('layout scope')
 for row in rows:
  if row['overflow'] or row['bodySize']!='17px' or row['bodyLine']!='24.65px' or not row['sourceSans'] or row['fonts']!='loaded':errors.append('readability')
  if any(float(s.removesuffix('px'))<13 for s in row['passageSizes']):errors.append('passage label size')
 c=facts['cases'];source=c['replayStart']['audio']['src'].split('?')[0]
 if source!=native['audio_path'] or packet.get('attempt_id')!=native['attempt_id']:errors.append('media/attempt identity')
 if c['complete']['score']!='Primary score: 60.0 / 100':errors.append('wrong result')
 if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
 if packet.get('unexecuted_cases')!=[]:errors.append('unexecuted')
 if packet.get('new_model_calls')!=0 or packet.get('new_synthesis_calls')!=0:errors.append('provider scope')
 if packet.get('performance_campaigns')!='excluded':errors.append('performance scope')
 return errors
