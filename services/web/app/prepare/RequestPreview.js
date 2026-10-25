import {requestError} from '../requestError.js';
import {blueprintRequest,severityOptions} from './request';
import {summaryVoices} from './summaryVoices.js';

export default function RequestPreview({form,categories,voices=[]}) {
  const display=value=>typeof value==='string'||typeof value==='number'?String(value):'Check advanced value';
  let blueprint,speakerVoices=[],labels=[],severity=[],families=[],patterns=[],error='';
  try{
    blueprint=blueprintRequest(form);speakerVoices=summaryVoices(blueprint,voices);
    const r=blueprint.exercise_request;
    labels=(Array.isArray(r.category_ids)?r.category_ids:[]).map(id=>display(categories.find(x=>x.id===id)?.label||id));
    severity=(Array.isArray(r.severity_levels)?r.severity_levels:[]).map(id=>severityOptions.find(x=>x[0]===id)?.[1]||display(id));
    families=(Array.isArray(r.category_families)?r.category_families:[]).map(x=>display(x).replaceAll('_',' ').replaceAll('.',' / '));
    patterns=(Array.isArray(r.recurring_errors)?r.recurring_errors:[]).map(p=>`Speaker ${display(p.speaker_number)}: target ${display(p.target_percent)}% of relevant opportunities${p.instruction?' · '+display(p.instruction):''}`);
  }
  catch(e){blueprint=null;error=requestError(e, 'Check the advanced blueprint values. Your choices are retained.');}
  const r=blueprint?.exercise_request;
  return <aside className="request-preview" aria-label="Exercise summary"><h2>Your exercise</h2>
    {error?<p className="field-help">{error}</p>:<>
      <dl className="summary-list"><div><dt>Speakers</dt><dd>{display(r.speaker_count)}</dd></div><div><dt>Length</dt><dd>About {display(r.text_length_words)} words</dd></div><div><dt>English level</dt><dd>{r.english_level==null?'Any level':display(r.english_level)}</dd></div><div><dt>Mistakes</dt><dd>{r.mutation_count==null?'Automatic':r.mutation_count===0?'None (control)':display(r.mutation_count)}</dd></div><div><dt>Severity</dt><dd>{severity.length?severity.join(', '):'Any severity'}</dd></div></dl>
      <h3>Speaker voices</h3><p>{speakerVoices.length?speakerVoices.join('; '):'Configured defaults for each speaker.'}</p>
      {patterns.length>0&&<><h3>{r.mutation_count===0?'Recurring patterns disabled':'Recurring patterns'}</h3>{r.mutation_count===0?<p>No recurring mistakes in this control exercise. Your pattern choices are retained.</p>:<>{patterns.map((p,i)=><p key={i}>{p}</p>)}<p className="field-help">Each recurring rule counts once. Repetitions and correct exceptions are saved. Actual frequency depends on whole occurrences.</p></>}</>}
      <h3>Practice focus</h3><p className="preview-categories">{labels.length?labels.join(', '):families.length?families.join(', '):'Let the LLM choose'}</p>
      {form.advanced.trim()&&<p className="field-help">Advanced fields override the matching choices above.</p>}
      <details className="request-details"><summary>View effective request</summary><pre>{JSON.stringify(blueprint,null,2)}</pre></details>
    </>}
  </aside>;
}
