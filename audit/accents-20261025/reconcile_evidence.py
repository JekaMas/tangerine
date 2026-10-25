"""Reconcile existing exact observed greens without executing them again."""
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'data/accents-20261025'
sys.path.insert(0,str(R/'.agents/workflow/scripts'))
from requirement_tests import parse_go_events,parse_unittest_events
logs=[('native.jsonl','go'),('affected-native.jsonl','go'),('frozen-green.jsonl','go'),('advanced-green.jsonl','go'),('advanced-fixture-green.jsonl','go'),('request-final.log','python'),('speech-pure.log','python'),('audio-evidence.log','python'),('browser-demo-evidence.log','python')]
observed={}
for name,kind in logs:
 raw=(O/name).read_text();events=(parse_go_events if kind=='go' else parse_unittest_events)(raw)
 for identity,status in events.items():
  # A repaired failing case supersedes its old result; other greens stay valid.
  observed[identity]=(status,name)
g=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());rows=[]
for case in g['cases']:
 if not case['id'].startswith('ACC-'):continue
 status,log=observed[case['test_id']];assert status=='pass',(case['id'],status,log)
 rows.append({'id':case['id'],'test_id':case['test_id'],'status':'passed','receipt':'data/accents-20261025/'+log,'expectation':case['green_expectation'],'retention':'Exact observed identity; unaffected leaf expectations retained. Only affected owners/assertions/fixtures repeated.'})
assert len(rows)==25
protected=[p for p in subprocess.check_output(['git','ls-tree','-r','--name-only','51b1da6ec99b654c0c4965afab1b099d07f71349'],cwd=R,text=True).splitlines() if p.startswith('services/api/internal/app/generationdata/') or p.startswith('services/api/internal/app/migrations/') or p in ['specification/v2/domain/error-taxonomy.v1.yaml','specification/v2/domain/mutation-recipes.v1.json','specification/v2/domain/metrics.v1.yaml','specification/v2/domain/corpus-sources.v1.yaml','specification/v2/domain/providers.v1.yaml']]
assert all(subprocess.check_output(['git','show','51b1da6:'+p],cwd=R)==(R/p).read_bytes() for p in protected)
result={'status':'passed','base_revision':'51b1da6ec99b654c0c4965afab1b099d07f71349','properties':4,'selected_cases':len(rows),'passed_cases':rows,'protected_unchanged':protected,'scope_limits':['No universal accent/perceptual correctness or all-acoustic-controller qualification','No unselected hosted provider or renewed full-release qualification','The actual demo answer was authored from its saved key to demonstrate one finding and one miss','Native raw frames retain real timing; the short video labels idle compression and separately synchronized saved audio','No separate independent reviewer was used']}
(R/'audit/accents-20261025/RECONCILIATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'status':'passed','cases':len(rows),'protected_unchanged':len(protected)}))
