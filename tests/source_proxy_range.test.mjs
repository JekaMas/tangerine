import test from 'node:test';
import assert from 'node:assert/strict';
import {GET} from '../services/web/app/api/[...path]/route.js';

// Substitute only the upstream HTTP response, through the real Next proxy.
// Real PostgreSQL/MinIO and browser range/metadata behavior are covered separately.
const target=['v1','sources','assets','11111111-1111-4111-8111-111111111111','bytes'];
async function proxy(upstream,range){
 const saved=globalThis.fetch;let received;
 try{
  globalThis.fetch=async(url,options)=>{received={url,options};return upstream};
  const request=new Request('http://localhost:3000/api/'+target.join('/'),{headers:{host:'localhost:3000',...(range?{range}:{})}});
  const response=await GET(request,{params:Promise.resolve({path:target})});return {response,received};
 }finally{globalThis.fetch=saved}
}
test('original WAVE range length and seek metadata survive the proxy unchanged',async()=>{
 const bytes=new Uint8Array(44);bytes.set(new TextEncoder().encode('RIFF'));
 const {response,received}=await proxy(new Response(bytes,{status:206,headers:{'Content-Type':'audio/wav','Content-Length':'44','Content-Range':'bytes 0-43/123456','Accept-Ranges':'bytes'}}),'bytes=0-43');
 assert.equal(response.status,206);assert.equal(received.options.headers.Range,'bytes=0-43');assert.equal(response.headers.get('Content-Length'),'44');assert.equal(response.headers.get('Content-Range'),'bytes 0-43/123456');assert.equal(response.headers.get('Accept-Ranges'),'bytes');assert.deepEqual(new Uint8Array(await response.arrayBuffer()),bytes);
});
test('complete original recording length is preserved without changing the stored bytes',async()=>{
 const {response}=await proxy(new Response('WAVE',{headers:{'Content-Type':'audio/wav','Content-Length':'4'}}));
 assert.equal(response.status,200);assert.equal(response.headers.get('Content-Length'),'4');assert.equal(await response.text(),'WAVE');
});
test('absent upstream length stays absent, including a dependency failure',async()=>{
 const {response}=await proxy(new Response('{"error":"source_unavailable"}',{status:503,headers:{'Content-Type':'application/json'}}));
 assert.equal(response.status,503);assert.equal(response.headers.has('Content-Length'),false);assert.deepEqual(await response.json(),{error:'source_unavailable'});
});
