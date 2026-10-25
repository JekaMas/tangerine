"""Literal I18 oracles over actual source-built CUA interactions.

The test gateway controls all writes and forwards only reads of saved local
records. No new generation, native storage write or provider quality is claimed.
"""
import copy
import importlib.util
import json
import os
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/os.environ.get('TANGERINE_I18_DATA','data/iteration-18-preparation-20261026')
AUDIT=ROOT/'audit/iteration-18-preparation-20261026'
REVIEW_RECORD=ROOT/os.environ.get('TANGERINE_I18_REVIEW','audit/iteration-18-preparation-20261026/REVIEW.json')
spec=importlib.util.spec_from_file_location('i18_review',AUDIT/'review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
class CompletionI18(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=json.loads((DATA/'observations.json').read_text())
        cls.c=cls.v['cases']
        cls.events=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]
        for path in cls.v.get('retained_request_evidence',[]):
            cls.events.extend(json.loads(x) for x in (ROOT/path).read_text().splitlines())
    def test_override_positive(self):
        rows=self.c['overrideWidths'];self.assertEqual([1280,960,390,320],[r['viewport'] for r in rows])
        for r in rows:
            self.assertEqual(['B1','C1','None (control)'],[r['formLevel'],r['fields']['English level'],r['fields']['Mistakes']])
            self.assertIn('Recurring patterns disabled',r['summary']);self.assertNotIn('target 85%',r['summary'])
            self.assertLess(r['summary'].index('Speaker 1: Australian English'),r['summary'].index('Speaker 2: British English'))
            self.assertFalse(r['overflow'])
        self.assertFalse(any(e['method']=='POST' and e.get('scenario')=='override-inspection' for e in self.events))
    def test_simple_positive(self):
        r=self.c['simple'];self.assertEqual({'Speakers':'2','Length':'About 90 words','English level':'B1','Mistakes':'2','Severity':'Minor'},r['fields'])
        self.assertIn('Number, Collocation',r['summary']);self.assertEqual(['bf_emma','melo_en_au'],r['voices'])
        posts=self.c['simplePosts'];self.assertEqual(1,len(posts));self.assertEqual('/api/v1/blueprints',posts[0]['path'])
        self.assertEqual({'topic':'Iteration 18: planning a picnic.','speaker_count':2,'text_length_words':90,'english_level':'B1','category_families':[],'mutation_count':2,'speaker_voice_ids':['bf_emma','melo_en_au'],'category_ids':['grammar.nouns.number','lexis.collocation'],'severity_levels':['minor']},posts[0]['body']['exercise_request'])
    def test_invalid_advanced_negative(self):
        r=self.c['invalidAdvanced'];self.assertEqual('{',r['advanced']);self.assertEqual({},r['fields'])
        self.assertIn('Advanced blueprint is not valid JSON',r['summary']);self.assertNotIn('None (control)',r['summary']);self.assertNotIn('C1',r['summary'])
        self.assertEqual([],self.c['invalidAdvancedPosts'])
        self.assertIn('Check the advanced blueprint values',self.c['invalidSpeaker']['summary']);self.assertEqual({},self.c['invalidSpeaker']['fields'])
    def test_cleared_override_negative(self):
        r=self.c['clearedOverride'];self.assertEqual('',r['advanced']);self.assertEqual(['B1','2'],[r['fields']['English level'],r['fields']['Mistakes']])
        self.assertNotIn('Advanced fields override',r['summary']);self.assertNotIn('None (control)',r['summary']);self.assertIn('target 85%',r['summary'])
    def test_simple_path_positive(self):
        self.assertFalse(any(e['method']=='POST' and not e.get('scenario') for e in self.events))
        self.assertEqual([1280,390,320],[r['viewport'] for r in self.c['quick']])
        for r in self.c['quick']:
            self.assertFalse(r['customizeOpen']);self.assertTrue(r['geometry']['summaryBeforeAction']);self.assertLess(r['geometry']['actionY'],2*r['geometry']['viewportHeight'])
            self.assertIn('Configured defaults for each speaker',r['summary']);self.assertTrue(r['generateEnabled']);self.assertEqual('Short picnic request.',r['retainedTopic'])
            posts=[e for e in self.events if e.get('scenario')=='quick-'+str(r['viewport']) and e['method']=='POST'];self.assertEqual(1,len(posts))
            self.assertEqual({'topic':'Short picnic request.','speaker_count':1,'text_length_words':150,'english_level':None,'category_families':[],'mutation_count':None},posts[0]['body']['exercise_request'])
    def test_expanded_options_positive(self):
        a,b,c=[self.c[k] for k in ['expandedBefore','expandedClosed','expandedAfter']]
        self.assertEqual([True,False,True],[r['customizeOpen'] for r in [a,b,c]])
        for r in [b,c]:
            for field in ['fields','voices','recurring','summary','topic']:self.assertEqual(a[field],r[field])
        self.assertTrue(c['recurring']);self.assertIn('target 85%',c['summary']);self.assertEqual('#saved-preparations',self.c['savedAnchor']['url'])
    def test_focus_negative(self):
        r=self.c['required'];self.assertEqual('Topic',r['focused']);self.assertTrue(r['missing']);self.assertGreater(r['top'],r['headerBottom']);self.assertLessEqual(r['bottom'],r['viewportHeight'])
        self.assertFalse(any(e['method']=='POST' and (e.get('scenario') or '').startswith('required-validation') for e in self.events))
        self.assertGreater(self.c['savedAnchor']['top'],self.c['savedAnchor']['headerBottom'])
        self.assertEqual(12,len(self.c['keyboard']))
        for step in self.c['keyboard']:
            self.assertNotEqual('BODY',step['tag']);self.assertGreaterEqual(step['top'],step['headerBottom']);self.assertLess(step['top']+24,step['viewportHeight']);self.assertEqual('3px',step['outline'])
        self.assertEqual('Generate exercise',self.c['keyboard'][4]['name']);self.assertEqual('Advanced blueprint',self.c['keyboard'][-1]['name'])
    def test_zero_negative(self):
        r=self.c['zero'];self.assertFalse(r['customizeOpen']);self.assertEqual('None (control)',r['fields']['Mistakes']);self.assertIn('Recurring patterns disabled',r['summary']);self.assertTrue(r['recurring'])
        posts=self.c['zeroPosts'];self.assertEqual(1,len(posts));q=posts[0]['body']['exercise_request'];self.assertEqual(0,q['mutation_count']);self.assertEqual(['grammar.nouns.number','lexis.collocation'],q['category_ids']);self.assertEqual(85,q['recurring_errors'][0]['target_percent'])
    def test_type_positive(self):
        self.assertEqual([1100,390,320],[x['width'] for x in self.c['captionWidths']])
        for row in self.c['captionWidths']:
            self.assertEqual([],review.readability_issues(row));self.assertEqual(['14px']*9,[n['size'] for n in row['nodes']]);self.assertEqual('24.65px',row['body']['line']);self.assertIn('Source Sans 3',row['body']['font'])
            self.assertEqual(['LLM chooses','1 per 100 words','2 per 100 words','4 per 100 words','Your number'],[n['text'] for n in row['nodes'][:5]])
        self.assertTrue(all(r['pressed']=='true' for r in self.c['captionPresets']));self.assertEqual(['Automatic','2','3','6','6'],[r['fields']['Mistakes'] for r in self.c['captionPresets']])
    def test_wrap_positive(self):
        row=self.c['captionWidths'][-1];self.assertEqual(320,row['width']);self.assertFalse(row['overflow'])
        for node in row['nodes'][5:]:
            self.assertGreater(len(node['text']),35);self.assertGreaterEqual(node['height'],1.9*review.px(node['line']));self.assertLessEqual(node['scrollWidth'],node['width']+1)
    def test_tiny_type_negative(self):
        tiny=self.c['tinyCaptions'];self.assertEqual([10]*5,[review.px(n['size']) for n in tiny['nodes'][:5]]);self.assertTrue(review.readability_issues(tiny));self.assertEqual([],review.readability_issues(self.c['captionsRestored']))
    def test_hierarchy_negative(self):
        r=self.c['hierarchy'];self.assertEqual(['BUTTON','Medium\n2 per 100 words','3px','Low\n1 per 100 words'],[r['tag'],r['focus'],r['outline'],r['lowSelected']]);self.assertEqual('17px',r['bodySize']);self.assertGreater(review.px(r['titleSize']),24);self.assertFalse(r['overflow'])
        self.assertEqual([],review.readability_issues(self.c['captionWidths'][-1]))
    def packet(self):return json.loads(REVIEW_RECORD.read_text())
    def errors(self,p,facts=None,submitted=None):return review.review_errors(p,facts or self.c['captionsRestored'],self.c['simple'],submitted or self.c['simplePosts'][0]['body']['exercise_request'])
    def test_review_positive(self):self.assertEqual([],self.errors(self.packet()))
    def test_ux_omission_negative(self):
        p=self.packet();p.pop('ui_ux');self.assertTrue(self.errors(p))
        p=self.packet();p['ui_ux']={'disposition':'pass','reason':'Build and pictures'};self.assertTrue(self.errors(p))
    def test_typography_omission_negative(self):
        p=self.packet();p.pop('typography');self.assertTrue(self.errors(p));self.assertTrue(self.errors(self.packet(),facts=self.c['tinyCaptions']))
    def test_evidence_mismatch_negative(self):
        q=copy.deepcopy(self.c['simplePosts'][0]['body']['exercise_request']);q['topic']='A different exercise';self.assertTrue(self.errors(self.packet(),submitted=q))
        for field,value in [('unexecuted_cases',['planned-case']),('reference_origin','candidate-generated gold'),('new_model_calls',50),('performance_campaigns','required')]:
            p=self.packet();p[field]=value;self.assertTrue(self.errors(p))
if __name__=='__main__':unittest.main(verbosity=2)
