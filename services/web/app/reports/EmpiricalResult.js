'use client';
import {useEffect,useRef,useState} from 'react';
import {measurement,populationNotice,populationFields,difficultyReason,exclusionLabel,coverageSummary} from './empiricalPresentation';

function Measurement({value}) {
  const shown=measurement(value);
  return <><span>{shown.value}</span>{shown.counts&&<small className="measurement-counts">{shown.counts}</small>}</>;
}
function Exclusions({values}) {
  const entries=Object.entries(values);
  return entries.length?<ul>{entries.map(([reason,count])=><li key={reason}>{exclusionLabel(reason)}: {count}</li>)}</ul>:<p>No exclusions recorded.</p>;
}

// Presentation only: no recomputation, asset checks or model calls on read.
export default function EmpiricalResult({value,onDownload}) {
  const [showAll,setShowAll]=useState(false);
  const article=useRef(null);
  useEffect(()=>{
    // A normal URL fragment can arrive before the asynchronous saved read.
    if(window.location.hash==='#empirical-result'){
      article.current?.focus({preventScroll:true});
      article.current?.scrollIntoView({block:'start'});
    }
  },[value.id]);
  const report=value.report,difficulty=value.difficulty,coverage=coverageSummary(report);
  const leaves=report.leaves.filter(leaf=>showAll||report.annotated_leaf_ids?.includes(leaf.id)||leaf.events>0||leaf.controls>0||leaf.secondary_labels>0);
  return <article ref={article} tabIndex={-1} id="empirical-result" className="empirical-result" aria-label="Selected empirical report">
    <h3>{value.title}</h3>
    <div className="actions"><button onClick={()=>onDownload('empirical-'+value.id+'.json',value)}>Download report</button><a href={'/reports?report='+encodeURIComponent(value.id)+'#empirical-result'}>Open saved report</a></div>
    <p className="population-notice">{populationNotice(report.population.label_origin)}</p>
    <h4>Selected population</h4>
    <dl className="population-fields">{populationFields(report.population).map(([label,text])=><div key={label}><dt>{label}</dt><dd>{text}</dd></div>)}</dl>
    <p>{report.annotated_windows} fully inspected mapped windows; {report.unannotated_windows} unannotated or incompletely mapped. {report.source_annotated_windows} source-annotated windows; {report.mapping_incomplete_windows} have incomplete category mappings.</p>
    <p>{report.eligible_events} distinct mapped mistakes; {report.unmapped_events} unmapped events. Inspected native tokens: {report.inspected_native_tokens??'Unknown'}.</p>
    <p>Declared annotation scope: {coverage.declared} of {coverage.total} categories. Categories with mapped mistakes: {coverage.withEvents}. Absence measurements require fully inspected mapped windows. Categories outside the scope remain unknown, including pronunciation in writing-only data.</p>
    <h4>Category measurements</h4>
    <p className="field-help">Each value is an exact fraction, with its unreduced numerator / denominator below it. Token density multiplies the mistake count by 1,000. An unavailable measurement is not zero.</p>
    <label><input type="checkbox" aria-label="Show unannotated categories" checked={showAll} onChange={event=>setShowAll(event.target.checked)}/> Show all categories, including those outside this report’s annotation scope</label>
    <table tabIndex={0} aria-label="Empirical category measurements"><thead><tr><th>Category</th><th>Mistakes</th><th>Event share</th><th>Window prevalence</th><th>Opportunity rate</th><th>Per 1,000 tokens</th></tr></thead><tbody>{leaves.map(leaf=><tr key={leaf.id}><td>{leaf.id}</td><td>{leaf.events}<small className="measurement-counts">{leaf.controls} correct controls · {leaf.secondary_labels} secondary labels</small></td>{[leaf.event_share,leaf.window_prevalence,leaf.opportunity_rate,leaf.per_1000_tokens].map((metric,index)=><td key={index}><Measurement value={metric}/></td>)}</tr>)}</tbody></table>
    {!leaves.length&&<p>No mapped or inspected categories in this population. Native labels and unknown coverage remain available below.</p>}
    <h4>Learner outcomes and difficulty</h4>
    <p>Difficulty: {difficulty.rating}. {difficulty.successes} successful outcomes / {difficulty.trials} eligible independent first answers. These outcomes are separate from source mistake frequencies.</p>
    {difficultyReason(difficulty.missing_reason)&&<p>{difficultyReason(difficulty.missing_reason)}</p>}
    {difficulty.lower_bound!=null&&difficulty.upper_bound!=null&&<p>95% Wilson success interval: {(Number(difficulty.lower_bound)*100).toFixed(1)}%–{(Number(difficulty.upper_bound)*100).toFixed(1)}% (rounded for display; full values are in the download).</p>}
    <p>Paired follow-up success change: <Measurement value={difficulty.paired_success_change}/>. This is descriptive change in the selected pairs; it does not establish that recommendations caused improvement.</p>
    <p className="field-help">Only observations declared genuine, with an identified participant and a recorded outcome, enter difficulty. A supplied origin label does not independently verify human participation. Constructed and model observations stay excluded.</p>
    <Exclusions values={difficulty.excluded}/>
    <details><summary>Native labels, relationships, confusion and exclusions</summary>
      <h4>Native-label frequencies</h4><p>Native annotations and mapped project categories describe different label systems. Unmapped source labels are retained here.</p>
      <table tabIndex={0} aria-label="Native label measurements"><thead><tr><th>Native label</th><th>Mistakes</th><th>Event share</th><th>Window prevalence</th></tr></thead><tbody>{report.native_frequencies.map(leaf=><tr key={leaf.id}><td>{leaf.id}</td><td>{leaf.events}</td><td><Measurement value={leaf.event_share}/></td><td><Measurement value={leaf.window_prevalence}/></td></tr>)}</tbody></table>
      {!report.native_frequencies.length&&<p>No native error labels observed.</p>}
      <h4>Distinct-event relationships</h4><p>Support uses fully inspected windows. Conditional frequency uses windows containing the first category; lift compares the two category frequencies. Multiple labels on one event do not form a pair. Unlisted pairs have zero observed windows only within a fully inspected population and its declared category scope. Without those observations, pair measurements remain unknown.</p>
      {report.pairs.length?<table tabIndex={0} aria-label="Category relationships"><thead><tr><th>First category</th><th>Second category</th><th>Joint windows</th><th>Support</th><th>Conditional</th><th>Lift</th></tr></thead><tbody>{report.pairs.map(pair=><tr key={pair.a+'/'+pair.b}><td>{pair.a}</td><td>{pair.b}</td><td>{pair.distinct_event_windows}</td><td><Measurement value={pair.support}/></td><td><Measurement value={pair.conditional}/></td><td><Measurement value={pair.lift}/></td></tr>)}</tbody></table>:<p>No observed distinct-event pairs. This does not establish absence outside the inspected population.</p>}
      <h4>Reference / prediction confusion</h4>{report.confusion.length?<table tabIndex={0} aria-label="Reference prediction confusion"><thead><tr><th>Reference</th><th>Prediction</th><th>Decisions</th><th>Within-reference proportion</th></tr></thead><tbody>{report.confusion.map(row=><tr key={row.reference+'/'+row.predicted}><td>{row.reference}</td><td>{row.predicted}</td><td>{row.count}</td><td><Measurement value={row.row_proportion}/></td></tr>)}</tbody></table>:<p>No reference / prediction decisions recorded. Model quality remains unknown.</p>}
      <h4>Source exclusions</h4><Exclusions values={report.excluded}/>
      <details><summary>Original saved measurements</summary><pre>{JSON.stringify({native:report.native_label_counts,pairs:report.pairs,confusion:report.confusion,excluded:report.excluded},null,2)}</pre></details>
    </details>
  </article>;
}
