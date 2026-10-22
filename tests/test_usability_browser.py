"""Independent literal expectations over the real owned browser/API/DB run.

Only model replies/timing and post-blueprint generation are constructed.
"""
from pathlib import Path
import json,os,subprocess,unittest,uuid
ROOT=Path(__file__).resolve().parents[1]

class UsabilityBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=ROOT/'data/interactive-usability-20261022'/('browser-'+uuid.uuid4().hex[:10])
        directory.mkdir(parents=True)
        result=subprocess.run([str(ROOT/'tests/usability-browser')],cwd=ROOT,env={**os.environ,'TANGERINE_USABILITY_EVIDENCE':str(directory)},capture_output=True,text=True,timeout=600)
        (directory/'driver.stdout').write_text(result.stdout);(directory/'driver.stderr').write_text(result.stderr)
        if result.returncode:raise AssertionError('Native browser run failed: '+str(directory/'driver.stderr'))
        cls.observation=json.loads((directory/'observations.json').read_text())
        cls.values=cls.observation['values']

    def test_controls_positive(self):
        self.assertEqual(self.values['test_controls_positive'],{'request':{'topic':'Insurance choices','speaker_count':2,'text_length_words':180,'english_level':'B2','category_families':['grammar','lexis'],'mutation_count':3,'mutation_seed':None,'audio_backend':None},'levels':['B2','B2']})
    def test_saved_summary_positive(self):self.assertIs(self.values['test_saved_summary_positive'],True)
    def test_levels_positive(self):self.assertEqual(self.values['test_levels_positive'],['A1','A2','B1','B2','C1','C2'])
    def test_families_positive(self):self.assertEqual(self.values['test_families_positive'],['grammar','lexis','pronunciation','pronunciation.segmental','pronunciation.suprasegmental','fluency','discourse','pragmatics_register'])
    def test_automatic_positive(self):self.assertEqual(self.values['test_automatic_positive'],{'english_level':None,'category_families':[],'mutation_count':None})
    def test_zero_positive(self):self.assertEqual(self.values['test_zero_positive'],0)
    def test_advanced_positive(self):self.assertEqual(self.values['test_advanced_positive'],{'english_level':'C1','category_families':['discourse'],'mutation_count':4})
    def test_invalid_json_negative(self):self.assertEqual(self.values['test_invalid_json_negative'],'Insurance choices')
    def test_invalid_count_negative(self):self.assertEqual(self.values['test_invalid_count_negative'],[False,False])
    def test_request_failure_negative(self):self.assertEqual(self.values['test_request_failure_negative'],{'topic':'Insurance choices','count':'3'})
    def test_extraction_progress_positive(self):self.assertEqual(self.values['test_extraction_progress_positive'],{'saved':True,'stage':True,'answer':'Use opens.'})
    def test_matching_progress_positive(self):self.assertIs(self.values['test_matching_progress_positive'],True)
    def test_score_before_comments_positive(self):self.assertEqual(self.values['test_score_before_comments_positive'],{'primary':'Primary score: 100.0 / 100','stage':True,'pending':True,'falseFailure':False})
    def test_reads_no_dispatch_negative(self):self.assertEqual(self.values['test_reads_no_dispatch_negative'],{'extractions':0,'mappings':0,'feedback':0,'submissions':0})
    def test_read_failure_negative(self):self.assertEqual(self.values['test_read_failure_negative'],{'answer':'Use opens.','saved':True,'disabled':True})
    def test_feedback_failure_negative(self):self.assertEqual(self.values['test_feedback_failure_negative'],{'primary':'Primary score: 100.0 / 100','answer':'Use opens.'})
    def test_feedback_retry_positive(self):self.assertEqual(self.values['test_feedback_retry_positive'],{'extractions':0,'mappings':0,'feedback':1,'submissions':0})
    def test_observer_stop_positive(self):self.assertEqual(self.values['test_observer_stop_positive'],0)
    def test_unmount_negative(self):self.assertEqual(self.values['test_unmount_negative'],{'additional_reads':0,'additional_submissions':0})
    def test_privacy_negative(self):self.assertIs(self.values['test_privacy_negative'],False)

if __name__=='__main__':unittest.main()
