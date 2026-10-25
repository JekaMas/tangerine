"""Independent ordered read outcomes through the shared production owner."""
import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class SavedList(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
import {createSavedList} from './services/web/app/savedList.js';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
const fixtures=()=>{let states=[];const owner=createSavedList({onChange:s=>states.push(structuredClone(s)),unavailable:'Saved work is unavailable. Refresh to retry.'});return {owner,states,last:()=>states.at(-1)}};
const page=(name,cursor=null)=>({items:[{id:name}],cursor});const out={};
let f=fixtures(),d=deferred();let p=f.owner.read(()=>d.promise);out.unread=f.last();d.resolve({items:[],cursor:null});await p;out.empty=f.last();
f=fixtures();await f.owner.read(async()=>{throw new Error('private backend detail')});out.initialError=f.last();
f=fixtures();await f.owner.read(async()=>page('saved','next'));await f.owner.read(async()=>{throw new SyntaxError('private parse detail')});out.retained=f.last();await f.owner.read(async()=>page('recovered'));out.recovered=f.last();
f=fixtures();d=deferred();p=f.owner.read(()=>d.promise);await f.owner.read(async()=>page('new'));d.resolve(page('old'));await p;out.lateSuccess=f.last();
f=fixtures();d=deferred();p=f.owner.read(()=>d.promise);await f.owner.read(async()=>page('new'));d.reject(new Error('obsolete error'));await p;out.lateError=f.last();
f=fixtures();await f.owner.read(async()=>page('retained'));d=deferred();p=f.owner.read(()=>d.promise);await f.owner.read(async()=>{throw new Error('latest failed')});d.resolve(page('obsolete'));await p;out.latestError=f.last();
f=fixtures();const old=deferred(),newer=deferred();p=f.owner.read(()=>old.promise);const q=f.owner.read(()=>newer.promise);old.resolve(page('old'));await p;out.latestPending=f.last();newer.resolve(page('new'));await q;
f=fixtures();await f.owner.read(async()=>page('a','next'));let used;await f.owner.read(async cursor=>{used=cursor;return page('b','after')},true);out.append={state:f.last(),used};await f.owner.read(async()=>{throw new Error('page failure')},true);out.appendError=f.last();
f=fixtures();await f.owner.read(async()=>page('a','next'));d=deferred();p=f.owner.read(()=>d.promise,true);await f.owner.read(async()=>page('fresh'));d.resolve(page('b'));await p;out.replacedAppend=f.last();
f=fixtures();d=deferred();p=f.owner.read(()=>d.promise);const before=f.states.length;f.owner.cancel();d.resolve(page('old'));await p;out.cancelled={before,after:f.states.length};
console.log(JSON.stringify(out));
"""
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout);cls.log=p.stderr
 def test_unread_positive(self):self.assertEqual({'items':[],'cursor':None,'loaded':False,'loading':True,'error':''},self.v['unread'])
 def test_empty_positive(self):self.assertEqual({'items':[],'cursor':None,'loaded':True,'loading':False,'error':''},self.v['empty'])
 def test_initial_failure_negative(self):self.assertFalse(self.v['initialError']['loaded']);self.assertEqual('Saved work is unavailable. Refresh to retry.',self.v['initialError']['error']);self.assertNotIn('private',self.v['initialError']['error'])
 def test_retention_positive(self):self.assertEqual([{'id':'saved'}],self.v['retained']['items']);self.assertEqual('next',self.v['retained']['cursor']);self.assertTrue(self.v['retained']['loaded']);self.assertEqual([{'id':'recovered'}],self.v['recovered']['items']);self.assertEqual('',self.v['recovered']['error'])
 def test_old_success_negative(self):self.assertEqual([{'id':'new'}],self.v['lateSuccess']['items']);self.assertEqual('',self.v['lateSuccess']['error'])
 def test_old_error_negative(self):self.assertEqual([{'id':'new'}],self.v['lateError']['items']);self.assertEqual('',self.v['lateError']['error'])
 def test_current_error_negative(self):self.assertEqual([{'id':'retained'}],self.v['latestError']['items']);self.assertTrue(self.v['latestError']['error'])
 def test_pending_positive(self):self.assertTrue(self.v['latestPending']['loading']);self.assertEqual([],self.v['latestPending']['items'])
 def test_pagination_positive(self):self.assertEqual('next',self.v['append']['used']);self.assertEqual([{'id':'a'},{'id':'b'}],self.v['append']['state']['items']);self.assertEqual('after',self.v['append']['state']['cursor']);self.assertEqual([{'id':'a'},{'id':'b'}],self.v['appendError']['items']);self.assertEqual('after',self.v['appendError']['cursor'])
 def test_old_append_negative(self):self.assertEqual([{'id':'fresh'}],self.v['replacedAppend']['items'])
 def test_unmounted_negative(self):self.assertEqual(self.v['cancelled']['before'],self.v['cancelled']['after'])
 def test_logging_positive(self):self.assertIn('Tangerine display recovery',self.log);self.assertIn('SyntaxError',self.log);self.assertNotIn('private backend detail',self.log);self.assertNotIn('private parse detail',self.log)
if __name__=='__main__':unittest.main(verbosity=2)
