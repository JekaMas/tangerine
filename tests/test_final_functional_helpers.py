"""Native JS owners with literal independent expectations; no model calls.

Media event source is controlled here. Actual browser playback is a separate case.
"""
from pathlib import Path
import hashlib,json,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'

class FinalFunctionalHelpers(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  script="""
  import {recordTitle,recordDate,recordState} from './services/web/app/savedRecord.js';
  import {failureMessage} from './services/web/app/prepare/failureMessage.js';
  import {reportStarter,experimentStarter} from './services/web/app/reports/starters.js';
  import {createPassageReplay,passageTime} from './services/web/app/listen/passageReplay.js';
  import fs from 'node:fs';
  const defaults=JSON.parse(fs.readFileSync('data/final-functional-ux-20261025/lab-defaults.json','utf8'));
  class Media extends EventTarget {
   constructor(){super();this.position=0;this.pauses=0;this.plays=0;this.playing=false;this.fail=false;}
   set currentTime(v){this.position=v;this.dispatchEvent(new Event('seeking'));}
   get currentTime(){return this.position;}
   async play(){if(this.fail)throw Error('Unavailable');this.plays++;if(!this.playing){this.playing=true;this.dispatchEvent(new Event('play'));}}
   pause(){this.pauses++;this.playing=false;this.dispatchEvent(new Event('pause'));}
   tick(v){this.position=v;this.dispatchEvent(new Event('timeupdate'));}
  }
  const a=new Media(),r=createPassageReplay(a), interval={start_ms:9590,end_ms:14839};
  const noAutoplay=[a.plays,a.pauses];await r.replay(interval);const start=[a.currentTime,a.plays,a.pauses];a.tick(14);const beforeEnd=a.pauses;a.tick(14.839);const end=[a.currentTime,a.pauses];
  await r.replay(interval);a.currentTime=20;a.tick(21);const manual=a.pauses;
  await r.replay(interval);await r.replay({start_ms:22000,end_ms:25000});a.tick(23);const replacedBefore=a.pauses;a.tick(25);const replacedEnd=a.pauses;
  await r.replay(interval);a.pause();await a.play();a.tick(20);const fullPlayback=a.pauses;
  await r.replay(interval);r.dispose();a.tick(20);const disposed=a.pauses;
  const b=new Media(),s=createPassageReplay(b);b.fail=true;let failed=false;try{await s.replay(interval)}catch{failed=true;}b.tick(20);const error=[failed,b.pauses];s.dispose();
  const fail=code=>failureMessage({phase_states:{render:'failed'},last_failure:{code,message:'',retryable:true}});
  const v={titles:[recordTitle({exercise_title:'Saved title',exercise_request:{topic:'Other'}}),recordTitle({exercise_request:{topic:'Topic'}}),recordTitle({id:'private'})], dates:[recordDate(null),recordDate('invalid'),recordDate('2026-10-20T12:34:00Z')],states:['started','completed','review_required'].map(recordState),failures:['DEADLINE_EXCEEDED','PROVIDER_FAILURE','PROVIDER_OUTPUT_INVALID','MISSING_CREDENTIAL','UNKNOWN'].map(fail),completed:failureMessage({audio_available:true,last_failure:{code:'PROVIDER_FAILURE'}}),noFailure:failureMessage({}), noAutoplay,start,beforeEnd,end,manual,replacedBefore,replacedEnd,fullPlayback,disposed,error,times:[passageTime(9590),passageTime(14839),passageTime(60000)],report:reportStarter('My constructed report','lexis.collocation'),experiment:await experimentStarter(defaults,{topic:'A café opens',words:'50',level:'B1',profile:defaults.configuration.llm_profile})};
  v.alternate=await experimentStarter(defaults,{topic:'A café opens',words:50,level:'B1',profile:'local-generation'});
  v.invalid=[];for(const f of [()=>reportStarter('','lexis.collocation'),()=>experimentStarter(defaults,{topic:'',words:50,profile:defaults.configuration.llm_profile}),()=>experimentStarter(defaults,{topic:'Topic',words:1.5,profile:defaults.configuration.llm_profile}),()=>experimentStarter(defaults,{topic:'Topic',words:50,profile:'invented'}),()=>experimentStarter({...defaults,configuration:{...defaults.configuration,llm_profiles:defaults.configuration.llm_profiles.map(p=>({...p,roles:['feedback']}))}},{topic:'Topic',words:50,profile:defaults.configuration.llm_profile})]){try{await f();v.invalid.push(false)}catch{v.invalid.push(true)}}
  console.log(JSON.stringify(v));
  """
  result=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
  if result.returncode:raise AssertionError(result.stderr)
  cls.v=json.loads(result.stdout)
 def test_title_positive(self):self.assertEqual(self.v['titles'][:2],['Saved title','Topic'])
 def test_legacy_negative(self):self.assertEqual(self.v['titles'][2],'Untitled exercise');self.assertEqual(self.v['dates'][:2],['Date unavailable']*2)
 def test_date_positive(self):self.assertIn('20 Oct 2026',self.v['dates'][2]);self.assertNotIn('T12:',self.v['dates'][2])
 def test_status_positive(self):self.assertEqual(self.v['states'],['Draft','Completed','Some findings uncertain'])
 def test_failure_reasons_positive(self):
  for reason,part in zip(self.v['failures'],['time limit','selected provider','incomplete or unusable','credential','did not complete']):self.assertIn(part,reason);self.assertIn('retained',reason)
 def test_failure_empty_message_negative(self):self.assertIn('resume this exercise explicitly',self.v['failures'][4])
 def test_completed_stale_failure_negative(self):self.assertEqual([self.v['completed'],self.v['noFailure']],['',''])
 def test_passage_start_positive(self):self.assertEqual(self.v['start'],[9.59,1,0]);self.assertEqual(self.v['times'],['0:09.59','0:14.84','1:00.00'])
 def test_passage_end_positive(self):self.assertEqual([self.v['beforeEnd'],self.v['end']],[0,[14.839,1]])
 def test_no_autoplay_negative(self):self.assertEqual(self.v['noAutoplay'],[0,0])
 def test_manual_seek_negative(self):self.assertEqual(self.v['manual'],1)
 def test_range_replaced_positive(self):self.assertEqual([self.v['replacedBefore'],self.v['replacedEnd']],[1,2])
 def test_full_playback_cancels_negative(self):self.assertEqual(self.v['fullPlayback'],3)
 def test_dispose_cancels_negative(self):self.assertEqual(self.v['disposed'],3)
 def test_media_failure_negative(self):self.assertEqual(self.v['error'],[True,0])
 def test_constructed_report_positive(self):
  r=self.v['report'];self.assertEqual([r['title'],r['input']['population']['label_origin']],['My constructed report','constructed']);self.assertEqual([len(r['input']['windows']),sum(len(w['events']) for w in r['input']['windows'])],[2,1]);self.assertEqual(r['attempts'],[])
 def test_portable_experiment_positive(self):
  v=self.v['experiment'];d=v['assets']['dataset'];self.assertEqual([v['experiment']['scope'],v['experiment']['repetitions'],d['cases'][0]['origin']],['generation_pipeline',1,'constructed']);self.assertEqual(v['assets']['input'],{'topic':'A café opens','speaker_count':1,'text_length_words':50,'english_level':'B1','category_families':['grammar'],'category_ids':['grammar.verbs.subject_verb_agreement'],'mutation_count':1})
 def test_independent_asset_hashes_positive(self):
  v=self.v['experiment'];a=v['assets'];sha=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();case=a['dataset']['cases'][0]
  self.assertEqual(case['input_sha256'],sha(a['input']));self.assertEqual(case['expectations_sha256'],sha(a['expected']));self.assertEqual(v['experiment']['variants'][0]['configuration_sha256'],sha(a['config']));d=dict(a['dataset']);d.pop('dataset_sha256');self.assertEqual(a['dataset']['dataset_sha256'],sha(d))
 def test_no_semantic_gold_invented_negative(self):self.assertEqual(self.v['experiment']['assets']['expected']['semantic_propositions'],[]);self.assertEqual(self.v['experiment']['assets']['dataset']['cases'][0]['reference_receipt_ids'],[])
 def test_invalid_fields_negative(self):self.assertEqual(self.v['invalid'],[True]*5)
 def test_selected_generation_binding_positive(self):
  v=self.v['alternate'];c=v['assets']['config'];self.assertEqual(v['experiment']['variants'][0]['profile_id'],'local-generation');self.assertEqual(c['llm_profile'],'local-generation');self.assertEqual(c['stage_profiles']['case_generation'],'local-generation');self.assertEqual(c['stage_profiles']['claim_mapping'],'chatgpt-plan-responses-v1')

if __name__=='__main__':unittest.main(verbosity=2)
