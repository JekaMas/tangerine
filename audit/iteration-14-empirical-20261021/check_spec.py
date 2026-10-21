"""Current structural checks plus literal review interface assertions; not behavior."""
from pathlib import Path
import json,sys,copy
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
code=(R/'audit/iteration-10-interpretation-20261020/check_spec.py').read_text().split("result={'status'")[0]
ns={'__file__':str(A/'check_spec.py')};exec(compile(code,'current-artifacts','exec'),ns)
pair=ns['namespace']['pair'];checks=ns['checks']
load=lambda name:json.loads((R/'specification/v2/contracts'/(name+'.schema.json')).read_text())
pair('review.explicit.purposes',load('review-request'),lambda d:set(d['properties']['purpose']['enum'])=={'case_review','dispute','answer_reconsideration'},lambda d:d['properties']['purpose']['enum'].remove('dispute'))
pair('review.view.private.excluded',load('review-view'),lambda d:d['additionalProperties'] is False and not {'frozen_asset_id','stages','configuration'}&set(d['properties']),lambda d:d['properties'].update(frozen_asset_id={'type':'string'}))
pair('review.machine.person.absent',load('review-view'),lambda d:d['properties']['person_id']=={'type':'null'} and d['properties']['qualification_ids']['maxItems']==0,lambda d:d['properties']['person_id'].update(type='string'))
pair('review.resolutions.complete',load('llm-review-output'),lambda d:set(d['properties']['resolution']['enum'])=={'supported','mapping_defect','key_defect','insufficient_evidence'},lambda d:d['properties']['resolution']['enum'].remove('key_defect'))
ops=json.loads((R/'specification/v2/domain/review-runtime-operations.yaml').read_text())['operations'];api=json.loads((R/'specification/v2/contracts/review-runtime.openapi.yaml').read_text())
for op in ops:
 row=api['paths'][op['path']][op['method'].lower()]
 assert row['operationId']==op['id'];assert row['responses'][str(op['success'])]['content']['application/json']['schema']['$ref']==op['response']+'.schema.json'
 assert (R/'specification/v2/contracts'/(op['response']+'.schema.json')).exists()
ns['namespace']['ck']('review.runtime.operations.exact',len(ops)==5)
# Typed model/runtime/source contracts stay copied to the actual schema owner.
for name in ['review-request','review-view','review-list','review-selection-result','review-decision','dispute']:
 ns['namespace']['ck']('review.schema.copy.'+name,(R/'specification/v2/contracts'/(name+'.schema.json')).read_bytes()==(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).read_bytes())
for name in ['source-release','source-release-request','format-binding-request','connector-request']:
 ns['namespace']['ck']('source.schema.copy.'+name,(R/'specification/v2/contracts'/(name+'.schema.json')).read_bytes()==(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).read_bytes())
ns['namespace']['ck']('source.exact.eleven',len(__import__('re').findall(r'"[A-Z][A-Z0-9.-]+"',(R/'services/api/internal/source/types.go').read_text().split('var IDs = ')[1].split('\n')[0]))==11)
for name in ['llm-quality-case','llm-quality-expectations','llm-quality-answer-input','llm-quality-judge-policy']:
 ns['namespace']['ck']('quality.schema.copy.'+name,(R/'specification/v2/contracts'/(name+'.schema.json')).read_bytes()==(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).read_bytes())
ns['namespace']['ck']('quality.exact22registry',len(json.loads((R/'specification/v2/domain/llm-quality-metrics.v1.json').read_text())['metrics'])==22)
ns['namespace']['ck']('quality.registry.copy',(R/'specification/v2/domain/llm-quality-metrics.v1.json').read_bytes()==(R/'services/api/internal/app/generationdata/llm-quality-metrics.v1.json').read_bytes())
result={'status':'passed','assertions':len(checks),'checks':checks,'proof_boundary':'Static contract/reference/vector/field/prompt/interface checks only; no behavior or model quality claim.'}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
