"""Expand I35 only; retain exact original native case/test bindings and receipts."""
import ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
BASE=ROOT/'openspec/changes/implement-teacher-error-trainer'
sys.path.insert(0,str(ROOT/'.agents/workflow/scripts'))
from requirement_tests import parse_delta_specs

def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n')

def main():
    spec=parse_delta_specs(BASE)[('iteration-thirty-five-official-l2','I35 Complete official L2-ARCTIC application import')]
    graph=json.loads((BASE/'verification.json').read_text())
    for row in graph['requirements']:
        if row['id']=='I35':row['fingerprint']=spec['fingerprint']
    props=['I35.P5','I35.P6','I35.P7'];command='iteration35-verify-evidence'
    graph['properties']=[r for r in graph['properties'] if r['id'] not in props]
    graph['cases']=[r for r in graph['cases'] if r['property_id'] not in props]
    graph['commands']=[r for r in graph['commands'] if r['id']!=command]
    source='tests/test_official_l2_verification.py';text=(ROOT/source).read_text();methods={}
    for cls in ast.parse(text).body:
        if isinstance(cls,ast.ClassDef):
            for method in cls.body:
                if isinstance(method,ast.FunctionDef) and method.name.startswith('test_'):methods[method.name]=ast.get_source_segment(text,method)
    scenarios=list(spec['scenario_fingerprints'])[4:]
    names=[['test_selection_positive','test_selection_negative'],['test_browsing_positive','test_recovery_negative'],['test_typography_positive','test_layout_and_evidence_negative']]
    owners=['services/web/app/sources/sourceSession.js','services/web/app/sources/page.js','services/web/app/style.css']
    deps=['services/web/app/sources/*.js','services/web/app/clientRequest.js','services/web/app/RefreshButton.js','services/web/app/requestError.js','services/web/app/AppShell.js','services/web/app/style.css','tests/source_session.test.mjs',source,'audit/iteration-35-verification-20261027/browser.cjs','audit/iteration-35-verification-20261027/browser_gateway.py','audit/iteration-35-verification-20261027/build_video.py','audit/iteration-35-verification-20261027/capture_report.cjs']
    evidence=['data/iteration-35-verification-20261027/source-session.tap','data/iteration-35-verification-20261027/browser/observations.json','data/iteration-35-verification-20261027/browser/requests.jsonl','data/iteration-35-verification-20261027/browser/video.json']
    for i,pid in enumerate(props):
        scenario=scenarios[i]
        graph['properties'].append(dict(id=pid,requirement_id='I35',statement=scenario,scenarios=[scenario],owner=owners[i],oracle='Literal stored identities/counts, actual Node production-owner assertions, native full-source Chrome reads and independently expected error/reflow states. Original native receipts remain unchanged.',source_globs=deps,iteration=35))
        for name in names[i]:
            graph['cases'].append(dict(id=pid+'.'+name,property_id=pid,polarity='negative' if name.endswith('negative') else 'positive',scenario=scenario,scenario_fingerprint=spec['scenario_fingerprints'][scenario],setup='Retained actual full official I35 PostgreSQL/MinIO, current source-built frontend and real API in private disposable containers. Installed Chrome; test gateway only controls connection failures and permits GET only.',observable=methods[name],red_expectation='The exact expected selection, release/count/native bytes, recovery, visible error, layout or evidence relation is absent or wrong.',green_expectation='Each literal assertion holds with actual production-owner/browser observations; no inferred successful data, provider dispatch or new corpus audit.',test_id='unittest::tests.test_official_l2_verification.OfficialL2Verification.'+name,command_id=command,state='implemented',source_path=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),invalidation_dependencies=deps+evidence,substitution=dict(classification='APPROVED_TEST_DOUBLE',owner_replaced='Only selected gateway HTTP connection-failure responses. Successful reads use the real API, complete imported PostgreSQL and original private media. No DOM, parser, projection or persistence double.',allowed_proof='Source selection owner positive/negative literals, actual stored full-release UI/readback and bounded error/retry/reflow behavior.',forbidden_claims=['A new full import or corpus integrity audit','Underlying dependency failure instead of controlled HTTP response','New audio/model/provider quality','A continuous unedited demo or synthesized audio']),distinct_reason=scenario+': '+name))
    graph['commands'].append(dict(id=command,runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_official_l2_verification'],cwd='.',env={},timeout_seconds=120,authority='local'))
    save(BASE/'verification.json',graph)
    all_props=[f'I35.P{i}' for i in range(1,8)];cases=[c for c in graph['cases'] if c['property_id'] in all_props]
    save(HERE/'SELECTION.json',dict(iteration=35,requirement_ids=['I35'],property_ids=all_props,case_ids=[c['id'] for c in cases],expected_case_count=len(cases),retained_native_acceptance='audit/iteration-35-official-l2-20261027/ACCEPTANCE.json'))
    p=BASE/'completion-iterations.json';v=json.loads(p.read_text())
    for row in v['iterations']:
        if row['iteration']==35:row.update(verify_property_ids=all_props,visual_applicable=True,visual_scope='Actual full official Sources status/report/rows/history/reload/original attachment, controlled HTTP recovery, keyboard and desktop/narrow typography.',selection=str(HERE.relative_to(ROOT)/'SELECTION.json'),verify_command_ids=['iteration35-evidence',command])
    save(p,v)
    p=BASE/'discovery.json';v=json.loads(p.read_text());v['scope']['property_ids']=list(dict.fromkeys(v['scope']['property_ids']+props));tests=[c['test_id'] for c in cases if c['property_id'] in props];v['scope']['test_ids']=list(dict.fromkeys(v['scope']['test_ids']+tests))
    v['reviews']=[r for r in v['reviews'] if r['id']!='iteration35-verification']
    v['reviews'].append(dict(id='iteration35-verification',question='Verify full official native import and newly requested actual source UI/recovery/typography; repair demonstrated siblings without repeated accepted-data checks.',disposition='current_change',rationale='The complete native import remains unchanged. Actual browser reproduction confirms full-manifest localStorage overflow; shared source session now caches locator identities and restores accepted data by existing reads. All source selection/recovery siblings and current actual UI evidence are included.',property_ids=props,test_ids=tests,searches=[dict(kind='exact',status='completed',query='Exact official full import storage/parser/projection/count/clock and Sources session/cache/request/transport/UI/tests plus native and browser receipts.',outcome='Single source-session owner and exact caller/sibling tests inspected. Full official browser repro, Node33 cases and current native/API readback provenance retained.',results=[dict(path=o,classification='interface_dependency',reason='Actual owner and direct callers inspected.') for o in owners]),dict(kind='semantic',status='unavailable',query='Complete official L2 import and saved source selection recovery ownership',reason='Earlier actual jbcontext call reported no index for github.com/jekamas/tangerine. Known exact owners inspected; no index was created.',outcome='No semantic evidence claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Sources session, browser/native execution and evidence review.',reason='Known exact owners and actual runtime observations; no PSI refactor or IDE operation needed.',outcome='No IDE/index evidence claimed.',results=[])]))
    save(p,v)
    print(json.dumps(dict(properties=len(all_props),cases=len(cases))))
if __name__=='__main__':main()
