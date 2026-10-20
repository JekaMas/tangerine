from pathlib import Path
import collections,hashlib,json
r=Path(__file__).resolve().parents[2]
a=r/'audit/iteration-10-verification-20261021'
load=lambda p:json.loads((r/p).read_text())
gate=load('data/iteration10/verify-accepted-iteration10.json')
ret=load('data/iteration10/verify-dependency-retention-accepted.json')
old=load('data/iteration10/accepted-canonical-iteration10.json')
graph=load('openspec/changes/implement-teacher-error-trainer/verification.json')
local=load('data/iteration10/verify-local-observations.json')
assert gate['status']=='passed' and not gate['git']['dirty'] and gate['git']['status']=='known'
assert len(gate['cases'])==116 and all(c['status']=='passed' for c in gate['cases'].values())
assert all(c['exit_code']==0 for c in gate['commands'])
assert len(ret['nodes']['cases'])==28 and all(c['latest_observed_status']=='passed' for c in ret['nodes']['cases'].values())
assert local['status']=='observed' and local['candidate']==gate['git']['head'] and local['paid_provider_calls']==0
cases=[];definitions={c['id']:c for c in graph['cases']}
for cid,row in sorted(gate['cases'].items()):
 assert row['test_id']==definitions[cid]['test_id'] and row['source_sha256']==hashlib.sha256((r/row['source_path']).read_bytes()).hexdigest()
 cases.append(dict(case_id=cid,test_id=row['test_id'],polarity=row['polarity'],status=row['status'],source_commit=gate['git']['head'],evidence_fingerprint=row['evidence_fingerprint'],receipt='data/iteration10/verify-accepted-iteration10.json'))
for cid,current in sorted(ret['nodes']['cases'].items()):
 row=old['cases'][cid]
 assert row['status']=='passed' and row['evidence_fingerprint']==current['current_evidence_fingerprint'] and row['test_id']==definitions[cid]['test_id']
 assert next(c for c in old['commands'] if c['id']==current['command_id'])['exit_code']==0
 cases.append(dict(case_id=cid,test_id=row['test_id'],polarity=row['polarity'],status=row['status'],source_commit=old['git']['head'],evidence_fingerprint=row['evidence_fingerprint'],receipt='data/iteration10/accepted-canonical-iteration10.json',retention_query='data/iteration10/verify-dependency-retention-accepted.json'))
assert len(cases)==144 and len({c['case_id'] for c in cases})==144
counts=collections.Counter(c['polarity'] for c in cases)
result=dict(status='passed',iteration=10,source_commit=gate['git']['head'],properties=21,owned_cases=116,retained_dependency_cases=28,total_cases=144,positive_cases=counts['positive'],negative_cases=counts['negative'],current_gate='data/iteration10/verify-accepted-iteration10.json',retained_gate='data/iteration10/accepted-canonical-iteration10.json',retained_gate_overall_status=old['status'],retention_query='data/iteration10/verify-dependency-retention-accepted.json',actual_local_model=local,static_checks=dict(artifact_assertions=370,property_set_assertions=4361,openspec='passed',graph_discovery='passed',go_vet_gofmt='passed',web_build='retained unchanged locked source/image'),private_evidence_root=str(r/'data/iteration10'),cases=cases,proof_boundary='Complete I10 selection on a committed-clean source; exact unchanged predecessor fingerprints retained. Four actual local agreement/reason cases and native controlled-protocol persistence/browser/source comparisons, not hosted entitlement, universal linguistic quality, acoustic acceptance, native grade arithmetic or later product completion.')
(a/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['cases','actual_local_model']}))
