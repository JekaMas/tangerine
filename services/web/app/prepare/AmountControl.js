import {blueprintRequest,categoryFloor,severityOptions} from './request';
import {recurringRequests} from './recurringRequest';

export default function AmountControl({form,update,overrides={}}) {
  let request,count;try{request=blueprintRequest(form).exercise_request;count=request.mutation_count;}catch{count=null;}
  const words=request?.text_length_words ?? form.words;
  const recurring=request?(Array.isArray(request.recurring_errors)?request.recurring_errors.length:0):recurringRequests(form).length;
  const floor=Math.max(categoryFloor(request?{categories:request.category_ids,families:request.category_families}:form),recurring), mode=form.amount || 'auto';
  return <>
    <fieldset className="control-section"><legend>How many mistakes?</legend>
      <div className="amount-options" role="group" aria-label="Mistake amount">{[['auto','Automatic','LLM chooses'],['low','Low','1 per 100 words'],['medium','Medium','2 per 100 words'],['high','High','4 per 100 words'],['exact','Exact','Your number']].map(([id,label,caption])=><button type="button" key={id} className={'amount-option'+(mode===id?' selected':'')} aria-pressed={mode===id} onClick={()=>{update('amount',id);if(id==='exact'&&form.mutationCount==='')update('mutationCount',String(count??Math.max(1,floor)));}}><strong>{label}</strong><small>{caption}</small></button>)}</div>
      {mode==='exact'&&<label className="exact-count">Number of mistakes<input aria-label="Number of mistakes" required disabled={Object.hasOwn(overrides,'mutation_count')} type="number" min="0" step="1" value={form.mutationCount} onChange={e=>update('mutationCount',e.target.value)}/></label>}
      <p className="field-help" aria-live="polite">{Object.hasOwn(overrides,'mutation_count')?'Mistake count comes from your advanced blueprint; see Your exercise above.':mode==='auto'?'The LLM chooses a positive count covering your selected categories.':count===0?'No mistakes will be injected. This is a control-only exercise.':count!=null?`${count} ${count===1?'mistake':'mistakes'} requested in approximately ${words} words.`:'Review the effective request above; your choices are retained.'} {['low','medium','high'].includes(mode)&&floor>Math.round(Number(words)*({low:1,medium:2,high:4}[mode])/100)?'The total was raised to cover selected categories and enabled recurring speakers.':''}</p>
      {recurring>0&&<p className="field-help">Each recurring speaker pattern counts once, with all repetitions saved. Other mistakes count separately. Exact zero disables recurring patterns too.</p>}
    </fieldset>
    <fieldset className="control-section"><legend>How much should the mistakes affect meaning?</legend>
      <p className="field-help">Severity is separate from English level and mistake count. Select one or more, or allow any.</p>
      <div className="severity-options"><button type="button" className={'choice-chip any-severity'+(!form.severities?.length?' active':'')} aria-pressed={!form.severities?.length} onClick={()=>update('severities',[])}>Any severity</button>{severityOptions.map(([id,label,description])=><label className="severity-option" key={id}><input type="checkbox" aria-label={label+' severity'} checked={form.severities?.includes(id)||false} onChange={()=>update('severities',form.severities?.includes(id)?form.severities.filter(x=>x!==id):[...(form.severities||[]),id])}/><span><strong>{label}</strong><small>{description}</small></span></label>)}</div>
    </fieldset>
  </>;
}
