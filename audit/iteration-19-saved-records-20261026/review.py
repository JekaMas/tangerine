"""Review checks over observed DOM metadata and native identity, not pass labels."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def readability_errors(row):
 errors=[]
 if row.get('overflow'):errors.append('horizontal overflow')
 if row.get('body',{}).get('size')!='17px':errors.append('body size')
 for n in row.get('identityType',[]):
  if float(n['size'].removesuffix('px'))<13:errors.append('identity size')
  if n['scroll']>n['width']+1:errors.append('identity clipped')
 return errors

def review_errors(packet,observations,native):
 errors=[]
 for section in ['ui_ux','typography','evidence']:
  value=packet.get(section,{})
  if not value.get('observations') or not value.get('references'):errors.append(section+' absent or unsupported')
  for path in value.get('references',[]):
   if not (ROOT/path).is_file():errors.append('missing artifact '+path)
 rows=observations['cases'].get('widths',[])
 if {(r['route'],r['width']) for r in rows}!={(r,w) for r in ['attempts','audio','prepare','reviews'] for w in [1280,390,320]}:errors.append('responsive scope')
 for r in rows:errors.extend(readability_errors(r))
 wanted=set(native['ids']['attempts'])
 actual={x['links'][0]['href'].split('=')[-1] for x in observations['cases']['nativeAttempts']['articles']}
 if wanted!=actual:errors.append('native/browser record identity mismatch')
 if packet.get('unexecuted_cases')!=[]:errors.append('unexecuted')
 if packet.get('reference_origin')!='independently authored literal expectations':errors.append('reference origin')
 if packet.get('new_model_calls')!=0 or packet.get('new_synthesis_calls')!=0:errors.append('unexpected provider use')
 if packet.get('performance_campaigns')!='excluded':errors.append('scope')
 return errors
