'use client';
import RefreshButton from '../RefreshButton.js';
import {clientFetch as fetch} from '../clientRequest.js';
import {requestError,userError} from '../requestError.js';
import {useEffect,useRef,useState} from 'react';

// Selection and foreground continuation only; the server owns all judgments.
export default function ReconsiderSelected({review}){
 const [answers,setAnswers]=useState([]),[selected,setSelected]=useState([]),[cursor,setCursor]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false),[outcomes,setOutcomes]=useState([]);
 const pending=useRef(null);
 async function load(after=''){
  setError('');try{const response=await fetch('/api/v1/attempts?limit=100&case_version_id='+encodeURIComponent(review.case_version_id)+(after?'&cursor='+encodeURIComponent(after):''),{cache:'no-store'});if(!response.ok)throw userError('Saved answers are unavailable. Refresh when the service is ready.');const rows=await response.json();setAnswers(old=>[...(after?old:[]),...rows.filter(row=>row.result_id)]);setCursor(response.headers.get('X-Tangerine-Next-Cursor')||'')}catch(e){setError(requestError(e))}
 }
 useEffect(()=>{setSelected([]);setOutcomes([]);pending.current=null;load()},[review.id]);
 async function apply(){
  setBusy(true);setError('');try{
   const body=JSON.stringify({dispute_id:review.id,attempt_ids:[...selected].sort(),unit_correspondence_id:review.unit_correspondence_id});
   if(pending.current?.body!==body)pending.current={body,key:crypto.randomUUID()};
   const response=await fetch('/api/v1/reviews/'+review.id+':reconsider',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':pending.current.key},body,signal:AbortSignal.timeout(310000)});const value=await response.json();if(value.reviews)setOutcomes(value.reviews);if(!response.ok)throw userError('Selected reconsideration stopped. Saved results and completed work are retained. Retry to continue the same selection.');pending.current=null;
  }catch(e){setError(requestError(e))}finally{setBusy(false)}
 }
 return <section aria-label="Selected answer reconsideration"><h3>Use this corrected key for saved answers</h3><p>Choose the answers to reconsider. Other saved answers keep their original results.</p>
  {error&&<p role="alert">{error}</p>}{answers.map(answer=><label key={answer.id}><input type="checkbox" disabled={busy} checked={selected.includes(answer.id)} onChange={e=>setSelected(old=>e.target.checked?[...old,answer.id]:old.filter(id=>id!==answer.id))}/>Answer from {answer.started_at}</label>)}
  <RefreshButton onClick={()=>load()}>Refresh saved answers</RefreshButton>{cursor&&<button disabled={busy} onClick={()=>load(cursor)}>Load more saved answers</button>}
  <button disabled={busy||selected.length===0} onClick={apply}>Reconsider selected answers</button>
  {outcomes.map(row=><p key={row.id}>{row.status} · <a href={'/reviews?attempt='+row.attempt_id}>Open answer and result history</a></p>)}
 </section>;
}
