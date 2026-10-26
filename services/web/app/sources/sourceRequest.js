import {clientFetch} from '../clientRequest.js';
import {userError} from '../requestError.js';

const unavailable = 'The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.';
const messages = new Map(Object.entries({
  source_input_invalid: 'Some source details need updating. Check the release, files and selected source. Your input is retained.',
  source_action_conflict: 'Saved source progress has changed. Refresh the saved import, then continue from its current state.',
  source_not_found: 'This saved source is unavailable. Refresh sources and choose an available saved release. Your uploaded files are retained.',
  intake_limit: 'This upload exceeds the local import limit. Upload the extracted files in smaller groups. Retained files remain available.',
  host_denied: 'The export address does not match the allowed source hosts. Use the documented source host and save the connector again.',
  interface_missing: 'Add the source owner’s documented export interface before fetching this source. Local file upload remains available.',
  remote_format: 'The downloaded export does not match its documented format. Check the source contract or upload the complete local export.',
}));
const archiveCodes = new Set(['unsafe_path','unsafe_member','duplicate_path','archive_format','archive_member','archive_duplicate','archive_link','archive_type','xlsx_member']);

// Transport recovery belongs to clientFetch. This owner only presents authored
// source guidance; it never displays a backend payload or rechecks saved data.
export function createSourceRequest({send=clientFetch, log=value=>console.warn('Tangerine source request',value)}={}) {
  return async function request(path,options={}) {
    let response;
    let body;
    try {
      response=await send('/api/v1/'+path,{cache:'no-store',signal:AbortSignal.timeout(270000),...options});
      body=await response.json();
    } catch (error) {
      log({path:path.split('?')[0],outcome:'unavailable',kind:error?.name});
      const failure=userError(unavailable);
      failure.importId=response?.headers.get('X-Tangerine-Import-ID');
      throw failure;
    }
    if (!response.ok) {
      const code=body?.error;
      const message=messages.get(code);
      log({path:path.split('?')[0],status:response.status,code:(message||archiveCodes.has(code))?code:'unavailable'});
      const text=archiveCodes.has(code)
        ? 'This archive cannot be imported as supplied. Use a regular ZIP or TAR with unique relative file paths, or upload the extracted files. Retained files remain available.'
        : message || unavailable;
      const error=userError(text);
      error.importId=response.headers.get('X-Tangerine-Import-ID');
      throw error;
    }
    return {body,response};
  };
}

export const sourceRequest=createSourceRequest();
