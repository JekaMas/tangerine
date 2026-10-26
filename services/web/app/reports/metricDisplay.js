// Ordinary summaries use authored explanations. Native details remain in Advanced.
const unavailable={
  leaf_annotation_scope_not_declared:'Not annotated',
  correct_opportunity_annotations_absent:'Correct-use observations needed',
  native_token_exposure_unknown:'Token count unavailable',
  no_error_events:'No mistakes observed',
  zero_denominator:'No eligible observations',
};
export function metricDisplay(metric) {
  if(metric?.missing_reason)return unavailable[metric.missing_reason]||'Not available';
  if(metric?.exact)return `${metric.exact.numerator}/${metric.exact.denominator}`;
  if(metric?.numerator!=null&&metric?.denominator!=null)return `${metric.numerator}/${metric.denominator}`;
  return metric?.value??'Not observed';
}
