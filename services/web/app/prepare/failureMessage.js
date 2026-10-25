const reasons = {
  DEADLINE_EXCEEDED: 'Generation reached its time limit.',
  PROVIDER_OUTPUT_INVALID: 'The provider returned an incomplete or unusable response.',
  PROVIDER_FAILURE: 'The selected provider could not complete this step.',
  INFRASTRUCTURE_UNAVAILABLE: 'A local dependency is unavailable.',
  CAPABILITY_UNQUALIFIED: 'The selected speech capability needs setup or a compatible voice.',
  MODEL_SETUP_REQUIRED: 'The selected local speech model needs setup.',
  MISSING_CREDENTIAL: 'The selected service needs its credential in Settings.',
  LOCAL_BUDGET_EXCEEDED: 'The selected included or free allowance is unavailable.',
  PAID_USE_FORBIDDEN: 'This profile has no confirmed local, free or included access.',
};

// Display saved state. Viewing an error owns no retry or provider action.
export function failureMessage(item) {
  if (item.audio_available || item.phase_states?.render === 'complete' || !item.last_failure) return '';
  const failure = item.last_failure;
  const reason = reasons[failure.code] || failure.message?.trim() || 'This preparation did not complete.';
  const guidance = ['MODEL_SETUP_REQUIRED','CAPABILITY_UNQUALIFIED','MISSING_CREDENTIAL','PAID_USE_FORBIDDEN','LOCAL_BUDGET_EXCEEDED'].includes(failure.code)
    ? 'Check Settings, then resume this exercise explicitly.'
    : failure.retryable === false ? 'Check the request and Settings before trying again.' : 'When the service is available, resume this exercise explicitly.';
  return `${reason} Saved text, mutations and completed audio pieces are retained. ${guidance}`;
}
