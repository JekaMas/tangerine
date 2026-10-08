"""Validate backup hashes and archive safety before any restore action."""
import argparse
import json
from pathlib import Path
import tarfile

from backup import ROOT, file_hash


def verify(path):
    path = path.resolve()
    if not path.is_relative_to((ROOT / 'data/backups').resolve()):
        raise ValueError('Backup must remain inside ignored data/backups.')
    manifest = json.loads((path / 'manifest.json').read_text())
    if manifest.get('version') != 1 or manifest.get('status') != 'complete':
        raise ValueError('Incomplete or unsupported backup.')
    for kind, filename in [('database', 'database.dump'), ('media', 'media.tar.gz')]:
        record = manifest[kind]
        target = path / filename
        if record['file'] != filename or target.is_symlink() or file_hash(target) != record['sha256']:
            raise ValueError('Backup hash/path mismatch.')
    with tarfile.open(path / 'media.tar.gz', mode='r|gz') as archive:
        total, count = 0, 0
        for member in archive:
            relative = Path(member.name)
            total += member.size
            count += 1
            if relative.is_absolute() or '..' in relative.parts or member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError('Unsafe media archive entry.')
            if total > 100 * 1024 ** 3 or count > 1000000:
                raise ValueError('Backup exceeds reviewed restore bounds.')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    args = parser.parse_args()
    verify(args.backup)
    print('Backup hashes and media archive verified. Restore has not been performed.')
