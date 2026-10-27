'use client';
import {useEffect,useRef,useState} from 'react';
import {populationNotice,difficultyReason,coverageSummary} from './empiricalPresentation';
import {count,readableMetric,nativeName,categoryName,sourceExclusion} from './sourcePresentation';

function Measurement({value,kind}) {const shown=readableMetric(value,kind);return <><span>{shown.value}</span><small className="measurement-counts">{shown.basis}</small></>;}
function Pairs({pairs,label,name}) {
  const [all,setAll]=useState(false);
  return <><p>Two distinct mistakes must occur in the same fully annotated example. The figures describe this source view; they do not establish a cause.</p>
    {!pairs.length?<p>Relationships are not measured here, or no pairs were observed within the annotated examples. This does not show that the categories are unrelated elsewhere.</p>:<>
      <div className="report-table"><table tabIndex={0} aria-label={name}><thead><tr><th>First mistake</th><th>Second mistake</th><th>Examples with both</th><th>Share of examples</th><th>Second when first occurs</th><th>Association</th></tr></thead><tbody>{(all?pairs:pairs.slice(0,12)).map(pair=><tr key={pair.a+'/'+pair.b}><td>{label(pair.a)}</td><td>{label(pair.b)}</td><td>{count(pair.distinct_event_windows)}</td><td><Measurement value={pair.support}/></td><td><Measurement value={pair.conditional}/></td><td><Measurement value={pair.lift} kind="lift"/></td></tr>)}</tbody></table></div>
      {pairs.length>12&&<button className="secondary" onClick={()=>setAll(!all)}>{all?'Show fewer relationships':'Show all '+count(pairs.length)+' relationships'}</button>}
    </>}
  </>;
}

// Saved reads only. All arithmetic, scope and lineage belong to the API owner.
export default function EmpiricalResult({value,onDownload}) {
  const [showAll,setShowAll]=useState(false),[showNative,setShowNative]=useState(false);
  const article=useRef(null);
  useEffect(()=>{article.current?.focus({preventScroll:true});article.current?.scrollIntoView({block:'start'});},[value.id]);
  const r=value.report,d=value.difficulty,summary=value.source_summary,coverage=coverageSummary(r),labels=value.category_labels||{};
  const native=r.native_population;
  const leaves=r.leaves.filter(leaf=>showAll||r.annotated_leaf_ids?.includes(leaf.id)||leaf.events>0||leaf.controls>0||leaf.secondary_labels>0);
  const sourceOnly=r.population.label_origin==='native_coverage_only';
  return <article ref={article} tabIndex={-1} id="empirical-result" className="empirical-result" aria-label="Selected empirical report">
    <h3>{value.title}</h3>
    <div className="actions"><button className="secondary" onClick={()=>onDownload('empirical-'+value.id+'.json',value)}>Download report</button><a href={'/reports?report='+encodeURIComponent(value.id)+'#empirical-result'}>Open saved report</a></div>
    <p className="population-notice">{summary?summary.source_name+' · '+summary.view_label:populationNotice(r.population.label_origin)}</p>
    <div className="report-overview"><div><strong>{count(r.observed_windows)}</strong><span>{summary?.unit||'examples'} in this view</span></div><div><strong>{sourceOnly?'Not measured':count(native?.eligible_events??r.eligible_events+r.unmapped_events)}</strong><span>original annotated mistakes</span></div><div><strong>{count(coverage.withEvents)} of {count(coverage.total)}</strong><span>categories with mapped examples</span></div></div>
    {summary&&<details><summary>How this source was interpreted</summary><dl className="population-fields"><div><dt>Source</dt><dd>{summary.source_name}</dd></div><div><dt>View</dt><dd>{summary.view_label}</dd></div><div><dt>Examples counted</dt><dd>{summary.unit}</dd></div></dl>{summary.notes.map(note=><p key={note}>{note}</p>)}</details>}

    {!!summary?.coverage.length&&<dl className="population-fields">{summary.coverage.map(row=><div key={row.label}><dt>{row.label}</dt><dd>{count(row.count)}</dd></div>)}</dl>}
    <h4>What was counted?</h4><p>Frequencies describe this source view. They are not estimates for all English learners.</p>
    {native&&<p>{count(native.annotated_windows)} of {count(native.observed_windows)} examples have usable original error annotations. {native.inspected_native_tokens==null?'A word-count exposure is not available.':count(native.inspected_native_tokens)+' words belong to those fully annotated examples.'}</p>}
    <p>{count(r.eligible_events)} mistakes have a derived Tangerine category; {count(r.unmapped_events)} remain outside the resolved mapping. Category proportions use only the mapped mistakes. Original source measurements use their own annotations.</p>
    <p>{coverage.declared?count(coverage.declared)+' categories have declared complete annotation coverage.':'No category has declared complete absence coverage.'} Categories without sufficient annotations are <strong>not measured</strong>, including pronunciation in writing-only data. Missing measurements never mean there are no mistakes.</p>
    <h4>Original source measurements</h4>
    {sourceOnly?<p>Not measured. This view contains examples or ratings without localized mistake labels.</p>:<>
      <p>“Share of mistakes” uses all eligible original error events. “Examples affected” uses fully annotated examples in this one view. A sentence or utterance with several mistakes is counted once for each type it contains.</p>
      <div className="report-table"><table tabIndex={0} aria-label="Native label measurements"><thead><tr><th>Mistake described by the source</th><th>Count</th><th>Share of mistakes</th><th>Examples affected</th></tr></thead><tbody>{(showNative?r.native_frequencies:r.native_frequencies.slice(0,12)).map(leaf=><tr key={leaf.id}><td>{nativeName(leaf.id)}</td><td>{count(leaf.events)}</td><td><Measurement value={leaf.event_share}/></td><td><Measurement value={leaf.window_prevalence}/></td></tr>)}</tbody></table></div>
      {!r.native_frequencies.length&&<p>No original error labels were observed. This does not establish error-free language outside annotated examples.</p>}
      {r.native_frequencies.length>12&&<button className="secondary" onClick={()=>setShowNative(!showNative)}>{showNative?'Show fewer source types':'Show all source types'}</button>}
      <details><summary>Which source mistakes occur together?</summary><Pairs pairs={r.native_pairs||[]} label={nativeName} name="Source relationships"/></details>
    </>}
    <h4>Tangerine category coverage</h4>
    <p>Mappings preserve source meanings. They do not supply complete annotation of every category or correct-use opportunity.</p>
    <label><input type="checkbox" aria-label="Show unannotated categories" checked={showAll} onChange={event=>setShowAll(event.target.checked)}/> Show all {count(coverage.total)} categories, including those not measured</label>
    <div className="report-table"><table tabIndex={0} aria-label="Empirical category measurements"><thead><tr><th>Category</th><th>Mapped mistakes</th><th>Share of mapped mistakes</th><th>Examples affected</th><th>Correct-use opportunity rate</th><th>Per 1,000 words</th></tr></thead><tbody>{leaves.map(leaf=><tr key={leaf.id}><td>{categoryName(leaf.id,labels)}</td><td>{count(leaf.events)}<small className="measurement-counts">{count(leaf.controls)} correct examples · {count(leaf.secondary_labels)} additional labels</small></td>{[leaf.event_share,leaf.window_prevalence,leaf.opportunity_rate,leaf.per_1000_tokens].map((metric,index)=><td key={index}><Measurement value={metric} kind={index===3?'density':'percent'}/></td>)}</tr>)}</tbody></table></div>
    {!leaves.length&&<p>No resolved category examples in this view. Use “Show all categories” to see the missing coverage.</p>}
    <details><summary>Category relationships and exclusions</summary><Pairs pairs={r.pairs} label={id=>categoryName(id,labels)} name="Category relationships"/><h4>Observations left out</h4>{Object.keys(r.excluded).length?<ul>{Object.entries(r.excluded).map(([reason,n])=><li key={reason}>{sourceExclusion(reason)}: {count(n)}</li>)}</ul>:<p>No source exclusions recorded.</p>}
      <p>{count(r.confusion.length)} reference and prediction comparisons were supplied. These are separate from native source frequencies. Full comparison details and original source identifiers are preserved in the download.</p>
    </details>
    <details><summary>Learner outcomes and difficulty</summary>
      <p>{count(d.successes)} successful outcomes from {count(d.trials)} eligible independent first answers. Difficulty {d.rating==='unrated'?'has not been established.':'is '+d.rating+'.'} These observations are separate from source mistake counts.</p>
      {difficultyReason(d.missing_reason)&&<p>{difficultyReason(d.missing_reason)}</p>}
      {d.lower_bound!=null&&d.upper_bound!=null&&<p>Estimated success range: {(Number(d.lower_bound)*100).toFixed(1)}%–{(Number(d.upper_bound)*100).toFixed(1)}% at 95% confidence.</p>}
      <p>Follow-up change: <Measurement value={d.paired_success_change}/>. This does not establish that recommendations caused improvement.</p>
      <p>Only observations declared to be genuine independent learner attempts enter this measure. Constructed and model answers are excluded. Original exclusions and complete values are in the download.</p>
    </details>
    <p className="field-help">Displayed percentages are rounded. The download preserves exact counts, fractions, source locations and mapping rules. Saved reports do not change when new data are imported.</p>
  </article>;
}
