'use client';
import RefreshButton from '../RefreshButton.js';
import {userError} from '../requestError.js';

import {clientFetch as fetch} from '../clientRequest.js';
import {useEffect,useState} from 'react';
import {recordTitle,recordDate,recordState} from '../savedRecord';

export default function RecordPicker({ids,onChange,busy}) {
  const [rows,setRows]=useState([]),[cursors,setCursors]=useState({}),[error,setError]=useState(''),[loading,setLoading]=useState(false);
  async function load(append=false){setLoading(true);setError('');try{
    const groups=await Promise.all(['attempts','preparations'].map(async kind=>{
      if(append&&!cursors[kind])return {kind,items:[],next:null};
      const q=new URLSearchParams({limit:'50'});if(kind==='preparations')q.set('view','public');if(append)q.set('cursor',cursors[kind]);
      const r=await fetch('/api/v1/'+kind+'?'+q,{cache:'no-store'});if(!r.ok)throw userError('Saved record choices are unavailable. Retry; your selection is retained.');const body=await r.json();return {kind,items:(Array.isArray(body)?body:body.items).map(x=>({...x,kind})),next:Array.isArray(body)?r.headers.get('x-tangerine-next-cursor'):body.next_cursor};
    }));
    setRows(old=>append?[...old,...groups.flatMap(g=>g.items)]:groups.flatMap(g=>g.items));setCursors(Object.fromEntries(groups.map(g=>[g.kind,g.next])));
  }catch{setError('Saved record choices are unavailable. Retry; your selection is retained.');}finally{setLoading(false);}}
  useEffect(()=>{load();},[]);
  const selected=ids.split(/[,\s]+/).filter(Boolean);
  function toggle(id,checked){onChange((checked?[...new Set([...selected,id])]:selected.filter(x=>x!==id)).join('\n'));}
  return <section aria-label="Saved records for cleanup"><h2>Choose saved records</h2><p>Select an answer or preparation, then preview its exact dependencies. Selection alone deletes nothing.</p>
    {loading&&<p role="status">Loading saved records…</p>}{error&&<p role="alert">{error}</p>}<RefreshButton onClick={()=>load()}>Refresh record choices</RefreshButton>
    <div className="record-picker">{rows.map(item=><label key={item.kind+'/'+item.id}><input type="checkbox" disabled={busy} checked={selected.includes(item.id)} aria-label={'Select '+item.kind+' '+item.id} onChange={e=>toggle(item.id,e.target.checked)}/><span>{recordTitle(item)}<small>{item.kind==='attempts'?recordState(item.state):'Preparation'} · {recordDate(item.started_at||item.created_at)}</small><small>{item.id}</small></span></label>)}{!loading&&!error&&!rows.length&&<p>No saved records. <a href="/prepare">Prepare an exercise</a> to begin.</p>}</div>
    {Object.values(cursors).some(Boolean)&&<button type="button" className="secondary" disabled={busy||loading} onClick={()=>load(true)}>Load more records</button>}
  </section>;
}
