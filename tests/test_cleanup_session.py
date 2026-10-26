"""Literal asynchronous selection/preview/confirmation through the actual owner."""
import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class CleanupSession(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
import {createCleanupSession} from './services/web/app/cleanup/session.js';
import {cleanupStatus,labCleanupStatus} from './services/web/app/cleanup/labels.js';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
const plan=id=>({id,state:'preview',confirmation_sha256:id+'-digest',blocked:[],documents:[id],assets:[]});
let state,calls=[];const pending=[];
const owner=createCleanupSession({onChange:value=>state=value,request:args=>{calls.push(args);const p=deferred();pending.push(p);return p.promise}}),out={};
owner.select('one');let old=owner.preview();owner.select('two');out.changed={ids:state.ids,plan:state.plan,pending:state.pending,confirmed:state.confirmed};let next=owner.preview();pending[1].resolve(plan('two'));await next;owner.confirm(true);pending[0].resolve(plan('one'));await old;out.newest={id:state.plan.id,confirmed:state.confirmed};
owner.select('three');out.invalidated={plan:state.plan,confirmed:state.confirmed};let n=calls.length;await owner.apply();out.unconfirmed=calls.length-n;
next=owner.preview();pending[2].resolve(plan('three'));await next;owner.confirm(true);next=owner.apply();out.apply=calls.at(-1);pending[3].resolve({...plan('three'),state:'erased'});await next;out.erased={state:state.plan.state,confirmed:state.confirmed,pending:state.pending};
owner.select('four');old=owner.preview();owner.select('five');next=owner.preview();pending[5].resolve(plan('five'));await next;pending[4].reject(Error('private backend payload'));await old;out.obsoleteError={id:state.plan.id,error:state.error};
owner.select('six');next=owner.preview();pending[6].reject(Error('private backend payload'));await next;out.failure={ids:state.ids,error:state.error,pending:state.pending};
next=owner.preview();pending[7].resolve({...plan('six'),blocked:['shared-audio']});await next;owner.confirm(true);n=calls.length;await owner.apply();out.blocked=calls.length-n;
next=owner.preview();owner.cancel();pending[8].resolve(plan('disposed'));await next;out.disposed=state.plan.id;
owner.select('six');next=owner.preview(true);pending[9].resolve(plan('orphans'));await next;owner.confirm(true);next=owner.apply();pending[10].resolve({...plan('orphans'),state:'erased'});await next;out.orphanScope=state.scope;
out.labels=['preview','blocked_active_reference','native_erased','native_erased_media_cleanup_pending','erased'].map(cleanupStatus);out.unknown=[cleanupStatus('private backend detail'),labCleanupStatus('private backend detail')];out.lab=['not_requested','pending_explicit_local_lab_cleanup','erased'].map(labCleanupStatus);
console.log(JSON.stringify(out));
"""
  p=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
  if p.returncode:raise AssertionError(p.stderr)
  cls.v=json.loads(p.stdout)
 def test_selection_during_preview_positive(self):self.assertEqual({'ids':'two','plan':None,'pending':None,'confirmed':False},self.v['changed'])
 def test_old_preview_negative(self):self.assertEqual({'id':'two','confirmed':True},self.v['newest'])
 def test_selection_clears_confirmation_negative(self):self.assertEqual({'plan':None,'confirmed':False},self.v['invalidated'])
 def test_unconfirmed_apply_negative(self):self.assertEqual(0,self.v['unconfirmed'])
 def test_apply_exact_plan_positive(self):self.assertEqual({'id':'three','state':'preview','confirmation_sha256':'three-digest','blocked':[],'documents':['three'],'assets':[]},self.v['apply']['plan']);self.assertEqual('three',self.v['apply']['ids']);self.assertTrue(self.v['apply']['apply']);self.assertEqual({'state':'erased','confirmed':False,'pending':None},self.v['erased'])
 def test_obsolete_error_negative(self):self.assertEqual({'id':'five','error':''},self.v['obsoleteError'])
 def test_current_failure_retains_selection_positive(self):self.assertEqual('six',self.v['failure']['ids']);self.assertIsNone(self.v['failure']['pending']);self.assertIn('selection is retained',self.v['failure']['error']);self.assertNotIn('private',self.v['failure']['error'])
 def test_blocked_apply_negative(self):self.assertEqual(0,self.v['blocked'])
 def test_readable_status_positive(self):self.assertEqual(['Preview ready','Still in use','Local records deleted; external cleanup remains','Local records deleted; media cleanup remains','Deletion complete'],self.v['labels']);self.assertEqual(['No external cleanup requested','External Lab cleanup remains','External copies deleted'],self.v['lab'])
 def test_unknown_status_negative(self):self.assertEqual(['Cleanup needs attention','Check external cleanup in Recovery'],self.v['unknown'])
 def test_orphan_scope_positive(self):self.assertEqual('Old unlinked media',self.v['orphanScope'])
 def test_disposal_negative(self):self.assertEqual('six',self.v['disposed'])
if __name__=='__main__':unittest.main(verbosity=2)
