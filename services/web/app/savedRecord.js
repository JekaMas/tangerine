export function recordTitle(item) {
  return item.exercise_title?.trim() || item.exercise_request?.topic?.trim() || item.title?.trim() || 'Untitled exercise';
}
export function recordDate(value) {
  if (!value || Number.isNaN(new Date(value).getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat('en-GB', {dateStyle:'medium', timeStyle:'short'}).format(new Date(value));
}
export function recordState(state) {
  return ({started:'Draft',saved:'Answer saved',evaluating:'Checking answer',completed:'Completed',evaluation_failed:'Checking interrupted',review_required:'Some findings uncertain'})[state] || state?.replaceAll('_',' ') || 'Status unavailable';
}

// Show a complete identity only when the ordinary title/date cannot distinguish
// records. Prefixes are not unique identifiers and never replace saved links.
export function needsRecordIdentity(item, items, dateField) {
  return items.some(other => other.id !== item.id &&
    recordTitle(other) === recordTitle(item) &&
    recordDate(other[dateField]) === recordDate(item[dateField]));
}
