'use client';
import {useEffect,useRef,useState} from 'react';
import Results from '../listen/Results';
import ReconsiderSelected from './ReconsiderSelected';
import Measurements from './Measurements';
import ChooseCase from './ChooseCase';

export default function Reviews(){
 const [scope,setScope]=useState(null),[rows,setRows]=useState([]),[selected,setSelected]=useState(null),[statement,setStatement]=useState(''),[result,setResult]=useState(null),[current,setCurrent]=useState(null),[caseItem,setCaseItem]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[cursor,setCursor]=useState('');
 const pending=useRef(null);
 async function request(path,options={}){const response=await fetch('/api/v1/'+path,{cache:'no-store',signal:AbortSignal.timeout(310000),...options});const body=await response.json();if(!response.ok){if(body.id){setSelected(body);throw Error('Review did not complete. Saved findings and the original answer/result are retained. Retry this review after the service is available.')}throw Error(response.status===409?'The selected version changed or work is already running. Refresh saved state.':'Review is unavailable. Your statement and saved data are retained.')}return {body,response};}
 async function refresh(value=scope,more=''){
  if(!value?.case&&!value?.attempt)return;setError('');try{
   const filter=value.attempt?'attempt_id='+value.attempt:'case_version_id='+value.case;
   const {body,response}=await request('reviews?'+filter+(more?'&cursor='+more:''));setRows(old=>more?[...old,...body]:body);setCursor(response.headers.get('X-Tangerine-Next-Cursor')||'');
   if(value.attempt){const {body:latest}=await request('attempts/'+value.attempt+'/results');setCurrent(latest);if(!more)setResult(latest)}else{const {body:items}=await request('library');setCaseItem(items.find(item=>item.id===value.case)||null)}
  }catch(e){setError(e.message)}
 }
 useEffect(()=>{const q=new URLSearchParams(window.location.search);const value={case:q.get('case'),attempt:q.get('attempt')};setScope(value);refresh(value)},[]);
 async function run(review){
  const signature='run|'+review.id+'|'+review.revision;if(pending.current?.signature!==signature)pending.current={signature,key:crypto.randomUUID()};
  const {body}=await request('reviews/'+review.id+':run',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':pending.current.key,'If-Match':String(review.revision)},body:'{}'});pending.current=null;setSelected(body);await refresh();
 }
 async function create(purpose){setBusy(true);setError('');try{
  const input={schema_version:'2.0.0',purpose,case_version_id:scope.attempt?current.score.case_version_id:scope.case};
  if(scope.attempt){input.attempt_id=scope.attempt;input.result_id=current.result_id;if(purpose==='dispute')input.statement=statement}else input.audio_sha256=caseItem.audio_sha256;
  const body=JSON.stringify(input),signature='create|'+body;if(pending.current?.signature!==signature)pending.current={signature,key:crypto.randomUUID()};
  const {body:review}=await request('reviews',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':pending.current.key},body});pending.current=null;setSelected(review);await run(review);
 }catch(e){setError(e.message)}finally{setBusy(false)}}
 async function select(id){setBusy(true);setError('');try{const {body}=await request('reviews/'+id);setSelected(body)}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function retry(){setBusy(true);setError('');try{const {body}=await request('reviews/'+selected.id);await run(body)}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function resultVersion(id){setBusy(true);setError('');try{const {body}=await request('attempts/'+scope.attempt+'/results?result_id='+id);setResult(body)}catch(e){setError(e.message)}finally{setBusy(false)}}
 return <main id="main-content">
  <section className="intro"><h1>Optional LLM review</h1><p>Ask the configured LLM to review a case or reconsider an answer. Your original recording, answer and result stay available.</p></section>
  <section className="card">
   {scope&&!scope.case&&!scope.attempt&&<ChooseCase/>}
   {error&&<p role="alert">{error}</p>}
   {(scope?.case||scope?.attempt)&&<>
   <button disabled={busy} onClick={()=>refresh()}>Refresh saved state</button>
   {scope?.attempt&&current?.score&&<><button disabled={busy} onClick={()=>create('answer_reconsideration')}>Reconsider answer</button><label>Dispute statement<textarea aria-label="Dispute statement" rows={5} value={statement} maxLength={20000} onChange={e=>setStatement(e.target.value)}/></label><button disabled={busy||!statement.trim()} onClick={()=>create('dispute')}>Submit dispute</button></>}
   {scope?.case&&caseItem&&<button disabled={busy} onClick={()=>create('case_review')}>Review case</button>}
   {selected&&<section aria-label="Review findings"><h2>Saved review</h2><p>{selected.status.replaceAll('_',' ')}{selected.resolution?' · '+selected.resolution.replaceAll('_',' '):''}</p><p>{selected.input_modality==='text'?'Text review; the LLM did not hear the recording.':'Review used text and saved speech observations; this is not direct hearing.'}</p>
    {selected.failure_code==='SOURCE_USE_RESTRICTED'&&<p>Source terms restrict processing of this case.</p>}
    {selected.statement&&<p>Statement: {selected.statement}</p>}
    {selected.findings&&<><p>{selected.findings.reason}</p>{selected.findings.unit_judgments.map(j=><article key={j.unit_id}><p>{j.judgment.replaceAll('_',' ')} · {j.confirmation}</p><p>{j.reason}</p></article>)}{selected.findings.issues.map((text,i)=><p key={i}>{text}</p>)}</>}
    {selected.resolution==='insufficient_evidence'&&<p>The original result is retained. The available evidence does not establish a change.</p>}
    {selected.status!=='complete'&&<button disabled={busy} onClick={retry}>Retry or resume saved review</button>}
    {selected.new_case_version_id&&<ReconsiderSelected review={selected}/>}
    {selected.new_case_version_id&&<p>A corrected key version uses the same recording. <a href="/">Open the Library</a></p>}
   </section>}
   <h2>Review history</h2>{rows.map(row=><p key={row.id}><button disabled={busy} onClick={()=>select(row.id)}>{row.purpose.replaceAll('_',' ')} · {row.status} · {row.created_at}</button></p>)}{cursor&&<button disabled={busy} onClick={()=>refresh(scope,cursor)}>More reviews</button>}
   </>}
  </section>
  {((scope?.case&&caseItem)||(scope?.attempt&&current?.score))&&<Measurements key={scope.attempt?current.score.case_version_id:scope.case} caseID={scope.attempt?current.score.case_version_id:scope.case} attemptID={scope.attempt} audioSHA={scope.attempt?null:caseItem.audio_sha256}/>}
  {scope?.attempt&&current&&<section className="card"><h2>Result history</h2><button disabled={busy} onClick={()=>resultVersion(current.result_id)}>Current result</button>{current.result_revision_ids?.map((id,i)=><button key={id} disabled={busy} onClick={()=>resultVersion(id)}>{i===0?'Original result':'Earlier result '+(i+1)}</button>)}<Results results={result} busy={true} retry={()=>{}}/><a href={'/listen?attempt='+scope.attempt}>Return to listening and results</a></section>}
 </main>;
}
