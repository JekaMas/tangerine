import test from 'node:test';
import assert from 'node:assert/strict';
import {createSourcePlayback} from '../services/web/app/sources/sourcePlayback.js';

// Constructed media events qualify the actual recovery owner. Browser tests
// separately prove real recorded bytes, gestures, seeking and finite playback.
class Media extends EventTarget {
  constructor(){super();this.position=0;this.paused=true;this.error=null;this.seeking=false;this.loads=0;this.plays=0;this.reject=null}
  get currentTime(){return this.position}
  set currentTime(value){this.position=value;this.seeking=true;this.emit('seeking');this.seeking=false;this.emit('seeked')}
  emit(name){this.dispatchEvent(new Event(name))}
  async play(){this.plays++;this.paused=false;this.emit('play');if(this.reject)throw this.reject;this.emit('playing')}
  pause(){this.paused=true;this.emit('pause')}
  load(){this.loads++;this.error=null;this.position=0;this.pause()}
  fail(code=4){this.error={code,message:'PRIVATE_BACKEND_CANARY'};this.paused=true;this.emit('error')}
  tick(time){this.position=time;this.emit('timeupdate')}
}
function fixture(){
 const media=new Media(),states=[],logs=[],timers=new Map();let id=0;
 const owner=createSourcePlayback(media,{publish:value=>states.push(value),log:value=>logs.push(value),schedule:(fn,ms)=>{timers.set(++id,{fn,ms});return id},unschedule:key=>timers.delete(key)});
 const advance=async()=>{const [key,timer]=timers.entries().next().value;timers.delete(key);timer.fn();await new Promise(resolve=>setImmediate(resolve))};
 return {media,owner,states,logs,timers,advance};
}
const interval={start_ms:9590,end_ms:14839};

test('source playback has no automatic start; requested interval stops at its saved end',async()=>{
 const {media,owner,states}=fixture();assert.equal(media.plays,0);assert.equal(media.loads,0);
 await owner.replay(interval);assert.equal(media.currentTime,9.59);assert.equal(media.paused,false);
 media.tick(14.838);assert.equal(media.paused,false);media.tick(14.839);assert.equal(media.paused,true);
 assert.deepEqual(states.at(-1),{error:'',loading:false});owner.dispose();
});
test('one media failure restores the same interval and logs only safe diagnostics',async()=>{
 const {media,owner,states,logs,timers,advance}=fixture();
 await owner.replay(interval);media.fail(2);assert.equal(timers.size,1);assert.equal(timers.values().next().value.ms,160);
 assert.deepEqual(states.at(-1),{error:'',loading:true});await advance();
 assert.equal(media.loads,1);assert.equal(media.currentTime,9.59);assert.equal(media.paused,false);
 media.tick(14.84);assert.equal(media.paused,true);
 assert.deepEqual(logs,[{outcome:'media_unavailable',code:2,attempt:1}]);
 assert.doesNotMatch(JSON.stringify(states)+JSON.stringify(logs),/PRIVATE|CANARY/);owner.dispose();
});
test('three unsuccessful reads stop automatic retries, retain the interval and allow explicit recovery',async()=>{
 const {media,owner,states,logs,timers,advance}=fixture();
 media.play=async()=>{media.plays++;media.fail();throw Error('PRIVATE_CANARY')};
 await owner.replay(interval);await advance();assert.equal(timers.values().next().value.ms,480);await advance();
 assert.equal(media.plays,3);assert.equal(media.loads,2);assert.equal(timers.size,0);
 assert.deepEqual(logs.map(v=>v.attempt),[1,2,3]);assert.deepEqual(states.at(-1),{loading:false,error:'This recording is unavailable right now. Retry playback; your source files are retained.'});
 media.play=Media.prototype.play;await owner.retry();assert.equal(media.currentTime,9.59);assert.equal(media.paused,false);
 assert.deepEqual(states.at(-1),{error:'',loading:false});media.tick(14.839);assert.equal(media.paused,true);owner.dispose();
});
test('native controls recover an ordinary seek without reinstating an obsolete finite range',async()=>{
 const {media,owner,advance}=fixture();await owner.replay(interval);media.currentTime=22.2;media.fail(2);await advance();
 assert.equal(media.currentTime,22.2);media.tick(26);assert.equal(media.paused,false);owner.dispose();
});
test('disposing a source cancels pending recovery, stops audio and prevents stale UI updates',async()=>{
 const {media,owner,states,timers}=fixture();await owner.replay(interval);media.fail();const delayed=timers.values().next().value.fn;
 owner.dispose();const count=states.length;assert.equal(timers.size,0);assert.equal(media.paused,true);delayed();media.fail();
 await new Promise(resolve=>setImmediate(resolve));assert.equal(media.loads,0);assert.equal(states.length,count);
});
test('a newer passage supersedes a delayed retry from the previous selection',async()=>{
 const {media,owner,timers}=fixture();await owner.replay(interval);media.fail();const delayed=timers.values().next().value.fn;
 await owner.replay({start_ms:22000,end_ms:25000});delayed();assert.equal(timers.size,0);assert.equal(media.currentTime,22);
 media.tick(25);assert.equal(media.paused,true);owner.dispose();
});
test('play permission failure is actionable and does not create a retry loop or expose the rejection',async()=>{
 const {media,owner,states,logs,timers}=fixture();media.reject=Object.assign(Error('PRIVATE_CANARY'),{name:'NotAllowedError'});
 await owner.replay(interval);assert.equal(timers.size,0);assert.deepEqual(states.at(-1),{loading:false,error:'Select Play to resume this recording.'});
 assert.deepEqual(logs,[{outcome:'play_unavailable',kind:'NotAllowedError'}]);owner.dispose();
});
test('late play rejection cannot replace the newer source action or disposed player',async()=>{
 const {media,owner,states}=fixture();let reject;media.play=()=>new Promise((_,r)=>{reject=r});
 const old=owner.replay(interval);media.play=Media.prototype.play;await owner.replay({start_ms:22000,end_ms:25000});const count=states.length;
 reject(Error('OLD_PRIVATE_CANARY'));await old;assert.equal(states.length,count);assert.equal(media.currentTime,22);owner.dispose();
});
