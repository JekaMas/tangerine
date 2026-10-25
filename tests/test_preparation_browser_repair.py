"""Independent expectations over actual CUA interactions and controlled HTTP.

Synthetic service outcomes prove frontend behavior only. No real generation,
provider, storage or acoustic acceptance is claimed.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-18-verification-20261026'

class PreparationBrowserRepair(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=json.loads((DATA/'repair-observations.json').read_text())
        cls.records=[json.loads(line) for line in (DATA/'requests.jsonl').read_text().splitlines()]

    def events(self,scenario,method=None,path=None):
        return [e for e in self.records if e.get('scenario')==scenario and (method is None or e['method']==method) and (path is None or e['path']==path)]

    def test_malformed_summary_negative(self):
        for row in self.v['malformed']:
            self.assertEqual(row['input'],json.loads(row['advanced']))
            self.assertEqual('Two friends plan a picnic.',row['topic'])
            self.assertTrue(row['generateEnabled'])
            self.assertNotIn('This page couldn’t load',row['summary'])
            self.assertNotIn('[object Object]',row['summary'])
            self.assertIn('Check',row['summary'])
            self.assertFalse(row['overflow'])

    def test_advanced_native_positive(self):
        r=self.v['advancedValid']
        self.assertEqual({'Speakers':'2','Length':'About 90 words','English level':'C1','Mistakes':'None (control)','Severity':'Any severity'},r['fields'])
        self.assertEqual('',r['topic'])
        self.assertTrue(all(c['disabled'] for c in r['native']['controls']))
        posts=self.events('advanced-valid-native','POST')
        self.assertEqual(1,len(posts))
        self.assertEqual({'topic':'Advanced picnic request','speaker_count':2,'text_length_words':90,'english_level':'C1','category_families':[],'mutation_count':0},posts[0]['body']['exercise_request'])

    def test_clear_restores_validation_negative(self):
        r=self.v['cleared']
        self.assertEqual('',r['advanced'])
        self.assertTrue(r['enabled'])
        self.assertEqual({'name':'Topic','missing':True},r['focus'])
        self.assertEqual(1,len(self.events('advanced-valid-native','POST')))

    def test_transient_read_positive(self):
        self.assertTrue(self.v['transient']['voiceEnabled'])
        for path in ['/api/v1/preparations','/api/v1/preparation-options']:
            self.assertEqual(2,len(self.events('transient-read','GET',path)))
        self.assertNotIn('private trace',self.v['transient']['body'])
        self.assertEqual([],self.events('transient-read','POST'))

    def test_bounded_read_failure_negative(self):
        r=self.v['persistentFinal']
        self.assertFalse(r['voiceEnabled'])
        self.assertTrue(r['generateEnabled'])
        self.assertIn('Retry categories',r['body'])
        self.assertIn('Refresh',r['body'])
        self.assertNotIn('private trace',r['body'])
        for path in ['/api/v1/preparations','/api/v1/preparation-options']:
            self.assertEqual(3,len(self.events('persistent-final','GET',path)))
        self.assertEqual([],self.events('persistent-final','POST'))

    def test_explicit_read_recovery_positive(self):
        r=self.v['recoveredFinal']
        self.assertEqual('Retained after catalogue error',r['topic'])
        self.assertTrue(r['voiceEnabled'])
        self.assertNotIn('are unavailable',r['body'])
        self.assertEqual([],self.events('recovered-final','POST'))

    def test_service_response_negative(self):
        r=self.v['html']
        self.assertEqual('Retained picnic topic',r['topic'])
        self.assertIn('local service returned an unreadable response',r['alert'])
        for technical in ['JSON','SQL','password','<html>']:
            self.assertNotIn(technical,r['alert'])
        self.assertEqual(1,len(self.events('html-recovery','POST')))

    def test_primary_error_preserved_negative(self):
        self.assertIn('Set up the selected local speech model',self.v['primary']['alert'])
        self.assertEqual(3,len(self.events('primary-error-and-list-failure','GET','/api/v1/preparations')))
        self.assertEqual(1,len(self.events('primary-error-and-list-failure','POST')))

    def test_write_lifecycle_positive(self):
        self.assertFalse(self.v['busy']['buttonEnabled'])
        self.assertFalse(self.v['busy']['topicEnabled'])
        self.assertEqual('Exercise saved. Open the Library to listen and answer.',self.v['success']['notice'])
        for scenario in ['controlled-success','feedback-success','stop-generation']:
            posts=self.events(scenario,'POST')
            self.assertEqual(['/api/v1/blueprints','/api/v1/candidates:generate'],[p['path'] for p in posts])
            self.assertEqual(2,len({p['idempotency_key'] for p in posts}))
        self.assertIn('Resume explicitly',self.v['stopped']['message'])
        self.assertTrue(self.v['stopped']['generateEnabled'])

    def test_feedback_visible_positive(self):
        for key in ['feedbackAfter','mobileFeedback']:
            r=self.v[key]
            self.assertLess(r['action']['bottom'],r['error']['top'])
            self.assertLessEqual(r['error']['top']-r['action']['bottom'],32)
            self.assertLessEqual(r['error']['bottom'],r['height'])
            self.assertEqual('16px',r['error']['size'])
        for key in ['busyFeedback','successFeedback']:
            self.assertLess(self.v[key]['bottom'],844)

    def test_effective_amount_help_positive(self):
        r=self.v['densityHelp']
        self.assertEqual('4',r['fields']['Mistakes'])
        self.assertIn('4 mistakes requested in approximately 400 words.',r['help'])
        self.assertEqual([],self.events('density-help','POST'))

    def test_current_typography_positive(self):
        r=self.v['typography']
        self.assertEqual('17px',r['body']['size'])
        self.assertEqual('24.65px',r['body']['line'])
        self.assertEqual('loaded',r['fontStatus'])
        self.assertFalse(r['overflow'])
        self.assertEqual(['14px']*9,[c['size'] for c in r['captions']])
        for c in r['captions']:
            self.assertLessEqual(c['scrollWidth'],c['width']+1)

if __name__=='__main__':
    unittest.main(verbosity=2)
