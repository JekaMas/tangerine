'use client';
import CategoryPicker from './CategoryPicker';
import AmountControl from './AmountControl';
import SpeakerVoices from './SpeakerVoices';
import {advancedBlueprint} from './request';

export default function Controls({form, update, busy, categories, voices, categoryLoading, categoryError, retryCategories, children}) {
  let overrides={};try{overrides=advancedBlueprint(form).exercise_request||{};}catch{}
  return <div className="preparation-controls"><fieldset disabled={busy} className="preparation-controls">
    <div className="control-section"><h2>Start with a conversation</h2>{Object.keys(overrides).length>0&&<p className="field-help">Matching controls use your advanced blueprint. Clear those advanced fields to edit their simple choices.</p>}<label>Topic<textarea className="topic-input" aria-label="Topic" disabled={Object.hasOwn(overrides,'topic')} required rows={3} placeholder="Two colleagues planning a weekend away…" value={form.topic} onChange={e => update('topic', e.target.value)}/></label>
    <div className="form-grid">
    <label>Speakers<input aria-label="Speakers" disabled={Object.hasOwn(overrides,'speaker_count')} required type="number" min="1" step="1" value={form.speakers} onChange={e => update('speakers', e.target.value)}/></label>
    <label>Approximate words<input aria-label="Approximate words" disabled={Object.hasOwn(overrides,'text_length_words')} required type="number" min="1" step="1" value={form.words} onChange={e => update('words', e.target.value)}/></label>
    <label>English level (optional)<select aria-label="English level" disabled={Object.hasOwn(overrides,'english_level')} value={form.level} onChange={e => update('level', e.target.value)}>
      <option value="">Any level</option>{['A1','A2','B1','B2','C1','C2'].map(x => <option key={x}>{x}</option>)}
    </select></label></div></div>
    </fieldset>{children}<fieldset disabled={busy} className="preparation-controls">
    <details className="customize-controls"><summary>Customize voices and mistakes</summary>
    <SpeakerVoices form={form} update={update} voices={voices} loading={categoryLoading} error={categoryError} retry={retryCategories}/>
    <CategoryPicker form={form} update={update} categories={categories} loading={categoryLoading} error={categoryError} retry={retryCategories}/>
    <AmountControl form={form} update={update} overrides={overrides}/>
    <details className="advanced-controls"><summary>Advanced blueprint and speaker voices</summary>
      <p>Optional blueprint JSON overrides the matching form fields. Use configured voice IDs, locales and requested accents for each speaker. Settings owns available speech profiles.</p>
      <textarea aria-label="Advanced blueprint" rows={10} value={form.advanced} onChange={e => update('advanced', e.target.value)}/>
    </details>
    </details>
  </fieldset></div>;
}
