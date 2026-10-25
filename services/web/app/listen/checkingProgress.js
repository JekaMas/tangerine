import {clientFetch as fetch} from '../clientRequest.js';
// Observe the existing foreground operation. Reads never start or retry work.
export function watchChecking(id, onProgress) {
  let active = true, timer, request;
  async function poll() {
    request = new AbortController();
    try {
      const response = await fetch('/api/v1/attempts/' + id, {
        cache: 'no-store', signal: AbortSignal.any([request.signal, AbortSignal.timeout(5000)]),
      });
      if (response.ok) {
        const attempt = await response.json();
        if (active && attempt.submitted_at != null) {
          // A failed result read must not hide the already confirmed save.
          onProgress(attempt, null);
          const saved = await fetch(attempt.results_path, {
            cache: 'no-store', signal: AbortSignal.any([request.signal, AbortSignal.timeout(5000)]),
          });
          if (saved.ok) {
            const results = await saved.json();
            if (active) onProgress(attempt, results);
          }
        }
      }
    } catch { /* The write owns its outcome; a progress read cannot cancel it. */ }
    if (active) timer = setTimeout(poll, 1000);
  }
  timer = setTimeout(poll, 250);
  return () => { active = false; clearTimeout(timer); request?.abort(); };
}
