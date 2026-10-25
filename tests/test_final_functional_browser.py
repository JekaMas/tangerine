"""Independent assertions over actual CUA actions, media clock and native reads.

Network-blocked negatives prove browser transport/recovery, not a database outage.
No browser is launched and no model call is dispatched by evidence readback.
"""
from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/final-functional-ux-20261025'
HEADINGS={'library':'A better ear for English.','prepare':'Prepare an exercise','attempts':'Saved attempts','audio':'Saved audio','listen':'Listen and respond','reviews':'Optional LLM review','reports':'Reports and quality experiments','sources':'Sources','settings':'Your LLM connection','recovery':'Recovery and local data','cleanup':'Cleanup and deletion'}
DRAFT='Final review draft: I heard “two ticket”; use “two tickets”.'
DRAFT_ID='0e7d0278-f199-4f79-b5aa-25295e23ce3c'
ANSWER='The second speaker says “two ticket”. It should be “two tickets”, because “ticket” is a countable noun and the number two requires its plural form.'
class FinalFunctionalBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v=json.loads((OUT/'browser-observations.json').read_text());cls.c=cls.v['checks'];cls.read=staticmethod(lambda name:json.loads((OUT/(name+'.json')).read_text()))
 def test_category_catalogue_positive(self):
  x=json.loads((ROOT/'audit/final-functional-ux-20261025/COVERAGE.json').read_text());self.assertEqual(x['family_counts'],{'grammar':51,'lexis':10,'fluency':9,'discourse':10,'pragmatics_register':8});self.assertEqual([len(x['categories']),x['native_written_replay_categories'],x['other_realizations']],[88,83,5])
  options={i['id'] for i in self.read('options-final')['categories'] if not i['control'] and not i['id'].startswith('pronunciation.')};self.assertEqual(options,{r['category_id'] for r in x['categories']})
 def test_audio_limits_negative(self):
  rows=json.loads((ROOT/'audit/final-functional-ux-20261025/COVERAGE.json').read_text())['categories'];states=[r['audio_evidence']['audio']['audio_confirmation'] for r in rows];self.assertEqual([states.count(s) for s in ['confirmed','uncertain','not_realized']],[39,45,4]);self.assertIn('discourse.turn_taking',[r['category_id'] for r in rows if not r['native_mutation_replay_cases']])
 def test_desktop_routes_positive(self):
  self.assertEqual(set(self.v['routes']),set(HEADINGS))
  for route,title in HEADINGS.items():
   row=self.v['routes'][route];self.assertEqual([row['heading'],row['mainCount'],row['viewport']],[title,1,1280]);self.assertIn('Source Sans 3',row['font']);self.assertTrue(row['current'])
 def test_mobile_routes_positive(self):
  self.assertEqual(set(self.v['narrow']),set(HEADINGS))
  for route,title in HEADINGS.items():self.assertEqual([self.v['narrow'][route]['heading'],self.v['narrow'][route]['mainCount'],self.v['narrow'][route]['viewport']],[title,1,390])
 def test_page_overflow_negative(self):
  for group in ['routes','narrow']:
   for row in self.v[group].values():self.assertLessEqual(row['width'],row['viewport'])
  for name in ['prepareOverride320','results320','reports320','cleanup320']:self.assertEqual([self.c[name]['width'],self.c[name]['viewport']],[320,320])
 def test_typography_baseline_positive(self):
  self.assertEqual(self.c['typography']['body'],{'font':'"Source Sans 3", sans-serif','line':'24.65px','size':'17px'});self.assertTrue(self.c['captions320']['loaded'])
 def test_caption_shrinkage_negative(self):
  self.assertEqual(len(self.c['typography']['captions']),9);self.assertEqual(self.c['captions320']['sizes'],['14px']*9);self.assertFalse(self.c['captions320']['overflow'])
 def test_keyboard_navigation_positive(self):
  v=self.c['menu'];self.assertEqual([v['opened'],v['closed'],v['destination'],v['links']],['true','false','Saved attempts',10]);self.assertEqual(v['focus']['outline'],'3px')
 def test_keyboard_focus_positive(self):self.assertEqual(self.c['keyboardFocus'],{'outline':'3px','tag':'SUMMARY','text':'Customize voices and mistakes'})
 def test_prepare_quick_path_positive(self):
  v=self.c['prepareQuick320'];self.assertLess(v['buttonY'],v['viewportHeight']*2);self.assertTrue(v['summaryVisible']);self.assertFalse(v['customizeOpen'])
 def test_prepare_choices_positive(self):
  v=self.c['prepareSelected'];self.assertTrue(v['visible'])
  for s in ['B1','About 200 words','Minor','Collocation, Formality','Australian English','Indian English']:self.assertIn(s,v['summary'])
 def test_prepare_native_request_positive(self):
  posts=self.c['prepareDispatch']['requests'];r=next(p['body']['exercise_request'] for p in posts if p['url'].endswith('/blueprints'));self.assertEqual(r['topic'],'Final review: two colleagues arranging a picnic.');self.assertEqual([r['speaker_count'],r['text_length_words'],r['english_level'],r['mutation_count']],[2,200,'B1',4]);self.assertEqual(r['category_ids'],['lexis.collocation','pragmatics_register.formality']);self.assertEqual(r['severity_levels'],['minor']);self.assertEqual(len(r['speaker_voice_ids']),2);self.assertEqual(r['category_families'],[])
 def test_prepare_interrupted_request_negative(self):self.assertIn('Your choices are retained',self.c['prepareDispatch']['state']['error']);self.assertEqual(self.c['prepareDispatch']['state']['topic'],'Final review: two colleagues arranging a picnic.')
 def test_prepare_override_positive(self):
  v=self.c['prepareOverride'];self.assertEqual(v['formLevel'],'B1');self.assertIn('C1',v['summary']);self.assertIn('None (control)',v['summary']);self.assertTrue(self.c['prepareOverride320']['visible']);self.assertIn('Advanced fields override',self.c['prepareOverride320']['summary'])
 def test_prepare_required_negative(self):self.assertEqual(self.c['prepareRequired'],{'focus':'Topic','missing':True,'posts':0})
 def test_prepare_malformed_negative(self):self.assertEqual(self.c['prepareInvalid'],{'error':'Advanced blueprint is not valid JSON. Your form values are retained.','posts':0})
 def test_prepare_stop_positive(self):self.assertTrue(self.c['prepareStop']['stopEnabled']);self.assertTrue(self.c['prepareStop']['topicDisabled']);self.assertIn('Generation stopped',self.c['prepareStop']['error'])
 def test_prepare_catalogue_failure_negative(self):self.assertEqual([self.c['catalogFailure']['grammar'],self.c['catalogFailure']['topic']],[True,'Keep my choices during a catalogue outage.']);self.assertIn('choices are retained',self.c['catalogFailure']['error'])
 def test_prepare_catalogue_recovery_positive(self):self.assertEqual(self.c['catalogRecovery'],{'categoryChoices':114,'errorCount':0,'grammar':True,'topic':'Keep my choices during a catalogue outage.'})
 def test_failure_reasons_positive(self):
  text=' '.join(self.v['routes']['prepare']['alerts']);self.assertIn('time limit',text);self.assertIn('incomplete or unusable response',text);self.assertIn('selected provider',text);self.assertIn('resume this exercise explicitly',text)
 def test_history_metadata_positive(self):
  v=self.c['history'];self.assertIn('car insurance in us',v['titles']);self.assertTrue(any('picnic' in s for s in v['titles']));self.assertEqual(len(v['links']),len(set(v['links'])));self.assertTrue(any('two tickets' in s for s in v['excerpts']));self.assertTrue(all('T' not in s for s in v['dates']))
 def test_history_native_projection_positive(self):
  rows=self.read('attempts-final');d=next(x for x in rows if x['id']==DRAFT_ID);self.assertEqual(d['answer_excerpt'],DRAFT);self.assertIn('picnic',d['exercise_title']);self.assertEqual(d['state'],'started');demo=next(x for x in rows if x['id']=='4f6bbb22-0dec-487c-a64e-afd05c2902e3');self.assertEqual(demo['answer_excerpt'],ANSWER)
 def test_history_failure_negative(self):self.assertEqual(self.c['historyFailure'],{'error':'Saved attempts are unavailable. Refresh to retry.','links':0})
 def test_history_recovery_positive(self):self.assertEqual(self.c['historyRecovery']['errorCount'],0);self.assertIn('/listen?attempt='+DRAFT_ID,self.c['historyRecovery']['links'])
 def test_audio_history_positive(self):
  self.assertIsNone(self.c['audioRecovery']['globalError']);self.assertGreaterEqual(self.c['audioRecovery']['players'],8);self.assertTrue(all('Exercise ' not in s for s in self.c['audioRecovery']['titles']))
  v=self.c['audioRecovery']['incompleteRecovery'];self.assertEqual(v['href'],'/prepare#saved-preparations');self.assertFalse(v['disabledGenerate']);self.assertIn('Audio: not started',v['text']);self.assertNotIn('kokoro-controlled-v1',v['text']);self.assertEqual(self.c['audioRecovery']['destination']['heading'],'Prepare an exercise')
 def test_audio_history_failure_negative(self):self.assertEqual(self.c['audioFailure'],'Saved audio is unavailable. Refresh to retry.')
 def test_result_hierarchy_positive(self):
  v=self.c['result'];self.assertEqual(v['score'],'Primary score: 60.0 / 100');self.assertEqual(v['scoreSize'],'38px');self.assertLess(v['scoreY'],v['savedAnswerY']);self.assertTrue(v['savedAnswerClosed']);self.assertEqual(v['editableEditors'],0)
 def test_result_optional_explanation_positive(self):self.assertIn('Optional explanation: 100.0%',self.c['result']['summary']);self.assertIn('Found 1 of 2 mistakes · 1 missed · 0 false positives',self.c['result']['summary']);self.assertIn('Missing explanations do not reduce',self.c['result']['summary'])
 def test_result_immutable_copyable_positive(self):self.assertEqual(self.c['savedAnswerCopyable'],{'answer':ANSWER,'disabled':False,'language':'en','readOnly':True});self.assertTrue(self.c['result']['readOnly'])
 def test_draft_save_reopen_positive(self):
  self.assertEqual([self.c['draftBefore']['answer'],self.c['draftReopen']['answer']],[DRAFT,DRAFT]);self.assertEqual(self.c['draftBefore']['notice'],'Draft saved.');self.assertTrue(self.c['draftReopen']['editable']);self.assertIn(DRAFT_ID,self.c['draftReopen']['url'])
 def test_draft_no_automatic_submission_negative(self):
  d=self.read('test-draft-final');self.assertIsNone(d['submitted_at']);self.assertEqual(d['state'],'started');self.assertEqual(d['answer_text'],DRAFT);self.assertTrue(self.c['draftBefore']['submitEnabled'])
 def test_replay_actual_range_positive(self):
  a,b=self.c['replayStart'],self.c['replayEnd'];self.assertFalse(a['paused']);self.assertGreaterEqual(a['current'],5.5);self.assertLess(a['current'],8);self.assertTrue(b['paused']);self.assertGreaterEqual(b['current'],12.25);self.assertLess(b['current'],12.65)
 def test_replay_literal_keyboard_positive(self):
  a,b=self.c['replayLiteralStart'],self.c['replayLiteralEnd'];self.assertFalse(a['paused']);self.assertGreaterEqual(a['current'],9.59);self.assertLess(a['current'],11);self.assertTrue(b['paused']);self.assertGreaterEqual(b['current'],14.839);self.assertLess(b['current'],15.239);self.assertEqual(a['buttonCount'],5)
 def test_replay_old_range_cancelled_negative(self):self.assertGreater(self.c['replayReplace']['current'],31.488);self.assertFalse(self.c['replayReplace']['paused']);self.assertGreater(self.c['replayManualSeekAfter']['current'],14.839);self.assertFalse(self.c['replayManualSeekAfter']['paused'])
 def test_replay_failure_negative(self):self.assertIn('Your answer is retained',self.c['replayFailure']['error']);self.assertEqual(self.c['replayFailure']['answer'],ANSWER);self.assertEqual(self.c['replayFailure']['score'],'Primary score: 60.0 / 100')
 def test_replay_recovery_positive(self):self.assertEqual(self.c['replayRecovery'],{'errors':0,'paused':True,'ready':4,'score':'Primary score: 60.0 / 100'})
 def test_no_autoplay_negative(self):self.assertTrue(self.c['result']['paused']);self.assertTrue(self.c['draftReopen']['audioPaused']);self.assertTrue(self.c['draftBefore']['audioPaused'])
 def test_starter_report_positive(self):
  self.assertEqual(self.c['starterReport']['errors'],[]);self.assertEqual(self.c['starterReport']['title'],'Final functional review · constructed collocation report');self.assertIn('2 annotated windows; 0 unannotated',self.c['starterReport']['text'])
 def test_starter_native_report_arithmetic_positive(self):
  item=next(x for x in self.read('reports-final') if x['title']=='Final functional review · constructed collocation report');full=self.read('constructed-report-final');self.assertEqual(full['id'],item['id']);r=full['report'];leaf=next(x for x in r['leaves'] if x['id']=='lexis.collocation');self.assertEqual(leaf['events'],1)
  for name,expected in [('event_share',('1','1')),('window_prevalence',('1','2')),('opportunity_rate',('1','2')),('per_1000_tokens',('125','1'))]:self.assertEqual((leaf[name]['exact']['numerator'],leaf[name]['exact']['denominator']),expected)
  self.assertEqual(full['difficulty']['trials'],0);self.assertEqual(r['population']['label_origin'],'constructed')
 def test_starter_experiment_no_calls_negative(self):
  self.assertEqual(self.c['starterExperiment']['statuses'],['planned · 0/1 completed']);self.assertEqual(self.c['starterExperiment']['errors'],[]);runs=self.read('experiments-final');r=next(x for x in runs if x['id']==self.read('starter-experiment-final')['id']);self.assertEqual(r['status'],'planned');full=self.read('starter-experiment-final');self.assertEqual(len(full['rows']),1);self.assertEqual(full['rows'][0]['status'],'not_run');self.assertEqual(full['rows'][0]['receipt_ids'],[]);self.assertEqual(self.read('starter-dataset-final')['cases'][0]['taxonomy_ids'],['grammar.verbs.subject_verb_agreement']);self.assertEqual(self.read('starter-input-final')['category_ids'],['grammar.verbs.subject_verb_agreement']);self.assertEqual(self.read('starter-configuration-final')['stage_profiles']['case_generation'],'local-generation');self.assertEqual(self.read('starter-configuration-final')['stage_profiles']['claim_mapping'],'chatgpt-plan-responses-v1')
 def test_starter_scope_filter_positive(self):self.assertEqual(self.c['reportScope'],{'rows':1,'text':'lexis.collocation\t1\t1/1\t1/2\t1/2\t125/1'});self.assertEqual(self.c['reportAll'],{'rows':122,'unknown':True})
 def test_starter_invalid_json_negative(self):self.assertEqual(self.c['reportInvalid'],{'error':'Report definition is not valid JSON. Your input is retained.','posts':0,'retained':'{'})
 def test_starter_failure_negative(self):self.assertIn('Retry or open Settings',self.c['starterFailure']['error']);self.assertIn('input is retained',self.c['starterFailure']['error'])
 def test_starter_recovery_positive(self):self.assertEqual(self.c['starterRecovery']['topic'],'Keep my experiment topic on retry.');self.assertEqual(self.c['starterRecovery']['errorCount'],0);self.assertGreater(self.c['starterRecovery']['profiles'],1)
 def test_cleanup_named_record_positive(self):self.assertEqual(self.c['cleanupSelection'],{'applyVisible':False,'selected':['Select attempts '+DRAFT_ID]})
 def test_cleanup_preview_shared_media_negative(self):
  v=self.c['cleanupPreview'];self.assertEqual(v['status'],'preview · 4 documents · 0 private objects');self.assertTrue(v['applyDisabled']);self.assertEqual(v['errors'],[]);details=json.loads(v['details'][0]);self.assertEqual(details['heads'],[DRAFT_ID]);self.assertEqual(details['assets'],[]);self.assertNotIn('3f4535dd-6210-4303-9c33-209e19016b55',details['documents'])
 def test_cleanup_selection_invalidates_negative(self):self.assertEqual(self.c['cleanupChanged'],{'applyVisible':False,'previewDisabled':True,'previewVisible':False})
 def test_cleanup_failure_retains_identity_negative(self):self.assertEqual(self.c['cleanupFailure']['ids'],DRAFT_ID);self.assertIn('selection is retained',self.c['cleanupFailure']['error'])
 def test_cleanup_recovery_positive(self):self.assertEqual(self.c['cleanupRecovery'],{'apply':False,'errors':0,'selected':['Select attempts '+DRAFT_ID]})
 def test_library_failure_negative(self):self.assertIn('local service',self.c['libraryFailure'])
 def test_library_recovery_positive(self):self.assertEqual(self.c['libraryRecovery'],{'entries':8,'errors':0})
 def test_source_transport_failure_negative(self):self.assertEqual(self.c['sourcesTransport'],['Could not reach the local service. Refresh saved state to check the outcome before retrying.']);self.assertEqual(self.c['sourcesTransportRecovery'],0)
 def test_settings_transport_recovery_positive(self):self.assertEqual(self.c['settingsTransport']['errors'],['Could not reach the local service. Refresh saved state to check the outcome before retrying.']);self.assertEqual(self.c['settingsRecovery'],{'errors':0,'title':'Your LLM connection'})
 def test_review_selection_positive(self):self.assertTrue(self.c['reviewSelection']['button']);self.assertEqual(self.c['reviewSelection']['errors'],[]);self.assertIn('case=ac41ec80-43f3-45cd-ae4f-b37bf57d0bdc',self.c['reviewSelection']['url'])
 def test_source_and_recovery_paths_positive(self):
  self.assertEqual(self.c['sources']['errors'],[]);self.assertEqual(self.c['recovery']['errors'],[])
  for s in ['database: ready','speech: ready','storage: ready']:self.assertIn(s,self.c['recovery']['text'])
 def test_original_user_data_unchanged_negative(self):
  self.assertEqual(self.read('original-attempt-before'),self.read('original-attempt-final'));self.assertEqual(self.read('configuration-before')['configuration'],self.read('configuration-final')['configuration'])
 def test_native_creation_dates_positive(self):
  p=next(x for x in self.read('preparations-final')['items'] if x['id']=='9a824669-74d2-4470-a23e-f602a299253c');self.assertTrue(p['created_at'].startswith('2026-10-25'));l=next(x for x in self.read('library-final') if x['id']=='ac41ec80-43f3-45cd-ae4f-b37bf57d0bdc');self.assertEqual(l['created_at'],'2026-10-25T14:47:13.526666Z')

if __name__=='__main__':unittest.main(verbosity=2)
