"""Controlled asynchronous media events through the actual range owner.

This proves ownership/cancellation and formatting, not a browser clock or speech.
"""
import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class PassageReplay(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
import {createPassageReplay,passageTime} from './services/web/app/listen/passageReplay.js';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
class Media extends EventTarget {
 constructor(){super();this.position=0;this.pauses=0;this.pending=[];}
 set currentTime(v){this.position=v;this.dispatchEvent(new Event('seeking'));}get currentTime(){return this.position;}
 play(){const d=deferred();this.pending.push(d);return d.promise;}
 pause(){this.pauses++;this.dispatchEvent(new Event('pause'));}
 tick(t){this.position=t;this.dispatchEvent(new Event('timeupdate'));}
 started(i){this.dispatchEvent(new Event('play'));this.pending[i].resolve();}
}
const range={start_ms:9590,end_ms:14839},next={start_ms:22000,end_ms:25000},out={};
let a=new Media(),r=createPassageReplay(a),failures=0;
let old=r.replay(range).catch(()=>failures++),fresh=r.replay(next);a.started(1);await fresh;a.pending[0].reject(Error('old failed'));await old;a.tick(25);out.oldFailure={pauses:a.pauses,failures};r.dispose();
a=new Media();r=createPassageReplay(a);old=r.replay(range);fresh=r.replay(next);a.pending[0].resolve();await old;a.started(1);await fresh;a.tick(25);out.oldResolve=a.pauses;r.dispose();
a=new Media();r=createPassageReplay(a);let rejected=false;old=r.replay(range).catch(()=>rejected=true);a.pending[0].reject(Error('current failed'));await old;a.tick(20);out.currentFailure={rejected,pauses:a.pauses};r.dispose();
a=new Media();r=createPassageReplay(a);failures=0;old=r.replay(range).catch(()=>failures++);a.currentTime=20;a.pending[0].reject(Error('cancelled failed'));await old;a.tick(21);out.cancelled={failures,pauses:a.pauses};r.dispose();
a=new Media();r=createPassageReplay(a);old=r.replay(range);a.started(0);await old;r.dispose();a.tick(20);out.disposed=a.pauses;
out.times=[0,9590,14839,59994,59999,3599999].map(passageTime);
console.log(JSON.stringify(out));
"""
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_superseded_failure_negative(self):self.assertEqual({'pauses':1,'failures':0},self.v['oldFailure'])
 def test_superseded_completion_negative(self):self.assertEqual(1,self.v['oldResolve'])
 def test_current_failure_positive(self):self.assertEqual({'rejected':True,'pauses':0},self.v['currentFailure'])
 def test_cancelled_failure_negative(self):self.assertEqual({'failures':0,'pauses':0},self.v['cancelled'])
 def test_disposal_positive(self):self.assertEqual(0,self.v['disposed'])
 def test_time_rollover_positive(self):self.assertEqual(['0:00.00','0:09.59','0:14.84','0:59.99','1:00.00','60:00.00'],self.v['times'])
if __name__=='__main__':unittest.main(verbosity=2)
