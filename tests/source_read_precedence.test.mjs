import test from 'node:test';
import assert from 'node:assert/strict';
import {createSourceSession} from '../services/web/app/sources/sourceSession.js';
import {userError} from '../services/web/app/requestError.js';

const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
const issue=code=>({code,source_locator:'constructed native history'});
const result=(items,next='')=>({body:{items,next_cursor:next}});
async function historyFixture(){
 const pending=[];const state={};
 const session=createSourceSession({request:async path=>{
  if(path.includes('/issues')){const d=deferred();pending.push(d);return d.promise}
  return path.endsWith('/progress')?{body:{report:{id:'saved'},format_binding_id:'native',permission_grant_ids:[]}}:result([]);
 },publish:value=>Object.assign(state,value)});
 await session.loadImport('saved');return {pending,state,session};
}
test('history_append_positive',async()=>{
 const f=await historyFixture(),first=f.session.history('saved');f.pending[0].resolve(result([issue('first')],'next'));await first;
 const more=f.session.history('saved','next',f.state.history);f.pending[1].resolve(result([issue('second')]));await more;
 assert.deepEqual(f.state.history.map(i=>i.code),['first','second']);assert.equal(f.state.historyCursor,'');
});
test('history_refresh_supersedes_more_negative',async()=>{
 const f=await historyFixture(),old=f.session.history('saved','old-page',[issue('old-first')]);
 const fresh=f.session.history('saved');f.pending[1].resolve(result([issue('current')],'current-next'));await fresh;
 f.pending[0].resolve(result([issue('obsolete')]));await old;
 assert.deepEqual(f.state.history.map(i=>i.code),['current']);assert.equal(f.state.historyCursor,'current-next');
});
test('history_refresh_supersedes_error_negative',async()=>{
 const f=await historyFixture(),old=f.session.history('saved','old-page',[issue('old-first')]);
 const fresh=f.session.history('saved');f.pending[1].resolve(result([issue('current')]));await fresh;
 f.pending[0].reject(userError('Old history is unavailable. Refresh to continue.'));await old;
 assert.deepEqual(f.state.history.map(i=>i.code),['current']);assert.equal(f.state.error,'');
});
test('source_rows_refresh_supersedes_more_negative',async()=>{
 const pending=deferred(),state={};let hold=false;
 const session=createSourceSession({request:async path=>{
  if(path.includes('cursor='))return pending.promise;
  return path.endsWith('/progress')?{body:{report:{id:'saved'},format_binding_id:'native',permission_grant_ids:[]}}:result([issue(hold?'current':'first')],'current-next');
 },publish:value=>Object.assign(state,value)});
 await session.loadImport('saved');const old=session.moreRows('saved','old-cursor',state.records);hold=true;await session.loadImport('saved');
 pending.resolve(result([issue('obsolete')],'obsolete-cursor'));await old;
 assert.deepEqual(state.records.map(i=>i.code),['current']);assert.equal(state.cursor,'current-next');
});
