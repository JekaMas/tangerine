"""Reconcile retained valid greens and changed-input observations once at closure."""
import collections
import json
from pathlib import Path
import re
import subprocess

R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;O=R/'data/linguistic-fullness-20261023'
g=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
native=[x for x in g['cases'] if x['id'].startswith('LF-') and x['command_id']=='linguistic-native']
receipts=['native-first','native-repair','native-selection','native-context-final','native-recipes-final','native-alias-final','native-prompts-final','native-contract-final']
observed={}
for name in receipts:
    for line in (O/(name+'.jsonl')).read_text().splitlines():
        if not line.startswith('{'):continue
        event=json.loads(line)
        if event.get('Action')=='pass' and event.get('Test'):
            observed['tangerine.local/api/internal/app::'+event['Test']]=name+'.jsonl'
missing=[x['test_id'] for x in native if x['test_id'] not in observed]
model=json.loads((O/'model-reconciliation.json').read_text())
assert model['current_matched']==model['current_observed']==model['total']==416
assert not missing,missing
rows=json.loads((R/'specification/v2/domain/linguistic-contrast-set.v1.json').read_text())['examples']
model_cases=json.loads((A/'MODEL-CASES.json').read_text())['cases']
index=json.loads((O/'model-observation-index.json').read_text())
baseline=subprocess.check_output(['git','show','da6766d:specification/v2/domain/error-taxonomy.v1.yaml'],cwd=R)
old=json.loads(subprocess.check_output(['ruby','-ryaml','-rjson','-e','puts JSON.generate(YAML.safe_load(STDIN.read))'],input=baseline))
old_by_id={x['id']:x for x in old['items']}
assert set(old_by_id)=={x['taxonomy_id'] for x in rows}
errata=[]
for row in rows:
    prev=old_by_id[row['taxonomy_id']]['example']
    new=dict(context=row['contrast_context'],illustrative_target=row['surface'],accepted_repair='No correction required' if row['surface_status']=='acceptable' else row['canonical'])
    if any(prev[k]!=v for k,v in new.items()):
        errata.append(dict(taxonomy_id=row['taxonomy_id'],before={k:prev[k] for k in new},after=new,correct_control=row['correct_control'],origin='authored contextual erratum; original imported source preserved'))
(A/'ILLUSTRATION-ERRATA.json').write_text(json.dumps(dict(baseline='da6766d',count=len(errata),items=errata),ensure_ascii=False,indent=2)+'\n')
out=['# Per-leaf coverage and actual observations','',
     'All rows are authored references. `3/3` means the current surface, canonical and correct-control semantic judgments agree with their withheld labels; it is not actual-audio accuracy. Native arithmetic assumes admitted semantic labels. Extra variety/policy cases are listed in MODEL-CASES.json.','',
     '| Taxonomy ID | Subtype mappings | Surface kind | Actual semantic cases | Native cases | Correct control |',
     '| --- | ---: | --- | ---: | ---: | --- |']
for row in rows:
    ident=row['taxonomy_id']
    selected=[x for x in model_cases if x['reference_id'].startswith(ident+'.')]
    matches=sum(index[x['id']]['verdict']==x['expected'] for x in selected)
    ns=[x for x in native if x['test_id'].endswith('/'+ident)]
    out.append('| '+ident+' | '+str(len(row['subtypes']))+' | '+row['surface_status']+' | '+str(matches)+'/'+str(len(selected))+' | '+str(len(ns))+'/'+str(len(ns))+' | '+row['correct_control']['text'].replace('|','/')+' |')
out += ['', 'Two alias checks are additional native tests. Six phone-plan compiler tests and four actual-flow readback cases have their own explicit proof boundaries in REPORT.md. The existing exact authored/shipped assembly checks and actual stage-context observations cover prompt wiring; redundant keyword-presence checks were rejected. No missing per-leaf native or current semantic case is hidden by a parent test pass.','']
(A/'COVERAGE.md').write_text('\n'.join(out))
calls=0;judgments=0
for p in O.glob('model-*/native-result.json'):
    r=json.loads(p.read_text());calls+=len(r['result']['receipt_ids']);judgments+=len((r.get('judgment') or {}).get('verdicts',[]))
summary=dict(properties=6,dag_cases=len([x for x in g['cases'] if x['id'].startswith('LF-')]),native_cases=len(native),native_missing=missing,native_case_receipts={x['id']:observed[x['test_id']] for x in native},semantic_current_cases=416,semantic_current_matched=416,semantic_all_observed_judgments=judgments,semantic_transport_receipts=calls,illustration_errata=len(errata),subtype_mappings=sum(len(x['subtypes']) for x in rows),native_injection_cases=6,actual_flow_cases=4,proof_boundary='Finite authored-reference/native/model agreement, not empirical gold or universal acoustic qualification',reuse='Named unchanged test bodies and consumed semantic fields retain original receipts. Only changed projection controls/subtypes, recipe pairs and new/changed model inputs are reobserved. Earlier red records remain.')
(A/'RECONCILIATION.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['native_case_receipts','reuse']}))
