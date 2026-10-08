"""One-time explicit reconciliation of retained receipts; never executes tests.

Original evidence stays immutable. Every selected output must match its actual
command receipt. Invalidation/reuse reasons are recorded beside current results.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CHANGE = 'implement-teacher-error-trainer'
C = ROOT / 'openspec/changes' / CHANGE
E = C / 'evidence'
sys.path.insert(0, str(ROOT / '.agents/workflow/scripts'))
from requirement_tests import EvidenceGraph, case_evidence_fingerprint, parse_go_events, parse_unittest_events


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    destination = E / 'current-foundation-results.json'
    if destination.exists():
        raise SystemExit('Current reconciliation exists; preserve it and reconcile subsequent inputs separately.')
    manifest = json.loads((C / 'verification.json').read_text())
    receipts = {r['id']: r for r in json.loads((E / 'command-receipts.json').read_text())['commands']}
    new_commands = [
        dict(id='ratio', runner='python-unittest', argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_ratio_boundary.py','-v'], cwd='.', env={}, timeout_seconds=30, authority='local'),
        dict(id='storage-config', runner='go-test-json', argv=['go','test','-json','-count=1','-run','^TestStorageConfiguration','./internal/app'], cwd='services/api', env={}, timeout_seconds=120, authority='local'),
        dict(id='storage-original', runner='python-unittest', argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_storage_runtime.py','-v'], cwd='.', env={'TANGERINE_RUN_STORAGE':'1'}, timeout_seconds=300, authority='local'),
        dict(id='storage-selected', runner='python-unittest', argv=['python3','-B','-m','unittest','test_storage_runtime.StorageRuntimeTests.test_initialization_idempotent_positive','test_storage_runtime.StorageRuntimeTests.test_restart_persists_session_and_state_positive','-v'], cwd='.', env={'TANGERINE_RUN_STORAGE':'1','PYTHONPATH':'tests'}, timeout_seconds=300, authority='local'),
    ]
    for arch, project in [('arm64','tangerine'),('amd64','tangerine-amd64')]:
        new_commands.append(dict(id=arch+'-architecture',runner='python-unittest',argv=['python3','-B','-m','unittest','discover','-s','tests','-p','test_architecture.py','-v'],cwd='.',env={'TANGERINE_CHECK_ARCH':arch,'TANGERINE_CHECK_PROJECT':project},timeout_seconds=60,authority='local'))
    manifest['commands'].extend(row for row in new_commands if row['id'] not in {c['id'] for c in manifest['commands']})
    for cmd in manifest['commands']:
        if cmd['id'] == 'go-security':
            cmd['env']={} # GOWORK is workflow execution policy, recorded in the receipt rather than a forbidden case env override.
        if cmd['id'] == 'storage-config':
            cmd['env']={}

    def pair(rid, suffix, statement, owner, source, command, positive, negative, negative_source=None, negative_command=None):
        template = next(c for c in manifest['cases'] if c['property_id'] == rid+'.P1')
        scenario = template['scenario']
        pid = rid+'.'+suffix
        if any(p['id']==pid for p in manifest['properties']):
            return
        manifest['properties'].append(dict(id=pid, requirement_id=rid, statement=statement, scenarios=[scenario], owner=owner, oracle='Independent boundary assertions in the named actual test methods; no inferred full requirement success.', source_globs=[owner,source]+([negative_source] if negative_source else [])))
        for polarity,method in [('positive',positive),('negative',negative)]:
            path = negative_source if polarity=='negative' and negative_source else source
            cmd = negative_command if polarity=='negative' and negative_command else command
            case=deepcopy(template)
            case.update(id=pid+'.'+polarity.upper(), property_id=pid, polarity=polarity,
                        setup='Run the named actual boundary test with its explicitly selected local inputs/dependencies.',
                        observable=statement+' '+polarity+' boundary is asserted by '+method+'.',
                        red_expectation='The assertion fails if the real owner violates its stated accepted/rejected boundary.',
                        green_expectation='The named actual assertions pass, within their stated scope.',
                        test_id=method, command_id=cmd, state='implemented', source_path=path, source_sha256=digest(path),
                        invalidation_dependencies=[path,owner],
                        substitution={'classification':'NO_TEST_DOUBLE','note':'Actual production owner or real local runtime. Invalid configuration/architecture inputs are boundary inputs; no teacher/provider/reviewer evidence is fabricated.'})
            manifest['cases'].append(case)

    pair('DOM-05','P2','The public ratio owner preserves exact rational fractions and rejects float/bool inputs.','services/speech/metrics.py','tests/test_ratio_boundary.py','ratio','unittest::test_ratio_boundary.RatioBoundaryTests.test_exact_fraction_positive','unittest::test_ratio_boundary.RatioBoundaryTests.test_inexact_types_negative')
    go='tangerine.local/api/internal/app::'
    pair('RUN-02','P2','Storage configuration admits a bounded local pool and bucket configuration and rejects malformed storage/bootstrap inputs before network access.','services/api/internal/app/storage.go','services/api/internal/app/storage_config_test.go','storage-config',go+'TestStorageConfigurationPositive',go+'TestStorageConfigurationNegative')
    live='unittest::test_storage_runtime.StorageRuntimeTests.'
    pair('RUN-02','P3','Actual initializers preserve account/migration/catalog bytes and private media denies anonymous access.','services/api/internal/app/storage.go','tests/test_storage_runtime.py','storage-selected',live+'test_initialization_idempotent_positive',live+'test_anonymous_media_negative',negative_command='storage-original')
    pair('RUN-06','P3','Restart preserves actual account/session/catalog state and isolated restore refuses an existing target without altering it.','scripts/restore_isolated.py','tests/test_storage_runtime.py','storage-selected',live+'test_restart_persists_session_and_state_positive',live+'test_existing_restore_project_negative',negative_command='storage-original')
    for arch in ['arm64','amd64']:
        pair('REL-03','P2' if arch=='arm64' else 'P3','The actual '+arch+' runtime has five matching service images and rejects a wrong expected architecture.','scripts/assert_runtime_architecture.py','tests/test_architecture.py',arch+'-architecture','unittest::test_architecture.ArchitectureTests.test_architecture_positive','unittest::test_architecture.ArchitectureTests.test_architecture_negative')
    for case in manifest['cases']:
        if case['command_id'] in ['arm64-architecture','amd64-architecture']:
            case['distinct_reason']=case['scenario']+': Same actual inspector runs with different selected expected architecture and Compose project; arm64 and amd64 observations are independently required.'
        if case['command_id'] in ['runtime','readiness-failure']:
            case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+['services/api/internal/app/storage.go','services/api/internal/app/security.go','services/api/internal/app/migrations/001_foundation.sql','services/web/app/api/[...path]/route.js','deploy/local/compose.yaml']))
        if case['command_id'] in ['storage-selected','storage-original','arm64-architecture','amd64-architecture']:
            case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+['services/api/internal/app/storage.go','services/api/internal/app/migrations/001_foundation.sql','deploy/local/compose.yaml']))
    (C / 'verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
    discovery=json.loads((C / 'discovery.json').read_text())
    props=[p['id'] for p in manifest['properties']]; tests=list(dict.fromkeys(c['test_id'] for c in manifest['cases']))
    discovery['scope']={'property_ids':props,'test_ids':tests}
    discovery['reviews'][0]['property_ids']=props; discovery['reviews'][0]['test_ids']=tests
    (C / 'discovery.json').write_text(json.dumps(discovery,indent=2)+'\n')
    graph=EvidenceGraph(ROOT,CHANGE)
    selections={'arithmetic':'arithmetic-after-fix','go-security':'go-security','runtime':'runtime','backup':'backup','readiness-failure':'readiness-failure','ratio':'ratio-after','storage-config':'storage-config','storage-original':'storage-original','storage-selected':'storage-secret-safe','arm64-architecture':'arm64-architecture'}
    observed={}; command_reports=[]
    for cmd,rid in selections.items():
        receipt=receipts[rid]
        if digest(receipt['artifact']) != receipt['artifact_sha256']:
            raise SystemExit('Receipt output hash mismatch: '+rid)
        raw=(ROOT / receipt['artifact']).read_text()
        observed[cmd]=parse_go_events(raw) if graph.commands[cmd]['runner']=='go-test-json' else parse_unittest_events(raw)
        command_reports.append(dict(receipt, graph_command_id=cmd, observed_tests=observed[cmd]))
    # Verify unchanged methods, not the whole modified test module, for reuse of
    # its two original negative observations. The modified methods use fresh logs.
    import ast
    before=(E / 'test_storage_runtime.before-secret-safe-diagnostics.py').read_text()
    after=(ROOT / 'tests/test_storage_runtime.py').read_text()
    def method_dump(text,name):
        return ast.dump(next(n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
    for method in ['test_anonymous_media_negative','test_existing_restore_project_negative']:
        if method_dump(before,method) != method_dump(after,method):
            raise SystemExit('Original negative assertion changed: '+method)
    report=dict(schema_version=2,change=CHANGE,status='incomplete',origin='Explicit retained native command receipts; no tests executed by reconciliation.',
                reuse_reason='Unchanged exercised owners and assertions retain their genuine observations. Arithmetic shared owner changed and has new 59-case receipt. Storage modified assertions use the fresh selected receipt, including its failed restart. Two unchanged storage rejection methods verified by AST comparison retain original receipts. Command metadata/dependency completeness corrections do not rerun unchanged behavior. See invalidation-record.md.',commands=command_reports,cases={})
    for cid,case in graph.cases.items():
        status=observed.get(case['command_id'],{}).get(case['test_id'])
        result='not_run' if status is None else ('passed' if status=='pass' else 'failed' if status=='fail' else status)
        report['cases'][cid]=dict(status=result,test_id=case['test_id'],property_id=case['property_id'],state=case['state'],source_sha256=case.get('source_sha256'),evidence_fingerprint=case_evidence_fingerprint(graph,cid),proof_boundary='Named arithmetic/local foundation boundary only; never full trainer, linguistic, corpus, human or provider acceptance.')
    report['counts']={s:sum(r['status']==s for r in report['cases'].values()) for s in ['passed','failed','not_run','skip']}
    report['requirements']=len(graph.requirements);report['properties']=len(graph.properties);report['case_edges']=len(graph.cases)
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['requirements','properties','case_edges','counts','status']}))

if __name__=='__main__':
    main()
