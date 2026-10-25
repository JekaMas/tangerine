import {failureReason} from '../requestError.js';
// Display saved state. Viewing an error owns no retry or provider action.
export function failureMessage(item) {
  if (item.audio_available || item.phase_states?.render === 'complete' || !item.last_failure) return '';
  const failure = item.last_failure;
  const reason = failureReason(failure.code);
  const guidance = ['MODEL_SETUP_REQUIRED','CAPABILITY_UNQUALIFIED','MISSING_CREDENTIAL','PAID_USE_FORBIDDEN','LOCAL_BUDGET_EXCEEDED'].includes(failure.code)
    ? 'Check Settings, then resume this exercise explicitly.'
    : failure.retryable === false ? 'Check the request and Settings before trying again.' : 'When the service is available, resume this exercise explicitly.';
  return `${reason} Saved text, mutations and completed audio pieces are retained. ${guidance}`;
}
