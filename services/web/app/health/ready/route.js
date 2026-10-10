import { createHash } from 'node:crypto';
export const dynamic = 'force-dynamic';
export async function GET() {
  try {
    const result = await fetch(`${process.env.API_INTERNAL_URL}/health/ready`, { headers: { Authorization: `Bearer ${process.env.API_INTERNAL_TOKEN}` }, cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(6000) });
    const headers = result.ok ? { 'X-Tangerine-Instance': createHash('sha256').update(process.env.API_INTERNAL_TOKEN).digest('hex') } : {};
    return Response.json({ status: result.ok ? 'ready' : 'unavailable' }, { status: result.ok ? 200 : 503, headers });
  } catch { return Response.json({ status: 'unavailable' }, { status: 503 }); }
}
