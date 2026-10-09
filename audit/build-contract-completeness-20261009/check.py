"""Finite active-spec structural trace; never reports application or linguistic acceptance."""
from pathlib import Path
import json,hashlib,collections,sys
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
G=json.load(open(C/'verification.json'));F=json.load(open(V/'domain/verification-fixtures.v1.json'));D=parse_delta_specs(C);checks=[]
def ck(n,c):
 checks.append({'name':n,'passed':bool(c)})
 if not c:raise AssertionError(n)
recipes=json.load(open(V/'domain/mutation-recipes.v1.json'))['recipes'];routes=json.load(open(V/'domain/acoustic-production.v1.json'))['rows'];rows={x['taxonomy_id']:x for x in routes}
ck('all122.original.recipe.routes',len(rows)==len(recipes)==122 and set(rows)=={x['taxonomy_id'] for x in recipes})
for r in recipes:
 row=rows[r['taxonomy_id']];ck(r['taxonomy_id']+'.original.operator',row['original_operator']==r['operator']);ck(r['taxonomy_id']+'.on.demand',row['external_recording_required'] is False);ck(r['taxonomy_id']+'.observation.not.fabricated',row['observation']=='not_run')
ck('all5.recorded.contrasts.have.exact.controllers',sum(r['operator']=='recorded_contrast' for r in recipes)==5 and all(rows[r['taxonomy_id']]['controller'] in ['phone_pair','vot_edit','vowel_duration'] for r in recipes if r['operator']=='recorded_contrast'))
expected={'consonant_aspiration':'vot_edit','consonant_place_manner':'phone_pair','vowel_length':'vowel_duration','linking_resyllabification':'phone_pair','assimilation':'phone_pair','compound_stress':'pitch_duration','sentence_stress_prominence':'pitch_duration','rhythm':'pitch_duration','intonation_contour':'pitch_duration','intonation_function':'pitch_duration','pitch_range':'pitch_duration','speech_rate':'pitch_duration','thought_group_chunking':'pause_insert','excessive_pausing':'pause_insert','pause_location':'pause_insert'}
for leaf,controller in expected.items():ck('independent.controller.'+leaf,next(r for r in routes if r['taxonomy_id'].rsplit('.',1)[-1]==leaf)['controller']==controller)
# Byte preservation versus immediately preceding scope and immutable original scope.
import subprocess
preserved=['domain/error-taxonomy.v1.yaml','domain/mutation-recipes.v1.json','domain/metrics.v1.yaml','domain/providers.v1.yaml','domain/corpus-sources.v1.yaml']
for rel in preserved:
 p=V/rel
 if not p.exists():raise AssertionError('Missing preserved original '+rel)
 b=subprocess.check_output(['git','show','HEAD:specification/v2/'+rel],cwd=R);ck('unchanged.original.'+rel,p.read_bytes()==b)
reqs={x['id']:x for x in G['requirements']};bind={x['case_id']:x for x in F['case_bindings']};pbind={x['property_id']:x for x in F['property_bindings']}
ck('all.properties.fixture.bound',len(pbind)==len(G['properties']))
ck('all.case.edges.fixture.bound',len(bind)==len(G['cases']))
for p in G['properties']:
 ck(p['id']+'.binding.present',p['id'] in pbind)
 r=reqs[p['requirement_id']];d=D[(r['capability'],r['title'])];ck(p['id']+'.definition.fingerprint',r['fingerprint']==d['fingerprint'])
 for scenario in p['scenarios']:
  cases=[x for x in G['cases'] if x['property_id']==p['id'] and x['scenario']==scenario];ck(p['id']+'.'+scenario+'.positive.negative',set(x['polarity'] for x in cases)=={'positive','negative'})
for c in G['cases']:
 b=bind[c['id']];ck(c['id']+'.concrete.packet','input' in b and 'expected' in b and bool(b['independent_oracle']))
 if c['id'].startswith('BUILD-'):ck(c['id']+'.not.executed',c['state']=='blocked' and b['observation_state']=='not_run')
fields=json.load(open(V/'language/field-index.json'));ck('all151.schemas.field.index',fields['schema_count']==len(list((V/'contracts').glob('*.schema.json')))==151)
# Every active file and line occurrence has retained exact identity. This does not claim semantic proof of every line.
files=[]
for p in sorted(V.rglob('*')):
 if not p.is_file():continue
 b=p.read_bytes();s=b.decode('utf-8');lines=s.splitlines();files.append({'path':p.relative_to(V).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'line_count':len(lines),'nonempty_lines':sum(bool(x.strip()) for x in lines)})
(A/'line-inventory.json').write_text(json.dumps({'scope':'Complete active v2 files and exact UTF-8 line identities; structural traversal, not linguistic/manual acceptance.','files':files},indent=2)+'\n')
out={'status':'passed','static_assertions':len(checks),'requirements':len(G['requirements']),'properties':len(G['properties']),'case_edges':len(G['cases']),'case_states':dict(collections.Counter(x['state'] for x in G['cases'])),'active_files':len(files),'line_occurrences':sum(x['line_count'] for x in files),'schemas':151,'field_occurrences':fields['field_count'],'new_behavior_plans':24,'behavior_tests_run':0,'preserved_contracts':preserved,'proof_boundary':'Finite definitions, exact line/file identities, original byte preservation, complete route/fixture graph and independent arithmetic design; no executable behavior, provider or audio acceptance.','checks':checks}
(A/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
