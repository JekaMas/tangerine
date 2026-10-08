export const dynamic = 'force-dynamic';
export async function GET() {
  try {
    const result = await fetch(`${process.env.API_INTERNAL_URL}/health/ready`, { cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(6000) });
    return Response.json({ status: result.ok ? 'ready' : 'unavailable' }, { status: result.ok ? 200 : 503 });
  } catch { return Response.json({ status: 'unavailable' }, { status: 503 }); }
}
