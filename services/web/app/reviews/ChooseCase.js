'use client';
import RefreshButton from '../RefreshButton.js';
import useSavedList from '../useSavedList.js';
import {recordDate,recordTitle} from '../savedRecord';
import RecordIdentity from '../RecordIdentity';

export default function ChooseCase(){
  const {items,error,loading,loaded,refresh}=useSavedList('/api/v1/library',{unavailable:'Exercises are unavailable. Your saved reviews are retained. Retry when the local service is ready.'});
  const available=(items||[]).filter(x=>x.case_sha256);
  return <div className="review-case-picker"><h2>Choose an exercise to review</h2><RefreshButton onClick={()=>refresh()}>Refresh exercises</RefreshButton><p>Open a saved exercise to inspect its review history or request a new LLM review. Choosing an exercise does not run a review.</p>
    {error&&<div className="error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={()=>refresh()}>Retry exercises</button></div>}
    {loading&&<p role="status">Loading saved exercises…</p>}
    {loaded&&!loading&&!error&&!available.length?<div className="empty"><h3>No exercises yet</h3><p>Prepare a conversation first. You can review it after generation.</p><a href="/prepare">Prepare an exercise</a></div>:<ul className="review-case-list">{available.map(item=><li key={item.id}><a href={'/reviews?case='+item.id}>{recordTitle(item)}</a><p className="field-help">{recordDate(item.created_at)} · {item.availability?.replaceAll('_',' ') || 'Status unavailable'}</p><RecordIdentity item={item} items={available} dateField="created_at"/><details><summary>Exercise identity</summary><p>{item.id}</p></details></li>)}</ul>}
    <p className="field-help">To reconsider a specific answer or dispute a result, open it from <a href="/attempts">Saved attempts</a>.</p>
  </div>;
}
