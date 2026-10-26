import assert from 'node:assert/strict';
import {test} from 'node:test';
import {measurement, populationNotice, populationFields, difficultyReason, exclusionLabel, coverageSummary} from '../services/web/app/reports/empiricalPresentation.js';

test('exact_denominator_positive',()=>{
  assert.deepEqual(measurement({numerator:'2',denominator:'10',exact:{numerator:'1',denominator:'5'},missing_reason:null}),{value:'1/5',counts:'2 / 10'});
});
test('zero_denominator_negative',()=>{
  assert.deepEqual(measurement({numerator:'2',denominator:'0',exact:null,missing_reason:'no_inspected_denominator'}),{value:'No eligible observations',counts:'2 / 0'});
});
test('unknown_exposure_negative',()=>{
  assert.deepEqual(measurement({numerator:null,denominator:null,exact:null,missing_reason:'native_token_exposure_unknown'}),{value:'Token count unavailable',counts:null});
});
test('constructed_origin_negative',()=>{
  for(const origin of ['constructed','authored_assertion']) assert.equal(populationNotice(origin),'Constructed observations. These demonstrate report calculations; they do not measure real learner frequencies.');
  assert.match(populationNotice('model'),/Model-generated observations/);
  assert.doesNotMatch(populationNotice('model'),/genuine learner/);
});
test('selected_provenance_positive',()=>{
  const p={release:'FCE-2.1',view:'train.m2',split:'train',annotator:'0',window:'sentence',modality:'text',taxonomy_version:'v1',crosswalk_version:'operator-v2',label_origin:'operator_localized_mapping',l1:null,cefr:'B1',task:'essay'};
  assert.deepEqual(populationFields(p),[['Release','FCE-2.1'],['View','train.m2'],['Split','train'],['Annotator','0'],['Window','sentence'],['Modality','text'],['Taxonomy','v1'],['Crosswalk','operator-v2'],['Label origin','operator_localized_mapping'],['First language','Unknown'],['English level','B1'],['Task','essay']]);
  assert.match(populationNotice(p.label_origin),/selected population/);
});
test('missing_provenance_negative',()=>{
  assert.equal(populationFields({})[0][1],'Unknown');
  assert.equal(populationNotice('unknown'),'Observation origin is unknown. This report does not establish real learner frequencies.');
});
test('coverage_positive',()=>{
  assert.deepEqual(coverageSummary({annotated_leaf_ids:['A'],leaves:[{id:'A',events:2},{id:'B',events:0},{id:'C',events:1}]}),{declared:1,total:3,withEvents:2});
});
test('uninspected_zero_negative',()=>{
  assert.deepEqual(coverageSummary({leaves:[{id:'A',events:0},{id:'B',events:0}]}),{declared:0,total:2,withEvents:0});
});
test('declared_scope_is_not_observation_negative',()=>{
  assert.deepEqual(coverageSummary({annotated_leaf_ids:['A'],annotated_windows:0,source_annotated_windows:1,mapping_incomplete_windows:1,leaves:[{id:'A',events:0},{id:'B',events:0}]}),{declared:1,total:2,withEvents:0});
});
test('difficulty_population_positive',()=>{
  assert.equal(difficultyReason('insufficient_sample'),'At least 100 independent first answers are needed to rate difficulty.');
  assert.equal(difficultyReason('interval_crosses_band'),'The confidence interval crosses difficulty bands. The difficulty remains unrated.');
  assert.equal(exclusionLabel('not_genuine_teacher'),'Constructed, model or other non-learner observations');
});
test('no_technical_reason_negative',()=>{
  assert.equal(difficultyReason('private backend detail'),'The selected observations do not support a difficulty rating.');
  assert.equal(exclusionLabel('private backend detail'),'Other excluded observations');
});
