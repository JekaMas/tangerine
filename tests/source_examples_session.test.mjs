import test from 'node:test';
import assert from 'node:assert/strict';
import {createExampleSession} from '../services/web/app/sources/exampleSession.js';
import {createSourceRequest} from '../services/web/app/sources/sourceRequest.js';
const wait=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
test('saved example pages and Refresh keep native rows and the current read owner',async()=>{
 const requests=[],deferred=[],state={};const session=createExampleSession({importId:'native',request:path=>{requests.push(path);const p=wait();deferred.push(p);return p.promise},publish:v=>Object.assign(state,v)});
 const first=session.load();deferred[0].resolve({body:{items:[{member:'A',ordinal:0}],next_cursor:'["A","turns",0]'}});await first;
 assert.equal(state.items[0].member,'A');const more=session.load(true);assert.match(requests[1],/cursor=%5B/);deferred[1].resolve({body:{items:[{member:'A',ordinal:1}],next_cursor:''}});await more;assert.deepEqual(state.items.map(v=>v.ordinal),[0,1]);
 const old=session.load(),latest=session.load();deferred[3].resolve({body:{items:[{member:'latest',ordinal:3}],next_cursor:''}});await latest;deferred[2].resolve({body:{items:[{member:'obsolete',ordinal:2}],next_cursor:''}});await old;assert.equal(state.items[0].member,'latest');assert.equal(state.loading,false);session.dispose();
});
test('failure retains rows, hides backend details, permits recovery and ignores disposed reads',async()=>{
 let failing=false;const logs=[],state={};const request=createSourceRequest({log:v=>logs.push(v),send:async()=>new Response(JSON.stringify(failing?{error:'INTERNAL_SECRET_CANARY',detail:'private traceback'}:{items:[{member:'saved',ordinal:7}],next_cursor:''}),{status:failing?503:200})});
 const session=createExampleSession({importId:'native',request,publish:v=>Object.assign(state,v)});await session.load();failing=true;await session.load();assert.equal(state.items[0].member,'saved');assert.match(state.error,/temporarily unavailable/);assert.doesNotMatch(state.error,/INTERNAL|CANARY|traceback/);assert.equal(logs.length,1);failing=false;await session.load();assert.equal(state.error,'');assert.equal(state.items[0].ordinal,7);
 const deferred=wait(),updates=[];const gone=createExampleSession({importId:'old',request:()=>deferred.promise,publish:v=>updates.push(v)});const reading=gone.load();gone.dispose();deferred.resolve({body:{items:[{member:'wrong'}],next_cursor:''}});await reading;assert.equal(updates.length,1);session.dispose();
});
test('named native views use the saved-example endpoint without rewriting native choices',async()=>{
 let requested='';const state={};const session=createExampleSession({importId:'native',view:'PIR_second_subtask_dataset',request:async path=>{requested=path;return {body:{items:[{projection:{source_example:{label_meaning:'zero_based_correct_choice_index',source_selected_choice:'Native answer'}}}],next_cursor:''}}},publish:v=>Object.assign(state,v)});await session.load();assert.equal(requested,'imports/native/examples?limit=20&view=PIR_second_subtask_dataset');assert.equal(state.items[0].projection.source_example.source_selected_choice,'Native answer');session.dispose();
});
