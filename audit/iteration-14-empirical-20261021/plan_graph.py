from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];C=R/'openspec/changes/implement-teacher-error-trainer';A=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.agents/workflow/scripts'));from requirement_tests import parse_delta_specs
save=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
g=json.loads((C/'verification.json').read_text());plan=json.loads((A/'PLAN.json').read_text());cap='iteration-fourteen-empirical';d=C/'specs'/cap;d.mkdir(exist_ok=True)
lines=['## ADDED Requirements','']
for rid,title,owner,rule in plan:
 lines += [f'### Requirement: {rid} {title}','','The application SHALL '+rule+'.','']
 for j in [1,2]:lines += [f'#### Scenario: {rid} packet {j}','','- **WHEN** the declared supported or negative empirical/experiment packet reaches the native owner','- **THEN** exact independently expected counts, missingness, provenance, persisted transitions and forbidden effects SHALL hold','']
(d/'spec.md').write_text('\n'.join(lines));parsed=parse_delta_specs(C)
for key in ['requirements','properties','cases']:g[key]=[x for x in g[key] if not x['id'].startswith('I14-')]
pending=next(x for x in g['commands'] if x['id']=='pending')
for rid,title,owner,rule in plan:
 rr=parsed[cap,rid+' '+title];pid=rid+'.P1';scenarios=list(rr['scenario_fingerprints']);g['requirements'].append(dict(id=rid,capability=cap,title=rid+' '+title,fingerprint=rr['fingerprint']));g['properties'].append(dict(id=pid,requirement_id=rid,statement=rule,scenarios=scenarios,owner=owner,oracle=rule,source_globs=[owner]))
 for j,scenario in enumerate(scenarios,1):
  for pol in ['positive','negative']:
   tid=f'planned::{rid}::{j}::{pol}';g['cases'].append(dict(id=f'{pid}.S{j}.{pol.upper()}',property_id=pid,polarity=pol,scenario=scenario,scenario_fingerprint=rr['scenario_fingerprints'][scenario],distinct_reason=f'{rid} packet {j} {pol} will materialize the exact literal plan through its real owner.',setup='Explicit constructed native packets; independently expected ratios, transitions and preserved data; actual local model separately labelled.',observable=rule,red_expectation='Wrong counts, omitted rows, invented provenance or forbidden effects fail.',green_expectation='Every independent expected observation holds.',test_id=tid,command_id='pending',state='planned',source_path='audit/iteration-14-empirical-20261021/PLAN.json',source_sha256=None,invalidation_dependencies=[owner],substitution=dict(classification='UNDECIDED',note='No current execution claim.'),blocker='Iteration14 test materialization/implementation in progress.'))
pending['expected_markers']=list(dict.fromkeys(x['test_id'] for x in g['cases'] if x['command_id']=='pending'));save(C/'verification.json',g)
disc=json.loads((C/'discovery.json').read_text());pids=[p[0]+'.P1' for p in plan];tids=[c['test_id'] for c in g['cases'] if c['id'].startswith('I14-')];disc['scope']['property_ids']+=pids;disc['scope']['test_ids']+=tids
disc['reviews'].append(dict(id='iteration14-discovery',question='Trace empirical populations, exact diagnostics and native experiment execution.',property_ids=pids,test_ids=tids,searches=[dict(kind='exact',status='completed',query='Read Lab contracts and concrete native provider/preparation/speech/interpretation/scoring/storage owners',outcome='Existing native owners are reusable; no experiment runner or empirical reporting owner yet.',results=[dict(path='services/api/internal/app/lab.go',classification='change_candidate',reason='Extend native Lab maintenance routing without duplicating runtime owners')]),dict(kind='semantic',status='unavailable',query='jbcontext exact iteration14 empirical reports and quality experiments',reason='Read-only context explorer observed no index for this exact worktree/revision.',outcome='Exact discovery retained; no semantic-index evidence claimed.',results=[]),dict(kind='jetbrains-index',status='unavailable',query='Exact iteration14 worktree',reason='New isolated worktree has not been opened/indexed in IDEA; no canonical index borrowed.',outcome='No IDE semantic evidence claimed.',results=[])],disposition='current_change',rationale='Authorized iteration14 application and evidence work; preserve all earlier scope and no paid use.'))
save(C/'discovery.json',disc)
