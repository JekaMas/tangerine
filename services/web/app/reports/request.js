import {clientFetch} from '../clientRequest.js';
import {userError} from '../requestError.js';

// Existing private API and transient-read recovery; no implicit write replay.
export async function reportRequest(path, options={}) {
  const response = await clientFetch('/api/v1/' + path, {cache:'no-store', ...options});
  if (!response.ok) throw userError(response.status===404
    ? 'This saved item is no longer available. Choose another saved item or create a new one.'
    : response.status===400||response.status===422
    ? 'Check your selections and try again. Your input and saved reports are retained.'
    : path==='reports/empirical'&&(options.method||'GET').toUpperCase()==='POST'
    ? 'We couldn’t confirm that this report was saved. Your inputs and earlier reports are retained. Refresh saved reports to check whether it was saved before trying again.'
    : path==='lab/defaults'?'Configured experiment choices are unavailable. Retry or open Settings. Your input is retained.'
      : 'Reports are temporarily unavailable. Your inputs and saved observations are retained. Refresh to continue.');
  return response.json();
}
