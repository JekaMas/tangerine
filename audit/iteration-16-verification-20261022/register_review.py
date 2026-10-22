"""Append the demonstrated Settings regressions without renumbering old cases."""
from pathlib import Path
import ast,copy,hashlib,json,re
R=Path(__file__).resolve().parents[2];A=R/'audit/iteration-16-release-20261021';C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
load=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'verification-fixtures.v1.json');a=load(A/'CASES.json');sets=load(V/'property-test-sets.v1.json');d=load(C/'discovery.json')
path='tests/test_custom_audio_profile_browser.py';text=(R/path).read_text();digest=hashlib.sha256(text.encode()).hexdigest();bodies={n.name:ast.get_source_segment(text,n) for cls in ast.parse(text).body if isinstance(cls,ast.ClassDef) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
command='iteration16-86-custom-audio-settings';env=copy.deepcopy(next(c for c in g['commands'] if c['id']=='iteration16-85-test_release_current_source')['env']);env.pop('TANGERINE_TEST_VIDEO_DIR',None)
if not any(c['id']==command for c in g['commands']):g['commands'].append(dict(id=command,runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p',Path(path).name,'-v'],cwd='.',env=env,timeout_seconds=2000,authority='local'))
bindings={b['case_id']:b for b in f['case_bindings']};fixtures={x['id']:x for x in f['fixtures']};plans={b['case_id']:b for b in a['plans']}
def replace(c,b,name):
 body=bodies[name];identity='unittest::test_custom_audio_profile_browser.CustomAudioProfileTests.'+name
 b.update(test_id=identity,action='Observe '+name+' in real source-built Settings/API/PostgreSQL/Chrome with zero inference')
 b['input'].update(exact_test=name,literal_executable_fixture=body,source_path=path,source_sha256=digest,shared_fixture_library='audit/iteration-16-release-20261021/FIXTURE-LIBRARY.json#'+path)
 b['expected']['independent_literal_assertions']=body
 c.update(test_id=identity,command_id=command,source_path=path,source_sha256=digest,distinct_reason='Scenario '+c['scenario']+': exact saved custom/overridden profile or current source assertion: '+name)
 c['invalidation_dependencies']=list(dict.fromkeys([path,'tests/release-current-source','tests/release_source.py','services/web/app/settings/AudioDiagnostics.js','services/web/app/settings/page.js','services/api/internal/app/provider_configuration.go','services/api/internal/app/audio_diagnostic_config.go',*c['invalidation_dependencies']]))
 c.update(setup=b['action']+' '+json.dumps(b['input'],sort_keys=True),observable=json.dumps(b['expected'],sort_keys=True))
 fixture=fixtures[b['fixture_id']];fixture.update(action=b['action']);fixture[b['polarity']]=dict(input=b['input'],expected=b['expected']);plans[c['id']].update(b)
 return identity
old='unittest::test_release_current_source.CurrentSourceTests.test_current_arm64_source_positive'
for c in g['cases']:
 if c['id'].startswith('I16-') and c['test_id']==old:replace(c,bindings[c['id']],'test_current_source_positive')
new=[]
for name in ['test_custom_profile_positive','test_saved_binding_positive','test_custom_profile_disable_negative']:
 identity='unittest::test_custom_audio_profile_browser.CustomAudioProfileTests.'+name
 if any(c['test_id']==identity for c in g['cases']):continue
 polarity='positive' if name.endswith('_positive') else 'negative';pid='I16-04.P1'
 template=next(c for c in g['cases'] if c['property_id']==pid and c['polarity']==polarity);c=copy.deepcopy(template);b=copy.deepcopy(bindings[template['id']]);fixture=copy.deepcopy(fixtures[b['fixture_id']])
 number=1+max(int(re.search(r'\.S(\d+)\.',c['id'])[1]) for c in g['cases'] if c['property_id']==pid and c['polarity']==polarity)
 cid=f'{pid}.S{number}.{polarity.upper()}';fid='iteration16-'+cid.replace('.','-');c['id']=cid;b.update(case_id=cid,fixture_id=fid);fixture['id']=fid
 f['case_bindings'].append(b);f['fixtures'].append(fixture);a['plans'].append(copy.deepcopy(b));bindings[cid]=b;fixtures[fid]=fixture;plans[cid]=a['plans'][-1]
 replace(c,b,name);g['cases'].append(c);new.append(cid)
 for row in sets['properties']:
  if row['property_id']==pid:row[polarity+'_cases'].append(cid);row[polarity+'_distinct_packets']=len(row[polarity+'_cases'])
for c in g['cases']:
 if c['source_path']==path:c['distinct_reason']='Scenario '+c['scenario']+': exact saved custom/overridden profile or current source assertion: '+c['test_id'].split('.')[-1]
replacement='unittest::test_custom_audio_profile_browser.CustomAudioProfileTests.test_current_source_positive'
d['scope']['test_ids']=list(dict.fromkeys(replacement if t==old else t for t in d['scope']['test_ids']))
for review in d['reviews']:
 review['test_ids']=list(dict.fromkeys(replacement if t==old else t for t in review['test_ids']))
new_ids=['unittest::test_custom_audio_profile_browser.CustomAudioProfileTests.'+n for n in bodies]
d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+new_ids))
if not any(r['id']=='iteration16-verification-custom-profile' for r in d['reviews']):d['reviews'].append(dict(id='iteration16-verification-custom-profile',question='Does Settings faithfully represent the actual saved custom/model-override audio profile and setup command?',property_ids=['I16-04.P1','I16-06.P1','I16-07.P1'],test_ids=new_ids,searches=[dict(kind='exact',status='completed',query='Exact AudioDiagnostics/Settings/runtime schema/custom source-built browser path',outcome='Real browser red: active custom profile displayed No audio judge selected; model setup selected7Bfor3B. Repair is UI-only.',results=[dict(path='services/web/app/settings/AudioDiagnostics.js',classification='change_candidate',reason='Saved profile identity/model and setup command must match actual accepted configuration.')])],disposition='current_change',rationale='User-authorized I16repair. Real source-built browser/API/DB, no model fixture supplied as actual inference; zero model calls. Existing unaffected greens remain retained.'))
for review in d['reviews']:
 if review['id']=='iteration16-verification-custom-profile':
  for kind in ['semantic','jetbrains-index']:
   if not any(s['kind']==kind for s in review['searches']):review['searches'].append(dict(kind=kind,status='unavailable',query='Exact iteration16worktree Settings custom-profile review',reason='No matching semantic/IDEindex was available in the retained exact-worktree discovery; current owner is directly identified. No index refresh or semantic result is claimed.',outcome='Exact known-owner source/native browser tracing only.',results=[]))
for p,x in [(C/'verification.json',g),(C/'discovery.json',d),(V/'verification-fixtures.v1.json',f),(V/'property-test-sets.v1.json',sets),(A/'CASES.json',a)]:save(p,x)
print(json.dumps(dict(new_cases=new,replaced_source_startup=old,selected_edges=sum(c['id'].startswith('I16-') for c in g['cases']))))
