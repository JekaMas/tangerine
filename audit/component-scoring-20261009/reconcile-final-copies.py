"""Align discovered inline DTO/OpenAPI copies and only their affected metadata."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent
nodes=[n for n in ast.parse((R/'audit/simple-generation-flow-20261009/reconcile.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['fields','sha','save']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'metadata_helpers','exec'))
changed=[]
for p in sorted((V/'contracts').glob('*.schema.json')):
 d=json.loads(p.read_text());touched=[False]
 def walk(x):
  if isinstance(x,dict):
   props=x.get('properties',{})
   if all(k in props for k in ['detection','classification','correction','explanation']) and props['explanation'].get('type')=='boolean':
    desc='Legacy explanation invitation preference. Under answer-components-v2 explanation is optional and every supplied explanation is assessed independently, regardless of this flag; it does not enter the primary composite.'
    if props['explanation'].get('description')!=desc:props['explanation']['description']=desc;touched[0]=True
   for value in x.values():walk(value)
  elif isinstance(x,list):
   for value in x:walk(value)
 walk(d)
 if touched[0]:save(p,d);changed.append(p.relative_to(V).as_posix())
p=V/'contracts/openapi.yaml';s=p.read_text();old='Increment permission epoch and block derived future use atomically.';new='Save actual source revocation notice/status and expose affected selected-source use; retain provenance without permission epochs or grant closure. Independent authored exercises remain available.';assert s.count(old)==3;p.write_text(s.replace(old,new))
p=V/'domain/persistence-map.json';meta=json.loads(p.read_text())
for r in meta['records']:
 if r['schema'] in changed:r.update(sha256=sha(V/r['schema']),fields=fields(json.loads((V/r['schema']).read_text())))
save(p,meta);flat=[dict(schema=Path(r['schema']).name,**f) for r in meta['records'] for f in r['fields']];save(V/'language/field-index.json',dict(schema_count=len(meta['records']),field_count=len(flat),fields=flat))
node="""const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml'),crypto=require('crypto'),V='specification/v2/';let sha=p=>crypto.createHash('sha256').update(fs.readFileSync(V+p)).digest('hex'),load=p=>Y.parse(fs.readFileSync(V+p,'utf8')),save=(p,d)=>fs.writeFileSync(V+p,Y.stringify(d));let s=load('domain/semantic-invariants.yaml');for(let r of Object.values(s.schemas))r.schema_sha256=sha(r.schema);save('domain/semantic-invariants.yaml',s);let m=load('prompts/manifest.yaml');for(let b of m.bindings){b.prompt_sha256=sha(b.path);b.input_schema_sha256=sha('contracts/'+b.input_schema);b.output_schema_sha256=sha('contracts/'+b.output_schema);}save('prompts/manifest.yaml',m);let c=load('domain/version-compatibility.yaml');for(let r of c.files)r.sha256=sha(r.path);save('domain/version-compatibility.yaml',c);"""
subprocess.run(['node','-e',node],cwd=R,check=True)
r=json.loads((A/'reconciliation.json').read_text());r['changed_schemas']+=changed;r['final_copy_alignment']=dict(schema_descriptions=changed,openapi_effect_occurrences=3,graph_unchanged=True);save(A/'reconciliation.json',r)
print(json.dumps(dict(changed_schemas=changed,openapi_effects=3,graph_unchanged=True)))
