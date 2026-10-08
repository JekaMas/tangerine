"""Real PostgreSQL/MinIO initialization, persistence and anonymous access checks."""
import json
import os
from pathlib import Path
import subprocess
import unittest
import test_runtime as runtime

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker', 'compose', '--env-file', str(ROOT / 'deploy/local/.env'),
           '-f', str(ROOT / 'deploy/local/compose.yaml')]


def snapshot():
    return subprocess.check_output(COMPOSE + ['exec', '-T', 'postgres', 'psql', '-U', 'tangerine',
        '-d', 'tangerine', '-Atc', "SELECT json_build_object('accounts',(SELECT json_agg(row(id,email,password_hash)) FROM accounts),'migrations',(SELECT json_agg(row(version,sha256)) FROM schema_migrations),'exercises',(SELECT count(*) FROM exercise_catalog))"], timeout=30)


@unittest.skipUnless(os.environ.get('TANGERINE_RUN_STORAGE') == '1', 'Actual storage initialization/restart not selected')
class StorageRuntimeTests(unittest.TestCase):
    setUp = runtime.RuntimeTests.setUp
    call = runtime.RuntimeTests.call
    login = runtime.RuntimeTests.login

    def test_initialization_idempotent_positive(self):
        before = snapshot()
        for job in ['migrate', 'media-init', 'initialize']:
            subprocess.run(COMPOSE + ['run', '--rm', '-T', '--no-deps', job], check=True,
                           timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertTrue(snapshot() == before, 'Initialization changed existing account/migration/catalog state')

    def test_anonymous_media_negative(self):
        code = "import urllib.request,urllib.error;\ntry:\n urllib.request.urlopen('http://minio:9000/tangerine-audio',timeout=5); raise SystemExit(1)\nexcept urllib.error.HTTPError as e:\n raise SystemExit(0 if e.code==403 else 2)"
        result = subprocess.run(COMPOSE + ['exec', '-T', 'speech', 'python', '-c', code],
                                timeout=15, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 0, 'Anonymous media request did not receive access denied')

    def test_restart_persists_session_and_state_positive(self):
        self.login()
        before = snapshot()
        subprocess.run(COMPOSE + ['restart', 'postgres', 'minio', 'speech', 'api', 'web'],
                       check=True, timeout=90, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(COMPOSE + ['start', '--wait', '--wait-timeout', '90', 'postgres', 'minio', 'speech', 'api', 'web'],
                       check=True, timeout=100, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertTrue(snapshot() == before, 'Restart changed persisted state')
        status, data = self.call('/api/auth/session')
        self.assertEqual(status, 200, 'Persisted original session failed after restart')
        self.assertEqual(data, {'email': self.email})
        self.assertEqual(self.call('/api/exercises'), (200, {'exercises': []}))

    def test_existing_restore_project_negative(self):
        project = 'tangerine-restore-20261008'
        restored = COMPOSE + ['--project-name', project]
        def counts():
            return subprocess.check_output(restored + ['exec', '-T', 'postgres', 'psql', '-U', 'tangerine',
                '-d', 'tangerine', '-Atc', 'SELECT count(*) FROM accounts'], timeout=15)
        before = counts()
        result = subprocess.run(['python3', '-B', 'scripts/restore_isolated.py', 'data/backups/foundation-20261008', '--project', project],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(counts(), before)


if __name__ == '__main__':
    unittest.main()
