"""Single owned actual workspace run; exact observed scenarios are separate tests."""
from pathlib import Path
import json,os,subprocess,unittest,uuid
R=Path(__file__).resolve().parents[1]
class RecoveryWorkspaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.path=R/'data/iteration15/workspace'/('run-'+uuid.uuid4().hex[:10]);cls.path.mkdir(parents=True)
  e=dict(os.environ,TANGERINE_RECOVERY_EVIDENCE=str(cls.path),TANGERINE_RECOVERY_SPEECH_IMAGE='sha256:906700d3eda940912899001feb08a3b1b0df3fa3d6c8f8a3ae6e0c5bb96256e9')
  cls.process=subprocess.run([str(R/'tests/recovery-workspace')],cwd=R,env=e,capture_output=True,text=True,timeout=1100)
  (cls.path/'stdout').write_text(cls.process.stdout);(cls.path/'stderr').write_text(cls.process.stderr)
  if cls.process.returncode:raise AssertionError('Actual recovery workspace failed: '+str(cls.path))
  cls.observations=json.loads((cls.path/'observations.json').read_text())
 def check(self,name):self.assertIs(self.observations[name],True)
 def test_navigation_positive(self):self.check('test_navigation_positive')
 def test_generate_positive(self):self.check('test_generate_positive')
 def test_saved_answer_positive(self):self.check('test_saved_answer_positive')
 def test_recovery_instructions_positive(self):self.check('test_recovery_instructions_positive')
 def test_dependency_failure_negative(self):self.check('test_dependency_failure_negative')
 def test_dependency_recovery_positive(self):self.check('test_dependency_recovery_positive')
 def test_restart_positive(self):self.check('test_restart_positive')
 def test_backup_positive(self):self.check('test_backup_positive')
 def test_private_backup_negative(self):self.check('test_private_backup_negative')
 def test_corrupt_restore_negative(self):self.check('test_corrupt_restore_negative')
 def test_fresh_restore_positive(self):self.check('test_fresh_restore_positive')
 def test_existing_target_negative(self):self.check('test_existing_target_negative')
 def test_switch_positive(self):self.check('test_switch_positive')
 def test_restored_draft_positive(self):self.check('test_restored_draft_positive')
 def test_restored_audio_positive(self):self.check('test_restored_audio_positive')
 def test_failed_switch_negative(self):self.check('test_failed_switch_negative')
 def test_switch_back_positive(self):self.check('test_switch_back_positive')
 def test_original_retained_negative(self):self.check('test_original_retained_negative')
 def test_cleanup_preview_positive(self):self.check('test_cleanup_preview_positive')
 def test_cleanup_unconfirmed_negative(self):self.check('test_cleanup_unconfirmed_negative')
 def test_cleanup_apply_positive(self):self.check('test_cleanup_apply_positive')
 def test_cleanup_unknown_negative(self):self.check('test_cleanup_unknown_negative')
 def test_backup_collision_negative(self):self.check('test_backup_collision_negative')
 def test_lab_purge_unconfirmed_negative(self):self.check('test_lab_purge_unconfirmed_negative')
 def test_lab_purge_positive(self):self.check('test_lab_purge_positive')
 def test_no_maintenance_inference_negative(self):self.check('test_no_maintenance_inference_negative')

 def test_selected_lab_native_positive(self):self.check('test_selected_lab_native_positive')
