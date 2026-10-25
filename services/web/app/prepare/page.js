'use client';
import RefreshButton from '../RefreshButton.js';
import Controls from './Controls';
import usePreparation from './usePreparation';
import RequestPreview from './RequestPreview';
import Icon from '../Icon';
import {mistakeFamilies} from './request';
import SavedFailure from './SavedFailure';
import {recordDate, recordTitle} from '../savedRecord';

function RequestSummary({request,categories}) {
  if (!request) return null;
  const selected=request.category_ids?.map(id=>categories.find(x=>x.id===id)?.label||id).join(', ') || request.category_families?.map(id=>mistakeFamilies.find(x=>x[0]===id)?.[1]||id).join(', ') || 'Automatic categories';
  return <><p>{request.speaker_count} {request.speaker_count===1?'speaker':'speakers'} · approximately {request.text_length_words} words · {request.english_level || 'Any level'} · {request.mutation_count == null ? 'Automatic mistakes' : request.mutation_count+(request.mutation_count===1?' mistake':' mistakes')} · {selected}</p>{request.severity_levels?.length>0&&<p>Severity: {request.severity_levels.map(x=>x.replaceAll('_',' ')).join(', ')}</p>}</>;
}

export default function Prepare() {
  const {form, update, items, cursor, busy, error, notice, generate, refresh, stop, categories, voices, categoryLoading, categoryError, retryCategories} = usePreparation();
  return <main id="main-content">

    <section className="intro"><h1>Prepare an exercise</h1><p>Choose a topic and generate a conversation to listen to. Voices, mistake types and difficulty are yours to customize.</p><a href="#saved-preparations">Continue a saved exercise</a></section>
    <section className="card preparation-card"><form onSubmit={e => {e.preventDefault(); generate();}}>
      <Controls form={form} update={update} busy={busy} categories={categories} voices={voices} categoryLoading={categoryLoading} categoryError={categoryError} retryCategories={retryCategories}>
      <RequestPreview form={form} categories={categories} voices={voices}/>
      <div className="form-submit"><button disabled={busy}>{busy ? 'Generating…' : 'Generate exercise'}<Icon name="arrow" size={18}/></button>
      {busy && <button type="button" className="secondary" onClick={stop}>Stop generation</button>}
      </div>
      </Controls>
    </form>{error && <p className="error" role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}</section>
    <section id="saved-preparations" className="card saved-preparations"><div className="row"><div><h2>Saved preparations</h2><p className="field-help">Your progress is saved. Resume any unfinished exercise.</p></div><RefreshButton onClick={() => refresh()}>Refresh</RefreshButton></div>
      {!items.length && <p>No saved preparations yet.</p>}
      {items.map(item => <article key={item.id}><h3>{recordTitle(item)}</h3><p>{recordDate(item.created_at)}</p>
        <RequestSummary request={item.exercise_request} categories={categories}/>
        <ol className="phase-list" aria-label="Preparation progress">{[['canonical_text','Clean text'],['mutation','Mistakes'],['render','Audio']].map(([key,label])=><li key={key} data-state={item.phase_states[key]}><span className="phase-dot"/>{label}<small>{item.phase_states[key].replaceAll('_',' ')}</small></li>)}</ol>
        {item.canonical_word_count != null && <p>Clean text: {item.canonical_word_count} words{item.surface_word_count != null ? ` · With mutations: ${item.surface_word_count} words` : ''}</p>}
        {item.render_progress_summary?.total_pieces > 0 && <p>{item.render_progress_summary.complete_pieces}/{item.render_progress_summary.total_pieces} audio pieces saved</p>}
        <SavedFailure item={item}/>
        {item.audio_available ? <a href="/">Open the Library to listen and answer</a> : <button disabled={busy} onClick={() => generate(item.id)}>Resume exercise</button>}<details><summary>Record details</summary><p>Preparation: {item.id}</p><p>Original date: {item.created_at||'unavailable'}</p></details>
      </article>)}
      {cursor && <button disabled={busy} onClick={() => refresh(true)}>Load more</button>}
    </section>
  </main>;
}
