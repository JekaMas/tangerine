import {requestError} from '../requestError.js';
import {blueprintRequest,severityOptions} from './request';
import {summaryVoices} from './summaryVoices.js';

export default function RequestPreview({form,categories,voices=[]}) {
  let blueprint,speakerVoices=[],error='';
  try{blueprint=blueprintRequest(form);speakerVoices=summaryVoices(blueprint,voices);}
  catch(e){blueprint=null;error=requestError(e, 'Check the advanced blueprint values. Your choices are retained.');}
  const r=blueprint?.exercise_request;
  const labels=(Array.isArray(r?.category_ids)?r.category_ids:[]).map(id=>categories.find(x=>x.id===id)?.label||id);
  const severity=Array.isArray(r?.severity_levels)?r.severity_levels:[];
  const families=Array.isArray(r?.category_families)?r.category_families:[];
  const display=value=>typeof value==='string'||typeof value==='number'?String(value):'Check advanced value';
  return <aside className="request-preview" aria-label="Exercise summary"><h2>Your exercise</h2>
    {error?<p className="field-help">{error}</p>:<>
      <dl className="summary-list"><div><dt>Speakers</dt><dd>{display(r.speaker_count)}</dd></div><div><dt>Length</dt><dd>About {display(r.text_length_words)} words</dd></div><div><dt>English level</dt><dd>{r.english_level==null?'Any level':display(r.english_level)}</dd></div><div><dt>Mistakes</dt><dd>{r.mutation_count==null?'Automatic':r.mutation_count===0?'None (control)':display(r.mutation_count)}</dd></div><div><dt>Severity</dt><dd>{severity.length?severity.map(id=>severityOptions.find(x=>x[0]===id)?.[1]||display(id)).join(', '):'Any severity'}</dd></div></dl>
      <h3>Speaker voices</h3><p>{speakerVoices.length?speakerVoices.join('; '):'Configured defaults for each speaker.'}</p>
      {Array.isArray(r.recurring_errors)&&r.recurring_errors.length>0&&<><h3>{r.mutation_count===0?'Recurring patterns disabled':'Recurring patterns'}</h3>{r.mutation_count===0?<p>No recurring mistakes in this control exercise. Your pattern choices are retained.</p>:<>{r.recurring_errors.map(p=><p key={p.speaker_number}>Speaker {p.speaker_number}: target {p.target_percent}% of relevant opportunities{p.instruction?' · '+p.instruction:''}</p>)}<p className="field-help">Each recurring rule counts once. Repetitions and correct exceptions are saved. Actual frequency depends on whole occurrences.</p></>}</>}
      <h3>Practice focus</h3><p className="preview-categories">{labels.length?labels.map(display).join(', '):families.length?families.map(x=>display(x).replaceAll('_',' ').replaceAll('.',' / ')).join(', '):'Let the LLM choose'}</p>
      {form.advanced.trim()&&<p className="field-help">Advanced fields override the matching choices above.</p>}
      <details className="request-details"><summary>View effective request</summary><pre>{JSON.stringify(blueprint,null,2)}</pre></details>
    </>}
  </aside>;
}
