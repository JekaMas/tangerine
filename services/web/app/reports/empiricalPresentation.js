import {metricDisplay} from './metricDisplay.js';

// Display accepted report values. Arithmetic and input admission stay native.
export function measurement(value) {
  return {value:metricDisplay(value),counts:value?.numerator!=null&&value?.denominator!=null
    ? `${value.numerator} / ${value.denominator}`:null};
}
export function populationFields(population) {
  return [['Release','release'],['View','view'],['Split','split'],['Annotator','annotator'],
    ['Window','window'],['Modality','modality'],['Taxonomy','taxonomy_version'],
    ['Crosswalk','crosswalk_version'],['Label origin','label_origin'],
    ['First language','l1'],['English level','cefr'],['Task','task']]
    .map(([label,key])=>[label,population[key]||'Unknown']);
}
export function populationNotice(origin) {
  if(['constructed','authored_assertion'].includes(origin))return 'Constructed observations. These demonstrate report calculations; they do not measure real learner frequencies.';
  if(['model','model_generated'].includes(origin))return 'Model-generated observations. Their frequencies describe these generated records only.';
  if(!origin||origin==='unknown')return 'Observation origin is unknown. This report does not establish real learner frequencies.';
  return 'These measurements describe only the selected population and its recorded annotations. They do not establish frequencies for all English learners.';
}
const difficultyReasons=new Map([
  ['insufficient_population','No eligible independent first answers were recorded.'],
  ['insufficient_sample','At least 100 independent first answers are needed to rate difficulty.'],
  ['interval_crosses_band','The confidence interval crosses difficulty bands. The difficulty remains unrated.'],
]);
export const difficultyReason=reason=>reason?difficultyReasons.get(reason)||'The selected observations do not support a difficulty rating.':null;
const exclusions=new Map([
  ['not_genuine_teacher','Constructed, model or other non-learner observations'],
  ['participant_unknown','Participant identity unknown'],['not_first_exposure','Later exposures'],
  ['duplicate_participant_exposure','Repeated participant first exposures'],['success_unknown','Outcome unknown'],
  ['noop','No-error annotations'],['invalid','Invalid source annotations'],
  ['unresolved_native_label','Unresolved native labels'],
  ['empirical_window_projection_absent','Window annotations unavailable'],
]);
export const exclusionLabel=reason=>exclusions.get(reason)||'Other excluded observations';
export function coverageSummary(report) {
  return {inspected:report.annotated_leaf_ids?.length||0,total:report.leaves.length,
    withEvents:report.leaves.filter(leaf=>leaf.events>0).length};
}
