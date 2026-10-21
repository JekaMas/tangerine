'use client';
import { useEffect, useState } from 'react';
export default function Page() {
  const [exercises, setExercises] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);
  async function refresh() {
    setBusy(true); setError('');
    try {
      const response = await fetch('/api/v1/library', { cache: 'no-store', signal: AbortSignal.timeout(270000) });
      if (!response.ok) throw new Error('The Library is unavailable. Your local data has been retained. Retry when the services are ready.');
      setExercises(await response.json());
    } catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }
  useEffect(() => { refresh(); }, []);
  return <main>
    <header><a className="brand" href="/" aria-label="Tangerine home"><span className="mark">t</span>Tangerine</a><a href="/audio">Saved audio</a><a href="/attempts">Saved attempts</a><a href="/settings">Settings</a><span className="local">Local workspace</span></header>
    <section className="intro"><p className="eyebrow">Teacher Error Trainer</p><h1>Listen closely.<br/>Notice what matters.</h1><p>Practice identifying learner errors, checking corrections and explaining your reasoning.</p></section>
    <section className="card"><div className="row"><h2>Exercise library</h2><button className="secondary" disabled={busy} onClick={refresh}>{busy ? 'Loading…' : 'Refresh'}</button></div>
      {error ? <p role="alert" className="error">{error}</p> : busy ? <p role="status">Loading your Library…</p> : exercises?.length === 0 ?
        <div className="empty"><span aria-hidden="true">◎</span><h3>No exercises yet</h3><p>Your workspace is ready. Saved exercises will appear here.</p></div> :
        <ul>{exercises?.map(item => <li key={item.id}><h3>{item.title}</h3><p>{item.public_context}</p><p>{item.format} · {item.difficulty} · {item.availability}</p>{item.availability==='published'&&item.case_sha256&&<a href={'/listen?case='+item.id+'&sha='+item.case_sha256}>Listen and answer</a>}{item.case_sha256&&<> · <a href={'/reviews?case='+item.id}>Optional LLM review</a></>}</li>)}</ul>}
    </section>
    <footer>Generated audio · Written observations · Targeted feedback</footer>
  </main>;
}
