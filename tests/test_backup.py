"""NO_TEST_DOUBLE: actual backup bytes and the real hash/archive validator.

Invalid metadata copies are controlled infrastructure inputs. No teacher record,
audio, provider output or human approval is synthesized.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_backup import verify


@unittest.skipUnless(os.environ.get('TANGERINE_BACKUP_UNDER_TEST'), 'Select an actual local backup explicitly')
class BackupTests(unittest.TestCase):
    def setUp(self):
        self.backup = ROOT / os.environ['TANGERINE_BACKUP_UNDER_TEST']

    def test_actual_backup_positive(self):
        result = verify(self.backup)
        self.assertEqual(result['status'], 'complete')
        self.assertFalse(result['secrets_included'])

    def test_hash_tamper_negative(self):
        with tempfile.TemporaryDirectory(prefix='invalid-metadata-', dir=ROOT / 'data/backups') as folder:
            target = Path(folder)
            for filename in ['database.dump', 'media.tar.gz']:
                shutil.copyfile(self.backup / filename, target / filename)
            manifest = json.loads((self.backup / 'manifest.json').read_text())
            manifest['database']['sha256'] = '0' * 64
            (target / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'hash/path mismatch'):
                verify(target)

    def test_incomplete_backup_negative(self):
        with tempfile.TemporaryDirectory(prefix='incomplete-metadata-', dir=ROOT / 'data/backups') as folder:
            target = Path(folder)
            (target / 'manifest.json').write_text('{"version":1,"status":"incomplete"}')
            with self.assertRaisesRegex(ValueError, 'Incomplete'):
                verify(target)


if __name__ == '__main__':
    unittest.main()
