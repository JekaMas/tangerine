'use client';
import {useState} from 'react';
import RecurringErrors from './RecurringErrors';

export function resizeVoices(voices,count){return Array.from({length:count},(_,i)=>voices?.[i]||'');}

export default function SpeakerVoices({form,update,voices,loading,error,retry}){
 const [previewError,setPreviewError]=useState('');
 const count=Number(form.speakers);const active=Number.isSafeInteger(count)&&count>0?resizeVoices(form.voices,count):[];
 const accents=[...new Map(voices.map(v=>[v.accent,v.accent_label])).entries()];
 function choose(i,id){const next=[...(form.voices||[])];next[i]=id;update('voices',next);setPreviewError('');}
 return <fieldset className="control-section speaker-section"><legend>How should the speakers sound?</legend>
  <p className="field-help">Choose an accent and voice for each speaker, or keep your configured defaults. These named voices run locally. Accent alone is never a mistake.</p>
  {loading&&<p role="status">Loading voice choices…</p>}
  {error&&<div className="error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={retry}>Retry voices</button></div>}
  <div className="speaker-choices">{active.map((id,i)=>{const selected=voices.find(v=>v.id===id);const accent=selected?.accent||'';const available=voices.filter(v=>v.accent===accent);return <div className="speaker-choice" key={i}>
   <h3>Speaker {i+1}</h3><div className="speaker-selects">
    <label>Accent<select aria-label={'Speaker '+(i+1)+' accent'} value={accent} disabled={loading||Boolean(error)} onChange={e=>choose(i,voices.find(v=>v.accent===e.target.value)?.id||'')}><option value="">Automatic</option>{accents.map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
    <label>Voice<select aria-label={'Speaker '+(i+1)+' voice'} value={id} disabled={!accent||loading||Boolean(error)} onChange={e=>choose(i,e.target.value)}><option value="">Configured default</option>{available.map(v=><option value={v.id} key={v.id}>{v.label}</option>)}</select></label>
   </div>
   {selected&&<div className="voice-preview"><p className="field-help">{selected.engine} · {selected.accent_label} · fixed sample</p><audio key={selected.id} aria-label={'Preview '+selected.label} controls preload="none" src={selected.preview_url} onError={()=>setPreviewError('This voice preview is unavailable. Your speaker choices are retained. Retry playback or choose another voice.')}/></div>}
   <RecurringErrors index={i} form={form} update={update}/>
  </div>;})}</div>
  {previewError&&<p className="error" role="alert">{previewError}</p>}
  <p className="field-help">Australian and Indian voices use MeloTTS; American and British voices use Kokoro. First-time model setup is explicit. Previews replay saved audio and make no LLM call.</p>
 </fieldset>;
}
