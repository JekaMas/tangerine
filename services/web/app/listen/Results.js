'use client';
import {passageTime} from './passageReplay';

// Presentation consumes authoritative displays; it never calculates a grade.
function Metric({name, value}) {
  return <p>{name}: {value?.status === 'available' ? value.display + '%' :
    value?.status === 'review_required' ? 'uncertain' : 'not applicable'}{value?.reason ? ' · ' + value.reason.replaceAll('_', ' ') : ''}</p>;
}
export default function Results({results, busy, checking, retry, replay}) {
  const score = results?.score;
  if (!score) return null;
  return <section aria-label="Scores and practice">
    <h3>Results</h3>
    <div className="score-summary"><p className="primary-score" aria-label="Primary score"><span className="score-label">Primary score: </span><span className={score.composite.display != null ? 'score-value' : undefined}>{score.composite.display != null ? score.composite.display + ' / 100' :
      score.status === 'review_required' ? 'uncertain' : 'not applicable'}</span></p>
    <Metric name="Optional explanation" value={score.optional_explanation}/>
    <p>Explanations are optional and scored separately. Missing explanations do not reduce your primary score.</p>
    {score.counts && <p>Found {score.counts.tp} of {score.counts.true_errors} mistakes · {score.counts.fn} missed · {score.counts.fp} false positives</p>}
    </div>
    <div className="result-next"><a className="button compact" href="/prepare">Practise another conversation</a><a href={'/reviews?attempt='+results.attempt_id}>Optional reconsideration and history</a></div>
    <h4>Comments and recommendations</h4>
    {results.feedback?.items.map((item, i) => <article key={i}>
      <p><strong>{item.kind === 'recommendation' ? 'New practice recommendation' : item.kind.replaceAll('_', ' ')}</strong>{item.status === 'needs_review' ? ' · uncertain' : ''}</p><p className="feedback-prose">{item.text}</p>
    </article>)}
    {results.feedback_status !== 'complete' && (checking ? <p>Comments and practice recommendations are being prepared. Your score and answer are saved.</p> : <><p>Comments and practice recommendations are unavailable. Your score and answer are saved.</p><button disabled={busy} onClick={retry}>Retry comments and recommendations</button></>)}
    <h4>Recording findings</h4>
    {score.items?.map((item, i) => <article key={i}><p>{item.kind.replaceAll('_', ' ')} · {item.category_id || 'unattributed assertion'}</p>
      {item.reference && <><p>Recorded target: {item.reference.target_texts.join(' · ')}</p>
        {item.reference.repairs.length > 0 && <p>Permitted repairs: {item.reference.repairs.join(' · ')}</p>}
        <p className="feedback-prose">{item.reference.rationale}</p>
        {item.reference.recurrence&&<div className="recurrence-result"><p><strong>Recurring pattern · Speaker {item.reference.recurrence.speaker_number}</strong></p><p>{item.reference.recurrence.rule}</p><p>Target {item.reference.recurrence.target_percent}% · Applied at {item.reference.recurrence.mutation_count} of {item.reference.recurrence.opportunity_count} relevant opportunities ({item.reference.recurrence.realized_percent_display}%). This pattern is scored once.</p>{item.reference.recurrence.correct_examples.length>0&&<p>Correct uses retained: {item.reference.recurrence.correct_examples.join(' · ')}</p>}</div>}
        {item.reference.audio_intervals.length===0&&<p>Passage timing unavailable. Use the full recording above.</p>}
        {item.reference.audio_intervals.map((interval, j) => <div className="passage" key={j}><span>{passageTime(interval.start_ms)}–{passageTime(interval.end_ms)}</span>{replay&&<button type="button" className="secondary" aria-label={`Replay passage ${i+1}.${j+1}`} onClick={()=>replay(interval)}>Replay passage</button>}</div>)}</>}
    </article>)}
    <details><summary>Detailed metrics and domains</summary>
      {Object.entries(score.metrics).map(([name, value]) => <Metric key={name} name={name} value={value}/>)}
      {score.domain_results.map(domain => <article key={domain.domain}><h4>{domain.domain}</h4>
        <Metric name="Detection precision" value={domain.precision}/><Metric name="Detection recall" value={domain.recall}/><Metric name="Detection F1" value={domain.f1}/></article>)}
      {Object.entries(results.auxiliary.measurements).map(([name, value]) => <p key={name}>{name}: {value.status === 'observed' ? value.display + (value.unit === 'ratio' ? '' : ' ' + value.unit.replaceAll('_', ' ')) : value.status.replaceAll('_', ' ')}</p>)}
    </details>
  </section>;
}
