'use client';
import {useEffect,useRef,useState} from 'react';
import RefreshButton from '../RefreshButton.js';
import {createCorrectionSession,emptyCorrections} from './correctionSession.js';

function saveDownload(body,partition){
 const url=URL.createObjectURL(new Blob([JSON.stringify(body,null,2)+'\n'],{type:'application/json'}));
 const link=document.createElement('a');link.href=url;link.download='jfleg-'+partition+'-correction-references.json';link.click();URL.revokeObjectURL(url);
}

// Browsing native alternatives never creates an exercise or starts an AI run.
export default function CorrectionExamples({importId,request}) {
 const [view,setView]=useState(emptyCorrections),session=useRef(null);
 const {items,cursor,loading,downloading,readError,downloadError,notice}=view,busy=loading||downloading;
 useEffect(()=>{
  setView(emptyCorrections());
  const current=createCorrectionSession({importId,request,publish:value=>setView(old=>({...old,...value})),saveDownload});session.current=current;current.load();
  return ()=>current.dispose();
 },[importId,request]);
 return <section aria-label="Written correction examples">
  <h3>Written correction examples</h3>
  <p>Original JFLEG text and all available supplied correction references. The complete release supplies four per sentence; a partial import shows only the references it contains. References are alternatives, not simultaneous mistakes or a complete list of valid corrections.</p>
  <div className="row"><RefreshButton onClick={()=>session.current.load()}>Refresh correction examples</RefreshButton><button className="secondary" disabled={busy} onClick={()=>session.current.download('dev')}>Download development dataset</button><button className="secondary" disabled={busy} onClick={()=>session.current.download('test')}>Download test dataset</button></div>
  <p>For local, noncommercial reference evaluation under JFLEG’s CC BY-NC-SA 4.0 terms. No generation, model call or learner score is produced by a download.</p>
  {loading&&<p role="status">Reading saved correction examples…</p>}{downloading&&<p role="status">Preparing the saved reference dataset…</p>}{readError&&<p role="alert">{readError}</p>}{downloadError&&<p role="alert">{downloadError}</p>}{notice&&<p role="status">{notice}</p>}
  {!loading&&!readError&&items.length===0&&<p>No converted written corrections are saved yet. Import or resume the selected release above.</p>}
  {items.map(item=><details key={item.id}><summary>{item.source_partition==='dev'?'Development':'Test'} sentence {Number(item.original.line_index)+1} · {item.references.length} supplied {item.references.length===1?'reference':'references'}</summary>
   <h4>Original text</h4><p style={{whiteSpace:'pre-wrap'}}>{item.original.text}</p>
   <ol>{item.references.map(reference=><li key={reference.reference_id}><h4>Reference {Number(reference.reference_id.slice(3))+1}</h4><p style={{whiteSpace:'pre-wrap'}}>{reference.text}</p></li>)}</ol>
   {item.spellchecked&&<details><summary>Separate source spellcheck</summary><p style={{whiteSpace:'pre-wrap'}}>{item.spellchecked.text}</p><p>Source tool output; this does not replace the original input.</p></details>}
   <details><summary>Derived text differences and provenance</summary><p>Coarse character differences are derived summaries. Linguistic alignment and project categories have not been assigned.</p><pre>{JSON.stringify({group_id:item.group_id,original:item.original,derived_differences:item.derived_differences},null,2)}</pre></details>
  </details>)}
  {cursor&&<button disabled={busy} onClick={()=>session.current.load(true)}>More correction examples</button>}
 </section>;
}
