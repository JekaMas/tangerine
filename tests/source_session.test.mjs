import test from 'node:test';
import assert from 'node:assert/strict';
import {createSourceSession,sourceIssueMessage,sourceStatusLabel,sourceRowData} from '../services/web/app/sources/sourceSession.js';
import {createSourceRequest} from '../services/web/app/sources/sourceRequest.js';
import {createClientFetch} from '../services/web/app/clientRequest.js';
import {requestError,userError} from '../services/web/app/requestError.js';
import {createSourceCache} from '../services/web/app/sources/sourceCache.js';

// Controlled HTTP inputs exercise the real read/presentation owners. They are
// not browser input, acquired corpora, original owner dictionaries or inference.
const release=id=>({id,source_version:'v-'+id,origin_uri:'constructed://'+id,scope_kind:'partial_export',permission_grant_ids:['release-notice-'+id]});
const progress=id=>({report:{id,release_id:'r-'+id,state:'complete'},format_binding_id:'binding-'+id,permission_grant_ids:['saved-notice-'+id]});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
function fixture(request){
  const state={};const saved=[];const seen=[];
  const session=createSourceSession({request,publish:value=>{for(const [key,item] of Object.entries(value))state[key]=typeof item==='function'?item(state[key]):item;seen.push({...state});},remember:value=>saved.push(value)});
  return {state,saved,seen,session};
}
const nativeRead=async path=>({body:path.endsWith('/progress')?progress(path.split('/')[1]):{items:[{member:'native-row'}],next_cursor:'next-page'}});

test('selection_positive',async()=>{
  const calls=[];
  const f=fixture(async path=>{calls.push(path);return path.startsWith('source-releases/')?{body:release('older')}:nativeRead(path);});
  await f.session.open({source_id:'FCE-2.1',release_import_report_ids:{older:['old-import'],newer:['new-import']}},'older');
  assert.deepEqual(calls,['source-releases/older','imports/old-import/progress','imports/old-import/records?limit=20']);
  assert.equal(f.state.release.id,'older');assert.equal(f.state.report.id,'old-import');
  assert.equal(f.state.binding,'binding-old-import');assert.deepEqual(f.state.permissionIds,['saved-notice-old-import']);
  assert.deepEqual(f.saved.at(-1),{source:'FCE-2.1',releaseId:'older',binding:'binding-old-import',importId:'old-import'});
});
test('refresh_recovery_positive',async()=>{
  let failed=true;const f=fixture(path=>failed?Promise.reject(userError('Saved progress is unavailable. Refresh to continue.')):nativeRead(path));
  await f.session.loadImport('saved');assert.equal(f.state.error,'Saved progress is unavailable. Refresh to continue.');assert.equal(f.state.importId,'saved');
  failed=false;await f.session.loadImport('saved');assert.equal(f.state.error,'');assert.equal(f.state.report.id,'saved');assert.equal(f.state.cursor,'next-page');
});
test('metadata_reset_negative',async()=>{
  const f=fixture(nativeRead);f.session.adopt('FCE-2.1',release('old'),'old-binding');await f.session.loadImport('saved');
  Object.assign(f.state,{files:['old-file'],program:'old-map',fieldMap:'old-field',notice:'old-notice',history:['old-issue']});
  f.session.reset('NIR-DATA');
  assert.equal(f.state.source,'NIR-DATA');
  for(const name of ['version','origin','program','fieldMap','notice','cursor','importId','historyCursor'])assert.equal(f.state[name],'');
  for(const name of ['files','permissionIds','records'])assert.deepEqual(f.state[name],[]);
  for(const name of ['release','run','report','history'])assert.equal(f.state[name],null);
  assert.equal(f.state.scope,'partial_export');assert.equal(f.state.binding,'native');assert.deepEqual(f.state.uses,['local_analysis']);assert.equal(f.saved.at(-1),null);
});
test('binding_reset_negative',async()=>{
  const f=fixture(nativeRead);f.session.adopt('FCE-2.1',release('r'));await f.session.loadImport('prior');
  f.session.changeBinding('raw-only');assert.equal(f.state.binding,'raw-only');assert.equal(f.state.report,null);assert.deepEqual(f.state.records,[]);assert.equal(f.state.cursor,'');assert.equal(f.state.importId,'');assert.equal(f.saved.at(-1).importId,undefined);
});
test('later_release_positive',async()=>{
  const first=deferred();const f=fixture(path=>path==='source-releases/old'?first.promise:Promise.resolve({body:release('new')}));
  const old=f.session.open({source_id:'FCE-2.1',release_import_report_ids:{}},'old');
  await f.session.open({source_id:'NIR-DATA',release_import_report_ids:{}},'new');first.resolve({body:release('old')});await old;
  assert.equal(f.state.source,'NIR-DATA');assert.equal(f.state.release.id,'new');assert.equal(f.saved.at(-1).releaseId,'new');
});
test('superseded_failure_negative',async()=>{
  let reject;const pending=new Promise((_,r)=>reject=r);const f=fixture(()=>pending);
  const old=f.session.open({source_id:'FCE-2.1'},'old');f.session.reset('NIR-DATA');reject(userError('An old request failed.'));await old;
  assert.equal(f.state.source,'NIR-DATA');assert.equal(f.state.error,'');assert.equal(f.state.release,null);
});
test('later_progress_positive',async()=>{
  const old=deferred();const f=fixture(path=>path==='imports/old/progress'?old.promise:nativeRead(path));
  const pending=f.session.loadImport('old');await f.session.loadImport('new');old.resolve({body:progress('old')});await pending;
  assert.equal(f.state.report.id,'new');assert.equal(f.state.importId,'new');assert.equal(f.state.binding,'binding-new');
  assert.equal(f.seen.some(x=>x.report?.id==='old'&&x.importId==='new'),false);
});
test('rows_recovery_positive',async()=>{
  let failed=true;const f=fixture(path=>path.endsWith('/progress')?nativeRead(path):failed?Promise.reject(userError('Source rows are unavailable. Refresh to continue.')):nativeRead(path));
  await f.session.loadImport('saved');assert.equal(f.state.report.id,'saved');assert.equal(f.state.binding,'binding-saved');assert.equal(f.state.error,'Source rows are unavailable. Refresh to continue.');
  failed=false;await f.session.loadImport('saved');assert.deepEqual(f.state.records,[{member:'native-row'}]);assert.equal(f.state.error,'');
});
test('stale_pagination_negative',async()=>{
  const page=deferred();const f=fixture(path=>path.includes('&cursor=')?page.promise:nativeRead(path));
  await f.session.loadImport('old');const pending=f.session.moreRows('old','old cursor',[{member:'old-row'}]);await f.session.loadImport('new');
  page.resolve({body:{items:[{member:'late-old-row'}],next_cursor:null}});await pending;
  assert.equal(f.state.report.id,'new');assert.deepEqual(f.state.records,[{member:'native-row'}]);assert.equal(f.state.cursor,'next-page');
});
test('restore_positive',async()=>{
  const f=fixture(nativeRead);await f.session.restore({source:'FCE-2.1',release:release('r'),binding:'custom',importId:'saved'});
  assert.equal(f.state.version,'v-r');assert.equal(f.state.origin,'constructed://r');assert.equal(f.state.scope,'partial_export');assert.equal(f.state.report.id,'saved');assert.equal(f.state.binding,'binding-saved');
});
test('history_positive',async()=>{
  const diagnostic='internal SQL diagnostic must not be displayed';
  const f=fixture(path=>path.includes('/issues')?Promise.resolve({body:{items:[{code:'import_failed',source_locator:'native.txt',detail:diagnostic}],next_cursor:''}}):nativeRead(path));
  await f.session.loadImport('saved');await f.session.history('saved');
  assert.equal(f.state.history.length,1);assert.equal(f.state.history[0].detail,diagnostic);
  assert.equal(sourceIssueMessage(f.state.history[0].code),'An earlier import was interrupted. Saved rows were retained; refresh its current progress before resuming.');
  assert.equal(sourceIssueMessage(diagnostic).includes(diagnostic),false);
});
test('history_recovery_negative',async()=>{
  let failed=true;const f=fixture(path=>path.includes('/issues')?(failed?Promise.reject(userError('History is unavailable. Refresh to continue.')):Promise.resolve({body:{items:[],next_cursor:''}})):nativeRead(path));
  await f.session.loadImport('saved');await f.session.history('saved');assert.equal(f.state.report.id,'saved');assert.equal(f.state.error,'History is unavailable. Refresh to continue.');
  failed=false;await f.session.history('saved');assert.deepEqual(f.state.history,[]);assert.equal(f.state.error,'');
});

function transport(responses){
  const calls=[];const logs=[];
  const send=createClientFetch({send:async(input,options)=>{calls.push({input,options});const value=responses.shift();if(value instanceof Error)throw value;return value;},wait:async()=>{},log:value=>logs.push(value)});
  return {calls,logs,request:createSourceRequest({send,log:value=>logs.push(value)})};
}
const reply=(status,body,headers={})=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json',...headers}});
test('transient_retry_positive',async()=>{
  const t=transport([reply(503,{error:'internal backend diagnostic'}),reply(200,{saved:'retained'})]);
  assert.deepEqual((await t.request('sources')).body,{saved:'retained'});assert.equal(t.calls.length,2);assert.equal(t.logs[0].status,503);
});
test('exhausted_read_negative',async()=>{
  const t=transport([reply(503,{error:'secret backend detail'}),reply(503,{}),reply(503,{})]);
  await assert.rejects(t.request('sources'),error=>{assert.equal(requestError(error),'The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.');return true;});assert.equal(t.calls.length,3);
});
test('input_guidance_negative',async()=>{
  for(const [status,code,expected] of [[400,'unsafe_path','This archive cannot be imported as supplied.'],[400,'host_denied','The export address does not match the allowed source hosts.'],[409,'source_action_conflict','Saved source progress has changed.'],[404,'source_not_found','This saved source is unavailable.'],[413,'intake_limit','This upload exceeds the local import limit.']]){
    const t=transport([reply(status,{error:code,detail:'internal secret diagnostic'})]);
    await assert.rejects(t.request('source-files',{method:'POST'}),error=>{assert.equal(requestError(error).startsWith(expected),true);assert.equal(requestError(error).includes('internal'),false);return true;});assert.equal(t.calls.length,1);
  }
});
test('write_resume_negative',async()=>{
  const t=transport([reply(503,{error:'native internal cause'},{'X-Tangerine-Import-ID':'saved-import'})]);
  await assert.rejects(t.request('source-releases/r:import',{method:'POST'}),error=>{assert.equal(error.importId,'saved-import');assert.equal(requestError(error).includes('native internal'),false);return true;});assert.equal(t.calls.length,1);
});
test('connection_recovery_positive',async()=>{
  const t=transport([new TypeError('native connection failure'),reply(200,{items:[]})]);assert.deepEqual((await t.request('imports/saved/issues')).body,{items:[]});assert.equal(t.calls.length,2);
});
test('unreadable_reply_negative',async()=>{
  const t=transport([new Response('<html>private backend error</html>',{status:502}),reply(502,{}),reply(502,{})]);
  await assert.rejects(t.request('sources'),error=>{assert.equal(requestError(error).includes('private backend'),false);assert.equal(requestError(error).includes('Refresh'),true);return true;});assert.equal(t.calls.length,3);
});
test('status_language_positive',()=>{
  assert.equal(sourceStatusLabel('incomplete'),'Saved release is incomplete');
  assert.equal(sourceStatusLabel('format_unbound'),'Retained; source conversion is unavailable');
  assert.equal(sourceStatusLabel('not_acquired'),'No source release saved');
});
test('status_language_negative',()=>{
  assert.equal(sourceStatusLabel('private backend exception'),'Saved source status is unavailable. Refresh sources to continue.');
  assert.equal(sourceStatusLabel('constructor'),'Saved source status is unavailable. Refresh sources to continue.');
});
test('unreadable_import_negative',async()=>{
  const t=transport([new Response('<html>internal proxy failure</html>',{status:503,headers:{'X-Tangerine-Import-ID':'retained-import'}})]);
  await assert.rejects(t.request('source-releases/r:import',{method:'POST'}),error=>{assert.equal(error.importId,'retained-import');assert.equal(requestError(error).includes('internal proxy'),false);return true;});assert.equal(t.calls.length,1);
});
test('unknown_code_negative',async()=>{
  const t=transport([reply(503,{error:'constructor'})]);
  await assert.rejects(t.request('source-formats',{method:'POST'}),error=>{assert.equal(requestError(error),'The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.');return true;});
});
test('row_diagnostics_negative',()=>{
  const row={member:'native.csv',raw_record:{answer:'Original native field'},issues:[{code:'mapping_failed',detail:'internal backend diagnostic'}],transformation:{method:'documented'}};
  assert.deepEqual(sourceRowData(row),{member:'native.csv',raw_record:{answer:'Original native field'},transformation:{method:'documented'}});
  assert.equal(row.issues[0].detail,'internal backend diagnostic');
  assert.equal(sourceIssueMessage(row.issues[0].code).includes('internal backend'),false);
});
test('source_files_positive',()=>{
  const f=fixture(nativeRead);f.session.reset('FCE-2.1');
  f.session.addFiles('FCE-2.1',[{relative_path:'native.csv',asset_id:'first'}]);
  f.session.addFiles('FCE-2.1',[{relative_path:'native.csv',asset_id:'updated'},{relative_path:'terms.txt',asset_id:'notice'}]);
  assert.deepEqual(f.state.files,[{relative_path:'native.csv',asset_id:'updated'},{relative_path:'terms.txt',asset_id:'notice'}]);
});
test('source_files_negative',()=>{
  const f=fixture(nativeRead);f.session.reset('NIR-DATA');
  f.session.addFiles('MOODRICK-DATA',[{relative_path:'late-export.csv',asset_id:'old-source'}]);
  assert.deepEqual(f.state.files,[]);assert.equal(f.state.source,'NIR-DATA');
});
test('cache_positive',()=>{
  const entries=new Map();const cache=createSourceCache({storage:()=>({getItem:key=>entries.get(key),setItem:(key,value)=>entries.set(key,value),removeItem:key=>entries.delete(key)})});
  cache.write('saved',{id:'native-import',revision:3});assert.deepEqual(cache.read('saved'),{id:'native-import',revision:3});cache.write('saved',null);assert.equal(cache.read('saved'),null);
});
test('cache_unavailable_negative',()=>{
  const logs=[];const cache=createSourceCache({storage:()=>{throw new DOMException('private storage failure','SecurityError');},log:value=>logs.push(value)});
  assert.equal(cache.read('saved'),null);assert.doesNotThrow(()=>cache.write('saved',{id:'retained-on-server'}));assert.deepEqual(logs,[{kind:'SecurityError'},{kind:'SecurityError'}]);
});

// Full official releases exceed localStorage if their manifest is duplicated.
// The DB owns that data. These literals exercise the shared session only.
test('compact_selection_positive',()=>{
  const large={...release('official'),files:Array.from({length:84296},(_,i)=>({relative_path:'ABA/wav/arctic_'+i+'.wav',sha256:'a'.repeat(64)}))};
  assert.ok(JSON.stringify(large).length>5*1024*1024);
  const f=fixture(nativeRead);f.session.adopt('L2-ARCTIC',large,'native');
  assert.deepEqual(f.saved.at(-1),{source:'L2-ARCTIC',releaseId:'official',binding:'native',importId:undefined});
  assert.ok(JSON.stringify(f.saved.at(-1)).length<200);
  assert.equal(f.state.release,large); // Full manifest remains usable in memory.
});
test('compact_restore_positive',async()=>{
  const calls=[];const f=fixture(async path=>{calls.push(path);return path==='source-releases/official'?{body:release('official')}:nativeRead(path);});
  await f.session.restore({source:'L2-ARCTIC',releaseId:'official',binding:'native',importId:'retained'});
  assert.deepEqual(calls,['source-releases/official','imports/retained/progress','imports/retained/records?limit=20']);
  assert.equal(f.state.release.id,'official');assert.equal(f.state.report.id,'retained');assert.equal(f.state.binding,'binding-retained');
  assert.deepEqual(f.saved.at(-1),{source:'L2-ARCTIC',releaseId:'official',binding:'binding-retained',importId:'retained'});
});
test('compact_unimported_negative',async()=>{
  const calls=[];const f=fixture(async path=>{calls.push(path);return {body:release('raw')};});
  await f.session.restore({source:'NIR-DATA',releaseId:'raw',binding:'raw-only'});
  assert.deepEqual(calls,['source-releases/raw']);assert.equal(f.state.binding,'raw-only');assert.equal(f.state.report,null);assert.equal(f.state.importId,'');
});
test('compact_unavailable_negative',async()=>{
  const calls=[];const f=fixture(async path=>{calls.push(path);throw userError('Source retained. Refresh to continue.');});
  await f.session.restore({source:'L2-ARCTIC',releaseId:'official',binding:'native',importId:'retained'});
  assert.deepEqual(calls,['source-releases/official']);assert.equal(f.state.error,'Source retained. Refresh to continue.');
  assert.equal(f.state.release,undefined);assert.equal(f.state.report,undefined);assert.equal(f.saved.length,0);
});
test('compact_superseded_negative',async()=>{
  const pending=deferred();const f=fixture(()=>pending.promise);
  const restore=f.session.restore({source:'L2-ARCTIC',releaseId:'old',binding:'native',importId:'old-import'});
  f.session.reset('MOODRICK-DATA');pending.resolve({body:release('old')});await restore;
  assert.equal(f.state.source,'MOODRICK-DATA');assert.equal(f.state.release,null);assert.equal(f.state.report,null);assert.equal(f.saved.at(-1),null);
});
test('legacy_cache_migration_positive',async()=>{
  const f=fixture(nativeRead);await f.session.restore({source:'FCE-2.1',release:release('legacy'),binding:'custom',importId:'old'});
  assert.equal(f.state.release.id,'legacy');assert.equal(f.state.report.id,'old');
  assert.deepEqual(f.saved.at(-1),{source:'FCE-2.1',releaseId:'legacy',binding:'binding-old',importId:'old'});
});
