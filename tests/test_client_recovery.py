"""Actual shared JS request/presentation owner with controlled HTTP/network inputs."""
import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class ClientRecovery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script=r"""
  import {createClientFetch} from './services/web/app/clientRequest.js';
  import {requestError,userError,parseUserJSON} from './services/web/app/requestError.js';
  import {failureMessage} from './services/web/app/prepare/failureMessage.js';
  const response=(status)=>new Response(JSON.stringify({message:'SQL database_password=secret',code:'INTERNAL_FAIL'}),{status});
  async function scenario(seq,options={}) {let calls=0;const waits=[],logs=[];const run=createClientFetch({send:async()=>{const v=seq[Math.min(calls++,seq.length-1)];if(v instanceof Error)throw v;return v;},wait:async n=>waits.push(n),log:v=>logs.push(v)});let status,error;try{status=(await run('/api/v1/library?credential=hidden',options)).status}catch(e){error=requestError(e)}return {calls,waits,logs,status,error};}
  const v={recovered:await scenario([response(503),response(200)]),exhausted:await scenario([response(503)]),network:await scenario([new TypeError('fetch with secret'),response(200)]),permission:await scenario([response(403)]),write:await scenario([new TypeError('network lost')],{method:'POST',headers:{'Idempotency-Key':'same'},body:'private answer'}),put:await scenario([response(503)],{method:'PUT'}),bad:requestError(new Error('SQL password=secret')),bug:requestError(new TypeError('Cannot read property id')),safe:requestError(userError('Your answer is saved. Refresh to continue.')),saved:failureMessage({phase_states:{render:'failed'},last_failure:{code:'UNKNOWN',message:'Traceback /secret/path'}})};
  const c=new AbortController();c.abort();v.cancel=await scenario([response(200)],{signal:c.signal});
  v.retained=[];const opts={method:'PUT',headers:{'Idempotency-Key':'same'},body:'exact saved answer'};await createClientFetch({send:async(p,o)=>{v.retained.push([p,o===opts,o.body,o.headers['Idempotency-Key']]);return response(503)},log:()=>{}})('/api/v1/attempts/a/answer',opts);
  const long=response(429);long.headers.set('Retry-After','60');v.waitReset=await scenario([long]);
  v.deadline=await scenario([new DOMException('private timeout','TimeoutError')]);
  const date=response(503);date.headers.set('Retry-After','Sat, 01 Jan 2050 00:00:00 GMT');v.dateReset=await scenario([date]);
  try{parseUserJSON('{invalid private content','Mapping program')}catch(e){v.parse=requestError(e)}
  console.log(JSON.stringify(v));
  """
  r=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=15)
  if r.returncode:raise AssertionError(r.stderr)
  cls.v=json.loads(r.stdout)
 def test_transient_read_recovers_positive(self):self.assertEqual([self.v['recovered']['calls'],self.v['recovered']['status'],self.v['recovered']['waits']],[2,200,[160]])
 def test_network_read_recovers_positive(self):self.assertEqual([self.v['network']['calls'],self.v['network']['status']],[2,200])
 def test_exhaustion_is_bounded_negative(self):self.assertEqual([self.v['exhausted']['calls'],self.v['exhausted']['status'],self.v['exhausted']['waits']],[3,503,[160,480]])
 def test_no_permission_or_quota_probe_negative(self):self.assertEqual(self.v['permission']['calls'],1);self.assertEqual(self.v['waitReset']['calls'],1)
 def test_deadline_stops_retry_negative(self):self.assertEqual(self.v['deadline']['calls'],1)
 def test_retry_after_date_respected_negative(self):self.assertEqual([self.v['dateReset']['calls'],self.v['dateReset']['status']],[1,503])
 def test_no_write_replay_negative(self):self.assertEqual(self.v['write']['calls'],1);self.assertEqual(self.v['put']['calls'],1)
 def test_cancel_never_dispatches_negative(self):self.assertEqual(self.v['cancel']['calls'],0)
 def test_write_identity_preserved_positive(self):self.assertEqual(self.v['retained'],[['/api/v1/attempts/a/answer',True,'exact saved answer','same']])
 def test_technical_errors_not_displayed_negative(self):
  for k in ['bad','bug','saved']:
   self.assertNotIn('secret',self.v[k]);self.assertNotIn('SQL',self.v[k]);self.assertNotIn('Traceback',self.v[k])
 def test_authored_recovery_positive(self):self.assertEqual(self.v['safe'],'Your answer is saved. Refresh to continue.')
 def test_invalid_json_has_field_guidance_negative(self):self.assertEqual(self.v['parse'],'Mapping program is not valid JSON. Your input is retained.')
 def test_diagnostic_log_redacted_negative(self):
  text=json.dumps(self.v['recovered']['logs']);self.assertNotIn('hidden',text);self.assertNotIn('private',text);self.assertNotIn('password',text);self.assertIn('503',text)
if __name__=='__main__':unittest.main(verbosity=2)
