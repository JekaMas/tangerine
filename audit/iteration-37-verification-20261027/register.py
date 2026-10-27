"""Reconcile I37's added literal regressions, retaining original native evidence."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASE=ROOT/'openspec/changes/implement-teacher-error-trainer'

def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def main():
    path='tests/test_speech_supplements.py';body=(ROOT/path).read_text()
    methods={node.name:ast.get_source_segment(body,node) for cls in ast.parse(body).body if isinstance(cls,ast.ClassDef) for node in cls.body if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}
    graph=json.loads((BASE/'verification.json').read_text())
    original=[case for case in graph['cases'] if case['id'].startswith('I37.')]
    template=next(c for c in original if c['id']=='I37.P7.test_consumers_positive')
    deps=['tests/source_playback.test.mjs','tests/source_proxy_range.test.mjs','tests/supplement_media_browser.cjs','tests/supplement_range_browser.cjs','tests/supplement_recovery_visual.cjs','audit/iteration-37-verification-20261027/EVIDENCE.json']
    added=[]
    for polarity in ['positive','negative']:
        name='test_media_recovery_'+polarity;case=copy.deepcopy(template)
        case.update(id='I37.P7.'+name,polarity=polarity,test_id='unittest::tests.test_speech_supplements.SpeechSupplements.'+name,
            setup='Actual admitted ELRD/EdAcc/DRAL media through Next/Go/private MinIO and installed Chrome; controlled503 responses only, plus constructed media events through the actual owner.',
            red_expectation='One transient failure becomes final; unbounded retries, wrong replay clock, lost data, raw backend text, stale playback or dropped native range metadata.',
            green_expectation='Same-asset bounded retry and explicit recovery, finite saved clocks, disposal, safe diagnostics and readable keyboard-operable UI match independent literal observations.')
        case['substitution']=dict(classification='APPROVED_TEST_DOUBLE',owner_replaced='Explicitly controlled HTTP503 media replies; constructed HTML media events; actual saved-window row selection for viewport.',allowed_proof='Actual native transport, stored playback, retry and source UI behavior; controlled event ownership.',forbidden_claims=['Live outage frequency','New synthesis or acoustic quality','Independent human labels','Every historical iteration reexecuted'])
        added.append(case)
    graph['cases']=[c for c in graph['cases'] if not c['id'].startswith('I37.P7.test_media_recovery_')]+added
    for case in graph['cases']:
        if not case['id'].startswith('I37.'):continue
        method=case['test_id'].split('.')[-1]
        case['source_sha256']=hashlib.sha256(body.encode()).hexdigest();case['observable']=methods[method]
        case['invalidation_dependencies']=list(dict.fromkeys(case['invalidation_dependencies']+deps))
    for prop in graph['properties']:
        if prop['id']=='I37.P7':prop['source_globs']=list(dict.fromkeys(prop['source_globs']+deps))
    save(BASE/'verification.json',graph)
    selected=[c for c in graph['cases'] if c['id'].startswith('I37.')]
    save(HERE/'SELECTION.json',dict(iteration=37,requirement_ids=['I37'],property_ids=['I37.P'+str(n) for n in range(1,8)],case_ids=[c['id'] for c in selected],expected_case_count=len(selected),prior_selection='audit/iteration-37-supplements-20261027/SELECTION.json'))
    discovery=json.loads((BASE/'discovery.json').read_text());ids=[c['test_id'] for c in added]
    discovery['scope']['test_ids']=list(dict.fromkeys(discovery['scope']['test_ids']+ids))
    review=dict(id='iteration37-verification',question='Source playback recovery/lifetime and original media range metadata through the actual web proxy.',disposition='current_change',rationale='Reproduced F1 media-error finalization and F2 metadata omission; one source playback owner and one existing proxy owner repaired.',property_ids=['I37.P7'],test_ids=ids,searches=[
        dict(kind='exact',status='completed',query='NativeExamples/createPassageReplay, sourceRequest/clientFetch, sourceFileGet, Next proxy and retained source/Chrome receipts.',outcome='Known owners and sibling playback/read cases traced; exact native field/count/clock/group contracts reviewed.',results=[dict(path=p,classification='interface_dependency',reason='Actual producer/consumer owner inspected.') for p in ['services/web/app/sources/NativeExamples.js','services/web/app/sources/sourcePlayback.js','services/web/app/api/[...path]/route.js','services/api/internal/app/source_supplements.go','services/api/internal/app/source_supplements_dral.go','services/api/internal/app/empirical_reports.go']]),
        dict(kind='semantic',status='unavailable',query='Where do empirical source reports count populations and group source records to avoid duplicate overlapping task views or corpus versions?',reason='Actual jbcontext query reports no index for github.com/jekamas/tangerine.',outcome='Exact source group_ids and single-population consumer tracing used; no semantic claim.',results=[]),
        dict(kind='jetbrains-index',status='not_applicable',query='Known source normalization and media recovery owners.',reason='No symbol refactor or PSI operation needed.',outcome='No IDE/index evidence claimed.',results=[])])
    discovery['reviews']=[r for r in discovery['reviews'] if r['id']!=review['id']]+[review];save(BASE/'discovery.json',discovery)
    continuation=json.loads((BASE/'completion-iterations.json').read_text());entry=next(r for r in continuation['iterations'] if r['iteration']==37);entry['selection']=str(HERE.relative_to(ROOT)/'SELECTION.json');save(BASE/'completion-iterations.json',continuation)
    print(json.dumps(dict(requirement='I37',properties=7,cases=len(selected),new_recovery_cases=len(added))))

if __name__=='__main__':main()
