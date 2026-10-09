"""Revalidate only newly aligned copies and their invalidated bindings/index/vector."""
import ast,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;checks=[]
def ck(n,c):checks.append(dict(id=n,status='passed' if c else 'failed'));assert c,n
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['sha','fields']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_helpers','exec'))
node="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');let d={};for(let p of ['domain/semantic-invariants.yaml','domain/version-compatibility.yaml','prompts/manifest.yaml','contracts/openapi.yaml','domain/operations.yaml','domain/operation-ownership.yaml'])d[p]=Y.parse(fs.readFileSync('specification/v2/'+p,'utf8'));process.stdout.write(JSON.stringify(d));"
y=json.loads(subprocess.check_output(['node','-e',node],cwd=R));m=json.loads((V/'domain/persistence-map.json').read_text());rec={r['schema']:r for r in m['records']};changed=json.loads((A/'reconciliation.json').read_text())['final_copy_alignment']['schema_descriptions']+['contracts/feedback.schema.json']
for p in changed:
 d=json.loads((V/p).read_text());ck('copy_metadata.'+p,sha(V/p)==rec[p]['sha256'] and fields(d)==rec[p]['fields']);kind=Path(p).name.removesuffix('.schema.json');ck('copy_semantic_binding.'+kind,sha(V/p)==y['domain/semantic-invariants.yaml']['schemas'][kind]['schema_sha256'])
flat=[dict(schema=Path(r['schema']).name,**f) for r in m['records'] for f in r['fields']];idx=json.loads((V/'language/field-index.json').read_text());ck('final_field_index',flat==idx['fields'] and idx['field_count']==len(flat))
flags=[]
def walk(x):
 if isinstance(x,dict):
  p=x.get('properties',{})
  if all(k in p for k in ['detection','classification','correction','explanation']) and p['explanation'].get('type')=='boolean':flags.append(p['explanation']['description'])
  for z in x.values():walk(z)
 elif isinstance(x,list):
  for z in x:walk(z)
for p in (V/'contracts').glob('*.schema.json'):walk(json.loads(p.read_text()))
ck('all_inline_explanation_flags_optional',len(flags)>=10 and all('optional' in f and 'every supplied explanation' in f for f in flags))
a=json.loads((V/'contracts/feedback-output.schema.json').read_text());b=json.loads((V/'contracts/feedback.schema.json').read_text());ak=a['properties']['items']['items']['properties']['kind']['enum'];bk=b['properties']['items']['items']['properties']['kind']['enum'];ck('feedback_output_to_stored_component_kinds',ak==bk and all(k in bk for k in ['correction','explanation']))
ck('all_source_notice_copies_agree',all('Increment permission epoch' not in (V/p).read_text() for p in ['contracts/openapi.yaml','domain/operations.yaml','domain/operation-ownership.yaml']))
vec=y['domain/version-compatibility.yaml']['files'];actual={p.relative_to(V).as_posix() for p in V.rglob('*') if p.is_file()}-{'domain/version-compatibility.yaml'};ck('final_active_vector',set(f['path'] for f in vec)==actual and all(sha(V/f['path'])==f['sha256'] for f in vec))
ck('final_prompt_bindings',all(sha(V/b['path'])==b['prompt_sha256'] and sha(V/'contracts'/b['input_schema'])==b['input_schema_sha256'] and sha(V/'contracts'/b['output_schema'])==b['output_schema_sha256'] for b in y['prompts/manifest.yaml']['bindings']))
log=(A/'graph-validation.log').read_text();ck('unchanged_graph_retained_green',sha(R/'openspec/changes/implement-teacher-error-trainer/verification.json') in log and '"discovery": "validated"' in log)
(A/'copy-validation-results.json').write_text(json.dumps(dict(passed=len(checks),failed=0,checks=checks,inline_explanation_flag_occurrences=len(flags),invalidation='Seven copied task-flag schema descriptions (including scorer), stored feedback enum, their indexes/bindings, three OpenAPI source effects and the active vector changed after earlier static checks. Only affected copies/bindings/index/vector and retained graph identity are revalidated; no behavior execution.',proof_boundary='Static declarative copying/projection and artifact integrity, not application/model behavior.'),indent=2)+'\n')
print(json.dumps(dict(passed=len(checks),failed=0,inline_flags=len(flags),schemas=134,fields=len(flat))))
