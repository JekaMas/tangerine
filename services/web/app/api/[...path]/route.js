export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const ALLOWED = new Set(['GET v1/library', 'GET v1/reviews', 'POST v1/reviews', 'GET v1/attempts', 'POST v1/attempts', 'GET v1/health', 'GET v1/provider-connections', 'POST v1/provider-connections:action', 'GET v1/configuration', 'GET v1/preparations', 'PUT v1/configuration']);
function failure(status, error) { return Response.json({ error }, { status, headers: { 'Cache-Control': 'no-store' } }); }
async function proxy(request, context) {
  const { path } = await context.params;
  const target = path.join('/');
  const host = request.headers.get('host');
  if (host !== 'localhost:3000' && host !== '127.0.0.1:3000') return failure(403, 'host_denied');
  if (request.method !== 'GET' && request.method !== 'HEAD' &&
      (request.headers.get('origin') !== `http://${host}` || request.headers.get('sec-fetch-site') === 'cross-site')) return failure(403, 'origin_denied');
  const modelBytes = request.method === 'GET' && /^v1\/prepare\/assets\/[a-f0-9-]{36}\/bytes$/.test(target);
  const audio = request.method === 'GET' && /^v1\/preparations\/[a-f0-9-]{36}\/audio$/.test(target);
  const render = request.method === 'POST' && /^v1\/preparations\/[a-f0-9-]{36}:render$/.test(target);
  const attempt = /^(v1\/attempts\/[a-f0-9-]{36})(?::(?:submit|retry|retry-feedback)|\/(?:answer|audio|playback|results))?$/.test(target) && ((request.method === 'GET' && !target.endsWith('/answer') && !target.endsWith('/playback') && !target.endsWith(':submit') && !target.endsWith(':retry') && !target.endsWith(':retry-feedback')) || (request.method === 'PUT' && target.endsWith('/answer')) || (request.method === 'POST' && (target.endsWith(':submit') || target.endsWith(':retry') || target.endsWith(':retry-feedback') || target.endsWith('/playback'))));
  const review = (request.method==='GET' && /^v1\/reviews\/[a-f0-9-]{36}$/.test(target)) || (request.method==='POST' && /^v1\/reviews\/[a-f0-9-]{36}:(?:run|reconsider)$/.test(target));
  if (!ALLOWED.has(`${request.method} ${target}`) && !modelBytes && !audio && !render && !attempt && !review) return failure(404, 'not_implemented');
  const query = new URLSearchParams();
  if(target==='v1/reviews'){const requested=new URL(request.url).searchParams;for(const name of ['case_version_id','attempt_id','cursor'])if(requested.has(name))query.set(name,requested.get(name));}
  if(attempt&&target.endsWith('/results')){const id=new URL(request.url).searchParams.get('result_id');if(id!==null)query.set('result_id',id);}

  if (target === 'v1/attempts') { const requested = new URL(request.url).searchParams;for(const name of ['limit','cursor','case_version_id'])if(requested.has(name))query.set(name,requested.get(name)); }
  if (target === 'v1/preparations') {
    query.set('view', 'public');
    const requested = new URL(request.url).searchParams;
    for (const name of ['limit', 'cursor']) if (requested.has(name)) query.set(name, requested.get(name));
  }
  if(attempt && target.endsWith('/audio')) { const refresh=new URL(request.url).searchParams.get('playback_revision');if(refresh!==null)query.set('playback_revision',refresh); }
  try {
    const response = await fetch(`${process.env.API_INTERNAL_URL}/api/${target}${query.size ? '?' + query.toString() : ''}`, {
      method: request.method,
      headers: { Authorization: `Bearer ${process.env.API_INTERNAL_TOKEN}`, Origin: request.headers.get('origin') || '', 'Content-Type': request.headers.get('content-type') || '', Range: request.headers.get('range') || '', 'If-Match': request.headers.get('if-match') || '', 'Idempotency-Key': request.headers.get('idempotency-key') || '' },
      body: request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.text(),
      redirect: 'error', cache: 'no-store',
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(270000)]),
    });
    return new Response(response.body, { status: response.status, headers: { 'Content-Type': response.headers.get('content-type') || 'application/json', 'Cache-Control': 'no-store', 'Content-Range': response.headers.get('content-range') || '', 'Accept-Ranges': response.headers.get('accept-ranges') || '', 'ETag': response.headers.get('etag') || '', 'X-Tangerine-Audio-SHA256': response.headers.get('x-tangerine-audio-sha256') || '', 'X-Tangerine-Answer-SHA256': response.headers.get('x-tangerine-answer-sha256') || '', 'X-Tangerine-Configuration-SHA256': response.headers.get('x-tangerine-configuration-sha256') || '', 'X-Tangerine-Next-Cursor': response.headers.get('x-tangerine-next-cursor') || '', 'X-Tangerine-Active-Connection': response.headers.get('x-tangerine-active-connection') || '' } });
  } catch { return failure(503, 'service_unavailable'); }
}
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
