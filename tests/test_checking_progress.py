"""Literal delivery expectations through the production progress owner.

Only transport and the timer queue are controlled. No model, native write or PBT.
"""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'


class CheckingProgress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = """
import {watchChecking} from './services/web/app/listen/checkingProgress.js';
const turn=()=>new Promise(setImmediate),timers=new Map(),out={};let timerID=0,calls=[],warnings=[];
globalThis.setTimeout=(fn,ms)=>{const id=++timerID;timers.set(id,{fn,ms});return id};
globalThis.clearTimeout=id=>timers.delete(id);
globalThis.fetch=(path,options)=>new Promise(resolve=>calls.push({path,options,resolve}));
console.warn=(...args)=>warnings.push(args);
const take=async()=>{const [id,t]=timers.entries().next().value;timers.delete(id);t.fn();await turn();return t.ms};
const answer=async(i,value)=>{calls[i].resolve({ok:true,json:async()=>value});await turn()};
const attempt={attempt_id:'fixture-attempt',submitted_at:'saved',results_path:'/api/v1/attempts/fixture-attempt/results'};
const setup=(shared=true)=>{
 calls=[];warnings=[];timers.clear();let version=0,seen=[];
 const begin=()=>{const current=++version;return ()=>current===version};
 const stop=watchChecking('fixture-attempt',(a,result)=>seen.push([a.attempt_id,result?.score??null]),...(shared?[begin]:[]));
 return {stop,begin,seen};
};
let s=setup(false);let first=await take();await answer(0,attempt);await answer(1,{score:60});out.current={seen:s.seen,first,next:[...timers.values()].map(t=>t.ms),calls:calls.map(c=>c.path)};s.stop();
s=setup();await take();s.begin();await answer(0,attempt);out.staleAttempt={seen:s.seen,calls:calls.length};s.stop();
s=setup();await take();await answer(0,attempt);s.begin();await answer(1,{score:null,status:'evaluating'});out.staleResult=s.seen;s.stop();
s=setup();await take();await answer(0,attempt);s.stop();await answer(1,{score:60});out.stopped={seen:s.seen,aborted:calls[1].options.signal.aborted,timers:timers.size};
s=setup();await take();await answer(0,attempt);calls[1].resolve({ok:true,json:async()=>{throw new SyntaxError('private backend detail and token')}});await turn();const retry=await take();await answer(2,attempt);await answer(3,{score:60});out.malformed={seen:s.seen,retry,warnings};s.stop();
s=setup();s.stop();out.neverStarted={calls:calls.length,timers:timers.size};
console.log(JSON.stringify(out));
"""
        result = subprocess.run([str(NODE), '--input-type=module', '-e', script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.facts = json.loads(result.stdout)

    def test_current_delivery_positive(self):
        self.assertEqual({
            'seen': [['fixture-attempt', None], ['fixture-attempt', 60]],
            'first': 250, 'next': [1000],
            'calls': ['/api/v1/attempts/fixture-attempt', '/api/v1/attempts/fixture-attempt/results'],
        }, self.facts['current'])

    def test_obsolete_attempt_negative(self):
        self.assertEqual({'seen': [], 'calls': 1}, self.facts['staleAttempt'])

    def test_obsolete_results_negative(self):
        self.assertEqual([['fixture-attempt', None]], self.facts['staleResult'])

    def test_stop_during_read_negative(self):
        self.assertEqual({'seen': [['fixture-attempt', None]], 'aborted': True, 'timers': 0},
                         self.facts['stopped'])

    def test_malformed_recovery_positive(self):
        self.assertEqual({
            'seen': [['fixture-attempt', None], ['fixture-attempt', None], ['fixture-attempt', 60]],
            'retry': 1000,
            'warnings': [['Tangerine display recovery', {'kind': 'SyntaxError'}]],
        }, self.facts['malformed'])

    def test_stop_before_start_negative(self):
        self.assertEqual({'calls': 0, 'timers': 0}, self.facts['neverStarted'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
