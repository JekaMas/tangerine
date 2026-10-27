import test from 'node:test';
import assert from 'node:assert/strict';
import {createCorrectionSession,emptyCorrections} from '../services/web/app/sources/correctionSession.js';
import {userError} from '../services/web/app/requestError.js';

const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
const page=(ids,next='')=>({body:{items:ids.map(id=>({id})),next_cursor:next}});
function fixture(){
 const state=emptyCorrections(),pending=[],saved=[],patches=[];
 const session=createCorrectionSession({importId:'saved',request:path=>{const d=deferred();pending.push({path,...d});return d.promise},publish:value=>{Object.assign(state,value);patches.push(value)},saveDownload:(body,partition)=>saved.push({body,partition})});
 return {state,pending,saved,patches,session};
}
test('corrections_append_positive',async()=>{
 const f=fixture(),first=f.session.load();f.pending[0].resolve(page(['dev:0'],'opaque & next'));await first;
 const next=f.session.load(true);assert.equal(f.pending[1].path,'imports/saved/corrections?limit=20&cursor=opaque%20%26%20next');
 f.pending[1].resolve(page(['dev:1']));await next;
 assert.deepEqual(f.state.items,[{id:'dev:0'},{id:'dev:1'}]);assert.equal(f.state.cursor,'');assert.equal(f.state.loading,false);
});
test('corrections_refresh_supersedes_more_negative',async()=>{
 const f=fixture(),first=f.session.load();f.pending[0].resolve(page(['dev:0'],'old-cursor'));await first;
 const more=f.session.load(true),fresh=f.session.load();f.pending[2].resolve(page(['current'],'fresh-cursor'));await fresh;
 f.pending[1].resolve(page(['obsolete'],'obsolete-cursor'));await more;
 assert.deepEqual(f.state.items,[{id:'current'}]);assert.equal(f.state.cursor,'fresh-cursor');assert.equal(f.state.readError,'');
});
test('corrections_old_completion_preserves_loading_negative',async()=>{
 const f=fixture(),old=f.session.load(),fresh=f.session.load();
 f.pending[0].resolve(page(['obsolete']));await old;assert.equal(f.state.loading,true);assert.deepEqual(f.state.items,[]);
 f.pending[1].resolve(page(['current']));await fresh;assert.equal(f.state.loading,false);assert.deepEqual(f.state.items,[{id:'current'}]);
});
test('corrections_old_error_is_ignored_negative',async()=>{
 const f=fixture(),old=f.session.load(),fresh=f.session.load();
 f.pending[1].resolve(page(['current']));await fresh;f.pending[0].reject(userError('Old request failed.'));await old;
 assert.deepEqual(f.state.items,[{id:'current'}]);assert.equal(f.state.readError,'');
});
test('corrections_failure_retains_then_recovers_positive',async()=>{
 const f=fixture(),initial=f.session.load();f.pending[0].resolve(page(['saved'],'saved-cursor'));await initial;
 const failure=f.session.load();f.pending[1].reject(userError('Saved examples are unavailable. Refresh to continue.'));await failure;
 assert.deepEqual(f.state.items,[{id:'saved'}]);assert.equal(f.state.cursor,'saved-cursor');assert.equal(f.state.readError,'Saved examples are unavailable. Refresh to continue.');assert.equal(f.state.loading,false);
 const retry=f.session.load();f.pending[2].resolve(page(['recovered']));await retry;
 assert.deepEqual(f.state.items,[{id:'recovered'}]);assert.equal(f.state.readError,'');
});
test('corrections_download_survives_refresh_positive',async()=>{
 const f=fixture(),download=f.session.download('dev'),refresh=f.session.load();
 f.pending[1].resolve(page(['dev:0']));await refresh;
 assert.equal(f.state.loading,false);assert.equal(f.state.downloading,true);assert.deepEqual(f.saved,[]);
 const dataset={examples:[{id:'dev:0'}]};f.pending[0].resolve({body:dataset});await download;
 assert.deepEqual(f.saved,[{body:dataset,partition:'dev'}]);assert.equal(f.state.downloading,false);assert.match(f.state.notice,/^1 development examples downloaded/);assert.deepEqual(f.state.items,[{id:'dev:0'}]);
});
test('corrections_download_failure_does_not_hide_examples_negative',async()=>{
 const f=fixture(),initial=f.session.load();f.pending[0].resolve(page(['saved']));await initial;
 const failed=f.session.download('test');f.pending[1].reject(userError('Dataset download is unavailable. Try again.'));await failed;
 assert.equal(f.state.downloading,false);assert.deepEqual(f.state.items,[{id:'saved'}]);assert.equal(f.state.downloadError,'Dataset download is unavailable. Try again.');assert.deepEqual(f.saved,[]);
 const retry=f.session.download('test');f.pending[2].resolve({body:{examples:[]}});await retry;
 assert.equal(f.state.downloadError,'');assert.deepEqual(f.saved,[{body:{examples:[]},partition:'test'}]);
});
test('corrections_disposal_ignores_late_results_negative',async()=>{
 const f=fixture(),read=f.session.load(),download=f.session.download('dev');f.session.dispose();const count=f.patches.length;
 f.pending[0].resolve(page(['old import']));f.pending[1].resolve({body:{examples:[{id:'old import'}]}});await Promise.all([read,download]);
 assert.equal(f.patches.length,count);assert.deepEqual(f.saved,[]);
});
