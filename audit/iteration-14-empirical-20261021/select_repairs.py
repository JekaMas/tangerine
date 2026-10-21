"""Select semantic repairs, retaining unchanged clean observation boundaries."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;C=R/'openspec/changes/implement-teacher-error-trainer';p=C/'verification.json';g=json.loads(p.read_text());selection=json.loads((A/'CASES.json').read_text());scope={v['case_id'] for v in selection['plans']};base=json.loads((R/'data/iteration14/acceptance-clean-2594009.json').read_text())
fresh_names={'TestQualityJSONPathPositive','TestQualityJSONPathNegative','TestQualityFractionalScorePositive','TestQualityMissingReferenceNegative','TestQualityFalsePositiveNegative','TestQualityDuplicateClaimPositive','TestQualityIndependentComponentsPositive','TestQualityWrongMappingNegative','TestQualityWrappedEvidencePositive','TestQualityAbsentWrappedEvidenceNegative','TestExperimentMetricPositive/llm_lab.score_mae_pp','TestExperimentMetricNegative/llm_lab.score_mae_pp'}
fresh=[];retained=[]
for c in g['cases']:
 if c['id'] not in scope:continue
 name=c['test_id'].split('::')[-1]
 if name in fresh_names:c['command_id']='iteration14-repair-go';fresh.append(c['id'])
 elif c['command_id'] in ['iteration14-3-local','iteration14-4-lab']:fresh.append(c['id'])
 else:
  # Case identifiers may be shifted by inserted regression cases. Match the
  # unchanged exact physical test and property/polarity to its prior clean row.
  prior=[(cid,v) for cid,v in base['cases'].items() if v['status']=='passed' and v['test_id']==c['test_id'] and v['property_id']==c['property_id'] and v['polarity']==c['polarity']]
  assert prior,(c['id'],name);retained.append(c['id'])
command=dict(id='iteration14-repair-go',runner='go-test-json',argv=['./tests/go-docker','test','-json','-race','-count=1','-run','^Test(Quality(JSONPath|FractionalScore|MissingReference|FalsePositive|DuplicateClaim|IndependentComponents|WrongMapping|WrappedEvidence|AbsentWrappedEvidence)(Positive|Negative)|ExperimentMetric(Positive|Negative))$/^llm_lab.score_mae_pp$','./internal/app','./internal/experiment'],cwd='.',env=dict(DOCKER_HOST='unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock'),timeout_seconds=600,authority='local')
g['commands']=[v for v in g['commands'] if v['id']!='iteration14-repair-go']+[command];p.write_text(json.dumps(g,indent=2)+'\n')
plan=dict(base='259400908b62a463d328bcd34c3303a3ba6beefe',base_receipt='data/iteration14/acceptance-clean-2594009.json',fresh_case_ids=fresh,retained_case_ids=retained,semantic_changes=['Diagnostic MAE preserves actual reference count for fractional errors','Independent diagnostic event detection counts native unsupported false-positive assertions once','Judge admits only source-resolved literal JSONPath field/index aliases at its existing single admission','Lab tests require the current selected actual run; all actual repair/transport attempts remain in dispatch/native/MLflow accounting'],retention_rule='Unchanged literal inputs/independent assertions and actual exercised production paths retain their original clean receipt. Changed fingerprints from broad globs are reported, never refreshed into the old receipt. Every actual semantic dependency change selects fresh observations; no failed local case is retained as green.')
(A/'REPAIR-SELECTION.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(dict(fresh=len(fresh),retained=len(retained),total=len(scope))))
