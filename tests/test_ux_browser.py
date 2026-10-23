"""Independent expectations over actual CUA/Chrome UI and persisted HTTP output.

Screenshots/observations were obtained through the real interface. These checks
read that evidence and current saved records; they dispatch no inference.
"""
from pathlib import Path
import json,unittest,urllib.request
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'data/ux-controls-20261023'
HEADINGS={'library':'A better ear for English.','prepare':'Prepare an exercise','attempts':'Saved attempts','audio':'Saved audio','listen':'Listen and respond','reviews':'Optional LLM review','reports':'Reports and quality experiments','sources':'Sources','settings':'Your LLM connection','recovery':'Recovery and local data','cleanup':'Cleanup and deletion'}
class UXBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.v=json.loads((O/'browser-observations.json').read_text())
 def test_routes_desktop_positive(self):
  self.assertEqual(set(self.v['routes']),set(HEADINGS))
  for route,heading in HEADINGS.items():
   row=self.v['routes'][route];self.assertEqual(row['heading'],heading);self.assertEqual([row['mainCount'],row['navLinks']],[1,10]);self.assertIn('Source Sans 3',row['font']);self.assertTrue(row['current']);self.assertEqual(row['alerts'],[])
   self.assertTrue((O/'screens'/(route+'-desktop.jpg')).is_file())
 def test_mobile_navigation_positive(self):self.assertEqual(self.v['checks']['mobileNavigation'],{'opened':True,'links':10,'destination':'New exercise','closed':True,'keyboardFocus':True})
 def test_no_horizontal_overflow_negative(self):
  self.assertEqual(set(self.v['narrow']),set(HEADINGS))
  for route,row in self.v['narrow'].items():self.assertEqual(row['viewport'],390);self.assertLessEqual(row['width'],390);self.assertTrue((O/'screens'/(route+'-mobile.jpg')).is_file())
 def test_saved_answer_unchanged_negative(self):
  old=json.loads((O/'attempt-before.json').read_text());new=json.load(urllib.request.urlopen('http://localhost:3000/api/v1/attempts/'+old['attempt_id'],timeout=8));self.assertEqual(old,new)
  before=json.loads((O/'configuration-before.json').read_text());after=json.load(urllib.request.urlopen('http://localhost:3000/api/v1/configuration',timeout=8));self.assertEqual(before['configuration'],after['configuration']);self.assertEqual([(x['name'],x['present']) for x in before['credentials']],[(x['name'],x['present']) for x in after['credentials']])
  self.assertEqual(self.v['checks']['uiModelRequests'],{'successful':0,'blockedSaveOnly':1})
 def test_category_failure_negative(self):
  fail=self.v['checks']['categoryFailure'];recovered=self.v['checks']['categoryRecovery'];self.assertEqual([fail['topic'],fail['grammar']],['Catalogue outage: retain my topic.',True]);self.assertIn('choices are retained',fail['error']);self.assertEqual(recovered,{'topic':'Catalogue outage: retain my topic.','grammar':True,'categoryCount':114,'error':None})
 def test_saved_request_positive(self):
  b=json.loads((O/'saved-blueprint.json').read_text());r=b['exercise_request'];self.assertEqual(r['category_ids'],['lexis.collocation','pragmatics_register.formality']);self.assertEqual(r['severity_levels'],['minor']);self.assertEqual(r['mutation_count'],4);self.assertEqual(r['category_families'],[]);self.assertEqual(b['provider_profile_id'],'kokoro-local-en-v1')
 def test_review_selection_positive(self):self.assertEqual(self.v['checks']['reviewSelection'],{'picker':True,'selected':True,'reviewButton':True,'noAutomaticRun':True})
 def test_review_selection_failure_negative(self):self.assertEqual(self.v['checks']['reviewFailure'],{'error':True,'retry':True,'recovered':True,'noAutomaticRun':True})
 def test_advanced_editor_negative(self):self.assertEqual(self.v['checks']['advancedEditor'],{'inputRetained':True,'pageUsable':True,'dispatched':False})
 def test_request_interruption_negative(self):
  v=self.v['checks']['requestInterruption'];self.assertEqual(v['topic'],'UX selection check: two colleagues planning a train journey.');self.assertIn('Your choices are retained',v['error']);self.assertEqual(v['request']['category_ids'],['lexis.collocation','pragmatics_register.formality']);self.assertEqual(v['request']['severity_levels'],['minor']);self.assertEqual(v['request']['mutation_count'],4)
 def test_zero_caption_positive(self):self.assertEqual(self.v['checks']['zeroCaption'],{'count':0,'selected':2,'noErrors':True})
if __name__=='__main__':unittest.main()
