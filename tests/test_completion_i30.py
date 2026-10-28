"""Iteration 30: real Git counterexamples and retained GitHub/ZIP/native/CUA proof.

No model calls, installation or publication are performed by this test command.
The release driver records the actual remote, downloaded archive and startup;
these observers assert literal expectations rather than accepting a pass label.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/completion-leftovers-20261028/release'
AUDIT = ROOT / 'audit/completion-leftovers-20261028'
REQUIRED = {
    'LICENSE', 'README.md', '.env.example', '.dockerignore', 'scripts/tangerine',
    'scripts/workspace-env', 'deploy/local/compose.yaml', 'deploy/local/minio.Dockerfile',
    'services/api/Dockerfile', 'services/api/go.mod', 'services/api/go.sum',
    'services/web/Dockerfile', 'services/web/package.json', 'services/web/package-lock.json',
    'services/speech/Dockerfile', 'services/speech/requirements.arm64.lock',
    'services/speech/requirements.amd64.lock',
}


def read(name):
    return json.loads((DATA / name).read_text())


def review_errors(packet, facts):
    """Development review bookkeeping, never a product or publication gate."""
    errors = []
    for part in ['ui_ux', 'typography', 'evidence']:
        value = packet.get(part, {})
        if not value.get('observations') or not value.get('references'):
            errors.append(part + ' unsupported')
        if value.get('status') != 'passed':
            errors.append(part + ' unverified')
    if packet.get('archive_revision') != facts['archive_revision']:
        errors.append('archive mismatch')
    if packet.get('reference_origin') != 'literal Git, Docker and browser expectations':
        errors.append('reference origin')
    if packet.get('performance_campaign') != 'excluded' or packet.get('new_model_calls') != 0:
        errors.append('execution scope')
    if packet.get('unexecuted_claimed_passed'):
        errors.append('unexecuted claim')
    if packet.get('actionable_caption_px', 0) < 13:
        errors.append('caption readability')
    return errors


class CompletionI30(unittest.TestCase):
    def git(self, cwd, *args, check=True):
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_TERMINAL_PROMPT='0', GIT_AUTHOR_NAME='Constructed release test',
                   GIT_AUTHOR_EMAIL='release-test@example.invalid',
                   GIT_COMMITTER_NAME='Constructed release test',
                   GIT_COMMITTER_EMAIL='release-test@example.invalid')
        result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args],
                                cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
        if check:
            self.assertEqual(0, result.returncode, result.stderr)
        return result

    def fixture(self, parent):
        repo = parent / 'work'; repo.mkdir()
        self.git(repo, 'init', '-q', '-b', 'main')
        (repo / 'product.txt').write_text('initial source\n')
        (repo / 'GAPS.md').write_text('protected original\n')
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-qm', 'Constructed initial source')
        return repo

    def test_missing_remote_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.fixture(Path(directory))
            before = self.git(repo, 'rev-parse', 'HEAD').stdout
            result = self.git(repo, 'push', check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('No configured push destination', result.stderr)
            self.assertEqual(before, self.git(repo, 'rev-parse', 'HEAD').stdout)
            self.assertEqual('initial source\n', (repo / 'product.txt').read_text())

    def test_failed_push_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory); repo = self.fixture(parent)
            remote = parent / 'remote.git'
            self.git(parent, 'init', '-q', '--bare', str(remote))
            self.git(repo, 'remote', 'add', 'origin', str(remote))
            self.git(repo, 'push', '-q', 'origin', 'main')
            old = self.git(remote, 'rev-parse', 'main').stdout
            self.git(remote, 'config', 'receive.denyNonFastForwards', 'true')
            # An independent root is a real rejected non-fast-forward, no network fake.
            self.git(repo, 'checkout', '--orphan', 'conflicting')
            (repo / 'product.txt').write_text('unlanded source\n')
            self.git(repo, 'add', '.'); self.git(repo, 'commit', '-qm', 'Conflicting source')
            result = self.git(repo, 'push', 'origin', 'HEAD:main', check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('rejected', result.stderr)
            self.assertEqual(old, self.git(remote, 'rev-parse', 'main').stdout)
            self.assertEqual('unlanded source\n', (repo / 'product.txt').read_text())

    def test_dirty_unrelated_landing_positive(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.fixture(Path(directory))
            self.git(repo, 'checkout', '-qb', 'release')
            (repo / 'product.txt').write_text('completed source\n')
            self.git(repo, 'commit', '-qam', 'Completed product')
            release = self.git(repo, 'rev-parse', 'HEAD').stdout
            self.git(repo, 'checkout', '-q', 'main')
            (repo / 'GAPS.md').write_text('unrelated user edit\n')
            self.git(repo, 'merge', '--ff-only', 'release')
            self.assertEqual(release, self.git(repo, 'rev-parse', 'HEAD').stdout)
            self.assertEqual('unrelated user edit\n', (repo / 'GAPS.md').read_text())
            self.assertEqual(' M GAPS.md\n', self.git(repo, 'status', '--porcelain').stdout)

    def test_overlapping_dirty_landing_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.fixture(Path(directory))
            main = self.git(repo, 'rev-parse', 'HEAD').stdout
            self.git(repo, 'checkout', '-qb', 'release')
            (repo / 'GAPS.md').write_text('release also edits this file\n')
            self.git(repo, 'commit', '-qam', 'Overlapping source')
            self.git(repo, 'checkout', '-q', 'main')
            (repo / 'GAPS.md').write_text('protected user edit\n')
            result = self.git(repo, 'merge', '--ff-only', 'release', check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(main, self.git(repo, 'rev-parse', 'HEAD').stdout)
            self.assertEqual('protected user edit\n', (repo / 'GAPS.md').read_text())
            self.assertFalse((repo / '.git/MERGE_HEAD').exists())

    def test_delivery_positive(self):
        facts = read('publication.json')
        self.assertEqual('JekaMas/tangerine', facts['repository'])
        self.assertEqual('PUBLIC', facts['visibility'])
        self.assertEqual('main', facts['default_branch'])
        self.assertEqual(facts['published_revision'], facts['remote_main'])
        self.assertEqual(facts['published_revision'], facts['github_main'])
        self.assertEqual(facts['published_revision'], facts['archive_revision'])
        self.assertEqual('https://github.com/JekaMas/tangerine', facts['repository_url'])
        self.assertTrue(facts['archive_url'].startswith('https://api.github.com/repos/JekaMas/tangerine/zipball/'))
        self.assertEqual(0, facts['push_exit'])
        self.git(ROOT, 'merge-base', '--is-ancestor', facts['published_revision'], 'main')

    def test_downloaded_archive_positive(self):
        facts = read('publication.json')
        path = DATA / facts['archive_file']
        self.assertEqual(facts['archive_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist(); prefixes = {n.split('/')[0] for n in names}
            self.assertEqual(1, len(prefixes))
            prefix = next(iter(prefixes)) + '/'
            relative = {n.removeprefix(prefix) for n in names if not n.endswith('/')}
            self.assertTrue(REQUIRED <= relative, REQUIRED - relative)
            self.assertNotIn('.env', relative)
            self.assertFalse(any(n.startswith(('data/config/', '.git/')) for n in relative))
            self.assertIn('Apache License', archive.read(prefix + 'LICENSE').decode())
            self.assertIn('sh scripts/tangerine start', archive.read(prefix + 'README.md').decode())
        self.assertFalse((Path(read('native.json')['source_root']) / '.git').exists())

    def test_launcher_start_positive(self):
        facts = read('native.json')
        self.assertEqual(0, facts['start_exit'])
        self.assertIn('Tangerine is ready at http://localhost:3000 (no sign-in).', facts['start_message'])
        self.assertEqual(['api', 'minio', 'postgres', 'speech', 'web'], sorted(facts['healthy_services']))
        self.assertEqual(1, facts['workspace_count_before'])
        self.assertEqual(0, facts['provider_receipts_before'])
        self.assertEqual(0, facts['exercise_count_before'])
        self.assertEqual(['.env', 'data/config/runtime.env'], sorted(facts['private_files']))
        self.assertTrue(all(value == '0o600' for value in facts['private_modes'].values()))
        self.assertEqual('arm64', facts['architecture'])
        self.assertEqual('Docker-only source launcher; isolated ports, source unchanged', facts['origin'])

    def test_restart_persistence_positive(self):
        facts = read('native.json')
        self.assertEqual((0, 0), (facts['stop_exit'], facts['restart_exit']))
        self.assertEqual(facts['saved_configuration_sha256'], facts['reopened_configuration_sha256'])
        self.assertEqual('kokoro-controlled-v1', facts['reopened_speech_profile'])
        self.assertEqual(facts['workspace_id_before'], facts['workspace_id_after'])
        self.assertTrue(facts['runtime_secret_file_unchanged'])
        self.assertEqual(facts['volumes_before_stop'], facts['volumes_after_restart'])
        self.assertEqual(0, facts['provider_receipts_after'])
        self.assertEqual(0, facts['exercise_count_after'])

    def test_port_isolation_positive(self):
        facts = read('native.json')
        self.assertEqual('http://localhost:3000', facts['actual_api_origin'])
        self.assertIs(True, facts['public_identity_matches'])
        self.assertEqual(0, facts['start_exit'])
        self.assertEqual(1, read('native-origin-fixture-failure.json')['start_exit'])

    def test_dropped_identity_header_negative(self):
        facts = read('readiness-header-discriminator.json')
        self.assertEqual({'status': 200, 'instance_header_present': True}, facts['direct_web'])
        self.assertEqual({'status': 200, 'instance_header_present': True}, facts['browser_network'])
        self.assertEqual({'status': 200, 'instance_header_present': False}, facts['old_probe_network'])
        self.assertEqual(1, read('native-header-fixture-failure.json')['start_exit'])
        self.assertEqual(0, read('native.json')['start_exit'])

    def test_unauthenticated_download_positive(self):
        facts = read('archive-native-readback.json')
        self.assertEqual(read('publication.json')['archive_revision'], facts['revision'])
        self.assertEqual('https://github.com/JekaMas/tangerine/archive/refs/heads/main.zip',
                         facts['unauthenticated_url'])
        with zipfile.ZipFile(DATA / 'public-main.zip') as archive, \
                zipfile.ZipFile(DATA / read('publication.json')['archive_file']) as immutable:
            prefix = immutable.namelist()[0]
            for name in REQUIRED:
                self.assertEqual(immutable.read(prefix + name), archive.read('tangerine-main/' + name), name)

    def test_delivery_negative(self):
        facts = read('launcher-negative.json')
        for value in facts['missing_inputs']:
            self.assertNotEqual(0, value['exit'])
            self.assertIn('SOURCE_INCOMPLETE: missing ' + value['removed'], value['stderr'])
            self.assertTrue(value['private_state_unchanged'])
        self.assertGreaterEqual(len(facts['missing_inputs']), 3)
        self.assertEqual([], facts['created_containers'])

    def test_actual_protected_edit_negative(self):
        before = read('preservation-before.json'); after = read('preservation-after.json')
        self.assertEqual(before['protected_file_sha256'], after['protected_file_sha256'])
        self.assertEqual(before['protected_diff_sha256'], after['protected_diff_sha256'])
        self.assertEqual(before['canonical_status_before'], after['canonical_status_after'])
        self.assertTrue(set(before['user_containers']) <= set(after['running_containers']))

    def packet(self):
        return json.loads((AUDIT / 'RELEASE-REVIEW.json').read_text())

    def test_review_positive(self):
        self.assertEqual([], review_errors(self.packet(), read('publication.json')))
        facts = read('ui-observations.json')
        self.assertEqual([(1280, 720), (390, 844), (320, 740)],
                         [(row['width'], row['height']) for row in facts['layouts']])
        for row in facts['layouts']:
            self.assertEqual(row['width'], row['pageWidth'])
            self.assertEqual(('17px', '24.65px', True),
                             (row['bodySize'], row['bodyLine'], row['fontLoaded']))
            self.assertTrue(row['heading'])
        self.assertTrue(facts['empty_library'])
        self.assertTrue(facts['prepare_navigation'])
        self.assertTrue(facts['settings_saved'])
        self.assertTrue(facts['settings_reopened'])
        self.assertTrue(facts['keyboard_navigation'])
        self.assertTrue(facts['mobile_navigation'])
        self.assertFalse(facts['raw_errors'])

    def test_ux_omission_negative(self):
        packet = self.packet(); packet.pop('ui_ux')
        self.assertIn('ui_ux unsupported', review_errors(packet, read('publication.json')))

    def test_typography_omission_negative(self):
        packet = self.packet(); packet.pop('typography')
        self.assertIn('typography unsupported', review_errors(packet, read('publication.json')))
        packet = self.packet(); packet['actionable_caption_px'] = 10
        self.assertIn('caption readability', review_errors(packet, read('publication.json')))

    def test_evidence_mismatch_negative(self):
        facts = read('publication.json'); packet = self.packet()
        packet['archive_revision'] = '0' * 40
        self.assertIn('archive mismatch', review_errors(packet, facts))
        for field, value, expected in [('new_model_calls', 50, 'execution scope'),
                                      ('unexecuted_claimed_passed', True, 'unexecuted claim'),
                                      ('reference_origin', 'candidate-generated gold', 'reference origin')]:
            packet = self.packet(); packet[field] = value
            self.assertIn(expected, review_errors(packet, facts))

    def test_partial_review_negative(self):
        packet = self.packet()
        packet['ui_ux']['status'] = 'partial'
        packet['typography']['status'] = 'partial'
        errors = review_errors(packet, read('publication.json'))
        self.assertIn('ui_ux unverified', errors)
        self.assertIn('typography unverified', errors)

    def test_independent_settings_recovery_positive(self):
        facts=read('ui-observations.json')
        self.assertEqual([
            'Transient configuration read recovered automatically',
            'Unavailable connection list leaves local settings usable',
            'Failed refresh retains accepted configuration',
            'Keyboard Refresh recovered settings'],facts['states'])
        self.assertTrue(facts['original_profile_restored'])
        self.assertEqual([],facts['pageErrors'])
        calls=read('requests.json')
        self.assertFalse([c for c in calls if c.get('forbidden')])
        self.assertEqual(1,len([c for c in calls if c['mode']=='transient' and c['status']==503]))
        self.assertEqual(3,len([c for c in calls if c['mode']=='provider-unavailable' and c['status']==503]))
        self.assertEqual(3,len([c for c in calls if c['mode']=='configuration-unavailable' and c['status']==503]))
        self.assertEqual([200,200],[c['status'] for c in calls if c['method']=='PUT'])


if __name__ == '__main__':
    unittest.main()
