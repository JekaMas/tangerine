export function recordTitle(item) {
  return item.exercise_title?.trim() || item.exercise_request?.topic?.trim() || 'Untitled exercise';
}
export function recordDate(value) {
  if (!value || Number.isNaN(new Date(value).getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat('en-GB', {dateStyle:'medium', timeStyle:'short'}).format(new Date(value));
}
export function recordState(state) {
  return ({started:'Draft',saved:'Answer saved',evaluating:'Checking answer',completed:'Completed',evaluation_failed:'Checking interrupted',review_required:'Some findings uncertain'})[state] || state?.replaceAll('_',' ') || 'Status unavailable';
}
