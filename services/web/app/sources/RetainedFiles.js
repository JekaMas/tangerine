'use client';
import {useState,useRef,useEffect} from 'react';
import RefreshButton from '../RefreshButton.js';
import {requestError} from '../requestError.js';
// Retained members include notices, scripts and original containers that do not
// produce transcript rows. Downloading one never executes or reconverts it.
export default function RetainedFiles({releaseId,request}){
 const [files,setFiles]=useState(null),[shown,setShown]=useState(20),[kind,setKind]=useState(''),[loading,setLoading]=useState(false),[error,setError]=useState(''),ticket=useRef(0),active=useRef(true);
 useEffect(()=>{active.current=true;return()=>{active.current=false;ticket.current++}},[]);
 async function load(){const current=++ticket.current;setLoading(true);setError('');try{const {body}=await request('source-releases/'+releaseId+'/files');if(active.current&&current===ticket.current)setFiles(body)}catch(e){if(active.current&&current===ticket.current)setError(requestError(e))}finally{if(active.current&&current===ticket.current)setLoading(false)}}
 const matching=files?.filter(file=>!kind||file.component===kind||kind==='archive'&&/\.(tgz|tar|tar\.gz|zip)$/i.test(file.relative_path))||[];
 return <section className="card"><details onToggle={event=>{if(event.currentTarget.open&&files===null&&!loading)load()}}><summary>Original files, notices and containers</summary><p>Every retained member remains available in its original form. Code and source commands are inert downloads. Third-party terms remain separate from the software licence.</p><RefreshButton onClick={load}>Refresh retained files</RefreshButton>
 {loading&&<p role="status">Reading retained file locations…</p>}{error&&<p role="alert">{error}</p>}
 {files&&<><label>File type<select aria-label="File type" value={kind} onChange={event=>{setKind(event.target.value);setShown(20)}}><option value="">All retained files</option><option value="documentation">Notices and documentation</option><option value="media">Recordings</option><option value="archive">Archives and containers</option></select></label><p>{files.length} retained files · {matching.length} in this view.</p><ul>{matching.slice(0,shown).map(file=><li key={file.relative_path}><a download={file.relative_path.split('/').at(-1)} href={'/api/v1/sources/assets/'+file.asset_id+'/bytes'}>{file.relative_path}</a> · {Number(file.byte_count).toLocaleString('en-US')} bytes</li>)}</ul>{matching.length>shown&&<button className="secondary" onClick={()=>setShown(value=>value+20)}>More retained files</button>}</>}
 </details></section>;
}
