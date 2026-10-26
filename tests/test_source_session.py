"""Execute exact JS production-owner assertions with controlled transport inputs."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'


class SourceSession(unittest.TestCase):
    def observe(self, name):
        result = subprocess.run([str(NODE), '--test', '--test-reporter=tap',
                                 '--test-name-pattern=^'+name+'$', 'tests/source_session.test.mjs'],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stdout+result.stderr)
        self.assertIn('# pass 1', result.stdout)

    def test_selection_positive(self): self.observe('selection_positive')
    def test_refresh_recovery_positive(self): self.observe('refresh_recovery_positive')
    def test_metadata_reset_negative(self): self.observe('metadata_reset_negative')
    def test_binding_reset_negative(self): self.observe('binding_reset_negative')
    def test_later_release_positive(self): self.observe('later_release_positive')
    def test_superseded_failure_negative(self): self.observe('superseded_failure_negative')
    def test_later_progress_positive(self): self.observe('later_progress_positive')
    def test_rows_recovery_positive(self): self.observe('rows_recovery_positive')
    def test_stale_pagination_negative(self): self.observe('stale_pagination_negative')
    def test_restore_positive(self): self.observe('restore_positive')
    def test_history_positive(self): self.observe('history_positive')
    def test_history_recovery_negative(self): self.observe('history_recovery_negative')
    def test_transient_retry_positive(self): self.observe('transient_retry_positive')
    def test_exhausted_read_negative(self): self.observe('exhausted_read_negative')
    def test_input_guidance_negative(self): self.observe('input_guidance_negative')
    def test_write_resume_negative(self): self.observe('write_resume_negative')
    def test_connection_recovery_positive(self): self.observe('connection_recovery_positive')
    def test_unreadable_reply_negative(self): self.observe('unreadable_reply_negative')
    def test_status_language_positive(self): self.observe('status_language_positive')
    def test_status_language_negative(self): self.observe('status_language_negative')
    def test_unreadable_import_negative(self): self.observe('unreadable_import_negative')
    def test_unknown_code_negative(self): self.observe('unknown_code_negative')
    def test_row_diagnostics_negative(self): self.observe('row_diagnostics_negative')
    def test_source_files_positive(self): self.observe('source_files_positive')
    def test_source_files_negative(self): self.observe('source_files_negative')
    def test_cache_positive(self): self.observe('cache_positive')
    def test_cache_unavailable_negative(self): self.observe('cache_unavailable_negative')


if __name__ == '__main__':
    unittest.main(verbosity=2)
