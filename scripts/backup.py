"""Create a consistent local database/media backup without exposing credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker', 'compose', '--env-file', str(ROOT / 'deploy/local/.env'),
           '-f', str(ROOT / 'deploy/local/compose.yaml')]


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def capture_file(argv, destination):
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        subprocess.run(argv, stdout=stream, stderr=subprocess.DEVNULL, check=True, timeout=300)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if not destination.is_relative_to((ROOT / 'data/backups').resolve()):
        raise SystemExit('Backup destination must be inside ignored data/backups.')
    destination.mkdir(parents=True, mode=0o700, exist_ok=False)
    # Explicitly quiesce every application writer, preserving persistent volumes.
    subprocess.run(COMPOSE + ['stop', 'web', 'api', 'speech'], check=True, timeout=60,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    completed = False
    try:
        capture_file(COMPOSE + ['exec', '-T', 'postgres', 'pg_dump', '-U', 'tangerine',
                               '-d', 'tangerine', '--format=custom'], destination / 'database.dump')
        capture_file(COMPOSE + ['exec', '-T', 'minio', 'tar', '-czf', '-', '-C', '/data', '.'],
                     destination / 'media.tar.gz')
        manifest = {'version': 1, 'status': 'complete',
                    'database': {'file': 'database.dump', 'sha256': file_hash(destination / 'database.dump')},
                    'media': {'file': 'media.tar.gz', 'sha256': file_hash(destination / 'media.tar.gz')},
                    'secrets_included': False,
                    'boundary': 'Quiesced database and MinIO data; local runtime secrets must be preserved separately.'}
        fd = os.open(destination / 'manifest.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            json.dump(manifest, stream, indent=2)
            stream.write('\n')
        completed = True
    finally:
        subprocess.run(COMPOSE + ['start', 'speech', 'api', 'web'], check=True, timeout=60,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if completed:
        print(json.dumps({'backup': str(destination.relative_to(ROOT)), 'status': 'complete'}))


if __name__ == '__main__':
    main()
