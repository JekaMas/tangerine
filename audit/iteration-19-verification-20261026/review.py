"""Current I19 review oracles over actual UI facts and source-native identities."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREFIX='data/iteration-19-verification-20261026/'
def readability(row):
 errors=[]
 if row['overflow']:errors.append('horizontal overflow')
 if row['bodySize']!='17px':errors.append('body size')
 for n in row['identities']:
  if float(n['size'].removesuffix('px'))<13:errors.append('identity size')
  if n['scroll']>n['width']+1:errors.append('identity clipped')
 return errors

def review_errors(packet,facts,expected):
 errors=[]
 for section in ['ui_ux','typography','evidence']:
  p=packet.get(section,{})
  if not p.get('observations') or PREFIX+'observations.json' not in p.get('references',[]):errors.append(section+' unsupported')
  for ref in p.get('references',[]):
   if not (ROOT/ref).is_file():errors.append('missing artifact '+ref)
 rows=facts['cases']['layout']
 if {(r['route'],r['width']) for r in rows}!={(r,w) for r in ['attempts','audio','prepare','reviews'] for w in [1280,390,320]}:errors.append('layout scope')
 for row in rows:errors.extend(readability(row))
 if facts['cases']['fonts']!={'fonts':'loaded','sourceSans':True}:errors.append('font not observed loaded')
 actual={x.split('=')[-1] for x in facts['cases']['unreadableRecovery']['links'] if x.startswith('/listen?attempt=')}
 if actual!=set(expected['ids']['attempts']) or set(packet.get('native_attempt_ids',[]))!=actual:errors.append('native/current UI identity mismatch')
 if packet.get('unexecuted_cases')!=[]:errors.append('unexecuted')
 if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
 if packet.get('new_model_calls')!=0 or packet.get('new_synthesis_calls')!=0:errors.append('provider scope')
 if packet.get('performance_campaigns')!='excluded':errors.append('performance scope')
 return errors
