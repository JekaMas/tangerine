export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ALLOWED = new Set(['GET auth/session', 'GET exercises', 'POST auth/login', 'POST auth/logout']);
const LIMIT = 16384;
function failure(status, error) { return Response.json({ error }, { status, headers: { 'Cache-Control': 'no-store' } }); }

async function proxy(request, context) {
  const { path } = await context.params;
  const target = path.join('/');
  if (!ALLOWED.has(`${request.method} ${target}`)) return failure(404, 'not_implemented');
  const origin = process.env.APP_ORIGIN;
  if (request.method === 'POST' && (request.headers.get('origin') !== origin || request.headers.get('sec-fetch-site') === 'cross-site')) return failure(403, 'origin_denied');
  const headers = new Headers();
  const cookie = request.headers.get('cookie')?.split(';').map(x => x.trim()).find(x => x.startsWith('tangerine_session='));
  if (cookie) headers.set('cookie', cookie);
  if (request.method === 'POST') headers.set('origin', origin || '');
  let body;
  if (request.method === 'POST' && target === 'auth/login') {
    if (request.headers.get('content-type') !== 'application/json') return failure(400, 'invalid_request');
    headers.set('content-type', 'application/json');
    const reader = request.body?.getReader();
    if (!reader) return failure(400, 'invalid_request');
    const chunks = []; let size = 0;
    try {
      while (true) {
        const { value, done } = await reader.read(); if (done) break;
        size += value.byteLength;
        if (size > LIMIT) { await reader.cancel(); return failure(413, 'request_too_large'); }
        chunks.push(value);
      }
    } finally { reader.releaseLock(); }
    body = Buffer.concat(chunks);
  }
  try {
    const response = await fetch(`${process.env.API_INTERNAL_URL}/api/${target}`, {
      method: request.method, headers, body, redirect: 'error', cache: 'no-store',
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(270000)]),
    });
    const outgoing = new Headers({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    const setCookie = response.headers.get('set-cookie');
    if (setCookie) outgoing.set('set-cookie', setCookie);
    return new Response(response.body, { status: response.status, headers: outgoing });
  } catch { return failure(503, 'service_unavailable'); }
}
export const GET = proxy;
export const POST = proxy;
