"""Readable join of existing category evidence; zero inference or stored checks."""
from collections import Counter
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
refs=json.loads((ROOT/'specification/v2/domain/linguistic-contrast-set.v1.json').read_text())['examples']
old=json.loads((ROOT/'audit/category-realization-20261025/COVERAGE.json').read_text())
prior={v['category_id']:v for v in old['categories']}
rows=[]
for ref in refs:
 id=ref['taxonomy_id']
 if id.startswith(('pronunciation.','acceptable_variant.')):continue
 previous=prior[id]
 rows.append(dict(category_id=id,family=id.split('.')[0],subtypes=ref['subtypes'],canonical=ref['canonical'],mutated=ref['surface'],correct_control=ref['correct_control'],modality=ref['modality'],native_context_and_scoring=previous['implementation'],native_mutation_replay_cases=['tangerine.local/api/internal/app::'+t+'/'+id for t in ['TestFXWrittenMutationPositive','TestFXWrittenMutationNegative']] if ref['modality']=='written_contextual_language' else [],audio_evidence={k:v for k,v in previous.items() if k not in ['category_id','implementation']}))
assert len(rows)==88
out=dict(scope='All 88 existing non-pronunciation leaves; authored finite cases, not all possible English errors',family_counts=dict(Counter(r['family'] for r in rows)),native_written_replay_categories=83,other_realizations=5,retained_native_index='audit/linguistic-fullness-20261023/RECONCILIATION.json',retained_semantic_cases='audit/linguistic-fullness-20261023/MODEL-CASES.json',retained_audio_index='audit/category-realization-20261025/COVERAGE.json',categories=rows)
(HERE/'COVERAGE.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
lines=['# Non-pronunciation category coverage','','All 88 existing leaves are selectable and have native context/scoring cases. The 83 written contrasts additionally pass native mutation admission and exact manifest replay. The five timing/interaction contrasts retain their acoustic controllers and original observation limits.','','The supplied correct alternatives are authored controls. Model opinions, requested changes, measurements and actual hearing remain distinct. No stored corpus or pregeneration is a prerequisite.','','| Category | Mutation path | Literal contrast | Correct alternative |','|---|---|---|---|']
for r in rows:lines.append('| '+r['category_id']+' | '+('Native written admission/replay' if r['native_mutation_replay_cases'] else r['modality'].replace('_',' '))+' | '+r['canonical'].replace('|','/')+' → '+r['mutated'].replace('|','/')+' | '+r['correct_control']['text'].replace('|','/')+' |')
(HERE/'COVERAGE.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='categories'}))
