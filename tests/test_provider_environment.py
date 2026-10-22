"""Installation provider references never inherit an unrelated caller's keys."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GEMINI_API_KEY', 'AZURE_SPEECH_KEY', 'ELEVENLABS_API_KEY']


class ProviderEnvironmentTests(unittest.TestCase):
    def test_ambient_credentials_cleared_negative(self):
        with tempfile.TemporaryDirectory() as folder:
            env = dict(os.environ, ROOT=folder, **{name: 'synthetic-unrelated-key' for name in KEYS})
            script = 'fail() { exit 9; }; . "$1"; for name in OPENAI_API_KEY DEEPSEEK_API_KEY GEMINI_API_KEY AZURE_SPEECH_KEY ELEVENLABS_API_KEY; do eval "present=\\${$name+x}"; test -z "$present" || exit 8; done'
            result = subprocess.run(['sh', '-c', script, 'provider-environment', str(ROOT / 'scripts/workspace-env')], env=env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_installation_credentials_preserved_positive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            operator = root / '.env'
            operator.write_text('GEMINI_API_KEY=synthetic-installation-key\n')
            result = subprocess.run(['sh', '-c', 'fail() { exit 9; }; . "$1"; printf "%s" "$COMPOSE_PROJECT_NAME"', 'provider-environment', str(ROOT / 'scripts/workspace-env')], env=dict(os.environ, ROOT=folder, COMPOSE_PROJECT_NAME='selected-local-workspace', GEMINI_API_KEY='synthetic-ambient-key'), capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.decode(), 'selected-local-workspace')
            self.assertEqual(operator.read_text(), 'GEMINI_API_KEY=synthetic-installation-key\n')


if __name__ == '__main__':
    unittest.main()
