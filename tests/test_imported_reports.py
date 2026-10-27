"""I38 acceptance: independent source censuses + actual native/API/Chrome receipts.

No model, speech, import, installation or provider call is made by discovery or
this reconciliation. Retained native case greens are reused individually; a
failed package or narrative status alone is never treated as a green case.
"""
import collections,json,unittest
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/iteration-38-empirical-20261027'

def load(path):return json.loads(path.read_text())
def native(case,*stems):
    rows=[]
    for stem in stems:
        rows.extend(json.loads(line) for line in (DATA/(stem+'.jsonl')).read_text().splitlines())
    selected=[r for r in rows if r.get('Test')==case and r['Action'] in ['pass','fail','skip']]
    if not selected or selected[-1]['Action']!='pass':raise AssertionError((case,selected))

def reports(store):
    folder=DATA/('native-'+store);choices=[c for c in load(folder/'catalogue.json') if c['data_origin']=='native']
    all_reports=[load(f) for f in sorted(folder.glob('report-*.json'),key=lambda p:p.stat().st_mtime_ns)]
    chosen=[]
    for c in choices:
        view=c['source']['member'] or c['source']['basis']
        candidates=[v for v in all_reports if v['report']['population']['release']==c['release_id'] and v['report']['population']['view']==view and v['source_summary'].get('constructed') is False]
        if not candidates:raise AssertionError(('Missing real selected source view',c))
        chosen.append(candidates[-1])
    return chosen

def exact(value):
    if value.get('missing_reason') or value.get('exact') is None:return None
    return Fraction(int(value['exact']['numerator']),int(value['exact']['denominator']))

class ImportedReports(unittest.TestCase):
 def test_catalogue_positive(self):
    native('TestImportedCataloguePositive','final-consumers-38')
    for store in ['35','36','37','38']:
        choices=load(DATA/('native-'+store)/'catalogue.json');keys=[]
        for c in choices:
            self.assertIn(' · ',c['title']);self.assertNotIn('/',c['title']);self.assertTrue(c['release_id']);self.assertTrue(c['source_manifest'])
            keys.append((c['source_name'],c['release'],c['source_manifest'],c['source']['basis'],c['source']['member'],c['source']['table']))
        self.assertEqual(len(keys),len(set(keys)),'Repeated imports became extra populations')
    self.assertEqual(2,len(reports('36')))
 def test_catalogue_negative(self):
    native('TestImportedCatalogueNegative','fixtures-38')
    for store in ['36','37']:
        for c in load(DATA/('native-'+store)/'catalogue.json'):
            if c['data_origin']=='constructed':self.assertIn('Constructed example',c['title']);self.assertIn('not an acquired corpus',c['description'])
    self.assertEqual(1,len([r for r in load(DATA/'browser/requests.json') if r['method']=='POST' and r['scenario']=='save_failure']))
 def test_writing_positive(self):
    native('TestImportedWritingPositive','fixtures-38')
    oracle=load(DATA/'independent-m2-oracle.json');actual=[v for v in reports('38') if v['report']['population']['view'] in oracle]
    self.assertEqual(12,len(actual))
    for v in actual:
        r=v['report'];o=oracle[r['population']['view']];n=r['native_population']
        self.assertEqual((o['windows'],o['annotated'],o['words'],o['events']),(n['observed_windows'],n['annotated_windows'],n['inspected_native_tokens'],n['eligible_events']))
        self.assertEqual(o['counts'],r['native_label_counts']);self.assertEqual(o['excluded'],r['excluded'])
        for leaf in r['native_frequencies']:
            self.assertEqual(o['counts'][leaf['id']],leaf['events'])
            self.assertEqual(Fraction(leaf['events'],o['events']),exact(leaf['event_share']))
            self.assertEqual(Fraction(o['presence'].get(leaf['id'],0),o['annotated']),exact(leaf['window_prevalence']))
 def test_writing_negative(self):
    native('TestImportedWritingNegative','fixtures-38')
    withheld=[v for v in reports('38') if v['source_summary']['source_id']=='WILOCNESS-2.1' and v['report']['population']['label_origin']=='native_coverage_only']
    self.assertEqual(1,len(withheld));r=withheld[0]['report'];self.assertEqual(4477,r['observed_windows']);self.assertEqual(0,r['native_population']['annotated_windows']);self.assertEqual([],r['native_frequencies']);self.assertEqual([],r['native_pairs'])
 def test_mappings_positive(self):
    native('TestSourceWritingMappingPositive','engine-stable');native('TestSourcePhoneMappingPositive','phone-mapping')
    for store in ['35','38']:
        for v in reports(store):
            self.assertEqual(122,len(v['category_labels']));self.assertEqual(122,len(v['report']['leaves']))
            self.assertTrue(all(not label.startswith(('grammar.','pronunciation.','lexis.')) for label in v['category_labels'].values()))
            self.assertEqual('not-supplied' if v['report']['population']['label_origin']=='native_coverage_only' else 'native-context-1',v['report']['population']['crosswalk_version'])
 def test_mappings_negative(self):
    native('TestSourceWritingMappingNegative','engine-stable');native('TestSourcePhoneMappingNegative','phone-mapping')
    for store in ['35','36','37','38']:
        for v in reports(store):
            self.assertEqual([],v['report']['annotated_leaf_ids'])
            for leaf in v['report']['leaves']:
                self.assertIsNone(exact(leaf['window_prevalence']));self.assertIsNone(exact(leaf['opportunity_rate']))
 def test_speech_positive(self):
    native('TestImportedSpeechPositive','final-consumers-38')
    actual=reports('35');self.assertEqual(2,len(actual))
    for v in actual:
        r=v['report'];story=r['population']['view']=='manual_phones_suitcase'
        expected={'s':1673,'d':456,'a':90} if story else {'s':14098,'d':3420,'a':1092}
        self.assertEqual(expected,r['native_label_counts']);self.assertEqual(22 if story else 3599,r['native_population']['annotated_windows']);self.assertEqual(sum(expected.values()),r['native_population']['eligible_events']);self.assertIsNone(r['native_population']['inspected_native_tokens'])
        coverage={c['label']:c['count'] for c in v['source_summary']['coverage']}
        self.assertEqual(22 if story else 26867,coverage['Available transcript utterances in this task'])
        self.assertEqual(22 if story else 3599,coverage['Utterances with manual phone annotations'])
        oracle=load(DATA/'independent-l2-oracle.json')['suitcase' if story else 'read']
        self.assertEqual(oracle['windows'],r['native_population']['annotated_windows']);self.assertEqual(oracle['counts'],r['native_label_counts'])
        for leaf in r['native_frequencies']:
            self.assertEqual(Fraction(oracle['counts'][leaf['id']],oracle['events']),exact(leaf['event_share']))
            self.assertEqual(Fraction(oracle['presence'][leaf['id']],oracle['windows']),exact(leaf['window_prevalence']))
        pairs={(p['a'],p['b']):p['count'] for p in oracle['pairs']}
        self.assertEqual(set(pairs),{(p['a'],p['b']) for p in r['native_pairs']})
        for pair in r['native_pairs']:
            joint=pairs[pair['a'],pair['b']];self.assertEqual(joint,pair['distinct_event_windows'])
            self.assertEqual(Fraction(joint,oracle['windows']),exact(pair['support']))
            self.assertEqual(Fraction(joint,oracle['presence'][pair['a']]),exact(pair['conditional']))
            self.assertEqual(Fraction(joint*oracle['windows'],oracle['presence'][pair['a']]*oracle['presence'][pair['b']]),exact(pair['lift']))
 def test_speech_negative(self):
    native('TestImportedSpeechNegative','final-consumers-38');native('TestSourcePhoneMappingNegative','phone-mapping')
    for v in reports('35'):
        self.assertEqual(set(['s','d','a']),set(v['report']['native_label_counts']))
        self.assertGreater(v['report']['unmapped_events'],0);self.assertIsNone(v['report']['native_population']['inspected_native_tokens'])
 def test_coverage_positive(self):
    native('TestImportedCoveragePositive','final-consumers-38')
    jfleg=reports('36');self.assertEqual([747,754],sorted(v['report']['observed_windows'] for v in jfleg))
    self.assertEqual(6004,sum(next(c['count'] for c in v['source_summary']['coverage'] if c['label']=='Supplied alternative corrections') for v in jfleg))
    speech=[v for v in reports('38') if v['source_summary']['source_id']=='SPEECHOCEAN762'];self.assertEqual(1,len(speech));self.assertEqual(5000,speech[0]['report']['observed_windows']);self.assertEqual(5245,next(c['count'] for c in speech[0]['source_summary']['coverage'] if c['label']=='Original recordings in this release'))
    by=collections.defaultdict(list)
    for v in reports('37'):by[v['source_summary']['source_id']].append(v['report']['observed_windows'])
    self.assertEqual(19137,sum(by['EDACC']));self.assertEqual(589,sum(by['ELRD']));self.assertEqual(35255,sum(by['DIPLOMAT']));self.assertEqual([208,272,4496,5692,5786,7632],sorted(by['DRAL']))
 def test_coverage_negative(self):
    native('TestImportedCoverageNegative','final-consumers-38')
    for v in reports('36')+reports('37')+[v for v in reports('38') if v['report']['population']['label_origin']=='native_coverage_only']:
        r=v['report'];self.assertEqual(0,r['eligible_events']);self.assertEqual(0,r['native_population']['annotated_windows']);self.assertIsNone(r['native_population']['inspected_native_tokens']);self.assertEqual([],r['native_frequencies']);self.assertEqual([],r['native_pairs'])
        self.assertTrue(all(exact(l['window_prevalence']) is None for l in r['leaves']))
 def test_relationships_positive(self):
    native('TestSourceNativeRelationshipsPositive','engine-stable')
    oracle=load(DATA/'independent-m2-oracle.json')
    for v in reports('38'):
        r=v['report'];o=oracle.get(r['population']['view'])
        if not o:continue
        expected={(p['a'],p['b']):p['count'] for p in o['pairs']};self.assertEqual(set(expected),{(p['a'],p['b']) for p in r['native_pairs']})
        for p in r['native_pairs']:
            joint=expected[p['a'],p['b']];self.assertEqual(joint,p['distinct_event_windows']);self.assertEqual(Fraction(joint,o['annotated']),exact(p['support']));self.assertEqual(Fraction(joint,o['presence'][p['a']]),exact(p['conditional']));self.assertEqual(Fraction(joint*o['annotated'],o['presence'][p['a']]*o['presence'][p['b']]),exact(p['lift']))
 def test_relationships_negative(self):
    native('TestSourceNativeRelationshipsNegative','engine-stable')
    native('TestNativeSavedReportSecondaryNegative','native-siblings')
    self.assertTrue(all(not v['report']['native_pairs'] for v in reports('36')+reports('37')))
 def test_persistence_positive(self):
    native('TestImportedPersistencePositive','repair-38');native('TestNativeSavedReportExistingReplayPositive','native-replay')
    p=load(DATA/'native-38/persistence.json');self.assertTrue(p['saved_read_unchanged']);self.assertEqual(0,p['provider_calls'])
    observed=load(DATA/'browser/observations.json');self.assertEqual(observed['reportID'],observed['download']);self.assertIn('Reloaded exact saved report',observed['actions']);self.assertIn('Reused frozen report observations through saved-population form',observed['actions'])
 def test_persistence_negative(self):
    native('TestImportedPersistenceNegative','missing-38')
    observed=load(DATA/'browser/observations.json');self.assertIn('save failure with retained input and saved result',observed['states']);self.assertIn('explicit save recovery',observed['states'])
    writes=[r for r in load(DATA/'browser/requests.json') if r['method']!='GET'];self.assertTrue(all(r['path']=='/api/v1/reports/empirical' and not r['forbidden'] for r in writes));self.assertEqual(1,sum(r['status']==503 for r in writes))
 def test_usability_positive(self):
    observed=load(DATA/'browser/observations.json');self.assertTrue(observed['completed']);self.assertEqual([],observed['pageErrors']);self.assertEqual([1280,390,320],[v['width'] for v in observed['layouts']])
    for layout in observed['layouts']:self.assertLessEqual(layout['documentWidth'],layout['width']);self.assertEqual('17px',layout['size']);self.assertEqual('24.65px',layout['lineHeight']);self.assertGreaterEqual(layout['small'],14)
    downloaded=load(DATA/'browser/downloaded-report.json');self.assertEqual(2219,downloaded['report']['native_population']['eligible_events']);self.assertEqual(22,downloaded['report']['native_population']['observed_windows'])
    coverage=load(DATA/'coverage-browser/observations.json');self.assertTrue(coverage['completed']);self.assertEqual(747,coverage['originals']);self.assertEqual(2988,coverage['alternatives']);self.assertEqual('Not measured',coverage['original_mistakes']);self.assertEqual([1280,390,320],[r['width'] for r in coverage['layouts']])
    self.assertEqual('0',(DATA/'presentation-exit-code').read_text().strip());self.assertEqual('0',(DATA/'web-candidate-exit-code').read_text().strip());self.assertEqual('0',(DATA/'stable-final-go-exit-code').read_text().strip())
 def test_usability_negative(self):
    observed=load(DATA/'browser/observations.json');self.assertIn('empty imports preserve saved report and practice',observed['states']);self.assertIn('keyboard retry recovered',observed['states'])
    calls=load(DATA/'browser/requests.json');source=[c for c in calls if c['path']=='/api/v1/reports/source-populations']
    self.assertEqual([503,200],[c['status'] for c in source if c['scenario']=='transient']);self.assertEqual([503,503,503],[c['status'] for c in source if c['scenario']=='unavailable']);self.assertFalse(any(c['forbidden'] for c in calls))
    self.assertEqual('0',(DATA/'list-siblings-exit-code').read_text().strip());self.assertTrue(any(c['type']=='warning' and 'Tangerine request' in c['text'] for c in observed['console']))

if __name__=='__main__':unittest.main(verbosity=2)
