"""Exact I28 oracles over native storage/browser observations, with no dispatch.

Actual Go/JS tests and native HTTP execution are retained with their proof scopes;
these observers do not fabricate a new provider run or a genuine population.
"""
import copy
import json
from pathlib import Path
import unittest
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-28-reports-20261026'
AUDIT=ROOT/'audit/iteration-28-reports-20261026'
A='grammar.verbs.subject_verb_agreement'
B='lexis.collocation'


def read(name): return json.loads((DATA/name).read_text())
def events(name): return [json.loads(x) for x in (DATA/name).read_text().splitlines() if x.startswith('{')]
def passed(name): return {x.get('Test') for x in events(name) if x['Action']=='pass'}
def normalize(value): return ' '.join(value.split())
def selected(url): return parse_qs(urlparse(url).query)['report'][0]


def review_errors(packet, facts):
    """Development evidence disposition only; never a runtime product gate."""
    errors=[]
    for part in ['ui_ux','typography','evidence']:
        if not packet.get(part,{}).get('observations') or not packet.get(part,{}).get('references'):
            errors.append(part+' unsupported')
    if packet.get('report_id')!=selected(facts['cases']['selectedReloadFinal']['url']): errors.append('report identity')
    if packet.get('reference_origin')!='independently authored literal expectations': errors.append('reference origin')
    if packet.get('unexecuted_cases')!=[]: errors.append('unexecuted claim')
    if packet.get('new_model_calls')!=0 or packet.get('new_synthesis_calls')!=0: errors.append('new provider execution')
    if packet.get('performance_campaigns')!='excluded': errors.append('excluded campaign')
    rows=facts['layouts']
    if {(r['width'],r['height']) for r in rows}!={(1280,720),(390,844),(320,740)}: errors.append('layout scope')
    for row in rows:
        if row['pageWidth']!=row['width'] or row['size']!='17px' or row['line']!='24.65px' or not row['fontLoaded']: errors.append('readability')
        if any(float(size.removesuffix('px'))<13 for size in row['counts']): errors.append('caption readability')
    if facts['metadataAlignment']!='left': errors.append('metadata alignment')
    if packet.get('browser_file_delivery_claimed'): errors.append('unobserved file receipt')
    return errors


class CompletionI28(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts=read('browser-observations.json');cls.c=cls.facts['cases']
        cls.requests=events('browser-requests.jsonl')

    def native(self,name):
        receipt='native-pair-green.jsonl' if name in ['TestNativeSavedReportDifficultyPositive','TestNativeSavedReportSelfFollowupNegative','TestNativeSavedReportFollowupOriginsNegative'] else 'native-red.jsonl'
        self.assertIn(name,passed(receipt))
        if receipt=='native-red.jsonl':
            self.assertEqual({'TestNativeSavedReportSelfFollowupNegative'}, {e['Test'] for e in events(receipt) if e['Action']=='fail' and e.get('Test')})
        else:self.assertFalse([e for e in events(receipt) if e['Action'] in ['fail','skip']])

    def test_empirical_positive(self):
        self.native('TestNativeSavedReportExposurePositive')
        report=read('exposure-report.json')['report'];self.assertEqual('constructed',report['population']['label_origin'])
        self.assertEqual((10,50,2,122),(report['annotated_windows'],report['inspected_native_tokens'],report['eligible_events'],len(report['leaves'])))
        leaf=next(x for x in report['leaves'] if x['id']==A)
        self.assertEqual((2,8),(leaf['events'],leaf['controls']))
        self.assertEqual(('2','10',{'numerator':'1','denominator':'5'}),tuple(leaf['opportunity_rate'][k] for k in ['numerator','denominator','exact']))

    def test_empirical_negative(self):
        self.native('TestNativeSavedReportMissingNegative');self.native('TestNativeSavedReportZeroDenominatorNegative')
        report=read('missing-report.json');self.assertEqual((0,[]),(report['observed_windows'],report['annotated_leaf_ids']))
        self.assertTrue(all(x['window_prevalence']['exact'] is None and x['opportunity_rate']['exact'] is None for x in report['leaves']))

    def test_mapping_negative(self): self.native('TestNativeSavedReportMappingNegative')

    def test_relationships_positive(self):
        self.native('TestNativeSavedReportRelationshipsPositive')
        report=read('relationships-report.json');self.assertEqual(2,len(report['pairs']))
        for pair in report['pairs']:
            self.assertEqual({'numerator':'1','denominator':'4'},pair['support']['exact'])
            self.assertEqual({'numerator':'1','denominator':'2'},pair['conditional']['exact'])
            self.assertEqual({'numerator':'1','denominator':'1'},pair['lift']['exact'])
        self.assertEqual([('2','3'),('1','3')],[(r['row_proportion']['numerator'],r['row_proportion']['denominator']) for r in report['confusion']])

    def test_secondary_negative(self): self.native('TestNativeSavedReportSecondaryNegative')
    def test_attempt_origins_negative(self): self.native('TestNativeSavedReportAttemptOriginsNegative')

    def test_difficulty_positive(self):
        self.native('TestNativeSavedReportDifficultyPositive')
        d=read('difficulty-fixture.json');self.assertEqual((2,1,'unrated','insufficient_sample'),(d['trials'],d['successes'],d['rating'],d['missing_reason']))
        self.assertEqual({'numerator':'1','denominator':'1'},d['paired_success_change']['exact'])

    def test_self_followup_negative(self):
        self.native('TestNativeSavedReportSelfFollowupNegative')
        self.assertIn('one observation became an independent before/after pair',(DATA/'native-red.jsonl').read_text())
        self.assertIn('TestEmpiricalFollowupPositive',passed('retained-followup-green.jsonl'))

    def test_followup_sources_negative(self):
        self.native('TestNativeSavedReportFollowupOriginsNegative')
        for child in ['constructed_before','other_participant','missing_before','unknown_outcome']:
            self.assertIn('TestNativeSavedReportFollowupOriginsNegative/'+child,passed('native-pair-green.jsonl'))

    def test_persistence_positive(self): self.native('TestNativeSavedReportPersistencePositive')

    def test_existing_report_replay_positive(self):
        self.native('TestNativeSavedReportExistingReplayPositive')
        old=read('saved-fadbb119-258f-4045-810b-a0abab20f26a.json');new=read('reproduced-existing-report.json')
        self.assertEqual(old['report']['report'],new['report']);self.assertEqual(old['report']['difficulty'],new['difficulty'])
        self.assertEqual([],old['submission']['attempts'])

    def test_coverage_positive(self):
        self.native('TestNativeSavedCoveragePositive')
        coverage=read('constructed-quality-coverage.json');self.assertEqual(122,len(coverage))
        row=next(x for x in coverage if x['taxonomy_id']==A)
        self.assertEqual((1,1,2,False),tuple(row[k] for k in ['positive_cases','negative_cases','completed_rows','missing']))

    def test_planned_coverage_negative(self):
        self.native('TestNativeSavedCoveragePlannedNegative')
        coverage=read('saved-planned-coverage.json');self.assertEqual(122,len(coverage))
        self.assertTrue(all(row['completed_rows']==0 and row['missing'] for row in coverage))
        for item in read('saved-experiments.json'):
            saved=read('experiment-'+item['id']+'.json');self.assertEqual('planned',saved['experiment']['status'])
            self.assertTrue(all(c['origin']=='constructed' for c in saved['dataset']['cases']))

    def test_zero_dispatch_negative(self):
        self.native('TestNativeSavedReportZeroDispatchNegative')
        self.assertEqual({'provider_receipts':0,'llm_or_speech_operations':0},read('zero-dispatch.json'))
        self.assertEqual(0,read('browser-final.json')['provider_receipts'])
        self.assertIn('TestSavedReportsBrowserFixture',passed('browser-native.jsonl'))
        self.assertFalse([r for r in self.requests if r['forbidden']])
        self.assertEqual({'/api/v1/reports/empirical'},{r['path'] for r in self.requests if r['method']=='POST'})

    def test_display_positive(self):
        log=(DATA/'presentation-green.log').read_text()
        for name in ['exact_denominator_positive','selected_provenance_positive','coverage_positive','difficulty_population_positive']:
            self.assertRegex(log,r'(?m)^✔ '+name+r' \(')
        self.assertIn('ℹ pass 10',log);self.assertIn('ℹ fail 0',log)
        self.assertIn('ℹ skipped 0',log)

    def test_display_negative(self):
        log=(DATA/'presentation-green.log').read_text()
        for name in ['zero_denominator_negative','unknown_exposure_negative','constructed_origin_negative','missing_provenance_negative','uninspected_zero_negative','no_technical_reason_negative']:
            self.assertRegex(log,r'(?m)^✔ '+name+r' \(')

    def test_browser_population_positive(self):
        value=self.c['selectedReloadFinal'];self.assertEqual([],value['alerts'])
        text=normalize(value['report']);self.assertIn('10 fully inspected mapped windows',text)
        self.assertIn('1 of 122 categories inspected for absence',text)
        self.assertEqual([A+'\t2\n8 correct controls · 0 secondary labels\n\t1/1\n2 / 2\n\t1/5\n2 / 10\n\t1/5\n2 / 10\n\t40/1\n2000 / 50'],value['rows'])
        self.assertIn('constructed-ten-exposures-v1',text)

    def test_browser_selection_positive(self):
        a,b=self.c['selectedURLFinal'],self.c['selectedReloadFinal']
        self.assertEqual(selected(a['url']),selected(b['url']));self.assertEqual(a['report'],b['report'])
        self.assertIn('Reproduced: preserved selection after input correction',b['report'])
        posts=[r for r in self.requests if r['method']=='POST'];self.assertEqual(3,len(posts))
        first=posts[0];self.assertEqual('constructed',first['body']['input']['population']['label_origin'])
        self.assertEqual(10,len(first['body']['input']['windows']))

    def test_browser_origins_negative(self):
        for name in ['selectedReloadFinal','relationshipsFinal','unknownAllCategories']:
            text=self.c[name]['report'];self.assertIn('Constructed observations.',text);self.assertIn('do not measure real learner frequencies',text)

    def test_browser_unknown_negative(self):
        c=self.c['unknownAllCategories'];self.assertEqual(122,len(c['rows']))
        self.assertTrue(all('No eligible observations' in row and 'Not annotated' in row for row in c['rows']))
        self.assertIn('No eligible independent first answers were recorded.',c['report'])
        self.assertEqual(0,len(self.c['unknownPopulation']['rows']))

    def test_browser_relationships_positive(self):
        c=self.c['relationshipsFinal'];tables={t['name']:t['rows'] for t in c['tables']}
        self.assertEqual([A+'\t'+B+'\t1\t1/4\n1 / 4\n\t1/2\n1 / 2\n\t1/1\n4 / 4',B+'\t'+A+'\t1\t1/4\n1 / 4\n\t1/2\n1 / 2\n\t1/1\n4 / 4'],tables['Category relationships'])
        self.assertEqual([A+'\t'+A+'\t2\t2/3\n2 / 3',A+'\tunknown\t1\t1/3\n1 / 3'],tables['Reference prediction confusion'])
        text=normalize(c['report']);self.assertIn('1 successful outcomes / 2 eligible independent first answers',text)
        self.assertIn('At least 100 independent first answers are needed',text)
        self.assertIn('9.5%–90.5%',text);self.assertIn('does not establish that recommendations caused improvement',text)

    def test_browser_invalid_definition_negative(self):
        c=self.c['invalidDefinition'];self.assertEqual(['Report definition is not valid JSON. Your input is retained.'],c['alerts'])
        self.assertIn('Constructed relationships',c['report'])
        self.assertEqual('{invalid',next(f['value'] for f in c['fields'] if f['label']=='Report definition'))
        self.assertEqual([],self.c['savedAfterInputError']['alerts'])

    def test_browser_read_recovery_positive(self):
        requests=[r for r in self.requests if r['scenario']=='transient-report-read' and r['path'].count('/')==5]
        self.assertEqual([503,503,200],[r['status'] for r in requests])
        self.assertEqual([],self.c['transientRecovered']['alerts'])
        self.assertEqual(self.c['savedAfterInputError']['report'],self.c['transientRecovered']['report'])

    def test_browser_persistent_negative(self):
        c=self.c['persistentError'];self.assertTrue(c['refreshEnabled'])
        self.assertEqual(['Reports are temporarily unavailable. Your inputs and saved observations are retained. Refresh to continue.'],c['alerts'])
        self.assertNotIn('private backend detail',c['main'])
        requests=[r for r in self.requests if r['scenario']=='persistent-report-read' and r['path'].count('/')==5]
        self.assertEqual([503,503,503],[r['status'] for r in requests])
        recovered=self.c['explicitRecovery'];self.assertEqual([],recovered['alerts']);self.assertEqual(c['report'],recovered['report']);self.assertEqual(c['fields'],recovered['fields'])

    def test_browser_missing_saved_negative(self):
        c=self.c['missingSavedReport'];self.assertEqual(['This saved item is no longer available. Choose another saved item or create a new one.'],c['alerts'])
        self.assertNotIn('report',c);self.assertEqual([],self.c['missingSavedRecovery']['alerts'])
        self.assertIn('Constructed: two mistakes in ten exposures',self.c['missingSavedRecovery']['report'])

    def test_browser_keyboard_positive(self):
        a,b=self.c['tableKeyboardFocus'],self.c['tableKeyboardScroll']
        self.assertEqual(('TABLE','3px'),(a['active']['tag'],a['active']['outline']))
        self.assertEqual(0,a['categoryTable']['left']);self.assertGreater(b['categoryTable']['left'],0)
        self.assertEqual(284,b['categoryTable']['width']);self.assertGreater(b['categoryTable']['scrollWidth'],284)

    def test_browser_layout_positive(self):
        self.assertEqual([1280,390,320],[r['width'] for r in self.facts['layouts']])
        for r in self.facts['layouts']:
            self.assertEqual(r['width'],r['pageWidth']);self.assertEqual(('17px','24.65px',True),(r['size'],r['line'],r['fontLoaded']))
            self.assertTrue(all(size=='14px' for size in r['counts']))
            self.assertGreaterEqual(r['reportTop'],0);self.assertLess(r['reportTop'],r['height'])
        self.assertEqual('left',self.facts['metadataAlignment'])

    def test_retained_lab_positive(self):
        lab=json.loads((ROOT/'data/iteration-23-gemini-20261026/lab-readback.json').read_text())
        self.assertEqual(('b83631af099449d1baed0ca39881a0f6',0),(lab['run_id'],lab['export_inference_calls']))
        dispatch=json.loads((ROOT/'data/iteration-23-gemini-20261026/live/dispatches.json').read_text());self.assertEqual(6,len(dispatch))
        # This is the retained baseline, including its failed transport. Reading
        # it neither turns that503into success nor dispatches a replacement.
        self.assertEqual([200,503,200,200,200,200],[r['http_status'] for r in dispatch])
        acoustic=json.loads((ROOT/'data/iteration-26-acoustic-20261026/lab-readback.json').read_text())
        self.assertIn('selected/assimilation/response.json',acoustic['checked'])
        for name,expected in [('assimilation','confirmed'),('weak-form','not_realized'),('thought-group','uncertain'),('intonation-function','uncertain')]:
            packet=json.loads((ROOT/('data/iteration-26-acoustic-20261026/selected/'+name+'/comparison.json')).read_text())
            self.assertEqual(expected,packet['audio_confirmation'])
        # These are retained finite provider observations, not independent gold,
        # current-run calls, genuine learners or complete taxonomy qualification.

    def packet(self): return json.loads((AUDIT/'REVIEW.json').read_text())
    def test_review_positive(self): self.assertEqual([],review_errors(self.packet(),self.facts))
    def test_ux_omission_negative(self):
        p=self.packet();p.pop('ui_ux');self.assertTrue(review_errors(p,self.facts))
    def test_typography_omission_negative(self):
        p=self.packet();p.pop('typography');self.assertTrue(review_errors(p,self.facts))
        facts=copy.deepcopy(self.facts);facts['layouts'][0]['size']='10px';self.assertTrue(review_errors(self.packet(),facts))
    def test_evidence_mismatch_negative(self):
        for key,value in [('report_id','another-record'),('new_model_calls',732),('reference_origin','candidate gold'),('unexecuted_cases',['planned']),('browser_file_delivery_claimed',True),('performance_campaigns','required')]:
            p=self.packet();p[key]=value;self.assertTrue(review_errors(p,self.facts),key)


if __name__=='__main__': unittest.main(verbosity=2)
