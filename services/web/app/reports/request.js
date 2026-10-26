import {clientFetch} from '../clientRequest.js';
import {userError} from '../requestError.js';

// Existing private API and transient-read recovery; no implicit write replay.
export async function reportRequest(path, options={}) {
  const response = await clientFetch('/api/v1/' + path, {cache:'no-store', ...options});
  if (!response.ok) throw userError(response.status===404
    ? 'This saved item is no longer available. Choose another saved item or create a new one.'
    : response.status===400||response.status===422
    ? 'Check the report or experiment fields. Your input is retained. Use the advanced definition for other workflows.'
    : path==='lab/defaults'?'Configured experiment choices are unavailable. Retry or open Settings. Your input is retained.'
      : 'Reports are temporarily unavailable. Your inputs and saved observations are retained. Refresh to continue.');
  return response.json();
}
