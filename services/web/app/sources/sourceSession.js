import {requestError} from '../requestError.js';

const emptyImport=()=>({run:null,report:null,records:[],cursor:'',importId:'',history:null,historyCursor:''});
const emptySelection=()=>({...emptyImport(),release:null,version:'',origin:'',scope:'partial_export',binding:'native',files:[],notice:'',permissionIds:[],program:'',fieldMap:'',uses:['local_analysis']});

// Own saved selection and asynchronous reads together. A superseded response is
// ignored, rather than mixing a previous release/report into the current view.
export function createSourceSession({request,publish,remember=()=>{},source='SPEECHOCEAN762'}) {
  let generation=0;
  let selection=null;
  let currentImport='';
  let selectedSource=source;
  const save=()=>{
    if (selection) remember({source:selection.source,releaseId:selection.release.id,binding:selection.binding,importId:currentImport||undefined});
  };
  const error=(value,ticket)=>{
    if (ticket===generation) publish({error:requestError(value)});
  };
  async function readImport(id,ticket) {
    const different=currentImport!==id;
    currentImport=id;
    publish(different?{...emptyImport(),importId:id}:{importId:id});
    save();
    let progress;
    try {
      ({body:progress}=await request('imports/'+id+'/progress'));
      if (ticket!==generation) return null;
      publish({run:progress,report:progress.report,binding:progress.format_binding_id,permissionIds:progress.permission_grant_ids,error:''});
      if (selection) selection={...selection,binding:progress.format_binding_id};
      save();
    } catch (failure) { error(failure,ticket); return null; }
    try {
      const {body}=await request('imports/'+id+'/records?limit=20');
      if (ticket!==generation) return null;
      publish({records:body.items,cursor:body.next_cursor,error:''});
    } catch (failure) { error(failure,ticket); }
    return ticket===generation?progress:null;
  }
  async function openRelease(item,id,saved={}) {
      const ticket=++generation;
      try {
        const {body:release}=await request('source-releases/'+id);
        if (ticket!==generation) return null;
        const binding=saved.binding||release.format_profile_id||'native';
        selectedSource=item.source_id; selection={source:item.source_id,release,binding}; currentImport='';
        publish({...emptySelection(),source:item.source_id,release,version:release.source_version,origin:release.origin_uri,scope:release.scope_kind||'partial_export',binding,permissionIds:release.permission_grant_ids,error:''});
        const importId=saved.importId||item.release_import_report_ids?.[release.id]?.at(-1);
        if (importId) return readImport(importId,ticket);
        save(); return release;
      } catch (failure) { error(failure,ticket); return null; }
  }
  return {
    reset(source) { generation++; selectedSource=source; selection=null; currentImport=''; remember(null); publish({...emptySelection(),source,error:''}); },
    adopt(source,release,binding='native') {
      generation++; selectedSource=source; selection={source,release,binding}; currentImport='';
      publish({...emptySelection(),source,release,version:release.source_version,origin:release.origin_uri,scope:release.scope_kind||'partial_export',binding,permissionIds:release.permission_grant_ids,error:''});
      save();
    },
    async restore(saved) {
      if (saved.releaseId) return openRelease({source_id:saved.source},saved.releaseId,saved);
      // Existing small cached selections migrate to the same compact locator.
      this.adopt(saved.source,saved.release,saved.binding||'native');
      if (saved.importId) return this.loadImport(saved.importId);
    },
    open(item,id) { return openRelease(item,id); },
    loadImport(id) { return readImport(id,++generation); },
    changeBinding(binding) {
      generation++; currentImport='';
      if (selection) selection={...selection,binding};
      publish({...emptyImport(),binding,error:''}); save();
    },
    addFiles(source,items) {
      if (source!==selectedSource) return;
      publish({files:old=>{
        const files=new Map(old.map(item=>[item.relative_path,item]));
        for (const item of items) files.set(item.relative_path,item);
        return [...files.values()];
      }});
    },
    async moreRows(id,cursor,rows) {
      const ticket=generation;
      try {
        const {body}=await request('imports/'+id+'/records?limit=20&cursor='+encodeURIComponent(cursor));
        if (ticket===generation&&id===currentImport) publish({records:[...rows,...body.items],cursor:body.next_cursor,error:''});
      } catch (failure) { error(failure,ticket); }
    },
    async history(id,cursor='',items=[]) {
      const ticket=generation;
      try {
        const {body}=await request('imports/'+id+'/issues'+(cursor?'?cursor='+encodeURIComponent(cursor):''));
        if (ticket===generation&&id===currentImport) publish({history:[...items,...body.items],historyCursor:body.next_cursor,error:''});
      } catch (failure) { error(failure,ticket); }
    },
  };
}

export function sourceIssueMessage(code) {
  if (code==='import_failed') return 'An earlier import was interrupted. Saved rows were retained; refresh its current progress before resuming.';
  if (code==='parse_failed') return 'A source file could not be read in its documented format. Check that file or use raw-only import.';
  if (code==='mapping_failed') return 'A record could not be converted with the selected source dictionary. Review the documented binding; the original record is retained.';
  return 'This source record needs attention. Review its retained original data and documented source format.';
}

const statusLabels=new Map(Object.entries({
    not_acquired:'No source release saved',
    ready_to_import:'Saved and ready to import',
    incomplete:'Saved release is incomplete',
    format_unbound:'Retained; source conversion is unavailable',
    complete:'Complete source release retained',
}));
export function sourceStatusLabel(status) {
  return statusLabels.get(status) || 'Saved source status is unavailable. Refresh sources to continue.';
}

export function sourceRowData({issues,...record}) {
  return record;
}
