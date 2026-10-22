'use client';
import {mistakeFamilies} from './request';

export default function Controls({form, update, busy}) {
  function toggle(id) {
    update('families', form.families.includes(id) ? form.families.filter(x => x !== id) : [...form.families, id]);
  }
  return <fieldset disabled={busy} className="preparation-controls">
    <label>Topic<textarea aria-label="Topic" required value={form.topic} onChange={e => update('topic', e.target.value)}/></label>
    <label>Speakers<input aria-label="Speakers" required type="number" min="1" step="1" value={form.speakers} onChange={e => update('speakers', e.target.value)}/></label>
    <label>Approximate words<input aria-label="Approximate words" required type="number" min="1" step="1" value={form.words} onChange={e => update('words', e.target.value)}/></label>
    <label>English level (optional)<select aria-label="English level" value={form.level} onChange={e => update('level', e.target.value)}>
      <option value="">Any level</option>{['A1','A2','B1','B2','C1','C2'].map(x => <option key={x}>{x}</option>)}
    </select></label>
    <fieldset className="mistake-families"><legend>Mistake categories (optional)</legend>
      <p>Leave all unchecked for automatic selection. Selected families each receive a mistake when the count is positive.</p>
      {mistakeFamilies.map(([id, label]) => <label key={id}><input className="check" type="checkbox" aria-label={label} checked={form.families.includes(id)} onChange={() => toggle(id)}/>{label}</label>)}
    </fieldset>
    <label>Number of mistakes (optional)<input aria-label="Number of mistakes" type="number" min="0" step="1" placeholder="Automatic" value={form.mutationCount} onChange={e => update('mutationCount', e.target.value)}/></label>
    <p>Blank lets the LLM choose. A number requests exactly that many independent mistakes. Zero creates a control-only exercise. Use enough mistakes to cover your selected families.</p>
    <details><summary>Advanced blueprint and speaker voices</summary>
      <p>Optional blueprint JSON overrides the matching form fields. Use configured voice IDs, locales and requested accents for each speaker. Settings owns available speech profiles.</p>
      <textarea aria-label="Advanced blueprint" rows={10} value={form.advanced} onChange={e => update('advanced', e.target.value)}/>
    </details>
  </fieldset>;
}
