'use client';

export default function RecurringErrors({index,form,update}) {
 const value=form.recurring?.[index]||{enabled:false,percent:85,instruction:''};
 function change(patch){const next=[...(form.recurring||[])];next[index]={...value,...patch};update('recurring',next);}
 return <div className="recurring-controls">
  <label className="recurring-toggle"><input className="check" type="checkbox" aria-label={'Speaker '+(index+1)+' recurring mistakes'} checked={Boolean(value.enabled)} onChange={e=>change({enabled:e.target.checked})}/>Recurring mistake pattern</label>
  {value.enabled&&<><label>Target frequency: {value.percent??85}%<input type="range" aria-label={'Speaker '+(index+1)+' recurring frequency'} min="70" max="95" step="1" value={value.percent??85} onChange={e=>change({percent:Number(e.target.value)})}/></label>
   <label>Pattern guidance (optional)<input aria-label={'Speaker '+(index+1)+' recurring pattern'} placeholder="For example, drop plural endings after numbers" value={value.instruction||''} onChange={e=>change({instruction:e.target.value})}/></label>
   <p className="field-help">Applies to relevant contexts for this speaker, within your selected categories. The LLM chooses a specific pattern if you leave guidance empty. The whole pattern counts as one mistake; every repetition is saved.</p>
   <p className="field-help">This simulates a persistent habit. 85% is a practice default, not a research estimate. Short dialogues round to whole occurrences; results show the actual fraction. Exact zero disables all mistakes.</p>
  </>}
 </div>;
}
