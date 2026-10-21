"""Real source-only complete installed-local-model exercise; no hosted dispatch.
The fixture retains every failed attempt and at most one explicit saved Resume.
"""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class ReleaseLiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=R/'data/iteration16/release'/('arm64-'+uuid.uuid4().hex[:10]);cls.root.mkdir(parents=True)
  env=dict(os.environ,TANGERINE_RELEASE_EVIDENCE=str(cls.root),TANGERINE_TEST_VIDEO_DIR=str(cls.root/'videos'))
  p=subprocess.run([str(R/'tests/release-live'),'arm64'],cwd=R,env=env,capture_output=True,text=True,timeout=2300)
  (cls.root/'stdout').write_text(p.stdout);(cls.root/'stderr').write_text(p.stderr)
  cls.failure='Actual local release exit '+str(p.returncode)+'; evidence: '+str(cls.root)
  cls.values=json.loads((cls.root/'observations.json').read_text()) if (cls.root/'observations.json').exists() else {}
  cls.receipt=json.loads((cls.root/'receipt.json').read_text()) if (cls.root/'receipt.json').exists() else {}
  if p.returncode==0 and cls.receipt.get('status')=='passed':
   pointer=R/'data/iteration16/release/live-current.json';pointer.write_text(json.dumps(dict(root=str(cls.root.relative_to(R)),receipt=cls.receipt),indent=2))
 def check(self,name):self.assertIs(self.values.get(name),True,self.failure)
 def test_source_without_workflow_positive(self):self.check('test_source_without_workflow_positive')
 def test_source_start_positive(self):self.check('test_source_start_positive')
 def test_architecture_positive(self):self.check('test_architecture_positive')
 def test_architecture_negative(self):self.check('test_architecture_negative')
 def test_library_positive(self):self.check('test_library_positive')
 def test_local_settings_positive(self):self.check('test_local_settings_positive')
 def test_generation_positive(self):self.check('test_generation_positive')
 def test_word_counts_positive(self):self.check('test_word_counts_positive')
 def test_actual_audio_positive(self):self.check('test_actual_audio_positive')
 def test_key_hidden_negative(self):self.check('test_key_hidden_negative')
 def test_draft_persistence_positive(self):self.check('test_draft_persistence_positive')
 def test_interpretation_positive(self):self.check('test_interpretation_positive')
 def test_primary_score_positive(self):self.check('test_primary_score_positive')
 def test_optional_explanation_negative(self):self.check('test_optional_explanation_negative')
 def test_recommendations_positive(self):self.check('test_recommendations_positive')
 def test_review_positive(self):self.check('test_review_positive')
 def test_dispute_positive(self):self.check('test_dispute_positive')
 def test_actual_receipts_positive(self):self.check('test_actual_receipts_positive')
 def test_actual_lab_positive(self):self.check('test_actual_lab_positive')
 def test_restart_positive(self):self.check('test_restart_positive')
 def test_backup_positive(self):self.check('test_backup_positive')
 def test_restore_positive(self):self.check('test_restore_positive')
 def test_existing_restore_negative(self):self.check('test_existing_restore_negative')
 def test_restored_media_positive(self):self.check('test_restored_media_positive')
 def test_restored_score_positive(self):self.check('test_restored_score_positive')
 def test_maintenance_no_inference_negative(self):self.check('test_maintenance_no_inference_negative')
if __name__=='__main__':unittest.main()
