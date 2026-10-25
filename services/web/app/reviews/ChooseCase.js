'use client';
import {useEffect,useState} from 'react';
import {recordDate} from '../savedRecord';

export default function ChooseCase(){
  const [items,setItems]=useState(null),[error,setError]=useState('');
  const available=(items||[]).filter(x=>x.case_sha256);
  async function refresh(){setError('');try{const r=await fetch('/api/v1/library',{cache:'no-store'});if(!r.ok)throw Error();setItems(await r.json());}catch{setError('Exercises are unavailable. Your saved reviews are retained. Retry when the local service is ready.');}}
  useEffect(()=>{refresh();},[]);
  return <div className="review-case-picker"><h2>Choose an exercise to review</h2><p>Open a saved exercise to inspect its review history or request a new LLM review. Choosing an exercise does not run a review.</p>
    {error?<div className="error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={refresh}>Retry exercises</button></div>:items===null?<p role="status">Loading saved exercises…</p>:!available.length?<div className="empty"><h3>No exercises yet</h3><p>Prepare a conversation first. You can review it after generation.</p><a href="/prepare">Prepare an exercise</a></div>:<ul className="review-case-list">{available.map(item=><li key={item.id}><a href={'/reviews?case='+item.id}>{item.title}</a><p className="field-help">{recordDate(item.created_at)} · {item.availability.replaceAll('_',' ')}</p><details><summary>Exercise identity</summary><p>{item.id}</p></details></li>)}</ul>}
    <p className="field-help">To reconsider a specific answer or dispute a result, open it from <a href="/attempts">Saved attempts</a>.</p>
  </div>;
}
