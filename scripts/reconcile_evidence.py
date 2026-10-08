"""Bind concrete tests and retained native observations to the project graph.

This adapter uses the pinned workflow's parsers/fingerprints. It never executes
tests or invents pass status for a planned case. Reuse is justified only while
the logged test bodies and exercised production owners remain unchanged.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CHANGE = 'implement-teacher-error-trainer'
C = ROOT / 'openspec/changes' / CHANGE
sys.path.insert(0, str(ROOT / '.agents/workflow/scripts'))
from requirement_tests import EvidenceGraph, case_evidence_fingerprint, parse_go_events, parse_unittest_events


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    if (C/'evidence/retained-native-results.json').exists():
        raise SystemExit('Retained evidence already exists. Do not mutate the graph or refresh observations implicitly.')
    manifest = json.loads((C / 'verification.json').read_text())
    commands = {
        'arithmetic': {'runner': 'python-unittest', 'argv': ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_metrics.py', '-v'], 'cwd': '.', 'env': {}, 'timeout_seconds': 30, 'authority': 'local'},
        'go-security': {'runner': 'go-test-json', 'argv': ['go', 'test', '-json', '-count=1', './...'], 'cwd': 'services/api', 'env': {}, 'timeout_seconds': 120, 'authority': 'local'},
        'runtime': {'runner': 'python-unittest', 'argv': ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_runtime.py', '-v'], 'cwd': '.', 'env': {'TANGERINE_RUN_LIVE': '1'}, 'timeout_seconds': 120, 'authority': 'local'},
        'backup': {'runner': 'python-unittest', 'argv': ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_backup.py', '-v'], 'cwd': '.', 'env': {'TANGERINE_BACKUP_UNDER_TEST': 'data/backups/foundation-20261008'}, 'timeout_seconds': 60, 'authority': 'local'},
        'readiness-failure': {'runner': 'python-unittest', 'argv': ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_readiness_failure.py', '-v'], 'cwd': '.', 'env': {'TANGERINE_ALLOW_DEPENDENCY_STOP': '1'}, 'timeout_seconds': 180, 'authority': 'local'},
    }
    inventory = json.loads((C / 'property-inventory.json').read_text())
    metric_rows = sorted([r for r in inventory if r['id'].startswith('MET-')], key=lambda r:r['id'])
    for row in metric_rows:
        metric = row['title'].split('Preserve ', 1)[1].replace('.', '_')
        for case in manifest['cases']:
            if case['property_id'] != row['id'] + '.P1':
                continue
            polarity = case['polarity']
            case.update(test_id=f'unittest::test_metrics.MetricsTests.test_{metric}_{polarity}',
                        command_id='arithmetic', state='implemented', source_path='tests/test_metrics.py',
                        source_sha256=digest('tests/test_metrics.py'),
                        invalidation_dependencies=['tests/test_metrics.py','services/speech/metrics.py','domain/metrics.v1.yaml'],
                        substitution={'classification':'NO_TEST_DOUBLE','note':'Independent exact arithmetic vectors exercise the real formula interpreter; no teacher answer, gold annotation or provider output is fabricated.'},
                        setup=f'Use the independently written VECTORS entry for {metric} with exact counters; the negative case uses zero, negative, floating and boolean counter inputs.',
                        observable=(f'Exact retained {metric} expression matches the independent rational result.' if polarity=='positive' else f'{metric} returns null/N/A for zero denominator and rejects invalid counters.'),
                        red_expectation=('A changed expression produces the wrong independently specified fraction.' if polarity=='positive' else 'A scorer replacing N/A with zero/one or accepting invalid counters is detected.'),
                        green_expectation=('Fraction equals the separately authored arithmetic expectation.' if polarity=='positive' else 'Zero is N/A and invalid input raises a validation error.'))

    def add_pair(requirement_id, suffix, statement, owner, oracle, source, command, positive, negative, *, negative_source=None, negative_command=None):
        existing = next(p for p in manifest['properties'] if p['id']==requirement_id+'.P1')
        scenario = existing['scenarios'][0]
        pid = requirement_id + '.' + suffix
        manifest['properties'].append(dict(id=pid,requirement_id=requirement_id,statement=statement,scenarios=[scenario],owner=owner,oracle=oracle,source_globs=[owner,source]+([negative_source] if negative_source else [])))
        template = next(c for c in manifest['cases'] if c['property_id']==existing['id'])
        for polarity,method in [('positive',positive),('negative',negative)]:
            path = negative_source if polarity=='negative' and negative_source else source
            cmd = negative_command if polarity=='negative' and negative_command else command
            case = deepcopy(template)
            case.update(id=pid+'.'+polarity.upper(),property_id=pid,polarity=polarity,
                        setup=f'Run {method} against the real {owner} boundary with the controlled infrastructure inputs or actual configured local dependencies described in that test.',
                        observable=statement + (' Accepted input satisfies its positive assertions.' if polarity=='positive' else ' Forbidden input is rejected as independently asserted.'),
                        red_expectation=('A wrong implementation rejects the actual accepted state or returns an independently incorrect result.' if polarity=='positive' else 'A wrong implementation admits unauthorized, malformed, unavailable or tampered state.'),
                        green_expectation='The exact test observation discriminates the stated '+polarity+' contract.',
                        test_id=method,command_id=cmd,state='implemented',source_path=path,source_sha256=digest(path),
                        invalidation_dependencies=[path,owner],
                        substitution={'classification':'NO_TEST_DOUBLE','note':'Real production owner. Controlled protocol metadata is input, not a replacement of storage, transport, crypto or service behavior.'})
            manifest['cases'].append(case)

    go='tangerine.local/api/internal/app::'
    sec='services/api/internal/app/security.go'
    add_pair('RUN-04','P2','Passwords use distinct random salts, accept the correct configured secret and reject wrong/malformed secrets.',sec,'Independent accepted/wrong password observations and unequal random salts.','services/api/internal/app/security_test.go','go-security',go+'TestPasswordAcceptsCorrectSecret',go+'TestPasswordRejectsWrongAndMalformedSecret')
    add_pair('RUN-04','P3','Session tokens are canonical random 32-byte values with distinct SHA-256 identity and malformed token denial.',sec,'Independent token length, encoding and changed-input identity checks.','services/api/internal/app/security_test.go','go-security',go+'TestTokenAcceptsCanonicalRandomToken',go+'TestTokenRejectsInvalidOrChangedToken')
    add_pair('RUN-05','P2','Origin configuration accepts exactly the prescribed local origin and rejects misleading hosts, userinfo, paths and queries.',sec,'Explicit independent URL rejection partitions.','services/api/internal/app/security_test.go','go-security',go+'TestOriginAcceptsLocalOrigin',go+'TestOriginRejectsForeignOrigin')
    add_pair('RUN-04','P4','The real request decoder accepts a single closed JSON object and rejects unknown fields, trailing JSON, oversize and invalid syntax.','services/api/internal/app/http.go','Protocol constraints independently expressed by accepted/invalid inputs.','services/api/internal/app/security_test.go','go-security',go+'TestJSONAcceptsClosedSingleObject',go+'TestJSONRejectsUnknownTrailingAndOversizedInput')
    live='unittest::test_runtime.RuntimeTests.'
    add_pair('RUN-04','P5','The configured real local account signs in through the web proxy and PostgreSQL; wrong credentials and logout invalidate access.','services/api/internal/app/http.go','Real HTTP responses, configured existing account and subsequent session denial.','tests/test_runtime.py','runtime',live+'test_authentication_positive',live+'test_authentication_negative')
    add_pair('RUN-03','P2','The authenticated first-start library returns the actual empty PostgreSQL result; unauthenticated reads are denied.','services/api/internal/app/http.go','Zero actual exercise rows versus unauthorized HTTP request.','tests/test_runtime.py','runtime',live+'test_library_empty_positive',live+'test_library_access_negative')
    add_pair('RUN-05','P3','The actual web proxy admits the configured same-origin logout and rejects foreign-origin login without secret disclosure.','services/web/app/api/[...path]/route.js','Real same-origin and cross-origin HTTP status observations.','tests/test_runtime.py','runtime',live+'test_origin_positive',live+'test_origin_negative')
    add_pair('RUN-06','P2','The backup validator accepts actual complete backup bytes and rejects tampered hash metadata.','scripts/verify_backup.py','SHA-256 of authentic backup files versus intentionally invalid integrity metadata.','tests/test_backup.py','backup','unittest::test_backup.BackupTests.test_actual_backup_positive','unittest::test_backup.BackupTests.test_hash_tamper_negative')
    add_pair('RUN-07','P2','Web readiness reflects actual healthy API/storage/speech and becomes unavailable when the real speech dependency stops.','services/api/internal/app/http.go','Live health versus a stopped real Compose dependency.','tests/test_runtime.py','runtime',live+'test_ready_positive','unittest::test_readiness_failure.ReadinessFailureTests.test_real_dependency_failure_negative',negative_source='tests/test_readiness_failure.py',negative_command='readiness-failure')

    # Block only dependencies that are currently unavailable. Later independent
    # implementation cases remain planned; no missing test becomes a pass.
    blocked_prefixes=('DEC-','DOM-01','DOM-02','DOM-03','DOM-04','DOM-07','AUT-','REV-','PUB-','DSP-','PRV-','TCH-','COR-','AUX-')
    for case in manifest['cases']:
        if case['state']=='planned' and case['property_id'].startswith(blocked_prefixes):
            case['state']='blocked'
            case['blocker']='Missing original domain contract, separate decision, genuine review/content or live-provider dependency; see audit/completeness.md.'
    pending = next(cmd for cmd in manifest['commands'] if cmd['id']=='pending')
    pending['expected_markers']=[case['test_id'] for case in manifest['cases'] if case['command_id']=='pending']
    manifest['commands']=[pending]+[dict(id=key,**row) for key,row in commands.items()]
    (C/'verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
    discovery=json.loads((C/'discovery.json').read_text())
    props=[row['id'] for row in manifest['properties']]
    tests=[row['test_id'] for row in manifest['cases']]
    discovery['scope']={'property_ids':props,'test_ids':tests}
    discovery['reviews'][0]['property_ids']=props
    discovery['reviews'][0]['test_ids']=tests
    discovery['reviews'][0]['searches'][0]['results'].append({'path':'services/api/internal/app/http.go','classification':'change_candidate','reason':'New actual local runtime owner implemented within requested foundation scope.'})
    (C/'discovery.json').write_text(json.dumps(discovery,indent=2)+'\n')
    graph=EvidenceGraph(ROOT,CHANGE)
    logs={'arithmetic':'evidence-python-tests.log','go-security':'evidence-go-tests.jsonl','runtime':'evidence-runtime-tests.log','backup':'evidence-backup-tests.log','readiness-failure':'evidence-readiness-failure.log'}
    observed={}
    for cmd,filename in logs.items():
        text=(C/filename).read_text()
        observed[cmd]=parse_go_events(text) if cmd=='go-security' else parse_unittest_events(text)
    report={'schema_version':2,'change':CHANGE,'status':'incomplete','origin':'retained genuine native test output; no test rerun',
            'reuse_reason':'No exercised production owner, original test body, formula or input vector changed after its recorded green run. New isolated failure/backup tests have separate logs.',
            'commands':[],'cases':{}}
    for cmd,filename in logs.items():
        report['commands'].append({'id':cmd,'argv':commands[cmd]['argv'],'cwd':commands[cmd]['cwd'],
            'exit_code':0,'observed_tests':observed[cmd],'retained_output':str((C/filename).relative_to(ROOT)),
            'output_sha256':digest(str((C/filename).relative_to(ROOT))),'boundary':'These initial receipts were observed to exit zero; future revisions must use explicit command receipts, never infer exits from parsed pass lines.'})
    for cid,case in graph.cases.items():
        status=observed.get(case['command_id'],{}).get(case['test_id'])
        if status is None:
            result='not_run'
        else:
            result='passed' if status=='pass' else status
        report['cases'][cid]={'status':result,'test_id':case['test_id'],'property_id':case['property_id'],
            'state':case['state'],'source_sha256':case.get('source_sha256'),
            'evidence_fingerprint':case_evidence_fingerprint(graph,cid),
            'proof_boundary':'Arithmetic or local foundation only; never linguistic, approved-content or full-release acceptance.'}
    evidence=C/'evidence';evidence.mkdir(exist_ok=True)
    destination=evidence/'retained-native-results.json'
    if destination.exists():
        raise SystemExit('Refusing to overwrite retained evidence. Reconcile changed inputs explicitly.')
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'requirements':len(graph.requirements),'properties':len(graph.properties),'cases':len(graph.cases),
        'observed_passed_cases':sum(row['status']=='passed' for row in report['cases'].values()),
        'not_run':sum(row['status']=='not_run' for row in report['cases'].values()),'full_acceptance':'incomplete'}))


if __name__=='__main__':
    main()
