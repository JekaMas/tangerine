'use client';
import {useEffect,useState} from 'react';
export default function Attempts(){
 const [items,setItems]=useState([]),[cursor,setCursor]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function load(append=false){setBusy(true);setError('');try{const q=new URLSearchParams({limit:'50'});if(append&&cursor)q.set('cursor',cursor);const response=await fetch('/api/v1/attempts?'+q,{cache:'no-store'});if(!response.ok)throw Error('Saved attempts are unavailable. Refresh to retry.');const rows=await response.json();setItems(old=>append?[...old,...rows]:rows);setCursor(response.headers.get('x-tangerine-next-cursor')||'');}catch(e){setError(e.message)}finally{setBusy(false)}}
 useEffect(()=>{load()},[]);
 return <main id="main-content"><section className="intro"><h1>Saved attempts</h1><p>Reopen your saved draft or submitted answer.</p></section><section className="card"><button className="secondary" onClick={()=>load()} disabled={busy}>Refresh</button>{error&&<p className="error" role="alert">{error}</p>}{items.length===0&&!busy&&!error?<p>No attempts yet. Choose an exercise from the Library.</p>:items.map(item=><article key={item.id}><h2>Attempt {item.id.slice(0,8)}</h2><p>{item.state} · Started {item.started_at}</p><a href={'/listen?attempt='+item.id}>Open saved answer</a></article>)}{cursor&&<button onClick={()=>load(true)} disabled={busy}>Load more</button>}</section></main>
}
