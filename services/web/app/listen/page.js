'use client';
import useListening from './useListening';
import Results from './Results';
import CheckingStatus from './CheckingStatus';

export default function Listen() {
  const {attempt, answer, language, recovered, error, notice, busy, checking, audioRevision,
    canRefresh, refresh, write, editAnswer, editLanguage, playback, audioError, results, retryChecking} = useListening();
  const submitted = attempt?.submitted_at != null;
  return <main>
    <header><a className="brand" href="/">Tangerine</a><a href="/attempts">Saved attempts</a><a href="/settings">Settings</a></header>
    <section className="intro"><h1>Listen and respond</h1><p>Describe the mistakes you hear and offer corrections. Reasons are optional. You can answer in English or Russian.</p></section>
    <section className="card">
      {error && <p role="alert" className="error">{error}</p>}
      {notice && <p role="status">{notice}</p>}
      <CheckingStatus checking={checking}/>
      <button className="secondary" onClick={refresh} disabled={busy || !canRefresh}>Refresh saved state</button>
      {attempt && <>
        <h2>{attempt.case.title}</h2><p>{attempt.case.public_context}</p>
        <p>Identify mistakes{attempt.task_components.classification ? ', name their categories' : ''}{attempt.task_components.correction ? ' and offer corrections' : ''}. Explanations are optional.</p>
        <audio key={audioRevision} controls preload="metadata" aria-label="Exercise audio"
          src={attempt.audio_path + '?playback_revision=' + audioRevision}
          onPlay={e => playback('play', e)} onPause={e => playback('pause', e)}
          onSeeked={e => playback('seek', e)} onEnded={e => playback('ended', e)} onError={audioError}/>
        <label>Response language<select aria-label="Response language" disabled={busy || submitted} value={language} onChange={e => editLanguage(e.target.value)}><option value="en">English</option><option value="ru">Russian</option></select></label>
        <label>Your answer<textarea aria-label="Your answer" rows={10} disabled={busy || submitted} value={answer} onChange={e => editAnswer(e.target.value)}/></label>
        <p>{Array.from(answer).length.toLocaleString('en-US')} / 20,000 characters · {attempt.state}</p>
        {submitted ? <p>Answer submitted and saved. <a href="/attempts">Open saved attempts</a></p>
          : <div className="actions"><button onClick={() => write(false)} disabled={busy}>Save draft</button><button onClick={() => write(true)} disabled={busy}>Submit answer</button></div>}
        {submitted&&<section aria-label="Answer findings">
          <Results results={results} busy={busy} checking={checking} retry={retryChecking}/>
          <h3>Answer findings</h3>
          {results?.interpretation?.status==='complete'&&<p>Answer interpretation ready.</p>}
          {results?.status==='review_required'&&<p>Some findings remain uncertain. Supported components are retained.</p>}
          {results?.status==='evaluation_failed'&&<p>Checking is unavailable. Your submitted answer is saved.</p>}
          {!results?.score&&(!results?.interpretation||results?.status==='evaluation_failed'||results?.status==='evaluating')&&<button disabled={busy} onClick={retryChecking}>{results?.status==='evaluating'?'Resume checking':'Check saved answer'}</button>}
          {results?.interpretation?.claims?.map(claim=>{
            const decision=results.interpretation.decisions.find(d=>d.claim_id===claim.id);
            return <article key={claim.id}><h4>{claim.claim_span.exact_text}</h4>
              {decision&&<><p>{decision.decision.replaceAll('_',' ')}{decision.category_id?' · '+decision.category_id:''}</p>
                <p>Correction: {decision.correction.supplied?decision.correction.status.replaceAll('_',' '):'not provided'}</p>
                <p>Explanation: {decision.explanation.supplied?decision.explanation.status.replaceAll('_',' '):'not provided (optional)'}</p>
                {decision.note&&<p>{decision.note}</p>}
                {[...decision.correction.additional_assertions,...decision.explanation.additional_assertions].map((a,i)=><p key={i}>{a.exact_text} · {a.judgment}: {a.reason}</p>)}
              </>}
            </article>
          })}
          {['failed','disagreement'].includes(results?.interpretation?.audit_status)&&<p>Optional mapping audit: {results.interpretation.audit_status}. Supported findings are retained.</p>}
          {results?.issues?.map(issue=><p key={issue.id}>{issue.explanation}</p>)}
        </section>}
        {recovered && <section aria-label="Unsubmitted response recovery">
          <h3>Unsubmitted local text</h3>
          <p>This attempt was submitted in another window. The submitted answer is shown above. Your different local text ({recovered.language}) is retained below for copying; it was not submitted.</p>
          <textarea aria-label="Unsubmitted local text" rows={6} readOnly value={recovered.answer}/>
        </section>}
      </>}
    </section>
    <footer>Stored audio · Exact saved answers · Optional explanations</footer>
  </main>;
}
