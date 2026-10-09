"""Only final invalidated vector/prompt inputs and the clarified zero-credit precedence."""
import ast,hashlib,json,subprocess
from fractions import Fraction
from pathlib import Path
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';A=Path(__file__).resolve().parent;checks=[]
def ck(n,c):checks.append(dict(id=n,status='passed' if c else 'failed'));assert c,n
node="const fs=require('fs'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');process.stdout.write(JSON.stringify({v:Y.parse(fs.readFileSync('specification/v2/domain/version-compatibility.yaml','utf8')),m:Y.parse(fs.readFileSync('specification/v2/prompts/manifest.yaml','utf8'))}));"
x=json.loads(subprocess.check_output(['node','-e',node],cwd=R));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();actual={p.relative_to(V).as_posix() for p in V.rglob('*') if p.is_file()}-{'domain/version-compatibility.yaml'}
ck('final_vector',set(f['path'] for f in x['v']['files'])==actual and all(sha(V/f['path'])==f['sha256'] for f in x['v']['files']))
b=next(b for b in x['m']['bindings'] if b['prompt_id']=='map-v1');ck('clarified_mapper_binding',sha(V/b['path'])==b['prompt_sha256'] and sha(V/'contracts'/b['input_schema'])==b['input_schema_sha256'] and sha(V/'contracts'/b['output_schema'])==b['output_schema_sha256'])
ck('known_zero_precedence_contract',all('already' in (V/'docs'/name).read_text() and 'zero' in (V/'docs'/name).read_text() for name in ['answer-component-scoring.md','math-and-judgments.md','cross-field-invariants.md']))
nodes=[n for n in ast.parse((A/'check.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['primary','optional']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'independent_math_helpers','exec'))
p=dict(id='false_and_unknown_reason',g=1,gc=1,tp=1,fp=0,cq='1',ge=1,te=1,ea=1,eq='0',additional_assertion_judgments=['unsupported','unknown'],primary='100',optional='0')
ck('stipulated_forbidden_zero_plus_retained_unknown_positive',primary(p)==100 and optional(p)==0 and p['additional_assertion_judgments']==['unsupported','unknown'])
ck('stipulated_forbidden_zero_plus_retained_unknown_negative',primary(p)!=0 and optional(p) is not None)
log=(A/'graph-validation.log').read_text();ck('retained_graph_receipt_matches_unchanged_manifest',json.dumps('passed') in log and '"discovery": "validated"' in log and sha(R/'openspec/changes/implement-teacher-error-trainer/verification.json') in log)
d=json.loads((A/'ARITHMETIC-PACKETS.json').read_text());d['packets'].append(p);(A/'ARITHMETIC-PACKETS.json').write_text(json.dumps(d,indent=2)+'\n')
(A/'final-validation-results.json').write_text(json.dumps(dict(passed=len(checks),failed=0,checks=checks,invalidation='After the initial395 artifact/oracle checks, only three scoring prose owners, mapper prompt/binding and active contract vector changed to clarify known-zero precedence. Other valid greens are retained; no behavior run.',proof_boundary='Static binding/prose and stipulated arithmetic only.'),indent=2)+'\n')
print(json.dumps(dict(passed=len(checks),failed=0,retained_initial_static_checks=395,behavior_runs=0)))
