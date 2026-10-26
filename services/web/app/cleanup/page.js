'use client';
import RecordPicker from './RecordPicker';
import useCleanup from './useCleanup';
import {cleanupStatus,labCleanupStatus} from './labels';

export default function Cleanup() {
  const {ids,plan,error,pending,confirmed,scope,select,confirm,preview,apply}=useCleanup();
  const applying=pending==='apply';
  return <main id="main-content"><section className="intro"><h1>Cleanup and deletion</h1><p>Preview exact affected records before applying. Shared audio stays while another exercise needs it. External backup copies remain under your control.</p></section>
    <section className="card">
      <RecordPicker ids={ids} onChange={select} busy={applying}/>
      <details><summary>Selected full IDs or manual entry</summary><label>Subject IDs (comma or space separated)<textarea aria-label="Deletion subjects" value={ids} disabled={applying} onChange={event=>select(event.target.value)}/></label></details>
      <div className="actions"><button disabled={!!pending||!ids.trim()} onClick={()=>preview()}>Preview deletion</button><button className="secondary" disabled={!!pending} onClick={()=>preview(true)}>Preview old unlinked media</button></div>
      {pending&&<p role="status">{applying?'Applying the confirmed preview…':'Preparing the selected preview…'}</p>}
      {error&&<p className="error" role="alert">{error}</p>}
      {plan&&<>
        <h2>Deletion preview</h2><p>{scope}</p><p role="status">{cleanupStatus(plan.state)} · {plan.documents.length} documents · {plan.assets.length} private objects</p>
        {plan.blocked.length>0&&<p role="alert">Some selected records are unavailable or still in use. Choose saved records by name or check the full IDs, then refresh the preview. Other exercises remain available.</p>}
        <details><summary>Affected identifiers</summary><pre>{JSON.stringify({documents:plan.documents,assets:plan.assets,heads:plan.heads,source:plan.source,blocked:plan.blocked},null,2)}</pre></details>
        <p>{labCleanupStatus(plan.lab_cleanup)}. For external copies, use the explicit Lab cleanup command in <a href="/recovery">Recovery</a>; local erasure alone does not erase external copies.</p>
        {plan.state==='preview'&&<><label><input type="checkbox" className="check" aria-label="Confirm deletion" checked={confirmed} disabled={applying} onChange={event=>confirm(event.target.checked)}/> Delete the records shown in this preview.</label><button disabled={!!pending||!confirmed||plan.blocked.length>0} onClick={apply}>Apply deletion</button></>}
      </>}
    </section>
  </main>;
}
