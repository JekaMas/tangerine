"""Restore a verified backup into a new isolated local project only.

No existing database or object-store volume is overwritten. The original running
project and its local secret configuration are preserved.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

from backup import COMPOSE
from verify_backup import verify


def run(command, *, stdin=None):
    subprocess.run(command, stdin=stdin, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True, timeout=300)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--project', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'tangerine-restore-[a-z0-9-]+', args.project):
        raise SystemExit('Use a new project named tangerine-restore-<suffix>.')
    verify(args.backup)
    for resource, label in [('volume', 'com.docker.compose.project'), ('container', 'com.docker.compose.project')]:
        command = ['docker', resource, 'ls', '--filter', label + '=' + args.project, '--format', '{{.ID}}'] if resource == 'container' else ['docker', 'volume', 'ls', '--filter', 'label=' + label + '=' + args.project, '--format', '{{.Name}}']
        if resource == 'container':
            command = ['docker', 'ps', '-a', '--filter', 'label=' + label + '=' + args.project, '--format', '{{.ID}}']
        if subprocess.check_output(command, text=True, timeout=30).strip():
            raise SystemExit('Restore project already owns resources; refusing to overwrite.')
    compose = COMPOSE + ['--project-name', args.project]
    backup = args.backup.resolve()
    with (backup / 'media.tar.gz').open('rb') as stream:
        run(compose + ['run', '--rm', '-T', '--no-deps', '--entrypoint', 'tar', 'minio', '-xzf', '-', '-C', '/data'], stdin=stream)
    run(compose + ['up', '-d', '--wait', '--wait-timeout', '120', 'postgres', 'minio'])
    with (backup / 'database.dump').open('rb') as stream:
        run(compose + ['exec', '-T', 'postgres', 'pg_restore', '-U', 'tangerine', '-d', 'tangerine', '--exit-on-error'], stdin=stream)
    result = subprocess.check_output(compose + ['exec', '-T', 'postgres', 'psql', '-U', 'tangerine', '-d', 'tangerine', '-Atc',
        "SELECT json_build_object('accounts',(SELECT count(*) FROM accounts),'exercises',(SELECT count(*) FROM exercise_catalog),'migrations',(SELECT count(*) FROM schema_migrations))"], text=True, timeout=30)
    counts = json.loads(result)
    if counts['accounts'] < 1 or counts['migrations'] < 1:
        raise SystemExit('Restored database is incomplete.')
    print(json.dumps({'status': 'restored', 'project': args.project, 'counts': counts,
                      'boundary': 'Actual isolated PostgreSQL and MinIO restore; no approved exercise/audio or full trainer acceptance.'}))


if __name__ == '__main__':
    main()
