import {failureReason} from '../requestError.js';
// Display saved state. Viewing an error owns no retry or provider action.
export function failureMessage(item) {
  if (item.audio_available || item.phase_states?.render === 'complete') return '';
  const phase = [['canonical_text','Clean text'],['mutation','Mistakes'],['render','Audio']]
    .find(([key]) => ['failed','interrupted'].includes(item.phase_states?.[key]));
  if (!item.last_failure && !phase) return '';
  const failure = item.last_failure || {};
  const reason = failureReason(failure.code);
  const guidance = failure.code === 'CONSTRAINT_CONFLICT'
    ? 'Check the selected model, service access and request settings in Settings before trying again.'
    : ['MODEL_SETUP_REQUIRED','CAPABILITY_UNQUALIFIED','MISSING_CREDENTIAL','MISSING_CREDENTIALS','PAID_USE_FORBIDDEN','LOCAL_BUDGET_EXCEEDED'].includes(failure.code)
    ? 'Check Settings, then resume this exercise explicitly.'
    : failure.retryable === false ? 'Check the request and Settings before trying again.' : 'When the service is available, resume this exercise explicitly.';
  return `${phase ? phase[1]+': ' : ''}${reason} Saved text, mutations and completed audio pieces are retained. ${guidance}`;
}
