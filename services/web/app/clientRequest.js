// Own transient read recovery. Writes keep their existing action/idempotency owner.
const transient = new Set([408, 425, 429, 500, 502, 503, 504]);
const pause = (ms, signal) => new Promise((resolve, reject) => {
  if (signal?.aborted) { reject(signal.reason); return; }
  const stop = () => { clearTimeout(timer); reject(signal.reason); };
  const timer = setTimeout(() => { signal?.removeEventListener('abort', stop); resolve(); }, ms);
  signal?.addEventListener('abort', stop, {once:true});
});

export function createClientFetch({send=(...args)=>globalThis.fetch(...args), wait=pause, log=(value)=>console.warn('Tangerine request',value)}={}) {
  return async function clientFetch(input, options={}) {
    const method=(options.method||'GET').toUpperCase();
    const attempts=['GET','HEAD'].includes(method)?3:1;
    const path=String(input).split('?')[0];
    for (let attempt=0;attempt<attempts;attempt++) {
      options.signal?.throwIfAborted();
      try {
        const response=await send(input,options);
        if (response.ok) return response;
        log({method,path,status:response.status,attempt:attempt+1});
        const header=response.headers.get('Retry-After');
        const seconds=Number(header);
        const retryAfter=Number.isFinite(seconds)?seconds:Math.max(0,(Date.parse(header)-Date.now())/1000);
        if (!transient.has(response.status)||attempt===attempts-1||retryAfter>1) return response;
      } catch (error) {
        if (options.signal?.aborted||error?.name==='AbortError'||error?.name==='TimeoutError') throw error;
        log({method,path,outcome:'connection_unavailable',attempt:attempt+1});
        if (!(error instanceof TypeError)||attempt===attempts-1) throw error;
      }
      await wait(attempt===0?160:480, options.signal);
    }
  };
}
export const clientFetch=createClientFetch();
