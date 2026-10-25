'use client';
import {requestError} from './requestError';
import { useEffect, useState } from 'react';
import Icon from './Icon';
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
    } catch (failure) { setError(requestError(failure)); }
    finally { setBusy(false); }
  }
  useEffect(() => { refresh(); }, []);
  return <main id="main-content">

    <section className="intro library-intro"><div><h1>A better ear for English.</h1><p>Listen closely, spot the mistakes, and put your understanding into words. Every conversation is a chance to notice something new.</p><a className="button" href="/prepare"><Icon name="create"/>Prepare an exercise</a></div><div className="listening-motif" aria-hidden="true"><svg width="220" height="180" viewBox="0 0 220 180"><rect x="28" y="18" width="166" height="128" rx="26" fill="#E4EEF5"/><path d="M65 82v-9a45 45 0 0 1 90 0v9" fill="none" stroke="#233E5B" strokeWidth="9" strokeLinecap="round"/><rect x="56" y="74" width="22" height="42" rx="9" fill="#233E5B"/><rect x="143" y="74" width="22" height="42" rx="9" fill="#233E5B"/><path d="M99 79v24m12-38v51m12-36v22" stroke="#D65718" strokeWidth="5" strokeLinecap="round"/><circle cx="176" cy="142" r="24" fill="#F27832"/><path d="m166 142 7 7 13-15" fill="none" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/></svg></div></section>
    <section className="card"><div className="row"><h2>Exercise library</h2><button className="secondary" disabled={busy} onClick={refresh}>{busy ? 'Loading…' : 'Refresh'}</button></div>
      {error ? <p role="alert" className="error">{error}</p> : busy ? <p role="status">Loading your Library…</p> : exercises?.length === 0 ?
        <div className="empty"><span aria-hidden="true">◎</span><h3>No exercises yet</h3><p>Your workspace is ready. Generate your first exercise from a topic.</p><a href="/prepare">Prepare an exercise</a></div> :
        <ul className="exercise-list">{exercises?.map(item => <li key={item.id}><div className="exercise-icon"><Icon name="audio" size={25}/></div><div className="exercise-copy"><h3>{item.title}</h3><p>{item.public_context}</p><div className="exercise-meta"><span>{item.format}</span><span>{item.difficulty==='unrated'?'Difficulty not yet rated':item.difficulty}</span><span>{item.availability==='published'?'Ready to listen':item.availability}</span></div><div className="actions">{item.availability==='published'&&item.case_sha256&&<a className="button compact" href={'/listen?case='+item.id+'&sha='+item.case_sha256}>Listen and answer<Icon name="arrow" size={17}/></a>}{item.case_sha256&&<a className="quiet-link" href={'/reviews?case='+item.id}>Optional LLM review</a>}</div></div></li>)}</ul>}
    </section>
    <footer>Generated audio · Written observations · Targeted feedback</footer>
  </main>;
}
