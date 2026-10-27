'use client';
import {useEffect,useRef,useState,useCallback} from 'react';
import RefreshButton from '../RefreshButton.js';
import {createExampleSession,emptyExamples} from './exampleSession.js';
import {createSourcePlayback} from './sourcePlayback.js';

const seconds=value=>{if(value==null)return null;const [a,b=1]=String(value).split('/').map(Number);return Number.isFinite(a/b)?a/b:null};
const clock=value=>value&&value.start!=null&&value.end!=null?`${seconds(value.start).toFixed(2)}–${seconds(value.end).toFixed(2)} seconds`:'Not supplied';
function Example({row}) {
 const item=row.projection.source_example,player=useRef(null),[playback,setPlayback]=useState({error:'',loading:false});
 const bind=useCallback(audio=>{player.current?.dispose();player.current=audio?createSourcePlayback(audio,{publish:setPlayback}):null},[]);
 useEffect(()=>()=>player.current?.dispose(),[]);
 const start=seconds(item.local_clock?.start),end=seconds(item.local_clock?.end);
 function replay(){void player.current?.replay({start_ms:start*1000,end_ms:end*1000})}
 const title=item.session||item.task||'Source example';
 return <details className="source-example"><summary>{title} · {item.native_id} · {item.speakers?.length?item.speakers.join(', '):'Speaker not supplied'}</summary>
  {item.text?<><h4>Source text</h4><p style={{whiteSpace:'pre-wrap',maxWidth:'75ch'}}>{item.text}</p></>:<p>No transcript is supplied for this recording.</p>}
  {item.text_origin==='source_asr_transcription'&&<p>Automatic transcript and speaker diarization from the source. These are not verified mistake annotations.</p>}
  {item.source_id==='EDACC'&&<p>Original reference transcript. Accents and natural speech variants are not mistake labels. Company ASR and filtered scoring views are retained separately.</p>}
  {item.source_id==='DIPLOMAT'&&<><p>Native pragmatic task: {item.task}. Related task views may reuse this context. No recording is supplied.</p>{item.source_selected_choice&&<><h4>Source answer choice</h4><p style={{whiteSpace:'pre-wrap',maxWidth:'75ch'}}>{item.source_selected_choice}</p><p>The label is the answer’s option index, not an error category.</p></>}</>}
  {item.source_id==='DRAL'&&<p>Original or re-enacted speech and translation pairs. Repeated fragments and release versions are related views, not independent populations.</p>}
  {item.media&&<><p>Recording interval: {clock(item.local_clock)}{item.source_id==='DRAL'&&<> · source conversation interval: {clock(item.source_clock)}</>}</p><audio ref={bind} controls preload="none" aria-label={'Original recording '+title+' '+item.native_id} src={'/api/v1/sources/assets/'+item.media.asset_id+'/bytes'}/>{start!=null&&end>start&&<button className="secondary" onClick={replay}>Play this source interval</button>}<p><a href={'/api/v1/sources/assets/'+item.media.asset_id+'/bytes'}>Open original recording</a></p></>}
  {item.media_representation==='native_recording_window'&&<p>This entry uses the native interval in the complete source recording. A separate fragment file is not supplied.</p>}
  {!item.media&&item.source_id!=='DIPLOMAT'&&<p>No recording is supplied for this entry in the selected source files. Its native metadata is retained.</p>}
  {playback.loading&&<p role="status">Restoring recording playback…</p>}
  {playback.error&&<><p role="alert">{playback.error}</p><button className="secondary" onClick={()=>void player.current?.retry()}>Retry recording</button></>}
  {item.source_terms&&<p>Source terms: {typeof item.source_terms==='string'?item.source_terms:Object.entries(item.source_terms).map(([kind,value])=>kind+': '+value).join(' · ')}</p>}
  {item.base_release_dependency&&<p>Recording retained from the compatible DRAL base release. The selected metadata version remains {item.source_version}.</p>}
  <details><summary>Native fields and provenance</summary><p>{row.member} · record {row.ordinal} · version {item.source_version}</p><pre>{JSON.stringify(item,null,2)}</pre></details>
 </details>;
}
export default function NativeExamples({importId,sourceId,request}) {
 const [view,setView]=useState(emptyExamples),[kind,setKind]=useState(''),session=useRef(null);
 const choices=sourceId==='DRAL'?[['recordings','Whole recordings'],['fragments-short','Short fragments'],['fragments-long','Long fragments']]:sourceId==='DIPLOMAT'?[['CQA_task_dataset','Conversational questions'],['PIR_first_subtask_dataset','Pragmatic target turns'],['PIR_second_subtask_dataset','Pragmatic answer choices'],['NLI_task_dataset','NLI with context'],['NLI_dataset_without_context','NLI without context']]:[];
 useEffect(()=>{setView(emptyExamples());const current=createExampleSession({importId,view:kind,request,publish:value=>setView(old=>({...old,...value}))});session.current=current;current.load();return()=>current.dispose()},[importId,kind,request]);
 return <section aria-label="Speech and dialogue examples"><h3>Speech and dialogue examples</h3><p>Saved source text, speakers, timing and original recordings where supplied. Native annotations keep their source meaning; no exercise, learner score or model call is created by browsing.</p><RefreshButton onClick={()=>session.current.load()}>Refresh source examples</RefreshButton>{choices.length>0&&<label>Example view<select aria-label="Example view" value={kind} onChange={event=>setKind(event.target.value)}><option value="">All examples</option>{choices.map(([value,title])=><option key={value} value={value}>{title}</option>)}</select></label>}
  {view.loading&&<p role="status">Reading saved source examples…</p>}{view.error&&<p role="alert">{view.error}</p>}{!view.loading&&!view.error&&view.items.length===0&&<p>No converted examples are saved yet. Import or resume the selected release above.</p>}
  {view.items.map(row=><Example key={row.member+'|'+row.table+'|'+row.ordinal} row={row}/>)}
  {view.cursor&&<button className="secondary" disabled={view.loading} onClick={()=>session.current.load(true)}>More source examples</button>}
 </section>;
}
