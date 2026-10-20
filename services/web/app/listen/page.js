'use client';
import {useEffect,useRef,useState} from 'react';
export default function Listen(){
 const [attempt,setAttempt]=useState(null),[answer,setAnswer]=useState(''),[language,setLanguage]=useState('en'),[error,setError]=useState(''),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false),[audioRevision,setAudioRevision]=useState(0);
 const revision=useRef('"0"'),audioHash=useRef(''),pending=useRef(null),sequence=useRef(0),page=useRef(''),dirty=useRef(false),attemptID=useRef('');
 async function load(preserve=false){
  const response=await fetch('/api/v1/attempts/'+attemptID.current,{cache:'no-store'});if(!response.ok)throw Error('Saved attempt is unavailable. Your text is retained. Refresh to retry.');
  const value=await response.json();revision.current=response.headers.get('etag');audioHash.current=response.headers.get('x-tangerine-audio-sha256');setAttempt(value);
  if(!preserve||!dirty.current){setAnswer(value.answer_text);setLanguage(value.requested_language);dirty.current=false;}
  return value;
 }
 useEffect(()=>{page.current=crypto.randomUUID();let active=true;
  async function open(){setBusy(true);try{
   const q=new URLSearchParams(window.location.search);attemptID.current=q.get('attempt')||'';
   if(!attemptID.current){const id=q.get('case'),sha=q.get('sha');if(!id||!sha)throw Error('Select a playable exercise from the Library.');
    const storageKey='tangerine-start:'+id;let key=sessionStorage.getItem(storageKey);if(!key){key=crypto.randomUUID();sessionStorage.setItem(storageKey,key);}
    const response=await fetch('/api/v1/attempts',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify({case_version_id:id,case_sha256:sha,requested_language:'en'})});
    if(!response.ok){const failure=await response.json();throw Error(failure.code==='CAPABILITY_UNQUALIFIED'?'Select an available included, free or local evaluator model in Settings before starting an attempt.':response.status===409?'This exercise is unavailable for a new attempt. Return to the Library.':'The attempt could not be started. Refresh to retry.');}
    const started=await response.json();attemptID.current=started.attempt_id;sessionStorage.removeItem(storageKey);history.replaceState(null,'','/listen?attempt='+attemptID.current);
   }
   if(active)await load();
  }catch(e){if(active)setError(e.message)}finally{if(active)setBusy(false)}}open();return()=>{active=false};
 },[]);
 async function refresh(){setBusy(true);setError('');try{await load(true);setAudioRevision(n=>n+1);setNotice(dirty.current?'Saved state refreshed. Your unsaved text is retained.':'Saved state refreshed.');}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function write(submit){if(Array.from(answer).length>20000){setError('Answers can contain up to 20,000 characters. Your text is retained.');return;}
  dirty.current=true;setBusy(true);setError('');setNotice('');const body=JSON.stringify({answer_text:answer,requested_language:language}),action=submit?':submit':'/answer';
  const signature=action+'|'+revision.current+'|'+body;if(pending.current?.signature!==signature)pending.current={signature,key:crypto.randomUUID()};
  try{const response=await fetch('/api/v1/attempts/'+attemptID.current+action,{method:submit?'POST':'PUT',headers:{'Content-Type':'application/json','If-Match':revision.current,'Idempotency-Key':pending.current.key},body,signal:AbortSignal.timeout(270000)});
   if(!response.ok)throw Error(response.status===412?'The saved draft changed. Your text is retained. Refresh saved state, then save again.':response.status===409?'This answer is already submitted or conflicts with a saved request. Your text is retained. Refresh saved state.':'Your answer could not be saved. Your text is retained. Retry the same action.');
   dirty.current=false;pending.current=null;await load();setNotice(submit?'Answer submitted and saved.':'Draft saved.');
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 function playback(kind,event){if(!attempt||!audioHash.current)return;const value={schema_version:'2.0.0',attempt_id:attemptID.current,audio_sha256:audioHash.current,kind,client_sequence:sequence.current++,page_instance_id:page.current,position_sample:Math.min(Math.round(event.currentTarget.currentTime*24000),attempt.case.duration_ms*24),client_time_ms:String(Date.now())};
  fetch('/api/v1/attempts/'+attemptID.current+'/playback',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':crypto.randomUUID()},body:JSON.stringify(value)}).catch(()=>{});
 }
 const submitted=attempt?.submitted_at!=null;
 return <main><header><a className="brand" href="/">Tangerine</a><a href="/attempts">Saved attempts</a><a href="/settings">Settings</a></header><section className="intro"><h1>Listen and respond</h1><p>Describe the mistakes you hear and offer corrections. Reasons are optional. You can answer in English or Russian.</p></section><section className="card">
 {error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status">{notice}</p>}
 <button className="secondary" onClick={refresh} disabled={busy||!attemptID.current}>Refresh saved state</button>
 {attempt&&<><h2>{attempt.case.title}</h2><p>{attempt.case.public_context}</p><p>Identify mistakes{attempt.task_components.classification?', name their categories':''}{attempt.task_components.correction?' and offer corrections':''}. Explanations are optional.</p>
 <audio key={audioRevision} controls preload="metadata" aria-label="Exercise audio" src={attempt.audio_path+'?playback_revision='+audioRevision} onPlay={e=>playback('play',e)} onPause={e=>playback('pause',e)} onSeeked={e=>playback('seek',e)} onEnded={e=>playback('ended',e)} onError={()=>setError('Saved audio is temporarily unavailable. Your answer is retained. Refresh saved state to retry playback.')}/>
 <label>Response language<select aria-label="Response language" disabled={busy||submitted} value={language} onChange={e=>{setLanguage(e.target.value);dirty.current=true}}><option value="en">English</option><option value="ru">Russian</option></select></label>
 <label>Your answer<textarea aria-label="Your answer" rows={10} disabled={busy||submitted} value={answer} onChange={e=>{setAnswer(e.target.value);dirty.current=true;setNotice('')}}/></label><p>{Array.from(answer).length.toLocaleString('en-US')} / 20,000 characters · {attempt.state}</p>
 {submitted?<p>Answer submitted and saved. <a href="/attempts">Open saved attempts</a></p>:<div className="actions"><button onClick={()=>write(false)} disabled={busy}>Save draft</button><button onClick={()=>write(true)} disabled={busy}>Submit answer</button></div>}</>}
 </section><footer>Stored audio · Exact saved answers · Optional explanations</footer></main>
}
