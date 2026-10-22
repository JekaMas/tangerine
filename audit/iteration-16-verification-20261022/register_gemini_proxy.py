"""Append explicit proxy/redirect/tunnel counterexamples without renumbering."""
from pathlib import Path
import ast,copy,hashlib,json,re
R=Path(__file__).resolve().parents[2];A=R/'audit/iteration-16-release-20261021';C=R/'openspec/changes/implement-teacher-error-trainer';V=R/'specification/v2/domain'
load=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
g=load(C/'verification.json');f=load(V/'verification-fixtures.v1.json');a=load(A/'CASES.json');sets=load(V/'property-test-sets.v1.json');d=load(C/'discovery.json');added=[]
for path,pid in [('tests/test_auditory_protocol.py','I16-03.P1'),('tests/test_release_network.py','I16-06.P1')]:
 text=(R/path).read_text();digest=hashlib.sha256(text.encode()).hexdigest()
 for cls in [x for x in ast.parse(text).body if isinstance(x,ast.ClassDef)]:
  for node in [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')]:
   identity='unittest::'+Path(path).stem+'.'+cls.name+'.'+node.name
   if any(c['test_id']==identity and c['property_id']==pid for c in g['cases']):continue
   polarity='negative' if 'negative' in node.name else 'positive';template=next(c for c in g['cases'] if c['source_path']==path and c['property_id']==pid and c['polarity']==polarity);case=copy.deepcopy(template);binding=copy.deepcopy(next(b for b in f['case_bindings'] if b['case_id']==case['id']));fixture=copy.deepcopy(next(x for x in f['fixtures'] if x['id']==binding['fixture_id']))
   number=1+max(int(re.search(r'\.S(\d+)\.',c['id'])[1]) for c in g['cases'] if c['property_id']==pid and c['polarity']==polarity);cid=f'{pid}.S{number}.{polarity.upper()}';fid='iteration16-'+cid.replace('.','-');body=ast.get_source_segment(text,node)
   binding.update(case_id=cid,fixture_id=fid,test_id=identity,action='Observe '+node.name+' through the actual proxy/tunnel owner with constructed transport only')
   binding['input'].update(exact_test=node.name,literal_executable_fixture=body,source_path=path,source_sha256=digest,shared_fixture_library='audit/iteration-16-release-20261021/FIXTURE-LIBRARY.json#'+path);binding['expected']['independent_literal_assertions']=body;binding['initial_state']['origin']='Constructed transport/control boundary with literal expected proxy, redirect and destination behavior; no actual provider or billing claim.'
   case.update(id=cid,test_id=identity,source_sha256=digest,distinct_reason='Scenario '+case['scenario']+': exact proxy/tunnel counterexample '+node.name,setup=binding['action']+' '+json.dumps(binding['input'],sort_keys=True),observable=json.dumps(binding['expected'],sort_keys=True),substitution=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Only constructed urllib transport or tunnel transfer callbacks',forbidden_claims=['No actual Google TLS, model response, entitlement, billing enforcement or acoustic accuracy inferred.']))
   fixture.update(id=fid,action=binding['action'],initial_state=copy.deepcopy(binding['initial_state']),origin=binding['initial_state']['origin']);fixture[polarity]=dict(input=binding['input'],expected=binding['expected'])
   g['cases'].append(case);f['case_bindings'].append(binding);f['fixtures'].append(fixture);a['plans'].append(copy.deepcopy(binding));added.append(identity)
   row=next(x for x in sets['properties'] if x['property_id']==pid);row[polarity+'_cases'].append(cid);row[polarity+'_distinct_packets']=len(row[polarity+'_cases'])
d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+added))
if not any(x['id']=='iteration16-gemini-proxy' for x in d['reviews']):
 searches=[dict(kind='exact',status='completed',query='Actual Gemini first-call network timeout, ignored HTTPS proxy, release TLS allowlist and current setup-guide status',outcome='Honor standard proxy environment in the existing HTTP owner; allow only approved Google TLS in the test bridge. Retain TLS/no-redirect/free-tier behavior and update stale implementation wording.',results=[dict(path='services/speech/diagnostic_models.py',classification='change_candidate',reason='Explicit ProxyHandler({}) bypasses configured proxies.'),dict(path='tests/release_network.py',classification='change_candidate',reason='Existing test-only allowlist excludes newly authorized Google destination.'),dict(path='specification/v2/docs/service-setup-guide.md',classification='change_candidate',reason='Historical unimplemented wording contradicts observed current local flow.')])]
 for kind in ['semantic','jetbrains-index']:searches.append(dict(kind=kind,status='unavailable',query='Exact known Gemini HTTP and release transport owners',reason='No matching semantic/IDE index is available for this checkout; actual failure and exact symbols identify the owners.',outcome='No semantic/index evidence claimed.',results=[]))
 d['reviews'].append(dict(id='iteration16-gemini-proxy',question='Can the authorized unbilled Gemini binding use configured TLS transport without redirects or another provider?',property_ids=['I16-03.P1','I16-06.P1'],test_ids=added,searches=searches,disposition='current_change',rationale='Existing user-authorized Gemini Free qualification; no new product, billing, proxy service or runtime audit.'))
for p,x in [(C/'verification.json',g),(C/'discovery.json',d),(V/'verification-fixtures.v1.json',f),(V/'property-test-sets.v1.json',sets),(A/'CASES.json',a)]:save(p,x)
print(json.dumps(dict(new_tests=added,iteration_edges=sum(c['id'].startswith('I16-') for c in g['cases']))))
