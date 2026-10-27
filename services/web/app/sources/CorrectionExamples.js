'use client';
import {useEffect,useState} from 'react';
import RefreshButton from '../RefreshButton.js';
import {requestError} from '../requestError.js';

// Browsing native alternatives never creates an exercise or starts an AI run.
export default function CorrectionExamples({importId,request}) {
 const [items,setItems]=useState([]),[cursor,setCursor]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 async function load(more=false){
  setBusy(true);setError('');
  try {const {body}=await request('imports/'+importId+'/corrections?limit=20'+(more?'&cursor='+encodeURIComponent(cursor):''));setItems(old=>more?[...old,...body.items]:body.items);setCursor(body.next_cursor||'');}
  catch(e){setError(requestError(e));}finally{setBusy(false);}
 }
 useEffect(()=>{load();},[importId]);
 async function download(partition){
  setBusy(true);setError('');
  try {
   const {body}=await request('imports/'+importId+'/corrections?format=dataset&partition='+partition);
   const url=URL.createObjectURL(new Blob([JSON.stringify(body,null,2)+'\n'],{type:'application/json'}));
   const link=document.createElement('a');link.href=url;link.download='jfleg-'+partition+'-correction-references.json';link.click();URL.revokeObjectURL(url);
   setNotice(body.examples.length+' '+(partition==='dev'?'development':'test')+' examples downloaded with their supplied references.');
  }catch(e){setError(requestError(e));}finally{setBusy(false);}
 }
 return <section aria-label="Written correction examples">
  <h3>Written correction examples</h3>
  <p>Original JFLEG text and its four supplied correction references. References are alternatives. They are not four simultaneous mistakes or a complete list of valid corrections.</p>
  <div className="row"><RefreshButton onClick={()=>load()}>Refresh correction examples</RefreshButton><button className="secondary" disabled={busy} onClick={()=>download('dev')}>Download development dataset</button><button className="secondary" disabled={busy} onClick={()=>download('test')}>Download test dataset</button></div>
  <p>For local, noncommercial reference evaluation under JFLEG’s CC BY-NC-SA 4.0 terms. No generation, model call or learner score is produced by a download.</p>
  {busy&&<p role="status">Reading saved correction examples…</p>}{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}
  {!busy&&!error&&items.length===0&&<p>No converted written corrections are saved yet. Import or resume the selected release above.</p>}
  {items.map(item=><details key={item.id}><summary>{item.source_partition==='dev'?'Development':'Test'} sentence {Number(item.original.line_index)+1} · {item.references.length} supplied references</summary>
   <h4>Original text</h4><p style={{whiteSpace:'pre-wrap'}}>{item.original.text}</p>
   <ol>{item.references.map(reference=><li key={reference.reference_id}><h4>Reference {Number(reference.reference_id.slice(3))+1}</h4><p style={{whiteSpace:'pre-wrap'}}>{reference.text}</p></li>)}</ol>
   {item.spellchecked&&<details><summary>Separate source spellcheck</summary><p style={{whiteSpace:'pre-wrap'}}>{item.spellchecked.text}</p><p>Source tool output; this does not replace the original input.</p></details>}
   <details><summary>Derived text differences and provenance</summary><p>Coarse character differences are derived summaries. Linguistic alignment and project categories have not been assigned.</p><pre>{JSON.stringify({group_id:item.group_id,original:item.original,derived_differences:item.derived_differences},null,2)}</pre></details>
  </details>)}
  {cursor&&<button disabled={busy} onClick={()=>load(true)}>More correction examples</button>}
 </section>;
}
