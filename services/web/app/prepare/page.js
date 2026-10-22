'use client';
import Controls from './Controls';
import usePreparation from './usePreparation';

function RequestSummary({request}) {
  if (!request) return null;
  return <p>{request.topic} · {request.speaker_count} speakers · approximately {request.text_length_words} words · {request.english_level || 'Any level'} · {request.mutation_count == null ? 'Automatic mistakes' : request.mutation_count+' mistakes'} · {request.category_families?.join(', ') || 'Automatic categories'}</p>;
}

export default function Prepare() {
  const {form, update, items, cursor, busy, error, notice, generate, refresh, stop} = usePreparation();
  return <main>
    <header><a className="brand" href="/">Tangerine</a><a href="/settings">Settings</a><a href="/recovery">Recovery</a></header>
    <section className="intro"><h1>Prepare an exercise</h1><p>Choose a topic. The LLM writes clean text and mutations, then your selected speech backend creates saved audio.</p></section>
    <section className="card"><form onSubmit={e => {e.preventDefault(); generate();}}>
      <Controls form={form} update={update} busy={busy}/>
      <button disabled={busy}>{busy ? 'Generating…' : 'Generate exercise'}</button>
      {busy && <button type="button" className="secondary" onClick={stop}>Stop generation</button>}
    </form>{error && <p className="error" role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}</section>
    <section className="card"><div className="row"><h2>Saved preparations</h2><button className="secondary" disabled={busy} onClick={() => refresh()}>Refresh</button></div>
      {!items.length && <p>No saved preparations yet.</p>}
      {items.map(item => <article key={item.id}><h3>Exercise {item.id.slice(0,8)}</h3>
        <RequestSummary request={item.exercise_request}/>
        <p>Clean text: {item.phase_states.canonical_text} · Mutations: {item.phase_states.mutation} · Audio: {item.phase_states.render}</p>
        {item.canonical_word_count != null && <p>Clean text: {item.canonical_word_count} words{item.surface_word_count != null ? ` · With mutations: ${item.surface_word_count} words` : ''}</p>}
        {item.render_progress_summary?.total_pieces > 0 && <p>{item.render_progress_summary.complete_pieces}/{item.render_progress_summary.total_pieces} audio pieces saved</p>}
        {item.audio_available ? <a href="/">Open the Library to listen and answer</a> : <button disabled={busy} onClick={() => generate(item.id)}>Resume exercise</button>}
      </article>)}
      {cursor && <button disabled={busy} onClick={() => refresh(true)}>Load more</button>}
    </section>
  </main>;
}
