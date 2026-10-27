'use client';
import {useState} from 'react';
import useSavedList from '../useSavedList';
import RefreshButton from '../RefreshButton';
import {recordDate} from '../savedRecord';
import ReportError from './ReportError';

// The source owner selects native rows. The form supplies no labels or counts.
export default function ImportedReports({busy,onSave,error}) {
  const choices=useSavedList('/api/v1/reports/source-populations',{unavailable:'Imported sources are temporarily unavailable. Your saved reports and practice are still available. Retry source choices.'});
  const [choice,setChoice]=useState(null),[title,setTitle]=useState('');
  const selected=choice?JSON.stringify(choice.source):'';
  const options=choice&&!choices.items.some(item=>JSON.stringify(item.source)===selected)?[choice,...choices.items]:choices.items;
  return <div className="imported-reports">
    <h3>Explore imported data</h3>
    <p>Choose one source and view. The report counts its original annotations and shows which Tangerine categories can be identified. Nothing is sent to an AI service.</p>
    {choices.loading&&<p role="status">Loading imported source choices…</p>}
    {choices.error&&<p role="alert">{choices.error}</p>}
    <RefreshButton onClick={choices.refresh}>Retry source choices</RefreshButton>
    {choices.loaded&&!choices.error&&!choices.items.length&&<p>No completed source imports yet. You can <a href="/sources">import a source</a>, open a saved report or continue practising.</p>}
    {!!choices.items.length&&<form onSubmit={event=>{event.preventDefault();if(choice)onSave(JSON.stringify({title:title.trim()||choice.title,source:choice.source}));}}>
      <label>Imported source and view<select aria-label="Imported source and view" value={selected} onChange={event=>setChoice(options.find(item=>JSON.stringify(item.source)===event.target.value)||null)} required><option value="">Choose a source view</option>{options.map(item=><option key={JSON.stringify(item.source)} value={JSON.stringify(item.source)}>{item.title} · {recordDate(item.imported_at)}</option>)}</select></label>
      {choice&&<p className="field-help">{choice.description}</p>}
      <label>Report name <span className="optional-label">optional</span><input aria-label="Report name" value={title} onChange={event=>setTitle(event.target.value)} placeholder={choice?.title||'A name you will recognise'}/></label>
      <button disabled={busy||!choice}>{busy?'Saving report…':'Create source report'}</button>
    </form>}
    <ReportError message={error}/>
  </div>;
}
