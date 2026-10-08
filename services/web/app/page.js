'use client';
import { useEffect, useState } from 'react';

async function request(path, options = {}) {
  const response = await fetch(path, { ...options, cache: 'no-store', signal: AbortSignal.timeout(270000) });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(response.status === 401 ? 'Please sign in with your local account.' :
      response.status === 403 ? 'The request origin was rejected.' : 'The service is unavailable. Your local data has not been replaced.');
    error.status = response.status;
    throw error;
  }
  return data;
}

export default function Page() {
  const [account, setAccount] = useState(null);
  const [exercises, setExercises] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);

  async function refresh() {
    const session = await request('/api/auth/session');
    const bank = await request('/api/exercises');
    setAccount(session);
    setExercises(bank.exercises);
  }
  useEffect(() => {
    refresh().catch(e => { if (e.status !== 401) setError(e.message); }).finally(() => setBusy(false));
  }, []);
  async function signIn(event) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      await request('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
      setPassword(''); await refresh();
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function signOut() {
    setBusy(true); setError('');
    try { await request('/api/auth/logout', { method: 'POST' }); setAccount(null); setExercises(null); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a className="brand" href="/" aria-label="Tangerine home"><span className="mark">t</span>Tangerine</a><span className="local">Local workspace</span></header>
    <section className="intro"><p className="eyebrow">Teacher Error Trainer</p><h1>Listen closely.<br/>Notice what matters.</h1><p>Practice identifying learner errors, checking corrections and explaining your reasoning.</p></section>
    {error && <p role="alert" className="error">{error}</p>}
    {!account ? <section className="card"><h2>Sign in to your workspace</h2><p>Use the account configured for this local installation.</p><form onSubmit={signIn}>
      <label>Email<input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} /></label>
      <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /></label>
      <button disabled={busy}>{busy ? 'Connecting…' : 'Sign in'}</button>
    </form></section> : <section className="card">
      <div className="row"><h2>Exercise library</h2><button className="secondary" disabled={busy} onClick={signOut}>Sign out</button></div>
      <p className="account">Signed in as {account.email}</p>
      {exercises?.length === 0 ? <div className="empty"><span aria-hidden="true">◎</span><h3>No published exercises yet</h3><p>Exercises will appear here after the required independent reviews and publication checks.</p></div> :
        <ul>{exercises?.map(item => <li key={item.id}>{item.title}</li>)}</ul>}
    </section>}
    <footer>Prepared audio · Written observations · Evidence-based feedback</footer>
  </main>;
}
