"""Append platform-cache counterexamples and the real post-cleanup observation."""
from pathlib import Path
import ast,copy,hashlib,json,re
R=Path(__file__).resolve().parents[2];A=R/'audit/iteration-16-release-20261021';C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
load=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'verification-fixtures.v1.json');a=load(A/'CASES.json');sets=load(V/'property-test-sets.v1.json');d=load(C/'discovery.json');library=load(A/'FIXTURE-LIBRARY.json')
unit_command='iteration16-87-platform-cache'
if not any(c['id']==unit_command for c in g['commands']):g['commands'].append(dict(id=unit_command,runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_release_images.py','-v'],cwd='.',env={},timeout_seconds=90,authority='local'))
new_tests=[];new_cases=[]
for path in ['tests/test_release_images.py','tests/test_release_portable.py']:
 text=(R/path).read_text();digest=hashlib.sha256(text.encode()).hexdigest()
 for cls in [c for c in ast.parse(text).body if isinstance(c,ast.ClassDef)]:
  for node in [n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]:
   if path.endswith('test_release_portable.py') and node.name!='test_original_cache_restore_positive':continue
   identity='unittest::'+Path(path).stem+'.'+cls.name+'.'+node.name
   if any(c['test_id']==identity for c in g['cases']):continue
   polarity='positive' if node.name.endswith('_positive') else 'negative';pid='I16-07.P1'
   template=next(c for c in g['cases'] if c['property_id']==pid and c['polarity']==polarity and c['source_path']=='tests/test_release_portable.py');c=copy.deepcopy(template);binding=copy.deepcopy(next(b for b in f['case_bindings'] if b['case_id']==template['id']));fixture=copy.deepcopy(next(x for x in f['fixtures'] if x['id']==binding['fixture_id']))
   number=1+max(int(re.search(r'\.S(\d+)\.',c['id'])[1]) for c in g['cases'] if c['property_id']==pid and c['polarity']==polarity);cid=f'{pid}.S{number}.{polarity.upper()}';fid='iteration16-'+cid.replace('.','-');body=ast.get_source_segment(text,node)
   binding.update(case_id=cid,fixture_id=fid,test_id=identity,action='Observe '+node.name+' through the platform-cache owner with independent original-state expectations')
   binding['input'].update(exact_test=node.name,literal_executable_fixture=body,source_path=path,source_sha256=digest,shared_fixture_library='audit/iteration-16-release-20261021/FIXTURE-LIBRARY.json#'+path);binding['expected']['independent_literal_assertions']=body
   c.update(id=cid,test_id=identity,source_path=path,source_sha256=digest,command_id=unit_command if path.endswith('test_release_images.py') else 'iteration16-95-test_release_portable',distinct_reason='Scenario '+c['scenario']+': exact platform selection/restoration counterexample '+node.name,setup=binding['action']+' '+json.dumps(binding['input'],sort_keys=True),observable=json.dumps(binding['expected'],sort_keys=True))
   c['invalidation_dependencies']=list(dict.fromkeys([path,'tests/release_images.py','tests/release-portable',*c['invalidation_dependencies']]))
   if path.endswith('test_release_images.py'):c['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Controlled Docker CLI result/state only',forbidden_claims=['No real image acquisition, architecture, cache restoration or application operation inferred from these literal boundary tests.'])
   fixture['id']=fid;fixture['action']=binding['action'];fixture[polarity]=dict(input=binding['input'],expected=binding['expected'])
   g['cases'].append(c);f['case_bindings'].append(binding);f['fixtures'].append(fixture);a['plans'].append(copy.deepcopy(binding));new_tests.append(identity);new_cases.append(cid)
   row=next(s for s in sets['properties'] if s['property_id']==pid);row[polarity+'_cases'].append(cid);row[polarity+'_distinct_packets']=len(row[polarity+'_cases'])
for name in ['tests/release_images.py','tests/test_release_images.py']:
 text=(R/name).read_text();library[name]=dict(source_path=name,source_sha256=hashlib.sha256(text.encode()).hexdigest(),fixture_source=text,origin='Platform-cache helper and controlled Docker boundary; actual qualification remains the real portable fixture.')
d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+new_tests))
if not any(r['id']=='iteration16-platform-cache-repair' for r in d['reviews']):
 searches=[dict(kind='exact',status='completed',query='Actual docker pull cannot overwrite digest after successful registry restart; release-portable platform owner',outcome='Protect original cache with an owned rollback-only tag, officially acquire target platform and observe final restoration after cleanup.',results=[dict(path='tests/release_images.py',classification='change_candidate',reason='Classic Docker image store holds one platform for the pinned digest reference.')])]
 for kind in ['semantic','jetbrains-index']:searches.append(dict(kind=kind,status='unavailable',query='Exact iteration16platform-cache test owner',reason='No matching semantic/IDEindex available; explicit failure identifies the exact existing fixture owner.',outcome='No semantic evidence claimed.',results=[]))
 d['reviews'].append(dict(id='iteration16-platform-cache-repair',question='Does genuine dual-architecture acquisition preserve the original image and protected host state, including a failed pull?',property_ids=['I16-07.P1'],test_ids=new_tests,searches=searches,disposition='current_change',rationale='User-authorized registry repair. Tests alone own cache switching; application keeps official pinned images and its existing launcher.'))
for case in g['cases']:
 if case['source_path']=='tests/test_release_images.py':
  for rows in [f['case_bindings'],a['plans']]:
   for b in rows:
    if b['case_id']==case['id']:b['initial_state']['origin']='Constructed Docker CLI boundary; real platform-cache helper, independently expected state/rollback, no actual image or architecture claim.'
  binding=next(b for b in f['case_bindings'] if b['case_id']==case['id']);fixture=next(x for x in f['fixtures'] if x['id']==binding['fixture_id']);fixture['origin']='Constructed Docker CLI boundary only; native portable cases qualify actual registry/images.';fixture['initial_state']=copy.deepcopy(binding['initial_state'])
for p,x in [(C/'verification.json',g),(C/'discovery.json',d),(V/'verification-fixtures.v1.json',f),(V/'property-test-sets.v1.json',sets),(A/'CASES.json',a),(A/'FIXTURE-LIBRARY.json',library)]:save(p,x)
print(json.dumps(dict(new_cases=new_cases,selected_edges=sum(c['id'].startswith('I16-') for c in g['cases']))))
