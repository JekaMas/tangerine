export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const ALLOWED = new Set(['GET v1/library', 'GET v1/health']);
function failure(status, error) { return Response.json({ error }, { status, headers: { 'Cache-Control': 'no-store' } }); }
async function proxy(request, context) {
  const { path } = await context.params;
  const target = path.join('/');
  if (request.method !== 'GET' && request.method !== 'HEAD' &&
      (request.headers.get('origin') !== process.env.APP_ORIGIN || request.headers.get('sec-fetch-site') === 'cross-site')) return failure(403, 'origin_denied');
  const host = request.headers.get('host');
  if (host !== 'localhost:3000' && host !== '127.0.0.1:3000') return failure(403, 'host_denied');
  if (!ALLOWED.has(`${request.method} ${target}`)) return failure(404, 'not_implemented');
  try {
    const response = await fetch(`${process.env.API_INTERNAL_URL}/api/${target}`, {
      headers: { Authorization: `Bearer ${process.env.API_INTERNAL_TOKEN}` }, redirect: 'error', cache: 'no-store',
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(270000)]),
    });
    return new Response(response.body, { status: response.status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
  } catch { return failure(503, 'service_unavailable'); }
}
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
