export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export async function GET(request) {
  const host = request.headers.get('host');
  if (host !== '127.0.0.1:3000') return new Response('Invalid callback host.', { status: 403 });
  let success = false;
  try {
    const url = new URL(request.url);
    const response = await fetch(`${process.env.API_INTERNAL_URL}/auth/callback${url.search}`, {
      headers: { Authorization: `Bearer ${process.env.API_INTERNAL_TOKEN}` }, redirect: 'error', cache: 'no-store',
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(270000)]),
    });
    success = response.ok;
  } catch { /* Authorization query and tokens must never enter diagnostic logs. */ }
  const text = success ? 'Connection saved. Return to Settings to confirm included usage and choose a model.' : 'Connection could not be completed. Return to Settings and reconnect.';
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="referrer" content="no-referrer"><title>Tangerine connection</title></head><body><main><h1>Tangerine</h1><p>${text}</p><a href="http://localhost:3000/settings">Return to Settings</a></main><script>history.replaceState(null,'','/auth/callback')</script></body></html>`, {
    status: success ? 200 : 400, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer', 'X-Content-Type-Options': 'nosniff' },
  });
}
