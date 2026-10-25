'use client';
import RecordIdentity from '../RecordIdentity';
import RefreshButton from '../RefreshButton.js';
import useSavedList from '../useSavedList.js';
import {recordTitle,recordDate,recordState} from '../savedRecord';
export default function Attempts(){
 const {items,cursor,error,loading:busy,loaded,refresh:load}=useSavedList('/api/v1/attempts',{limit:50,unavailable:'Saved attempts are unavailable. Refresh to retry.'});
 return <main id="main-content"><section className="intro"><h1>Saved attempts</h1><p>Reopen your saved draft or submitted answer.</p></section><section className="card"><RefreshButton onClick={()=>load()}>Refresh</RefreshButton>{busy&&<p role="status">Loading saved attempts…</p>}{error&&<p className="error" role="alert">{error}</p>}{loaded&&items.length===0&&!busy&&!error?<p>No attempts yet. <a href="/">Choose an exercise from the Library.</a></p>:items.map(item=><article key={item.id}><h2>{recordTitle(item)}</h2><p>{recordState(item.state)} · <time dateTime={item.started_at}>{recordDate(item.started_at)}</time></p><RecordIdentity item={item} items={items} dateField="started_at"/>{item.answer_excerpt&&<p className="answer-excerpt">{item.answer_excerpt}</p>}<a href={'/listen?attempt='+item.id}>Open saved answer</a><details><summary>Record details</summary><p>Attempt: {item.id}</p><p>Original date: {item.started_at||'unavailable'}</p><a href={'/cleanup?subject='+item.id}>Preview deletion</a></details></article>)}{cursor&&<button onClick={()=>load(true)} disabled={busy}>Load more</button>}</section></main>
}
