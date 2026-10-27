import {requestError,userError} from '../requestError.js';
import {failureMessage,fixedSpeechFailure} from './failureMessage.js';

// Own preparation transport messages. Only authored guidance reaches the page.
const messages = {
  PAID_USE_FORBIDDEN:'This profile has no confirmed free, local or included access. Choose an eligible profile in Settings. No paid fallback was used.',
  LOCAL_BUDGET_EXCEEDED:'Included allowance is unavailable. Check Settings or retry after reset.',
  MODEL_SETUP_REQUIRED:'Set up the selected local speech model, then Resume. For Australian or Indian voices, run scripts/tangerine model-setup local-english-accents-v1.',
  MISSING_CREDENTIAL:'Supply the selected credential in Settings, then Resume.',
  MISSING_CREDENTIALS:'Supply the selected credential in Settings, then Resume.',
  CONSTRAINT_CONFLICT:'Check the selected model, service access and request settings in Settings. Your choices and saved progress are retained. No provider was switched.',
  LEASE_ACTIVE:'This preparation is still running. Refresh after it finishes or its foreground deadline expires.',
  REVISION_STALE:'The saved state changed. Refresh before resuming.',
};
const incomplete='This step could not be completed. Your choices are retained. Refresh saved preparations before trying again.';

export async function preparationResponse(response) {
  let data;
  try { data=await response.json(); }
  catch(error) {
    requestError(error); // Redacted diagnostic; never call this a user JSON error.
    throw userError('The local service returned an unreadable response. Your choices are retained. Refresh saved preparations before trying again.');
  }
  if (!response.ok) throw userError(fixedSpeechFailure(data?.preparation) ? failureMessage(data.preparation) : messages[data?.code] || incomplete);
  return data;
}
