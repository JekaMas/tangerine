import {blueprintRequest,severityOptions} from './request';

export default function RequestPreview({form,categories,voices=[]}) {
  let blueprint,error='';try{blueprint=blueprintRequest(form);}catch(e){error=e.message;}
  const r=blueprint?.exercise_request;
  const labels=(Array.isArray(r?.category_ids)?r.category_ids:[]).map(id=>categories.find(x=>x.id===id)?.label||id);
  const severity=Array.isArray(r?.severity_levels)?r.severity_levels:[];
  const families=Array.isArray(r?.category_families)?r.category_families:[];
  const display=value=>typeof value==='string'||typeof value==='number'?String(value):'Check advanced value';
  return <aside className="request-preview" aria-label="Exercise summary"><h2>Your exercise</h2>
    <p>A new conversation, with mistakes chosen for your practice.</p>
    {error?<p className="field-help">{error}</p>:<>
      <dl className="summary-list"><div><dt>Speakers</dt><dd>{display(r.speaker_count)}</dd></div><div><dt>Length</dt><dd>About {display(r.text_length_words)} words</dd></div><div><dt>English level</dt><dd>{r.english_level==null?'Any level':display(r.english_level)}</dd></div><div><dt>Mistakes</dt><dd>{r.mutation_count==null?'Automatic':r.mutation_count===0?'None (control)':display(r.mutation_count)}</dd></div><div><dt>Severity</dt><dd>{severity.length?severity.map(id=>severityOptions.find(x=>x[0]===id)?.[1]||display(id)).join(', '):'Any severity'}</dd></div></dl>
      {Array.isArray(r.speaker_voice_ids)&&r.speaker_voice_ids.some(Boolean)&&<><h3>Speaker voices</h3><p>{r.speaker_voice_ids.map((id,i)=>{const voice=voices.find(v=>v.id===id);return `Speaker ${i+1}: ${voice?voice.accent_label+' · '+voice.label:id||'Automatic'}`;}).join('; ')}</p></>}
      {Array.isArray(r.recurring_errors)&&r.recurring_errors.length>0&&<><h3>Recurring patterns</h3>{r.recurring_errors.map(p=><p key={p.speaker_number}>Speaker {p.speaker_number}: target {p.target_percent}% of relevant opportunities{p.instruction?' · '+p.instruction:''}</p>)}<p className="field-help">Each recurring rule counts once. Repetitions and correct exceptions are saved. {r.mutation_count===0?'Zero mistakes disables these patterns.':'Actual frequency depends on whole occurrences.'}</p></>}
      <h3>Practice focus</h3><p className="preview-categories">{labels.length?labels.map(display).join(', '):families.length?families.map(x=>display(x).replaceAll('_',' ').replaceAll('.',' / ')).join(', '):'Let the LLM choose'}</p>
      <div className="flow-note"><span>Listen to the conversation</span><span>Describe what you notice</span><span>Get feedback and recommendations</span></div>
      {form.advanced.trim()&&<p className="field-help">Advanced fields override the matching choices above.</p>}
      <details className="request-details"><summary>View effective request</summary><pre>{JSON.stringify(blueprint,null,2)}</pre></details>
    </>}
  </aside>;
}
