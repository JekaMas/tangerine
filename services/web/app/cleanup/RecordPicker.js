'use client';
import RefreshButton from '../RefreshButton.js';
import useSavedList from '../useSavedList';
import {recordTitle,recordDate,recordState} from '../savedRecord';

export default function RecordPicker({ids,onChange,busy}) {
  const unavailable='Saved record choices are unavailable. Retry; your selection is retained.';
  const attempts=useSavedList('/api/v1/attempts',{limit:50,unavailable});
  const preparations=useSavedList('/api/v1/preparations',{limit:50,publicView:true,wrapped:true,unavailable});
  const rows=[...attempts.items.map(item=>({...item,kind:'attempts'})),...preparations.items.map(item=>({...item,kind:'preparations'}))];
  const loading=attempts.loading||preparations.loading,loaded=attempts.loaded&&preparations.loaded;
  const error=attempts.error||preparations.error;
  function refresh(append=false){for(const list of [attempts,preparations])if(!append||list.cursor)list.refresh(append);}
  const selected=ids.split(/[,\s]+/).filter(Boolean);
  function toggle(id,checked){onChange((checked?[...new Set([...selected,id])]:selected.filter(value=>value!==id)).join('\n'));}
  return <section aria-label="Saved records for cleanup"><h2>Choose saved records</h2><p>Select an answer or preparation, then preview its exact dependencies. Selection alone deletes nothing.</p>
    {loading&&<p role="status">Loading saved records…</p>}{error&&<p role="alert">{error}</p>}<RefreshButton onClick={()=>refresh()}>Refresh record choices</RefreshButton>
    <div className="record-picker">{rows.map(item=><label key={item.kind+'/'+item.id}><input type="checkbox" disabled={busy} checked={selected.includes(item.id)} aria-label={'Select '+recordTitle(item)+' · '+(item.kind==='attempts'?'attempt':'preparation')+' · '+item.id} onChange={event=>toggle(item.id,event.target.checked)}/><span>{recordTitle(item)}<small>{item.kind==='attempts'?recordState(item.state):'Preparation'} · {recordDate(item.started_at||item.created_at)}</small><small>{item.id}</small></span></label>)}
      {loaded&&!loading&&!error&&!rows.length&&<p>No saved records. <a href="/prepare">Prepare an exercise</a> to begin.</p>}
    </div>
    {(attempts.cursor||preparations.cursor)&&<button type="button" className="secondary" disabled={busy||loading} onClick={()=>refresh(true)}>Load more records</button>}
  </section>;
}
