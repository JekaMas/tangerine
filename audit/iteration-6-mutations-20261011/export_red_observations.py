"""Retain selected unsuccessful actual-local observations in Lab, without inference."""
from pathlib import Path
import json,os,subprocess
R=Path(__file__).resolve().parents[2];base=R/'data/iteration6/local';names=['tangerine-local-mutation-714d67bff522','tangerine-local-mutation-ce5a4a152f48','tangerine-local-mutation-a8240411cefb'];packets={}
for name in names:
 for path in (base/name).glob('TestNativeLocal*/diagnostic-*.json'):
  p=json.loads(path.read_text());packets[p['operation']]=p
script="import runpy,json,sys,contextlib\nm=runpy.run_path('/tangerine/lab.py'); out=[]\nfor p in json.load(sys.stdin):\n with contextlib.redirect_stdout(sys.stderr):\n  v=m['sync'](p); check=m['verify'](v)\n assert check['status']=='observed' and check['provider_calls']==0\n out.append({'operation':p['operation'],'export':v,'readback':check})\nprint(json.dumps(out))\n"
result=subprocess.run(['docker','exec','-i','tangerine-i1-llm-lab-1','python','-c',script],input=json.dumps(list(packets.values())),capture_output=True,text=True,timeout=180,check=True,env=os.environ)
v=json.loads(result.stdout);(base/'red-lab-exports.json').write_text(json.dumps(v,indent=2)+'\n');assert len(v)==len(packets) and all(x['export']['provider_calls']==0 for x in v)
summary={'status':'retained_unsuccessful_observations','runs':names,'operations':len(packets),'lab_runs':[x['export']['run'] for x in v],'readback':'observed','export_provider_calls':0,'counts_as_acceptance':False,'private_exports':'data/iteration6/local/red-lab-exports.json','failures':['unchanged surface with an error key then repair deadline','recipe-example mismatch then empty key','duplicate key, missing association and no-op preferred correction'],'proof_boundary':'These failed or superseded runs are kept for debugging; none supplies a green linguistic claim.'}
(R/'audit/iteration-6-mutations-20261011/RED-OBSERVATIONS.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
