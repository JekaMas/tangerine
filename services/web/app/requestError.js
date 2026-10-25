// Only locally authored recovery messages are displayed. Technical payloads stay
// with the request/server diagnostics; a backend string is never a UI message.
class UserMessage extends Error {}
export const userError = message => new UserMessage(message);
export const defaultRecovery = 'This step could not be completed. Your input is retained. Refresh saved state before trying again.';
export function requestError(error, fallback=defaultRecovery) {
  if (error instanceof UserMessage) return error.message;
  if (error) console.warn('Tangerine display recovery', {kind:error.name||'UnknownError'});
  return fallback;
}

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
export const failureReason = code => reasons[code] || 'This preparation did not complete.';

export function parseUserJSON(value, label) {
  try { return JSON.parse(value); }
  catch { throw userError(`${label} is not valid JSON. Your input is retained.`); }
}
