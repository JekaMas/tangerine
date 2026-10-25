import {categoryFloor,mistakeCount,severityOptions} from './request';
import {recurringRequests} from './recurringRequest';

export default function AmountControl({form,update}) {
  let count;try{count=mistakeCount(form);}catch{count=null;}
  const recurring=recurringRequests(form).length, floor=Math.max(categoryFloor(form),recurring), mode=form.amount || 'auto';
  return <>
    <fieldset className="control-section"><legend>How many mistakes?</legend>
      <div className="amount-options" role="group" aria-label="Mistake amount">{[['auto','Automatic','LLM chooses'],['low','Low','1 per 100 words'],['medium','Medium','2 per 100 words'],['high','High','4 per 100 words'],['exact','Exact','Your number']].map(([id,label,caption])=><button type="button" key={id} className={'amount-option'+(mode===id?' selected':'')} aria-pressed={mode===id} onClick={()=>{update('amount',id);if(id==='exact'&&form.mutationCount==='')update('mutationCount',String(count??Math.max(1,floor)));}}><strong>{label}</strong><small>{caption}</small></button>)}</div>
      {mode==='exact'&&<label className="exact-count">Number of mistakes<input aria-label="Number of mistakes" required type="number" min="0" step="1" value={form.mutationCount} onChange={e=>update('mutationCount',e.target.value)}/></label>}
      <p className="field-help" aria-live="polite">{mode==='auto'?'The LLM chooses a positive count covering your selected categories.':count===0?'No mistakes will be injected. This is a control-only exercise.':count!=null?`${count} ${count===1?'mistake':'mistakes'} requested in approximately ${form.words} words.`:'Enter a whole number, zero or greater.'} {['low','medium','high'].includes(mode)&&floor>Math.round(Number(form.words)*({low:1,medium:2,high:4}[mode])/100)?'The total was raised to cover selected categories and enabled recurring speakers.':''}</p>
      {recurring>0&&<p className="field-help">Each recurring speaker pattern counts once, with all repetitions saved. Other mistakes count separately. Exact zero disables recurring patterns too.</p>}
    </fieldset>
    <fieldset className="control-section"><legend>How much should the mistakes affect meaning?</legend>
      <p className="field-help">Severity is separate from English level and mistake count. Select one or more, or allow any.</p>
      <div className="severity-options"><button type="button" className={'choice-chip any-severity'+(!form.severities?.length?' active':'')} aria-pressed={!form.severities?.length} onClick={()=>update('severities',[])}>Any severity</button>{severityOptions.map(([id,label,description])=><label className="severity-option" key={id}><input type="checkbox" aria-label={label+' severity'} checked={form.severities?.includes(id)||false} onChange={()=>update('severities',form.severities?.includes(id)?form.severities.filter(x=>x!==id):[...(form.severities||[]),id])}/><span><strong>{label}</strong><small>{description}</small></span></label>)}</div>
    </fieldset>
  </>;
}
